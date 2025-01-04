import weaviate
from embedding_manager import EmbeddingManager
from scripts.generate_clean_embeddings import clean_text_data

# Initialize Weaviate client
weaviate_client = weaviate.connect_to_local()

# Initialize Embedding Manager
embedding_manager = EmbeddingManager(weaviate_client)

def generate_embeddings():
    """Generate embeddings from combined sources."""
    # Step 1: Collect raw text data
    from scripts.crawl_web import crawl_web_content
    from scripts.extract_pdf import extract_pdf_text
    from scripts.add_documents import load_additional_documents

    web_data = crawl_web_content(["https://example.com/scope3"])
    pdf_data = extract_pdf_text("path_to_guidance.pdf")
    additional_data = load_additional_documents("path_to_folder")

    # Combine all text data
    combined_data = web_data + pdf_data + additional_data

    # Step 2: Clean the text
    cleaned_data = clean_text_data(combined_data)

    # Step 3: Generate embeddings
    embedding_manager.index_documents(cleaned_data)
    print("Embeddings successfully created!")

if __name__ == "__main__":
    generate_embeddings()
