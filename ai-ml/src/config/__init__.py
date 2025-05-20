"""
Configuration management for RAG system
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv
from .config_loader import ConfigLoader

# Load environment variables
load_dotenv()

def get_config(config_name: str, section: str = None) -> Dict[str, Any]:
    """Get configuration from specified config file and optional section.
    
    Args:
        config_name: Name of the config file (e.g., 'llm_config', 'retrieval_config')
        section: Optional section name within the config file
        
    Returns:
        Dict containing the requested configuration
    """
    return ConfigLoader.get_instance().get_config(config_name, section)

__all__ = [
    "get_config",
    "ConfigLoader"
]