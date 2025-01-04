import json
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from weaviate.util import generate_uuid5
from weaviate import connect_to_local
import weaviate 
from weaviate.classes.init import AdditionalConfig, Timeout
import weaviate.classes.config as wvcc
import os
import warnings

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
WEAVIATE_URL = "http://localhost:8080"  # Update this if hosting Weaviate remotely
USE_WEAVIATE = True  # Switch between FAISS (False) and Weaviate (True)
EMBEDDING_FILE = "ai-ml/models/combined_clean_embeddings.json"
CLIENT = connect_to_local()

# Load Hugging Face Inference API Endpoint
def load_huggingface_llm():
    """Initialize Hugging Face LLM using the Hugging Face Inference API."""
    try:
        return HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
            model_kwargs={"headers": {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}}
        )
    except Exception as e:
        raise Exception(f"Failed to initialize HuggingFaceEndpoint: {e}")

# Load FAISS Vector Store with HuggingFace Embeddings
def load_faiss_store():
    """Load FAISS vector store with Hugging Face embeddings."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        return FAISS.load_local(
            "C:/PRJ/scope3-emissions-mvp/ai-ml/models/faiss_index",
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        raise Exception(f"Failed to load FAISS vector store: {e}")

# Load Weaviate Client
def load_weaviate_client():
    """Initialize Weaviate client."""
   
    try:
        client = weaviate.connect_to_local(
            port=8080,
            grpc_port=50051,
            additional_config=AdditionalConfig(
            timeout=Timeout(init=30, query=60, insert=120)  # Values in seconds
            )
        )
        # Check if the client is ready
        if client.is_ready():
            print("Connected to Weaviate successfully.")
            # Define the collection configuration
            collection_config = wvcc.CollectionConfig(
                name="Document",
                vectorizer_config=wvcc.Configure.Vectorizer.none(),
                properties=[
                    wvcc.Property(name="content", data_type=wvcc.DataType.TEXT),
                    wvcc.Property(name="vector", data_type=wvcc.DataType.NUMERIC_VECTOR),
                ]
            )

            # Create the collection
            client.collections.create(collection_config)
        else:
            print("Failed to connect to Weaviate.")
        return client
    except Exception as e:
        raise Exception(f"Failed to connect to Weaviate: {e}")
  
# Query Weaviate for similar documents
def query_weaviate(client, query):
    """Perform similarity search in Weaviate."""
    collection = client.collections.get(name="Document")
    vector = collection.vectorize(query)
    results = collection.query(
        vector_search=collection.VectorSearch(vector=vector, top_k=5),
    )
    return [doc["properties"]["content"] for doc in results.documents]

# Index clean embeddings into Weaviate
def index_clean_embeddings_weaviate(client, embedding_file):
    """Index clean embeddings from JSON into Weaviate."""
    try:
        # Load embeddings from JSON
        with open(embedding_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Access the 'Document' collection
        collection = client.collections.get("Document")
        
        # Index data into Weaviate
        with collection.batch() as batch:
            for record in data:
                content = record["text"]
                vector = record["embedding"]
                uuid = generate_uuid5(content)
                batch.add_object(
                    properties={"content": content},
                    vector=vector,
                    uuid=uuid
                )
        print("Embeddings successfully indexed in Weaviate.")
    except Exception as e:
        raise Exception(f"Error during indexing embeddings in Weaviate: {e}")

# Search using Weaviate
def weaviate_similarity_search(client, query, embeddings):
    """Perform similarity search in Weaviate."""
    try:
        # with weaviate.connect_to_local() as client:
        # Index clean embeddings if not already indexed
        index_clean_embeddings_weaviate(client, EMBEDDING_FILE)

        vector = embeddings.embed_query(query)  # Generate query embeddings
        results = client.query.get("Document", ["content"]) \
            .with_near_vector({"vector": vector, "certainty": 0.7}) \
            .with_limit(5) \
            .do()
        if not results["data"]["Get"]["Document"]:
            return []
        return [
            {"text": result["content"], "metadata": {"certainty": result["_additional"]["certainty"]}}
            for result in results["data"]["Get"]["Document"]
        ]
    except Exception as e:
        raise Exception(f"Error during Weaviate similarity search: {e}")

# Initialize the pipeline with a query and custom prompt
def initialize_pipeline(query, custom_prompt=None):
    """Set up the LLM and query pipeline."""
    llm = HuggingFaceEndpoint(
        endpoint_url="https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
        model_kwargs={"headers": {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}}
    )
    results = query_weaviate(CLIENT, query)
    context = " ".join(results)

    prompt = custom_prompt or (
        "As a maritime sustainability expert, analyze the following context and answer:\n\n"
        "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=None,
        chain_type_kwargs={"prompt": PromptTemplate(input_variables=["context", "question"], template=prompt)},
    )

    return chain.run({"context": context, "question": query})

# Initialize RetrievalQA pipeline with dynamic prompt support
def query_pipeline(question: str, custom_prompt: str = None) -> str:
    """
    Query pipeline that initializes the retrieval and LLM components,
    performs similarity search using either Weaviate or FAISS, and runs the QA chain.
    """
    try:
        # Load the LLM
        llama3_llm = load_huggingface_llm()

        # Load retriever based on configuration (Weaviate or FAISS)
        if USE_WEAVIATE:
            client = load_weaviate_client()
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            retriever = lambda query: weaviate_similarity_search(client, query, embeddings)
            retrieved_docs = retriever(question)
        else:
            faiss_store = load_faiss_store()
            retriever = faiss_store.as_retriever(search_kwargs={"k": 5})
            retrieved_docs = retriever.get_relevant_documents(question)

        # Check if documents were retrieved
        if not retrieved_docs:
            return {"response": "No relevant documents found."}

        # Combine retrieved results into context
        if USE_WEAVIATE:
            filtered_context = " ".join([doc["text"] for doc in retrieved_docs])
        else:
            filtered_context = " ".join([doc.page_content for doc in retrieved_docs])

        # Define the prompt template
        default_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "As a maritime sustainability expert with access to a database of Scope 3 emissions information, analyze the following data:\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n\n"
                "Provide a concise and actionable insight."
            )
        )

        # Use custom prompt if provided
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=custom_prompt
        ) if custom_prompt else default_prompt_template

        # Combine LLM and context into a QA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llama3_llm,
            retriever=None,  # We are manually managing retrieval
            chain_type_kwargs={"prompt": prompt_template}
        )

        # Prepare the input for the LLM
        input_data = {"context": filtered_context, "question": question}

        # Run the QA chain
        response = qa_chain.run(input_data)
        return {"response": response}

    except Exception as e:
        return {"response": f"An error occurred: {str(e)}"}
