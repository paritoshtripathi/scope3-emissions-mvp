import os
import PyPDF2
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
import json

# Paths
PDF_PATH = "ai-ml/kb/Imp-1-Scope3_Calculation_Guidance.pdf"
OUTPUT_PATH = "ai-ml/models/combined_clean_embeddings.json"
WEB_URLS = [
    "https://ghgprotocol.org/scope-3-technical-calculation-guidance",
    "https://www.epa.gov/ghgemissions/scope-3-inventory"
]

# Clean text function
def clean_text(text):
    """Clean and preprocess text: tokenization, stopword removal, lemmatization."""
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text)
    clean_tokens = [
        lemmatizer.lemmatize(token.lower()) 
        for token in tokens 
        if token.isalnum() and token.lower() not in stop_words
    ]
    return " ".join(clean_tokens)

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
                text += clean_text(raw_text) + " "
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
                clean_content = clean_text(" ".join(paragraphs))
                combined_text += clean_content + " "
                print(f"Successfully crawled: {url}")
            else:
                print(f"Failed to fetch {url}: HTTP {response.status_code}")
        except Exception as e:
            print(f"Error crawling {url}: {e}")
    return combined_text

# Generate embeddings
def generate_embeddings(texts, model, output_path):
    """Generate embeddings using Hugging Face Sentence Transformer."""
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # Combine text and embeddings
    output_data = [{"text": text, "embedding": emb.tolist()} for text, emb in zip(texts, embeddings)]

    # Save to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4)

    print(f"Embeddings saved to: {output_path}")

# Main function
def build_clean_embeddings():
    """Build clean embeddings from PDF and web content."""
    print("Building clean embeddings for Scope 3 knowledge base...")

    # Step 1: Extract PDF text
    pdf_text = extract_text_from_pdf(PDF_PATH)
    print(f"Extracted {len(pdf_text)} characters from PDF.")

    # Step 2: Crawl web content
    web_text = crawl_web_data(WEB_URLS)
    print(f"Extracted {len(web_text)} characters from web crawling.")

    # Step 3: Combine texts
    combined_texts = [pdf_text, web_text]
    print("Combined clean PDF and web content.")

    # Step 4: Generate embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    generate_embeddings(combined_texts, model, OUTPUT_PATH)

if __name__ == "__main__":
    build_clean_embeddings()
