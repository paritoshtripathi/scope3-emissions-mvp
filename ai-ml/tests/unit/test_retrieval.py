"""
Unit tests for retrieval components
"""
import pytest
import numpy as np
from src.rag.retrieval.multi_vector_retriever import MultiVectorRetriever
from src.rag.retrieval.context_augmenter import ContextAugmenter

@pytest.fixture
def retriever():
    return MultiVectorRetriever()

@pytest.fixture
def augmenter():
    return ContextAugmenter()

def test_retriever_initialization(retriever):
    assert retriever is not None
    assert retriever.index is None  # Should be None until documents are added
    assert isinstance(retriever.chunks, dict)

def test_document_addition(retriever):
    documents = [
        {
            'text': 'Test document 1',
            'metadata': {'source': 'test'}
        }
    ]
    embeddings = {
        'document': [[0.1] * 768]  # Example embedding
    }
    
    retriever.add_documents(documents, embeddings)
    assert retriever.index is not None
    assert len(retriever.chunks) == 1

def test_document_retrieval(retriever):
    # Add test document
    documents = [
        {
            'text': 'Test document for retrieval',
            'metadata': {'source': 'test'}
        }
    ]
    embeddings = {
        'document': [[0.1] * 768]
    }
    retriever.add_documents(documents, embeddings)
    
    # Test retrieval
    query_embeddings = {
        'document': [0.1] * 768
    }
    results = retriever.retrieve(query_embeddings, top_k=1)
    
    assert len(results) == 1
    assert 'text' in results[0]
    assert 'score' in results[0]

def test_context_augmentation(augmenter):
    retrieved_docs = [
        {
            'text': 'Test document 1',
            'metadata': {'source': 'test1'},
            'score': 0.9
        },
        {
            'text': 'Test document 2',
            'metadata': {'source': 'test2'},
            'score': 0.7
        }
    ]
    
    result = augmenter.augment(retrieved_docs, "test query")
    
    assert 'context' in result
    assert 'sources' in result
    assert 'confidence' in result
    assert len(result['sources']) == 2
    assert result['confidence'] > 0