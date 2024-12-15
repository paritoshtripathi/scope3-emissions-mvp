from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.llms import Llama

# Initialize LangChain pipeline
def initialize_pipeline():
    # Load the FAISS vector store
    vectorstore = FAISS.load_local("ai-ml/models/faiss_index", Llama(model_path="llama3"))
    # Create a Retrieval-based QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=Llama(model_path="llama3"),
        retriever=vectorstore.as_retriever(),
        return_source_documents=True
    )
    return qa_chain

# Process a user query
def query_pipeline(question: str):
    qa_chain = initialize_pipeline()
    response = qa_chain.run(question)
    return response
