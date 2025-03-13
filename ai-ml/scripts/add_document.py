from inference.weaviate_client import WeaviateClientSingleton

def add_documents_to_weaviate(documents):
    """
    Add a list of documents to the Weaviate collection.
    
    Each document should be a dictionary containing the necessary properties.
    """
    if not documents:
        print("No documents provided for addition.")
        return

    try:
        client = WeaviateClientSingleton.get_client()
        collection_name = "Document"
        
        # Check if the collection exists
        if not client.collections.exists(collection_name):
            raise ValueError(f"Collection '{collection_name}' does not exist.")

        # Batch add documents to the collection
        collection = client.collections.get(name=collection_name)
        with collection.batch() as batch:
            for doc in documents:
                batch.add_object(properties=doc)

        print(f"Successfully added {len(documents)} documents to the '{collection_name}' collection.")
    except Exception as e:
        print(f"Error adding documents to Weaviate: {e}")
