"""
Integration tests for RAG pipeline
"""
import pytest
import asyncio
from src.rag import EnhancedRAGPipeline, InferenceEngine

@pytest.fixture
def pipeline():
    return EnhancedRAGPipeline()

@pytest.fixture
def inference():
    return InferenceEngine()

# Rest of the implementation remains the same