# predict_api.py
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import faiss, json, os
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Paths clearly defined
BASE_DIR = Path(__file__).resolve().parent
FAISS_INDEX_PATH = BASE_DIR / "models" / "embeddings.index"
CHUNKS_JSON_PATH = BASE_DIR / "models" / "chunks.json"

# Load model and embeddings clearly
embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
with open(CHUNKS_JSON_PATH, 'r') as f:
    chunks = json.load(f)

# Setup HuggingFace LLM clearly (Llama3-8B)
llm = HuggingFaceHub(
    huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_TOKEN'),
    repo_id='meta-llama/Meta-Llama-3-8B-Instruct'
)

app = FastAPI()

def retrieve_context(query, k=5):
    query_embedding = embedding_model.encode([query])
    _, indices = faiss_index.search(query_embedding, k)
    return "\n".join(chunks[i] for i in indices[0])

@app.get("/predict")
async def predict(query: str):
    context = retrieve_context(query)

    prompt = PromptTemplate(
        template="""Use the provided context to answer the question accurately:

Context:
{context}

Question:
{question}

Answer:""",
        input_variables=["context", "question"]
    )

    formatted_prompt = prompt.format(context=context, question=query)
    response = llm.invoke(formatted_prompt)
    return {"response": response}
