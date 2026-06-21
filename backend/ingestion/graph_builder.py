import networkx as nx

def build_document_graph(elements):
    """
    Takes a list of parsed document elements and builds a NetworkX directed graph.
    Nodes = Document elements (paragraphs, tables, headings)
    Edges = Relationships (e.g., 'FOLLOWS', 'ON_SAME_PAGE')
    """
    G = nx.DiGraph()
    
    if not elements:
        return G

    current_heading = None
    # Step 1: Add all elements as nodes
    for i, el in enumerate(elements):
        if el.get("type") == "image":
            print(
                "IMAGE FOUND:",
                el["element_id"],
                "PAGE:",
                el["page"]
            )

        node_id = el["element_id"]
        
        # Add the node with its metadata
        G.add_node(
            node_id, 
            type=el.get("type", "text"),
            page=el.get("page", 0),
            content=el.get("content", "")
        )
        element_type = el.get("type", "paragraph")

        # Track latest heading
        if element_type == "heading":
            current_heading = node_id

        # Link content to heading
        elif current_heading:
            if element_type == "image":
                print(
                    f"IMAGE LINKED TO HEADING: {current_heading}"
                )
            G.add_edge(
                current_heading,
                node_id,
                relation="BELONGS_TO_SECTION"
            )
        
        # Step 2: Create Relationships (Edges)
        # Heuristic 1: Sequential Flow (Paragraph A is followed by Paragraph B)
        if i > 0:
            prev_node_id = elements[i-1]["element_id"]
            G.add_edge(prev_node_id, node_id, relation="FOLLOWS")
            
        # Heuristic 2: Same Page Linking
        # If they are on the same page, link them to establish spatial context
        if i > 0 and elements[i-1].get("page") == el.get("page"):
             G.add_edge(prev_node_id, node_id, relation="ON_SAME_PAGE")


    image_count = 0

    for _, data in G.nodes(data=True):
        if data.get("type") == "image":
            image_count += 1

    print(f"IMAGE NODES IN GRAPH: {image_count}")
    return G