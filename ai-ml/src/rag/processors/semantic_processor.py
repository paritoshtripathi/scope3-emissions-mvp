from typing import List, Dict
import re
from collections import defaultdict

class SemanticProcessor:
    def __init__(self):
        self.semantic_patterns = {
            'definition': r'(?:is defined as|means|refers to|is characterized by)',
            'example': r'(?:for example|e\.g\.|such as|including)',
            'comparison': r'(?:compared to|similar to|different from|unlike)',
            'cause_effect': r'(?:because|therefore|thus|as a result)'
        }
    
    def process_semantic_units(self, text: str) -> List[Dict[str, str]]:
        """
        Extract and process semantic units from text.
        
        Args:
            text: Input text to process
            
        Returns:
            List of dictionaries containing semantic units with metadata
        """
        semantic_units = []
        
        # Split into sentences (basic implementation)
        sentences = re.split(r'[.!?]+', text)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            # Identify semantic types
            semantic_types = self._identify_semantic_types(sentence)
            
            unit = {
                'id': f'semantic_{i}',
                'text': sentence.strip(),
                'semantic_types': semantic_types,
                'position': i
            }
            
            semantic_units.append(unit)
            
        return semantic_units
    
    def _identify_semantic_types(self, text: str) -> List[str]:
        """Identify semantic types present in the text."""
        types = []
        for semantic_type, pattern in self.semantic_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                types.append(semantic_type)
        return types
    
    def extract_key_concepts(self, semantic_units: List[Dict[str, str]]) -> Dict[str, List[str]]:
        """
        Extract key concepts from semantic units.
        
        Args:
            semantic_units: List of processed semantic units
            
        Returns:
            Dictionary mapping concept types to lists of concepts
        """
        concepts = defaultdict(list)
        
        for unit in semantic_units:
            for semantic_type in unit['semantic_types']:
                concepts[semantic_type].append(unit['text'])
                
        return dict(concepts)
    
    def __repr__(self) -> str:
        return f"SemanticProcessor(patterns={list(self.semantic_patterns.keys())})"