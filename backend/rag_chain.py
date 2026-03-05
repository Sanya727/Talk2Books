import os
import shutil
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from deep_translator import GoogleTranslator
from langdetect import detect

# Directory to store temporary uploads
DOCS_DIR = "sample_docs"
INDEX_PATH = "faiss_multilang_index"

# --- Load and split documents ---
def load_documents(folder_path):
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            continue

        loader = TextLoader(file_path, encoding="utf-8")
        data = loader.load()

        try:
            lang = detect(data[0].page_content)
        except:
            lang = "unknown"

        splits = splitter.split_documents(data)
        for doc in splits:
            doc.metadata["source"] = file_name
            doc.metadata["lang"] = lang
        docs.extend(splits)
        print(f"✅ Processed {file_name} | Detected language: {lang} | Chunks: {len(splits)}")

    print(f"\n📚 Total document chunks loaded: {len(docs)}")
    return docs


# --- Build FAISS vector store ---
def build_vector_store(docs):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

    if not docs:
        print("⚠️ No documents found to embed.")
        return None

    print("🔍 Building FAISS vector store...")
    store = FAISS.from_documents(docs, embeddings)
    store.save_local(INDEX_PATH)
    print(f"✅ FAISS vector store saved at: {INDEX_PATH}")
    return store


# --- Load or rebuild FAISS store ---
def load_or_create_store():
    if os.path.exists(INDEX_PATH):
        print(f"📂 Loading FAISS index from {INDEX_PATH}...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        print("⚠️ No FAISS index found, please upload files first.")
        return None


# --- Answer a question ---
def answer_question(question, question_lang="en", answer_lang="en"):
    print(f"🈶 Question Lang: {question_lang} | Target Answer Lang: {answer_lang}")

    # Load FAISS vector store
    store = load_or_create_store()
    if store is None:
        return {"answer": "No data available. Please upload files first.", "source": None}

    # Translate the input question to English (for retrieval)
    try:
        translated_query = GoogleTranslator(source=question_lang, target="en").translate(question)
    except Exception as e:
        translated_query = question
        print("⚠️ Translation to English failed:", e)

    print(f"🔁 Translated Query: {translated_query}")

    # Perform retrieval
    retriever = store.as_retriever(search_kwargs={"k": 3})
    try:
    # ✅ Compatible with new LangChain versions
        results = retriever.invoke(translated_query)
    except Exception as e:
        print("❌ Retrieval error:", e)
        return {"answer": "Error retrieving documents.", "source": None}


    if not results:
        return {"answer": "No relevant information found in the uploaded files.", "source": None}

    # Prepare context from retrieved documents
    context = "\n\n".join([d.page_content for d in results[:3]])
    source_files = list(set([d.metadata.get("source", "unknown") for d in results]))

    # Use Ollama LLM to generate the answer
    llm = OllamaLLM(model="qwen2.5:3b")
    prompt = f"Based on the following text, answer the question briefly:\n\n{context}\n\nQuestion: {translated_query}\nAnswer:"

    try:
        answer_en = llm.invoke(prompt)
    except Exception as e:
        print("❌ LLM error:", e)
        return {"answer": "Model failed to generate answer.", "source": source_files}

    # Translate answer back to target language (if not English)
    final_answer = answer_en
    if answer_lang != "en":
        try:
            final_answer = GoogleTranslator(source="en", target=answer_lang).translate(answer_en)
        except Exception as e:
            print("⚠️ Translation back to target failed:", e)

    print(f"💭 Generating answer in {answer_lang}...")
    print(f"✅ Answer generated successfully in {answer_lang}.")

    return {"answer": final_answer, "source": ", ".join(source_files)}


# --- Optional: run standalone test ---
if __name__ == "__main__":
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR, exist_ok=True)

    docs = load_documents(DOCS_DIR)
    if docs:
        build_vector_store(docs)
    else:
        print("⚠️ No docs found in sample_docs folder.")
