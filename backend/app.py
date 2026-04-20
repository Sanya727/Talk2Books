import os
import shutil
from quart import Quart, request, jsonify
from quart_cors import cors

from loaders import load_documents, load_documents_from_text
from rag_chain import build_vector_store, answer_question
from external_sources import get_youtube_transcript, get_website_text

app = Quart(__name__)
app = cors(app, allow_origin="*")

UPLOAD_FOLDER = "sample_docs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

VECTOR_READY = False


@app.route("/upload", methods=["POST"])
async def upload_files():

    form = await request.files

    saved = []

    for key, file in form.items():

        path = os.path.join(UPLOAD_FOLDER, file.filename)

        await file.save(path)

        saved.append(file.filename)

    docs = load_documents(UPLOAD_FOLDER)

    if not docs:
        return jsonify({"error": "No readable documents"}), 400

    build_vector_store(docs)

    global VECTOR_READY
    VECTOR_READY = True

    return jsonify({"message": "Documents indexed"})


@app.route("/youtube", methods=["POST"])
async def youtube():

    data = await request.get_json()

    url = data.get("url")

    text = get_youtube_transcript(url)

    if not text:
        return jsonify({"error": "Transcript not available"}), 400

    docs = load_documents_from_text(text, "youtube")

    build_vector_store(docs)

    global VECTOR_READY
    VECTOR_READY = True

    return jsonify({"message": "YouTube transcript indexed"})


@app.route("/website", methods=["POST"])
async def website():

    data = await request.get_json()

    url = data.get("url")

    text = get_website_text(url)

    docs = load_documents_from_text(text, "website")

    build_vector_store(docs)

    global VECTOR_READY
    VECTOR_READY = True

    return jsonify({"message": "Website indexed"})


@app.route("/ask", methods=["POST"])
async def ask():

    if not VECTOR_READY:
        return jsonify({"error": "No indexed data"}), 400

    data = await request.get_json()

    question = data.get("question")
    question_lang = data.get("question_lang")
    answer_lang = data.get("answer_lang")

    result = answer_question(question, question_lang, answer_lang)

    return jsonify(result)


if __name__ == "__main__":

    print("Server started")

    app.run(host="0.0.0.0", port=5000)