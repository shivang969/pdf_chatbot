import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from retrieval_graph import app_graph



from database import get_db

# FIXED: Added 'title=' keyword
app = FastAPI(title="AI PDF Chatbot API")

app.add_middleware(
    CORSMiddleware,
    # FIXED: Changed 'https' to 'http'
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="bhai mere only pdf are allowed")
    
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        text_splitters = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = text_splitters.split_documents(documents)
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        supabase_client = get_db()
        
        SupabaseVectorStore.from_documents(
            documents=chunks,
            embedding=embeddings,
            client=supabase_client,
            table_name="documents",
            query_name="match_documents"
        )
        
        return {
           "message": f"success ! '{file.filename}' processed using HuggingFace and saved to Supabase",
           "chunks_created": len(chunks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
            

class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")

async def chat_with_pdf(request:ChatRequest):
    try:
        inputs={"messages":[HumanMessage(content=request.question)]}
        
        output=app_graph.invoke(inputs)
        final_answer= output["messages"][-1].content
        
        return {
            "answer":final_answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))    