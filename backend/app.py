import os
import shutil
import atexit
from quart import Quart, request, jsonify
from quart_cors import cors

from loaders import load_documents
from rag_chain import build_vector_store, answer_question

from speech.stt import speech_to_text
from speech.tts import text_to_speech

app = Quart(__name__)
app = cors(app, allow_origin="*")

UPLOAD_FOLDER = "sample_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

from quart import send_from_directory

@app.route("/audio/<filename>")
async def serve_audio(filename):
    return await send_from_directory(UPLOAD_FOLDER, filename)

VECTOR_STORE_READY = False


@app.route("/upload", methods=["POST"])
async def upload_files():
    """Upload up to 5 .txt files and rebuild FAISS vector store."""

    form = await request.files

    if not form:
        return jsonify({"error": "No files uploaded"}), 400

    # Ensure folder exists (DO NOT DELETE)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    saved_files = []

    for key, file in form.items():

        if file.filename.endswith(".txt"):

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)

            # overwrite if file already exists
            if os.path.exists(filepath):
                os.remove(filepath)

            await file.save(filepath)

            saved_files.append(file.filename)

    if not saved_files:
        return jsonify({"error": "No valid .txt files uploaded"}), 400

    docs = load_documents(UPLOAD_FOLDER)

    if not docs:
        return jsonify({"error": "No readable text content found"}), 400

    build_vector_store(docs)

    global VECTOR_STORE_READY
    VECTOR_STORE_READY = True

    return jsonify({
        "message": f"Uploaded {len(saved_files)} files successfully!",
        "files": saved_files
    })

@app.route("/ask", methods=["POST"])
async def ask_question():

    if not VECTOR_STORE_READY:
        return jsonify({"error": "Please upload files first"}), 400

    data = await request.get_json()

    question = data.get("question")
    question_lang = data.get("question_lang", "en").lower().strip()
    answer_lang = data.get("answer_lang", "en").lower().strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    print(f"Received question: {question} | QLang: {question_lang} | ALang: {answer_lang}")

    result = answer_question(question, question_lang, answer_lang)

    answer_text = result["answer"]

    audio_file = text_to_speech(answer_text, answer_lang)

    return jsonify({
        "answer": answer_text,
        "source": result["source"],
        "audio_file": audio_file
    })

@app.route("/ask-voice", methods=["POST"])
async def ask_voice():

    if not VECTOR_STORE_READY:
        return jsonify({"error": "Please upload files first"}), 400

    form = await request.form
    files = await request.files

    question_lang = form.get("question_lang", "en").lower().strip()
    answer_lang = form.get("answer_lang", "en").lower().strip()

    if "audio" not in files:
        return jsonify({"error": "Audio file missing"}), 400

    audio = files["audio"]

    audio_path = os.path.join(UPLOAD_FOLDER, "voice_question.wav")

    await audio.save(audio_path)

    print("🎤 Received voice question")

    question_text = speech_to_text(audio_path)

    print("🗣 Transcribed question:", question_text)

    result = answer_question(question_text, question_lang, answer_lang)

    answer_text = result["answer"]

    audio_file = text_to_speech(answer_text, answer_lang)

    return jsonify({
        "question": question_text,
        "answer": answer_text,
        "source": result["source"],
        "audio_file": audio_file
    })




@app.route("/cleanup", methods=["POST"])
async def cleanup_files():
    """Manual cleanup triggered from frontend."""
    try:
        if os.path.exists(UPLOAD_FOLDER):
            shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        if os.path.exists("faiss_multilang_index"):
            shutil.rmtree("faiss_multilang_index")

        global VECTOR_STORE_READY
        VECTOR_STORE_READY = False

        return jsonify({"message": "🧹 Cleanup successful. All uploaded files removed!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def auto_cleanup():
    """Auto delete temp files when backend stops."""
    # if os.path.exists(UPLOAD_FOLDER):
    #     shutil.rmtree(UPLOAD_FOLDER)
    if os.path.exists("faiss_multilang_index"):
        shutil.rmtree("faiss_multilang_index")
    print("🧹 Auto-cleanup complete — temporary data removed.")


atexit.register(auto_cleanup)


if __name__ == "__main__":
    print("Starting Talk2Books backend (multi-language, temp session mode)...")
    app.run(host="0.0.0.0", port=5000)