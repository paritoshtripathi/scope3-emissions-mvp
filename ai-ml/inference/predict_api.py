from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import faiss, json, os
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from pathlib import Path
from langchain_huggingface import HuggingFaceEndpoint

load_dotenv()

# Paths clearly defined
BASE_DIR = Path(__file__).resolve().parent.parent
FAISS_INDEX_PATH = BASE_DIR / "models" / "embeddings.index"
CHUNKS_JSON_PATH = BASE_DIR / "models" / "chunks.json"

# Load embeddings clearly
embedding_model = SentenceTransformer('BAAI/bge-large-en-v1.5')
faiss_index = faiss.read_index(str(FAISS_INDEX_PATH))
with open(CHUNKS_JSON_PATH, 'r') as f:
    chunks = json.load(f)

# HuggingFace updated LLM endpoint clearly
llm = HuggingFaceEndpoint(
    huggingfacehub_api_token=os.getenv('HUGGINGFACE_API_TOKEN'),
    repo_id='meta-llama/Meta-Llama-3-8B-Instruct',
    task="text-generation",
    temperature=0.2,
    max_new_tokens=250,
    stop=["[91]", "Technical Guidance"] # clearly defined stop sequences
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
    template="""Answer the following question using only the provided context.:

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
