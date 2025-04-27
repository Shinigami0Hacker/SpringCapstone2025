import argparse
import io
import os
import tempfile
import wave
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from peft import PeftModel

def load_lora_model(model_path=""):
    """Load base model with LoRA adapters"""
    model = WhisperForConditionalGeneration.from_pretrained(base_model_name)
    processor = WhisperProcessor.from_pretrained(base_model_name)
    
    model = PeftModel.from_pretrained(model, lora_weights_path)
    
    model = model.merge_and_unload()
    
    return model, processor

def record_audio_with_vad():
    """Capture audio from microphone using VAD to detect speech presence"""
    sample_rate = 16000
    frame_duration = 30
    chunk_size = int(sample_rate * frame_duration / 1000)
    vad = webrtcvad.Vad(3)
    
    audio_buffer = []
    num_silent_frames = 0
    speech_detected = False

    def callback(indata, frames, time, status):
        nonlocal num_silent_frames, speech_detected
        audio_data = (indata * 32767).astype(np.int16).tobytes()
        
        if vad.is_speech(audio_data, sample_rate):
            num_silent_frames = 0
            if not speech_detected:
                speech_detected = True
        else:
            if speech_detected:
                num_silent_frames += 1
                if num_silent_frames > 100:
                    raise sd.CallbackStop

        if speech_detected:
            audio_buffer.append(indata.copy())

    with sd.InputStream(samplerate=sample_rate, blocksize=chunk_size,
                        channels=1, dtype='float32', callback=callback):
        print("Listening...", flush=True)
        sd.sleep(100000)
    return np.concatenate(audio_buffer), sample_rate

def transcribe_audio(model, audio_np, sr):
    """Transcribe audio using Whisper model with LoRA layers"""
    audio_int16 = (audio_np * 32767).astype(np.int16)
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        with wave.open(f, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(audio_int16.tobytes())
        
    segments, _ = model.transcribe(f.name, language="en")
    os.unlink(f.name)
    return " ".join([seg.text for seg in segments])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="tiny")
    parser.add_argument("--device", type=str, default="cpu")
    args = parser.parse_args()

    model = load_lora_model()

    try:
        while True:
            audio, sr = record_audio_with_vad()
            transcript = transcribe_audio(model, audio, sr)
            print(transcript.strip(), flush=True)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()


import argparse
import os
import numpy as np
import speech_recognition as sr
import whisper
import torch

from datetime import datetime, timedelta
from queue import Queue
from time import sleep
from sys import platform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="medium", help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the english model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for mic to detect.", type=int)
    parser.add_argument("--record_timeout", default=2,
                        help="How real time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=3,
                        help="How much empty space between recordings before we "
                             "consider it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                 "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    phrase_time = None
    data_queue = Queue()
    recorder = sr.Recognizer()

    recorder.energy_threshold = args.energy_threshold

    recorder.dynamic_energy_threshold = False

    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return
        else:
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                if mic_name in name:
                    source = sr.Microphone(sample_rate=16000, device_index=index)
                    break
    else:
        source = sr.Microphone(sample_rate=16000)

    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        data = audio.get_raw_data()
        data_queue.put(data)

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Model loaded.\n")

    while True:
        try:
            now = datetime.utcnow()
            if not data_queue.empty():
                phrase_complete = False

                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_complete = True

                phrase_time = now
                
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()
                
                audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                text = result['text'].strip()

                if phrase_complete:
                    transcription.append(text)
                else:
                    transcription[-1] = text

                os.system('cls' if os.name=='nt' else 'clear')
                for line in transcription:
                    print(line)
                # Flush stdout.
                print('', end='', flush=True)
            else:
                sleep(0.25)
        except KeyboardInterrupt:
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()