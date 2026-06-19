import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Connect to the local Qdrant instance running in your Docker container
client = QdrantClient("http://localhost:6333")
collection_name = "dell_document_intelligence"

# Load the embedding model (runs locally, no API keys needed)
print("Loading embedding model...")
encoder = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")

def init_qdrant():
    """Creates the Qdrant collection if it doesn't already exist."""
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

def index_graph_nodes(doc_graph):
    """
    Takes the NetworkX graph, converts the text inside each node into an embedding,
    and upserts it into the Qdrant Vector DB with its metadata.
    """
    init_qdrant()
    points = []
    
    # Iterate through every node in the graph
    for node_id, data in doc_graph.nodes(data=True):
        text_content = data.get("content", "")
        
        # Skip empty nodes
        if not text_content.strip():
            continue
            
        # Convert text to vector embedding
        vector = encoder.encode(text_content).tolist()
        
        # Package it for Qdrant
        points.append(
            PointStruct(
                id=str(uuid.uuid5(uuid.NAMESPACE_DNS, node_id)), # Generate consistent ID
                vector=vector,
                payload={
                    "element_id": node_id,
                    "type": data.get("type", "text"),
                    "page": data.get("page", 0),
                    "content": text_content
                }
            )
        )
    
    # Upsert the vectors into the database
    if points:
        client.upsert(collection_name=collection_name, points=points)
        
    return len(points)

def search_similar_nodes(query, limit=5):

    query_vector = encoder.encode(query).tolist()

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=limit
    )

    return results