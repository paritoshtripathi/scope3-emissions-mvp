from sentence_transformers import SentenceTransformer
from typing import List, Dict, Union
import numpy as np

class MultiLevelEmbedder:
    def __init__(self):
        self.models = {
            'document': SentenceTransformer('sentence-transformers/all-mpnet-base-v2'),
            'chunk': SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2'),
            'semantic': SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
        }
    
    def embed(self, text_units: Union[str, List[str]], level: str = 'chunk') -> np.ndarray:
        """
        Generate embeddings for given text units using specified model level.
        
        Args:
            text_units: Single text string or list of text strings
            level: Model level to use ('document', 'chunk', or 'semantic')
            
        Returns:
            Numpy array of embeddings
        """
        if level not in self.models:
            raise ValueError(f"Invalid level: {level}. Must be one of {list(self.models.keys())}")
            
        # Ensure text_units is a list
        if isinstance(text_units, str):
            text_units = [text_units]
            
        # Generate embeddings
        embeddings = self.models[level].encode(
            text_units,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        
        return embeddings
    
    def embed_multi_level(self, text_units: Union[str, List[str]]) -> Dict[str, np.ndarray]:
        """
        Generate embeddings at all levels for given text units.
        
        Args:
            text_units: Single text string or list of text strings
            
        Returns:
            Dictionary mapping level names to embedding arrays
        """
        return {
            level: self.embed(text_units, level)
            for level in self.models.keys()
        }
    
    def __repr__(self) -> str:
        return f"MultiLevelEmbedder(models={list(self.models.keys())})"