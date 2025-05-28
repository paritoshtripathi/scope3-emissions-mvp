"""
Configuration management for RAG system
"""
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from .config_loader import ConfigLoader

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def validate_environment() -> bool:
    """
    Validate required environment variables
    Returns True if all required variables are present
    """
    required_vars = [
        'OPENAI_API_KEY',
        'NEO4J_URI',
        'NEO4J_USER',
        'NEO4J_PASSWORD'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var, '').strip()]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        return False
        
    return True

def get_config(config_name: str, section: Optional[str] = None) -> Dict[str, Any]:
    """
    Get configuration from specified config file and optional section.
    
    Args:
        config_name: Name of the config file (e.g., 'llm_config', 'retrieval_config')
        section: Optional section name within the config file
        
    Returns:
        Dict containing the requested configuration
    """
    try:
        return ConfigLoader.get_instance().get_config(config_name, section)
    except Exception as e:
        logger.error(f"Error getting config {config_name}: {str(e)}")
        return {}

__all__ = [
    "get_config",
    "validate_environment",
    "ConfigLoader"
]