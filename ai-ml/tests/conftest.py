"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import fixtures from test modules
pytest_plugins = [
    "tests.unit.test_embeddings",
    "tests.unit.test_processors",
    "tests.unit.test_retrieval",
    "tests.integration.test_rag_pipeline",
    "tests.integration.test_api"
]