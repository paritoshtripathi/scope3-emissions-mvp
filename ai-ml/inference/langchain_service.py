from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint

import os

# Load Hugging Face Inference API Endpoint
def load_huggingface_llm():
    """Initialize Hugging Face LLM using the Hugging Face Inference API."""
    return HuggingFaceEndpoint(
        endpoint_url="https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
        headers={"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
    )

# Initialize LangChain RetrievalQA pipeline
def initialize_pipeline():
    # Load Hugging Face LLM
    llama3_llm = load_huggingface_llm()

    # Load FAISS vector store
    faiss_store = FAISS.load_local("ai-ml/models/faiss_index")

    # Define the prompt template
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "You are an assistant answering Scope 3 emissions-related questions."
            "Given the following context:\n\n{context}\n\nAnswer the following question:\n\n{question}"
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
    pipeline = initialize_pipeline()
    response = pipeline.run(question)
    return response
