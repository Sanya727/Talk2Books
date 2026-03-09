import uuid
from gtts import gTTS
import os

OUTPUT_FOLDER = "sample_docs"

def text_to_speech(text, lang="en"):

    filename = f"audio_{uuid.uuid4().hex}.mp3"

    filepath = os.path.join(OUTPUT_FOLDER, filename)

    tts = gTTS(text=text, lang=lang)

    tts.save(filepath)

    return filename