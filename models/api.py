import io
import wave
import io

def transcript(model, audio_bytes):
    audio_stream = io.BytesIO(audio_bytes)
    segments, _ = model.transcribe(audio_stream, language="vi")
    return "".join(segment.text for segment in segments)