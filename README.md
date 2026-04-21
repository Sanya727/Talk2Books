# Talk2Books – Multilingual RAG System

Talk2Books is a **Retrieval-Augmented Generation (RAG)** based question answering system that allows users to upload documents and ask questions in **multiple languages**.

The system retrieves relevant document chunks using **FAISS vector search** and generates answers using a **Large Language Model (LLM) via Ollama**.

---

# Features

-  Upload documents (.txt)
-  Ask questions in multiple languages
  - English
  - Hindi
  - Punjabi
-  Semantic search using **FAISS vector database**
-  AI-generated answers using **Ollama LLM**
-  Simple and interactive web interface
-  Retrieval-Augmented Generation pipeline

---



# Quick Start (Docker)
The easiest way to run this project is using **Docker**, which automatically sets up all dependencies including the backend API and Ollama server.

### 1) Install Docker Desktop
Download from:  
https://www.docker.com/products/docker-desktop

### 2) Clone the repository

git clone https://github.com/Sanya727/Talk2Books.git  
cd Talk2Books

### 3) Start the system

docker compose up --build

This will start:
- Backend API
- Ollama server

### 4) Download the LLM model

Open another terminal and run:
docker exec -it talk2books_ollama ollama pull qwen2.5:3b

### 5) Open the frontend

Open the file:
frontend/index.html
in your browser and start asking questions.


Alternative: Run Without Docker
1) Create virtual environment

python -m venv venv
venv\Scripts\activate

2) Install dependencies

pip install -r requirements.txt

3) Run backend

cd backend
python app.py

4) Start Ollama

Make sure Ollama is running and model is installed:

ollama run qwen2.5:3b

5) Open frontend

Open:

frontend/index.html


# Tech Stack
Backend -> Python, Quart 
Vector Database -> FAISS 
LLM -> Ollama 
Framework -> LangChain 
Embeddings -> HuggingFace 
Translation -> GoogleTranslator 
Frontend -> HTML, CSS, JavaScript 

---

# Project Structure
Talk2Books
│
├── backend
│ ├── app.py
│ ├── loaders.py
│ └── rag_chain.py
│
├── frontend
│ ├── index.html
│ ├── script.js
│ └── style.css
│
├── sample_docs
│
├── requirements.txt
│
└── README.md

---

# Installation Guide

## 1️⃣ Clone the repository

git clone https://github.com/Sanya727/Talk2Books.git
cd Talk2Books

---

## 2️⃣ Install dependencies

pip install -r requirements.txt

---

## 3️⃣ Install Ollama

Download from:
https://ollama.com

---

## 4️⃣ Pull the required model

ollama pull qwen2.5:3b

---

## 5️⃣ Run the backend server

python app.py

The backend server will start at:

http://localhost:5000

---

## 6️⃣ Open the frontend

Open the file:
frontend/index.html
in your browser.

---

# How the System Works

1️⃣ User uploads documents  
2️⃣ Documents are split into smaller chunks  
3️⃣ Chunks are converted into vector embeddings  
4️⃣ FAISS stores the embeddings  
5️⃣ User asks a question  
6️⃣ Relevant chunks are retrieved using similarity search  
7️⃣ Ollama LLM generates the final answer  

This is known as a *Retrieval-Augmented Generation (RAG)* pipeline.

---

# Example Workflow

Upload Document → Ask Question → System retrieves relevant context → LLM generates answer.

---

# Future Improvements

- Chat-style conversational interface
- Support for more languages
- Document preview feature
- Streaming LLM responses
- Deployment as a web application

---

# Author
Sanya Gupta

GitHub:  
https://github.com/Sanya727
