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

        print(f"TOTAL ELEMENTS: {len(elements)}")

        for el in elements:
            if el["type"] == "image":
                print(el)
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
        print("\n===== TOP RETRIEVED CHUNKS =====")

        for point in results.points:
            print(
                point.payload.get("type"),
                "| Page:",
                point.payload.get("page"),
                "| Score:",
                round(point.score, 3)
            )
            print(point.payload.get("content", "")[:120])
            print("----------------")

        print("===============================\n")

        retrieved_chunks = []

        for point in results.points:
            retrieved_chunks.append(point.payload)
        
        expanded_context = []

        retrieved_ids = []
        score_lookup = {}

        for point in results.points:

            retrieved_ids.append(
                point.payload.get("element_id")
            )

            score_lookup[
                point.payload.get("element_id")
            ] = point.score

        for point in results.points:
            retrieved_ids.append(point.payload.get("element_id"))
        
        expanded_context.append(
            point.payload.get("content", "")
        )
        sources = []
        seen_sources = set()

        for point in results.points:
            page = point.payload.get("page")
            title = point.payload.get("content", "")[:80]

            source_key = (page, title)

            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)


            sources.append({
                "page": point.payload.get("page"),
                "title": point.payload.get("content", "")[:80],
                "type": point.payload.get("type"),
                "confidence": round(point.score * 100, 1),
                "reason": "Direct match to user query"
                            if point.score > 0.85
                            else "Supporting contextual evidence"
                            
            })
            print(point.payload.get("content", "")[:50])
            print("SCORE:", point.score)
            print("-----------")

        print("\n===== SOURCES =====")
        print(sources)
        print("===================\n")

        print("\n===== RETRIEVED CHUNKS =====")

        for chunk in retrieved_chunks:
            print(chunk)

        print("============================\n")

        for node_id in retrieved_ids:

            if node_id not in doc_graph:
                continue

            for _, target, edge_data in doc_graph.out_edges(node_id, data=True):

                if edge_data.get("relation") == "BELONGS_TO_SECTION":

                    target_node = doc_graph.nodes[target]

                    expanded_context.append(
                        target_node.get("content", "")
                    )
        print("\n===== EXPANDED CONTEXT COUNT =====")
        print(len(expanded_context))
        print("============================\n")
        retrieved_text = "\n\n".join(expanded_context)
        
        print("\n===== EXPANDED CONTEXT =====")
        print(retrieved_text[:2000])
        print("============================\n")

        prompt = f"""
        You are an advanced Graph-RAG system.

        The document has already been expanded using graph relationships.

        Each heading contains supporting paragraphs, tables, and images.

        Use the graph context below to answer the user's question.
        IMPORTANT:

       The PRIMARY SECTION is the most relevant evidence.

        Answer primarily using information from the PRIMARY SECTION.

        Use SUPPORTING SECTIONS only when necessary for additional context.
        If the PRIMARY SECTION has a relevance score at least 15% higher than a SUPPORTING SECTION,
        prioritize the PRIMARY SECTION and only briefly mention the supporting section if it directly contributes to answering the question.
        Do not merge unrelated sections.
        GRAPH CONTEXT:
        {expanded_context}

        QUESTION:
        {payload.question}

        Instructions:
        1. Synthesize information across related components.
        2. Mention relevant sections when appropriate.
        3. Do not answer from a single paragraph.
        4. Combine evidence across headings if necessary.
        5. Cite page numbers when useful.
        """
        class MockResponse:
            text = "TEST ANSWER"

        response = MockResponse()

        #response = text_model.generate_content(prompt)
        relationship_view = []

        for node_id, data in doc_graph.nodes(data=True):

            if node_id not in retrieved_ids:
                continue

            if data.get("type") == "heading":

                connected_items = []

                for _, target, edge_data in doc_graph.out_edges(node_id, data=True):

                    if edge_data.get("relation") == "BELONGS_TO_SECTION":

                        target_node = doc_graph.nodes[target]

                        connected_items.append({
                            "type": target_node.get("type"),
                            "page": target_node.get("page"),
                            "content": target_node.get("content", "")[:100],
                            "full_content": target_node.get("content", "")
                        })

                if connected_items:

                    relationship_view.append({
                        "heading": data.get("content"),
                        "page": data.get("page"),
                        "score": score_lookup.get(node_id, 0),
                        "components": connected_items
                    })
                    relationship_view.sort(
                        key=lambda x: x["score"],
                        reverse=True
                    )
        print("\n===== RELATIONSHIPS =====")
        print(relationship_view)
        print("========================\n")

        overall_confidence = round(
            sum(point.score for point in results.points)
            / len(results.points)
            * 100,
            1
        )

        expanded_context = ""

        for i, rel in enumerate(relationship_view):

            if i == 0:
                expanded_context += "\n\n===== PRIMARY SECTION =====\n"
            else:
                expanded_context += "\n\n===== SUPPORTING SECTION =====\n"

            expanded_context += (
                f"HEADING: {rel['heading']}\n"
                f"PAGE: {rel['page']}\n"
                f"RELEVANCE: {rel['score']:.2f}\n"
                f"RELATED COMPONENTS:\n"
            )

            for comp in rel["components"]:

                expanded_context += (
                    f"- {comp['type'].upper()} "
                    f"(Page {comp['page']}): "
                    f"{comp['full_content']}\n"
                )
                print("\n===== GRAPH CONTEXT LENGTH =====")
                print(len(expanded_context))
                print("================================\n")
                print("\n===== GRAPH CONTEXT =====")
                print(expanded_context[:5000])
                print("=========================\n")
        print("SOURCES COUNT:",len(sources))

        total_paragraphs = 0
        total_images = 0
        total_tables = 0

        for rel in relationship_view:

            total_paragraphs += len([
                c for c in rel.get("components", [])
                if c.get("type") == "paragraph"
            ])

            total_images += len([
                c for c in rel.get("components", [])
                if c.get("type") == "image"
            ])

            total_tables += len([
                c for c in rel.get("components", [])
                if c.get("type") == "table"
            ])
        return {
            "answer": response.text,
            "strategy": "RAG Retrieval",
            "relationships": relationship_view,
            "sources": sources,
            "confidence": overall_confidence,
            "stats": {
                "headings": len(relationship_view),
                "paragraphs": total_paragraphs,
                "images": total_images,
                "tables": total_tables,
                "sources": len(sources)
            }
        }
        
    except Exception as e:
        print(f"ASK ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))