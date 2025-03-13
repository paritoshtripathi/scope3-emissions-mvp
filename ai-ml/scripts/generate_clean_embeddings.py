import os
import PyPDF2
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import json
import faiss
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

# Paths
PDF_PATH = "ai-ml/kb/Imp-1-Scope3_Calculation_Guidance.pdf"
OUTPUT_PATH = "ai-ml/models/combined_clean_embeddings.json"
FAISS_INDEX_PATH = "ai-ml/models/faiss_index"
WEB_URLS = [
    "https://ghgprotocol.org/scope-3-technical-calculation-guidance",
    "https://www.pwc.com/us/en/services/esg/library/measuring-scope-3-emissions.html",
]

# Chunk size for embeddings (measured in characters)
CHUNK_SIZE = 500

# Clean text function
def clean_text(text):
    """Clean and preprocess text."""
    
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

     # Remove placeholder content like "..."
    text = text.replace("...", "").strip()

    tokens = sent_tokenize(text)
    return [
        " ".join(
            [lemmatizer.lemmatize(token.lower()) for token in sentence.split() if token.lower() not in stop_words]
        )
        for sentence in tokens
    ]

# Updated Chunking Function with Cleaning
def chunk_and_clean_text(text, chunk_size=CHUNK_SIZE):
    """Clean and split text into smaller chunks for embedding."""
    cleaned_sentences = clean_text(text)  # Clean the text first
    chunks = []
    current_chunk = ""

    for sentence in cleaned_sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:  # Add any remaining text as the last chunk
        chunks.append(current_chunk.strip())

    return chunks

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    """Extract and clean text from a PDF file."""
    print("Extracting text from PDF...")
    text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                raw_text = page.extract_text() or ""
                text += raw_text + " "
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text

# Crawl web content
def crawl_web_data(urls):
    """Crawl content from specified URLs."""
    print("Crawling web content...")
    combined_text = ""
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                combined_text += " ".join(paragraphs) + " "
                print(f"Successfully crawled: {url}")
            else:
                print(f"Failed to fetch {url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    return combined_text

# Generate embeddings
def generate_embeddings(chunks, model):
    """Generate embeddings using Hugging Face Sentence Transformer."""
    print("Generating embeddings...")
    embeddings = model.encode(chunks, show_progress_bar=True)
    return chunks, embeddings

# Save FAISS index
def save_faiss_index(chunks, embeddings, index_path):
    """Save FAISS index using precomputed embeddings."""
    print("Creating and saving FAISS index...")
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    # Ensure embeddings are in NumPy array format
    embeddings_np = embeddings.astype("float32")

    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings_np.shape[1])
    index.add(embeddings_np)

    # Create FAISS wrapper with proper mapping
    docstore = InMemoryDocstore({str(i): {"text": chunks[i]} for i in range(len(chunks))})
    index_to_docstore_id = {i: str(i) for i in range(len(chunks))}
    vector_store = FAISS(
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"),
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    
    print("Index to Docstore Mapping:", index_to_docstore_id)

    # Save FAISS index to disk
    vector_store.save_local(index_path)
    print(f"FAISS index saved to: {index_path}")

# Save embeddings to JSON
def save_embeddings_to_json(chunks, embeddings, output_path):
    """Save embeddings to JSON."""
    print("Saving embeddings to JSON...")
    output_data = [{"text": chunk, "embedding": emb.tolist()} for chunk, emb in zip(chunks, embeddings)]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)
    print(f"Embeddings saved to: {output_path}")

# Main function
# Updated Chunking Function with Cleaning
def chunk_and_clean_text(text, chunk_size=CHUNK_SIZE):
    """Clean and split text into smaller chunks for embedding."""
    cleaned_sentences = clean_text(text)  # Clean the text first
    chunks = []
    current_chunk = ""

    for sentence in cleaned_sentences:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:  # Add any remaining text as the last chunk
        chunks.append(current_chunk.strip())

    return chunks

def filter_chunks(chunks):
    """Remove empty or invalid chunks."""
    return [chunk for chunk in chunks if chunk.strip()]

# Main Function Updates
def build_clean_embeddings():
    """Build clean embeddings and FAISS index for Scope 3 knowledge base."""
    print("Building clean embeddings for Scope 3 knowledge base...")

    # Step 1: Extract and clean PDF text
    pdf_text = extract_text_from_pdf(PDF_PATH)
    pdf_chunks = chunk_and_clean_text(pdf_text)
    pdf_chunks = filter_chunks(pdf_chunks)

    print(f"Extracted and cleaned {len(pdf_text)} characters from PDF into {len(pdf_chunks)} chunks.")

    # Step 2: Crawl and clean web content
    web_text = crawl_web_data(WEB_URLS)
    web_chunks = chunk_and_clean_text(web_text)
    web_chunks = filter_chunks(web_chunks)

    print(f"Extracted and cleaned {len(web_text)} characters from web crawling into {len(web_chunks)} chunks.")

    # Step 3: Combine all chunks
    combined_chunks = pdf_chunks + web_chunks
    combined_chunks = filter_chunks(combined_chunks)  # Final filtering

    if not combined_chunks:
        raise ValueError("No valid content found for embeddings.")

    # Step 4: Generate embeddings
    model = SentenceTransformer("all-mpnet-base-v2")
    chunks, embeddings = generate_embeddings(combined_chunks, model)

    # Step 5: Save embeddings to JSON
    save_embeddings_to_json(chunks, embeddings, OUTPUT_PATH)

    # Step 6: Save FAISS index
    save_faiss_index(chunks, embeddings, FAISS_INDEX_PATH)

if __name__ == "__main__":
    build_clean_embeddings()
