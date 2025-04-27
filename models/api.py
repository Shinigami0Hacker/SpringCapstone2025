import io
def transcript(model, audio):
    transcription = ""
    audio_stream = io.BytesIO(audio)
    segments, _ = model.transcribe(audio_stream)
    for segment in segments:
        transcription += segment.text
    return transcription