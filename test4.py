# from faster_whisper import WhisperModel
# import io
# pip install webrtcvad

# pipeline = Pipeline.from_pretrained("pyannote/voice-activity-detection")
# vad = pipeline("audio.wav")

# for speech_region in vad.get_timeline():
#     print(f"Speech from {speech_region.start:.2f} to {speech_region.end:.2f} seconds")

# model = WhisperModel(
#     "models/hubs/pho-whisper-tiny",
#     compute_type="int8",
#     device="cpu",
#     cpu_threads=4
# )

# def transcript(model, audio):
#     transcription = ""
#     audio_stream = io.BytesIO(audio)
#     segments, _ = model.transcribe(audio_stream)
#     for segment in segments:
#         transcription += segment.text
#     return transcription

# # Fill in the missing part:12345.mp3
audio_path = r"C:\Users\skt1t\Downloads\123321321.wav"

# with open(audio_path, "rb") as f:
#     audio = f.read()

# print(transcript(model, audio))

import webrtcvad

def vad_func(f, threshold = 0.7):
    sample_rate = f.getframerate()
    audio = f.readframes(f.getnframes())
    vad = webrtcvad.Vad()
    vad.set_mode(3)
    frame_duration = 30
    frame_size = int(sample_rate * frame_duration / 1000) * 2
    frames = [audio[i:i + frame_size] for i in range(0, len(audio), frame_size)]

    total_frames_have_speech = 0
    for i, frame in enumerate(frames):
        if len(frame) < frame_size:
            continue
        is_speech = vad.is_speech(frame, sample_rate)
        if is_speech:
            total_frames_have_speech += 1
    return True if (total_frames_have_speech / len(frames)) > threshold else False

