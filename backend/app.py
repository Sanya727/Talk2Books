import os
import shutil
import atexit
from quart import Quart, request, jsonify
from quart_cors import cors

from loaders import load_documents
from rag_chain import build_vector_store, answer_question

app = Quart(__name__)
app = cors(app, allow_origin="*")

UPLOAD_FOLDER = "sample_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VECTOR_STORE_READY = False


@app.route("/upload", methods=["POST"])
async def upload_files():
    """Upload up to 5 .txt files and rebuild FAISS vector store."""

    form = await request.files

    if not form:
        return jsonify({"error": "No files uploaded"}), 400

    # ✅ Ensure folder exists (DO NOT DELETE)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    saved_files = []

    for key, file in form.items():

        if file.filename.endswith(".txt"):

            filepath = os.path.join(UPLOAD_FOLDER, file.filename)

            # ✅ overwrite if file already exists
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
    """Handle multilingual questions."""
    if not VECTOR_STORE_READY:
        return jsonify({"error": "Please upload files first"}), 400

    data = await request.get_json()
    question = data.get("question")
    question_lang = data.get("question_lang", "en").lower().strip()
    answer_lang = data.get("answer_lang", "en").lower().strip()

    if not question:
        return jsonify({"error": "Question is required"}), 400

    print(f"🈶 Received question: {question} | QLang: {question_lang} | ALang: {answer_lang}")

    # Call RAG pipeline with both language parameters
    result = answer_question(question, question_lang, answer_lang)

    # Ensure JSON structure
    if isinstance(result, dict):
        return jsonify(result)
    else:
        return jsonify({"answer": result})


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
    print("🚀 Starting Talk2Books backend (multi-language, temp session mode)...")
    app.run(host="0.0.0.0", port=5000)
