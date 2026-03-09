import os
import shutil
import atexit
from quart import Quart, request, jsonify, send_from_directory
from quart_cors import cors

from loaders import load_documents
from rag_chain import build_vector_store, answer_question

from speech.stt import speech_to_text
from speech.tts import text_to_speech

app = Quart(__name__)
app = cors(app, allow_origin="*")

UPLOAD_FOLDER = "sample_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VECTOR_READY = False

ALLOWED_TYPES = (".txt", ".pdf", ".docx", ".pptx")


@app.route("/audio/<filename>")
async def serve_audio(filename):
    return await send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/upload", methods=["POST"])
async def upload_files():

    form = await request.files

    if not form:
        return jsonify({"error": "No files uploaded"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # SAFE CLEANUP
    for f in os.listdir(UPLOAD_FOLDER):
        try:
            os.remove(os.path.join(UPLOAD_FOLDER, f))
        except:
            pass

    saved_files = []

    for key, file in form.items():
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        await file.save(filepath)
        saved_files.append(file.filename)

    if not saved_files:
        return jsonify({"error": "No valid files uploaded"}), 400

    docs = load_documents(UPLOAD_FOLDER)

    if not docs:
        return jsonify({"error": "No readable data found"}), 400

    build_vector_store(docs)

    global VECTOR_READY
    VECTOR_READY = True

    return jsonify({
        "message": "Files processed successfully",
        "files": saved_files
    })


@app.route("/ask", methods=["POST"])
async def ask():

    if not VECTOR_READY:
        return jsonify({"error": "Upload files first"}), 400

    data = await request.get_json()

    question = data.get("question")

    q_lang = data.get("question_lang", "en")
    a_lang = data.get("answer_lang", "en")

    result = answer_question(question, q_lang, a_lang)

    answer_text = result["answer"]

    audio_file = text_to_speech(answer_text, a_lang)

    return jsonify({
        "answer": answer_text,
        "source": result["source"],
        "audio_file": audio_file
    })


@app.route("/ask-voice", methods=["POST"])
async def ask_voice():

    if not VECTOR_READY:
        return jsonify({"error": "Upload files first"}), 400

    form = await request.form
    files = await request.files

    q_lang = form.get("question_lang", "en")
    a_lang = form.get("answer_lang", "en")

    if "audio" not in files:
        return jsonify({"error": "Audio missing"}), 400

    audio = files["audio"]

    audio_path = os.path.join(UPLOAD_FOLDER, "voice_question.wav")

    await audio.save(audio_path)

    print("Voice question received")

    question_text = speech_to_text(audio_path)

    print("Transcribed:", question_text)

    result = answer_question(question_text, q_lang, a_lang)

    answer_text = result["answer"]

    audio_file = text_to_speech(answer_text, a_lang)

    return jsonify({
        "question": question_text,
        "answer": answer_text,
        "source": result["source"],
        "audio_file": audio_file
    })


@app.route("/cleanup", methods=["POST"])
async def cleanup():

    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)

    if os.path.exists("faiss_index"):
        shutil.rmtree("faiss_index")

    os.makedirs(UPLOAD_FOLDER)

    return jsonify({"message": "Cleaned"})


def auto_cleanup():

    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)

    if os.path.exists("faiss_index"):
        shutil.rmtree("faiss_index")


atexit.register(auto_cleanup)


if __name__ == "__main__":

    print("🚀 Talk2Books server started")

    app.run(host="0.0.0.0", port=5000)