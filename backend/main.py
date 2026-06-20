import os
import json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

# Ingestion Modules
from ingestion.parser import parse_document  
from ingestion.graph_builder import build_document_graph

# Retrieval Modules
from retrieval.vector_store import (
    index_graph_nodes,
    client,
    collection_name,
    encoder,
    search_similar_nodes
)
app = FastAPI()

# Configure Gemini (Fails gracefully if key is missing)
#api_key = "AQ.Ab8RN6I9aZQJJCY-id1ym68UYZrt0o0BWj-1FyZ6eLtC5dsQSw" 
# # Hardcode here temporarily if env variables keep dropping
api_key=os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# We use the standard model for text, and configure one specifically for JSON output
text_model = genai.GenerativeModel('gemini-2.5-flash')
json_model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})

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
        doc_graph = build_document_graph(elements)

        results = search_similar_nodes(payload.question)

        retrieved_chunks = []

        for point in results.points:
            retrieved_chunks.append(point.payload)

        retrieved_ids = set()

        for point in results.points:
            retrieved_ids.add(point.payload.get("element_id"))
        
        sources = []

        for point in results.points:

            sources.append({
                "page": point.payload.get("page"),
                "title": point.payload.get("content", "")[:80],
                "type": point.payload.get("type")
            })

        print("\n===== SOURCES =====")
        print(sources)
        print("===================\n")

        print("\n===== RETRIEVED CHUNKS =====")

        for chunk in retrieved_chunks:
            print(chunk)

        print("============================\n")

        retrieved_text = "\n\n".join(
            chunk["content"]
            for chunk in retrieved_chunks
        )
        
        prompt = f"""
        You are a Graph-RAG AI. Answer the user's question using the provided document.
        
        CRITICAL FORMATTING INSTRUCTION: 
        The user wants the answer presented as: {payload.format_preference}.
        If they requested 'graphical' or 'visual', use ASCII art, markdown tables, or structured diagrams. 
        If 'paragraph', use standard text. If 'bullet points', use a list.
        
        DOCUMENT TEXT:
        {retrieved_text}
        
        USER QUESTION: {payload.question}
        """
        
        class MockResponse:
            text = "TEST ANSWER"

        response = MockResponse()
        relationship_view = []

        for node_id, data in doc_graph.nodes(data=True):

            if node_id not in retrieved_ids:
                continue

            if data.get("type") == "heading":

                paragraph_count = 0
                table_count = 0

                connected_items = []

                for _, target, edge_data in doc_graph.out_edges(node_id, data=True):

                    if edge_data.get("relation") == "BELONGS_TO_SECTION":

                        target_node = doc_graph.nodes[target]

                        if target_node.get("type") == "paragraph":
                            paragraph_count += 1

                        elif target_node.get("type") == "table":
                            table_count += 1

                if paragraph_count > 0 or table_count > 0:

                    relationship_view.append({
                        "heading": data.get("content"),
                        "page": data.get("page"),
                        "paragraphs": paragraph_count,
                        "tables": table_count
                    })
        print("\n===== RELATIONSHIPS =====")
        print(relationship_view)
        print("========================\n")
        return {
            "answer": response.text,
            "strategy": "RAG Retrieval",
            "relationships": relationship_view,
            "sources": sources
        }
        
    except Exception as e:
        print(f"ASK ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))