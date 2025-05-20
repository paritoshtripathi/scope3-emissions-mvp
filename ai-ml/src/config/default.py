"""
Default configuration for RAG system
"""
from typing import Dict, Any

def get_default_config() -> Dict[str, Any]:
    return {
        # Model Configuration
        'models': {
            'document': 'sentence-transformers/all-mpnet-base-v2',
            'chunk': 'sentence-transformers/all-MiniLM-L6-v2',
            'semantic': 'sentence-transformers/paraphrase-multilingual-mpnet-base-v2'
        },
        
        # Processing Parameters
        'chunking': {
            'document_size': 1000,
            'paragraph_size': 300,
            'semantic_size': 100
        },
        
        # Indexing Configuration
        'indexing': {
            'type': 'IVF,Flat',
            'metric': 'l2',
            'nlist': 100,
            'embedding_dim': 768
        },
        
        # Retrieval Settings
        'retrieval': {
            'top_k': 5,
            'min_score': 0.6
        },
        
        # Agent Configuration
        'agents': {
            'max_depth': 3,
            'min_confidence': 0.7,
            'timeout': 30
        },
        
        # API Settings
        'api': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False,
            'workers': 4
        },
        
        # Monitoring
        'monitoring': {
            'log_level': 'INFO',
            'metrics_port': 9090,
            'enable_tracing': True
        }
    }