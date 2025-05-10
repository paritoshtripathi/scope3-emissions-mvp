# generate_embeddings.py
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss, PyPDF2, json
from pathlib import Path

# Define base path clearly relative to the script's location
BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "kb" / "Imp-1-Scope3_Calculation_Guidance.pdf"
FAISS_INDEX_PATH = BASE_DIR / "models" / "embeddings.index"
CHUNKS_JSON_PATH = BASE_DIR / "models" / "chunks.json"

# PDF extraction clearly
def extract_pdf_text(pdf_path):
    reader = PyPDF2.PdfReader(str(pdf_path))
    return "\n".join(page.extract_text() for page in reader.pages)

# Chunking clearly
def chunk_text(text, chunk_size=500, chunk_overlap=20):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

# Embedding generation clearly
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

def generate_and_store_embeddings(chunks):
    embeddings = model.encode(chunks, show_progress_bar=True)
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(embeddings)

    # Ensure the models directory clearly exists
    FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    faiss.write_index(faiss_index, str(FAISS_INDEX_PATH))

    # Save chunks clearly for RAG retrieval
    with open(CHUNKS_JSON_PATH, 'w') as f:
        json.dump(chunks, f)

if __name__ == "__main__":
    text = extract_pdf_text(PDF_PATH)
    chunks = chunk_text(text)
    generate_and_store_embeddings(chunks)
    print(f"Embeddings generated and stored at {FAISS_INDEX_PATH} and {CHUNKS_JSON_PATH}.")
    print(f"PDF text extracted from {PDF_PATH}.")