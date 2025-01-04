import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

INDEX_PATH = "ai-ml/models/faiss_index"

def inspect_faiss_index():
    """Inspect the FAISS index and metadata."""
    print("Inspecting FAISS index and mappings...")
    count=0
    try:
        # Load the embedding model used during index creation
        embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        
        # Load the FAISS index
        vector_store = FAISS.load_local(INDEX_PATH, embeddings=embeddings_model, allow_dangerous_deserialization=True)

        # Extract details from the FAISS index
        index = vector_store.index
        docstore = vector_store.docstore._dict
        index_to_docstore_id = vector_store.index_to_docstore_id

        print(f"FAISS index contains {index.ntotal} vectors.")
        print(f"Number of documents in the docstore: {len(docstore)}")
        # print("Docstore contents:")
        # for doc_id, doc_content in docstore.items():
        #     print(f"ID: {doc_id}, Content: {doc_content['text'][:200]}...")  # Show first 200 characters of each document
        # print(f"Index to Docstore Mapping: {index_to_docstore_id}")

        # Validate mappings
        for idx, doc_id in vector_store.index_to_docstore_id.items():
            if doc_id not in vector_store.docstore._dict:
                print(f"WARNING: ID {doc_id} in index_to_docstore_id not found in docstore!")
            else:
                count+=1
        print(f"ID {count} found in docstore")

        # Check the number of vectors in the FAISS index
        print(f"FAISS index contains {index.ntotal} vectors.")

        # Retrieve and verify individual vector mappings
        for i in range(index.ntotal):
            vector = index.reconstruct(i)
            print(f"Vector {i}: {vector}")

    except Exception as e:
        print(f"Error inspecting FAISS index and mappings: {e}")

if __name__ == "__main__":
    inspect_faiss_index()
