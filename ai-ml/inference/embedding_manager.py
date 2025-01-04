import json
from inference.weaviate_client import WeaviateClientSingleton

def setup_schema(collection_name, vectorizer_model):
    """Set up the schema for Weaviate."""
    client = WeaviateClientSingleton.get_client()
    collection = client.collections.get_or_create(
        name=collection_name,
        config=init.CollectionConfig(
            vectorizer_config=init.Configure.Vectorizer.transformers(
                transformer_model=vectorizer_model
            ),
            properties=[
                init.Property(name="content", data_type=types.DataType.TEXT),
                init.Property(name="url", data_type=types.DataType.TEXT),
            ],
        ),
    )
    print(f"Schema for {collection_name} initialized.")
    return collection

def index_embeddings(json_path, collection_name):
    """Index embeddings from a JSON file into Weaviate."""
    client = WeaviateClientSingleton.get_client()
    collection = client.collections.get(name=collection_name)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for record in data:
        collection.batch.add_object(properties=record)

    print(f"Successfully indexed {len(data)} records into {collection_name}.")
