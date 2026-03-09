from faster_whisper import WhisperModel

# Load model once
model = WhisperModel("base", compute_type="int8")

def speech_to_text(audio_path: str):

    segments, info = model.transcribe(audio_path)

    text = ""

    for segment in segments:
        text += segment.text

    return text.strip()