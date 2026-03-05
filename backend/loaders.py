import os
from langdetect import detect
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# ✅ Function: detect language safely
def detect_language_safe(text):
    try:
        return detect(text)
    except:
        return "unknown"

# ✅ Function: load and chunk all supported documents
def load_documents(folder_path: str):
    all_docs = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if not os.path.isfile(file_path):
            continue

        # Load based on extension
        if file_name.lower().endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
        elif file_name.lower().endswith(".pdf"):
            loader = PyMuPDFLoader(file_path)
        elif file_name.lower().endswith(".docx"):
            loader = Docx2txtLoader(file_path)
        else:
            print(f"⚠️ Skipping unsupported file: {file_name}")
            continue

        try:
            docs = loader.load()
        except Exception as e:
            print(f"❌ Error loading {file_name}: {e}")
            continue

        # Split into chunks
        split_docs = text_splitter.split_documents(docs)

        # Detect language for metadata
        for d in split_docs:
            lang = detect_language_safe(d.page_content)
            d.metadata["language"] = lang
            d.metadata["source"] = file_name

        print(f"✅ Processed {file_name} | Detected language: {lang} | Chunks: {len(split_docs)}")
        all_docs.extend(split_docs)

    print(f"\n📚 Total document chunks loaded: {len(all_docs)}")
    return all_docs
