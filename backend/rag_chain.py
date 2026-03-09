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


def load_store():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    return FAISS.load_local(
        INDEX,
        embeddings,
        allow_dangerous_deserialization=True
    )


def answer_question(question, q_lang="en", a_lang="en"):

    store = load_store()

    try:
        q_en = GoogleTranslator(source=q_lang, target="en").translate(question)
    except:
        q_en = question

    retriever = store.as_retriever(search_kwargs={"k": 3})

    docs = retriever.invoke(q_en)

    context = "\n\n".join([d.page_content for d in docs])

    llm = OllamaLLM(model="qwen2.5:3b")

    prompt = f"""
Use the context to answer the question.

Context:
{context}

Question:
{q_en}

Answer clearly.
"""

    answer = llm.invoke(prompt)

    if a_lang != "en":

        try:
            answer = GoogleTranslator(
                source="en",
                target=a_lang
            ).translate(answer)
        except:
            pass

    return {
        "answer": answer,
        "source": list(set([d.metadata["source"] for d in docs]))
    }