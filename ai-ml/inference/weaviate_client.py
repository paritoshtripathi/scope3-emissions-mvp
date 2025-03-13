import os
import json
import weaviate
from weaviate import connect_to_local
from weaviate.exceptions import WeaviateStartUpError
from weaviate.classes.config import Property, DataType, Configure
from weaviate.classes.init import AdditionalConfig, Timeout
from scripts.crawl_web import crawl_web_content
from scripts.extract_pdf import extract_text_from_pdf
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

PDF_PATH = "ai-ml/kb/Imp-1-Scope3_Calculation_Guidance.pdf"
OUTPUT_PATH = "ai-ml/models/combined_clean_embeddings.json"
WEB_URLS = [
    "https://ghgprotocol.org/scope-3-technical-calculation-guidance",
    "https://www.pwc.com/us/en/services/esg/library/measuring-scope-3-emissions.html",
]

class WeaviateClientSingleton:
    """Singleton to manage a single instance of the Weaviate client and provide utility functions."""
    _client_instance = None

    @classmethod
    def get_client(cls):
        """Get or initialize the Weaviate client instance."""
        if cls._client_instance is None:
            try:
                cls._client_instance = connect_to_local(
                    port=8080,
                    grpc_port=50051,
                    additional_config=AdditionalConfig(
                        timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
                    ),
                    
                )
                print("Weaviate client initialized.")
            except WeaviateStartUpError as e:
                print(f"Failed to start Weaviate client: {e}")
                raise e
        return cls._client_instance

    @classmethod
    def close_client(cls):
        """Close the Weaviate client connection."""
        if cls._client_instance:
            cls._client_instance.close()
            cls._client_instance = None
            print("Weaviate client connection closed.")

    @classmethod
    def setup_collection(cls, collection_name, vectorizer_model="sentence-transformers/all-mpnet-base-v2"):
        """
        Set up a collection in Weaviate. Ensures it exists and is properly configured.
        """
        client = cls.get_client()
        if not client.collections.exists(collection_name):
            print(f"Collection '{collection_name}' does not exist. Creating...")

            # Define the properties of the collection
            properties = [
                Property(name="content", data_type=DataType.TEXT),
                Property(name="url", data_type=DataType.TEXT),
                Property(name="embedding", data_type=DataType.NUMBER_ARRAY),
            ]
            client.collections.create(
                name=collection_name,
                vectorizer_config=Configure.Vectorizer.text2vec_huggingface(
                    model=vectorizer_model,
                ),
                properties=properties
            )
            print(f"Collection '{collection_name}' created.")
        else:
            print(f"Collection '{collection_name}' already exists.")
        
            # Define the inverted index configuration with stopwords
            
    @classmethod
    def add_documents(cls, collection_name, documents):
        """
        Batch add documents to the specified collection.
        """
        cls.setup_collection(collection_name)

        client = cls.get_client()
        # if not client.collections.exists(collection_name):
        #     raise ValueError(f"Collection '{collection_name}' does not exist.")

        collection = client.collections.get(name=collection_name)
        with collection.batch() as batch:
            for doc in documents:
                batch.add_object(properties=doc)
        print(f"Successfully added {len(documents)} documents to the '{collection_name}' collection.")

    @classmethod
    def index_embeddings(cls, collection_name, json_path):
        """
        Index embeddings from a JSON file into a Weaviate collection.
        """
        cls.setup_collection(collection_name)

        client = cls.get_client()
        # if not client.collections.exists(collection_name):
        #     raise ValueError(f"Collection '{collection_name}' does not exist.")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        collection = client.collections.get(name=collection_name)
        with collection.batch() as batch:
            for record in data:
                batch.add_object(
                    properties={
                        "content": record.get("text", ""),
                        "url": record.get("url", "unknown"),
                        "embedding": record.get("embedding", []),
                    }
                )

        print(f"Successfully indexed {len(data)} records into collection '{collection_name}'.")

    @classmethod
    def generate_embeddings(cls, collection_name):
        """
        Generate embeddings from various data sources and index them into Weaviate.
        """
        try:
            cls.setup_collection(collection_name)

            # Step 1: Collect raw text data
            web_data = crawl_web_content(WEB_URLS)
            pdf_text = extract_text_from_pdf(PDF_PATH)
            additional_documents = [{"content": "Sample additional document."}]  # Replace with actual loader

            # Combine all text data
            combined_data = web_data + [{"content": pdf_text}] + additional_documents

            # Step 2: Index the data
            cls.add_documents(collection_name, combined_data)
            print("Embeddings successfully created and indexed!")
        except Exception as e:
            print(f"Error in generating embeddings: {e}")

    @classmethod
    def query_collection(cls, collection_name, query, top_k=5):
        """
        Perform a similarity search on the specified Weaviate collection.
        
        Args:
            collection_name (str): Name of the Weaviate collection.
            query (str): The search query.
            top_k (int): Number of top results to return.
        
        Returns:
            list: A list of matching documents from the collection.
        """
        try:
            cls.setup_collection(collection_name)
  
            client = cls.get_client()
  
            # if not client.collections.exists(collection_name):
            #     raise ValueError(f"Collection '{collection_name}' does not exist.")

            collection = client.collections.get(name=collection_name)
            vector = collection.vectorize(query)

            results = collection.query(
                vector_search=collection.VectorSearch(vector=vector, top_k=top_k)
            )

            if not results.documents:
                print(f"No results found for query: {query}")
                return []

            return [doc["properties"]["content"] for doc in results.documents]
        except Exception as e:
            print(f"Error querying collection '{collection_name}': {e}")
            return []


if __name__ == "__main__":
    WeaviateClientSingleton.generate_embeddings("Document")
