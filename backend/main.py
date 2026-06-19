import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai

# Ingestion Modules
from ingestion.parser import parse_document  
from ingestion.graph_builder import build_document_graph

# Retrieval Modules
from retrieval.vector_store import index_graph_nodes, client, collection_name, encoder

app = FastAPI()

# Configure Gemini (Fails gracefully if key is missing)
api_key = os.environ.get("AQ.Ab8RN6I9aZQJJCY-id1ym68UYZrt0o0BWj-1FyZ6eLtC5dsQSw") # Hardcode here temporarily if env variables keep dropping
genai.configure(api_key=api_key)

# We use the standard model for text, and configure one specifically for JSON output
text_model = genai.GenerativeModel('gemini-1.5-flash')
json_model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("data", exist_ok=True)

class QueryRequest(BaseModel):
    question: str
    format_preference: str = "paragraph" # e.g., "visual", "bullet points", "paragraph"

@app.get("/health")
def health_check():
    return {"status": "Backend is locked in and ready."}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Ingests file, builds graph, stores vectors, and saves active context."""
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
        
    try:
        elements = parse_document(file_path)
        doc_graph = build_document_graph(elements)
        indexed_count = index_graph_nodes(doc_graph)
        
        # Save active file path for global whole-document queries
        with open("data/active_file.txt", "w") as f:
            f.write(file_path)
            
        print(f"Ingestion Complete! {file.filename} | Vectors: {indexed_count}")
        return {"filename": file.filename, "status": "Success", "vectors": indexed_count}
    except Exception as e:
        print(f"UPLOAD ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze")
async def analyze_document():
    """
    Automatically called after upload. Reads the whole document and generates 
    a Summary, plus 3 Quiz questions with 'Why this answer' tracing logic.
    """
    try:
        if not os.path.exists("data/active_file.txt"):
            return {"error": "No document uploaded yet."}
            
        with open("data/active_file.txt", "r") as f:
            file_path = f.read().strip()
            
        elements = parse_document(file_path)
        full_text = "\n".join([el.get("content", "") for el in elements])
        
        prompt = f"""
        Analyze the following document and return a strictly formatted JSON object.
        The JSON must have this exact structure:
        {{
            "summary": "A 3-sentence executive summary of the document.",
            "quiz": [
                {{
                    "question": "A challenging question based on the document.",
                    "answer": "The correct answer.",
                    "why_this_answer": "Explain the pipeline of how you found this: e.g., 'Found in Section X -> Linked to Table Y -> Synthesized conclusion'."
                }}
            ]
        }}
        Generate exactly 3 quiz questions.
        
        DOCUMENT TEXT:
        {full_text[:500000]} # Safe cutoff for massive documents
        """
        
        response = json_model.generate_content(prompt)
        return json.loads(response.text)
        
    except Exception as e:
        print(f"ANALYZE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask_document(payload: QueryRequest):
    """Answers queries using WHOLE document context, applying requested formatting."""
    try:
        if not os.path.exists("data/active_file.txt"):
            return {"answer": "No document uploaded yet."}
            
        with open("data/active_file.txt", "r") as f:
            file_path = f.read().strip()
            
        elements = parse_document(file_path)
        full_text = "\n".join([el.get("content", "") for el in elements])
        
        prompt = f"""
        You are a Graph-RAG AI. Answer the user's question using the provided document.
        
        CRITICAL FORMATTING INSTRUCTION: 
        The user wants the answer presented as: {payload.format_preference}.
        If they requested 'graphical' or 'visual', use ASCII art, markdown tables, or structured diagrams. 
        If 'paragraph', use standard text. If 'bullet points', use a list.
        
        DOCUMENT TEXT:
        {full_text[:500000]}
        
        USER QUESTION: {payload.question}
        """
        
        response = text_model.generate_content(prompt)
        return {"answer": response.text, "strategy": "Global Context Window"}
        
    except Exception as e:
        print(f"ASK ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))