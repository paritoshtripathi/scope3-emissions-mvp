import os
import json
import warnings
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from inference.weaviate_client import WeaviateClientSingleton

# Ignore deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configuration
WEAVIATE_COLLECTION = "Document"
USE_WEAVIATE = True
EMBEDDING_FILE = "ai-ml/models/combined_clean_embeddings.json"
HUGGINGFACE_MODEL_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

# Load Hugging Face Inference API Endpoint
def load_huggingface_llm():
    """Initialize Hugging Face LLM using the Hugging Face Inference API."""
    try:
        return HuggingFaceEndpoint(
            endpoint_url=HUGGINGFACE_MODEL_URL,
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

# Query Pipeline
def query_pipeline(question: str, custom_prompt: str = None) -> dict:
    """
    Query pipeline that combines similarity search, RAG QA, and LLM for accurate responses.
    """
    try:
        # Load the LLM
        llm = load_huggingface_llm()

        # Retrieval logic
        if USE_WEAVIATE:
            # Perform similarity search using Weaviate
            documents = WeaviateClientSingleton.query_collection(WEAVIATE_COLLECTION, question, top_k=5)
        else:
            faiss_store = load_faiss_store()
            documents = faiss_store.as_retriever(search_kwargs={"k": 5}).get_relevant_documents(question)

        # Check if any documents were retrieved
        if not documents:
            return {"response": "No relevant documents found."}

        # Prepare context from retrieved documents
        context = " ".join(
            [doc["text"] for doc in documents] if USE_WEAVIATE else [doc.page_content for doc in documents]
        )

        # Define the prompt
        default_prompt = (
            "As a maritime sustainability expert, analyze the following context and answer:\n\n"
            "Context: {context}\n\nQuestion: {question}\n\nAnswer:"
        )
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=custom_prompt or default_prompt
        )

        # Initialize the RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=None,  # Manual retrieval (already handled)
            chain_type_kwargs={"prompt": prompt_template}
        )

        # Execute the QA chain
        response = qa_chain.run({"context": context, "question": question})
        return {"response": response}
    except Exception as e:
        return {"response": f"An error occurred: {e}"}

# Index Clean Embeddings
def index_clean_embeddings(json_path):
    """
    Index clean embeddings from a JSON file into Weaviate.
    Ensures the 'Document' collection exists before indexing.
    """
    try:
        # Ensure the collection exists
        WeaviateClientSingleton.setup_collection(
            WEAVIATE_COLLECTION,
            vectorizer_model="sentence-transformers/all-mpnet-base-v2"
        )

        # Index embeddings
        WeaviateClientSingleton.index_embeddings(WEAVIATE_COLLECTION, json_path)
    except Exception as e:
        raise Exception(f"Error during indexing embeddings in Weaviate: {e}")


# Query Weaviate for Similar Documents
def query_weaviate(query):
    """
    Perform a similarity search in Weaviate and return top matching documents.
    """
    try:
        return WeaviateClientSingleton.query_collection(WEAVIATE_COLLECTION, query, top_k=5)
    except Exception as e:
        raise Exception(f"Error querying Weaviate: {e}")

# Weaviate Similarity Search + RAG QA
def weaviate_similarity_search(query, embeddings):
    """
    Perform similarity search in Weaviate and return documents with metadata.
    """
    try:
        return WeaviateClientSingleton.query_collection(WEAVIATE_COLLECTION, query, top_k=5)
    except Exception as e:
        raise Exception(f"Error during Weaviate similarity search: {e}")

# Initialize the Pipeline
def initialize_pipeline(query, custom_prompt=None):
    """
    Initialize the pipeline for querying LLM with context retrieved via Weaviate.
    """
    try:
        llm = load_huggingface_llm()
        results = query_weaviate(query)
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
    except Exception as e:
        raise Exception(f"Error initializing pipeline: {e}")
