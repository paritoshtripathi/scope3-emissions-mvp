from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import os

# Load Hugging Face Inference API Endpoint
def load_huggingface_llm():
    """Initialize Hugging Face LLM using the Hugging Face Inference API."""
    try:
        return HuggingFaceEndpoint(
            endpoint_url="https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
            headers={"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        )
    except Exception as e:
        raise Exception(f"Failed to initialize HuggingFaceEndpoint: {e}")

# Load FAISS Vector Store with HuggingFace Embeddings
def load_faiss_store():
    """Load FAISS vector store with Hugging Face embeddings."""
    try:
        embeddings = HuggingFaceEmbeddings()
        return FAISS.load_local("ai-ml/models/faiss_index", embeddings=embeddings)
    except Exception as e:
        raise Exception(f"Failed to load FAISS vector store: {e}")

# Initialize RetrievalQA pipeline
def initialize_pipeline():
    """Initialize the LangChain RetrievalQA pipeline."""
    # Load the LLM and FAISS vector store
    llama3_llm = load_huggingface_llm()
    faiss_store = load_faiss_store()

    # Define a clean prompt template for better responses
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are an AI assistant with access to a database of Scope 3 emissions information.\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Provide a concise and accurate response."
        )
    )

    # Combine LLM and retriever into a RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llama3_llm,
        retriever=faiss_store.as_retriever(),
        chain_type_kwargs={"prompt": prompt_template}
    )
    return qa_chain

# Process a query
def query_pipeline(question: str) -> str:
    """Run the pipeline with a user question."""
    try:
        pipeline = initialize_pipeline()
        response = pipeline.run(question)
        return response
    except Exception as e:
        return f"An error occurred: {e}"
