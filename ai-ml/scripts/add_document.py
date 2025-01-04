from inference.weaviate_client import WeaviateClientSingleton

def add_documents_to_weaviate(documents):
    """Add documents dynamically to Weaviate."""
    client = WeaviateClientSingleton.get_client()
    collection = client.collections.get(name="Document")
    for doc in documents:
        collection.batch.add_object(properties=doc)
    print(f"Added {len(documents)} documents successfully.")
