import requests
import faiss
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Load your FAISS index and metadata
INDEX_PATH = "path/to/faiss_index"
DOCS_PATH = "path/to/doc_chunks.json"  # list of docs in order of embeddings
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Load on first call
model = SentenceTransformer(EMBED_MODEL)
index = faiss.read_index(INDEX_PATH)
with open(DOCS_PATH, 'r') as f:
    documents = json.load(f)

def get_rag_context(query, top_k=5):
    embedding = model.encode([query])
    scores, indices = index.search(np.array(embedding).astype('float32'), top_k)
    return "\n\n".join([documents[i] for i in indices[0]])

def generate_insights(raw_data):
    # Step 1: Run FAISS search on task
    query = "What can be visualized or analyzed from uploaded Scope 3 emissions data?"
    context = get_rag_context(query)

    # Step 2: Inject into prompt
    prompt = f"""
You are a sustainability insights agent specialized in maritime Scope 3 emissions.

Use the following KNOWLEDGE BASE CONTEXT to assist you:
{context}

Here is the raw uploaded data:
{raw_data}

Instructions:
1. Identify relevant KPIs or anomalies.
2. Create visual or card-style insights.
3. Format output as a valid JSON array using: 
   - type: tile | card | chart
   - chartType: pie | bar (for charts)
   - labels, values, message, title, value, description as needed

ONLY return valid JSON.
"""

    response = requests.post(
        "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
        headers={"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"},  # or hardcoded if testing
        json={"inputs": prompt}
    )

    try:
        output = response.json()
        return eval(output[0]["generated_text"])  # You can also use `json.loads()` if safe
    except Exception as e:
        return [{"type": "card", "message": f"Failed to generate insights: {str(e)}"}]
