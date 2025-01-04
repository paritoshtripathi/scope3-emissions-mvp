from inference.weaviate_client import WeaviateClientSingleton

def query_weaviate(query, collection_name, top_k=5):
    """Perform a similarity search on the Weaviate collection."""
    client = WeaviateClientSingleton.get_client()
    collection = client.collections.get(name=collection_name)
    vector = collection.vectorize(query)

    results = collection.query(
        vector_search=collection.VectorSearch(vector=vector, top_k=top_k)
    )

    if not results.documents:
        return []

    return [doc["properties"]["content"] for doc in results.documents]
