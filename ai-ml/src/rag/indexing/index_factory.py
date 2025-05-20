from typing import Optional, Dict, Any
from .faiss_indexes import EnhancedFAISSIndex

class VectorStoreFactory:
    """Factory class for creating and managing vector stores."""
    
    @staticmethod
    def get_store(
        store_type: str = 'faiss',
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Create and return a vector store instance.
        
        Args:
            store_type: Type of vector store ('faiss' or 'weaviate')
            config: Configuration dictionary for the store
            
        Returns:
            Vector store instance
        """
        config = config or {}
        
        if store_type == 'faiss':
            return EnhancedFAISSIndex(
                dim=config.get('dim', 768),
                index_type=config.get('index_type', 'IVF,Flat'),
                metric=config.get('metric', 'l2'),
                nlist=config.get('nlist', 100),
                save_dir=config.get('save_dir')
            )
        elif store_type == 'weaviate':
            try:
                import weaviate
                client = weaviate.Client(
                    url=config['url'],
                    auth_client_secret=weaviate.AuthApiKey(api_key=config.get('api_key')),
                    additional_headers=config.get('additional_headers', {})
                )
                return client
            except ImportError:
                raise ImportError("Weaviate client not installed. Please install weaviate-client.")
            except KeyError:
                raise ValueError("Weaviate configuration must include 'url'")
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")
    
    @staticmethod
    def get_default_config(store_type: str) -> Dict[str, Any]:
        """
        Get default configuration for a vector store type.
        
        Args:
            store_type: Type of vector store
            
        Returns:
            Default configuration dictionary
        """
        if store_type == 'faiss':
            return {
                'dim': 768,
                'index_type': 'IVF,Flat',
                'metric': 'l2',
                'nlist': 100
            }
        elif store_type == 'weaviate':
            return {
                'url': 'http://localhost:8080',
                'additional_headers': {
                    'X-OpenAI-Api-Key': None  # To be filled by user
                }
            }
        else:
            raise ValueError(f"Unsupported vector store type: {store_type}")