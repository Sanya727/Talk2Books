import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from deep_translator import GoogleTranslator

INDEX = "faiss_index"


def build_vector_store(docs):

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    store = FAISS.from_documents(docs, embeddings)

    store.save_local(INDEX)

    print("FAISS index created")


def load_store():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    return FAISS.load_local(
        INDEX,
        embeddings,
        allow_dangerous_deserialization=True
    )


def translate(text, src, tgt):

    try:
        return GoogleTranslator(source=src, target=tgt).translate(text)
    except:
        return text


def answer_question(question, question_lang, answer_lang):

    store = load_store()

    if question_lang != "en":
        question = translate(question, question_lang, "en")

    retriever = store.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(question)

    context = "\n\n".join([d.page_content for d in docs])

    llm = OllamaLLM(model="qwen2.5:3b")

    prompt = f"""
Answer based on context.

Context:
{context}

Question:
{question}
"""

    answer = llm.invoke(prompt)

    if answer_lang != "en":
        answer = translate(answer, "en", answer_lang)

    return {
        "answer": answer,
        "source": ", ".join([d.metadata["source"] for d in docs])
    }