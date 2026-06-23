# 📄 AI Document Agent (RAG-Powered Chatbot)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-orange)
![Supabase](https://img.shields.io/badge/Supabase-pgvector-3ECF8E)

An intelligent, agent-based Retrieval-Augmented Generation (RAG) system that allows users to upload PDF documents and interact with them through a conversational interface. Built with an autonomous LangGraph agent, this system doesn't just retrieve text—it reasons, searches, and performs exact mathematical calculations using custom tools.

## ✨ Key Features

* **Agentic Reasoning (LangGraph):** Implements a cyclic state-machine graph, allowing the LLM to autonomously decide when to use tools, when to search the database, and when to chat normally.
* **Smart Context Retrieval:** Uses HuggingFace embeddings (`all-MiniLM-L6-v2`) and Supabase (`pgvector`) for highly accurate semantic similarity search.
* **Custom Tool Execution:** Includes a built-in Python calculator tool, bypassing standard LLM arithmetic hallucinations to provide 100% accurate mathematical answers.
* **Decoupled Architecture:** A robust FastAPI backend handling heavy AI processing, completely separated from a lightweight, reactive Streamlit frontend.
* **Streaming-Ready:** Engineered to support conversational memory and context retention across sessions.

## 🏗️ Tech Stack

* **Backend:** FastAPI, Python, Uvicorn
* **Frontend:** Streamlit, Requests
* **AI & Orchestration:** LangChain, LangGraph, OpenRouter (GPT-3.5-Turbo)
* **Database:** Supabase (PostgreSQL with `pgvector` and `JSONB` metadata filtering)
* **Embeddings:** HuggingFace

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/pdf-chatbot.git](https://github.com/YOUR_USERNAME/pdf-chatbot.git)
cd pdf-chatbot