from typing import Dict, List

class DocumentProcessor:
    """Processor for splitting documents into various chunk sizes"""
    
    def __init__(self):
        self.chunk_sizes = {
            'document': 1000,
            'paragraph': 300,
            'semantic': 100
        }
    
    def _split_document(self, document: str, chunk_size: int) -> List[str]:
        """Split document into chunks of specified size"""
        if not document or not isinstance(document, str):
            return []
            
        # Split into words
        words = document.split()
        chunks = []
        
        # Create chunks
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:  # Only add non-empty chunks
                chunks.append(chunk)
                
        return chunks
    
    def _extract_semantic_units(self, document: str) -> List[str]:
        """Extract semantic units (sentences) from document"""
        if not document or not isinstance(document, str):
            return []
            
        # Simple sentence splitting
        sentences = [s.strip() for s in document.split('.')]
        return [s for s in sentences if s]  # Remove empty strings
    
    def process(self, document: str) -> Dict[str, List[str]]:
        """
        Process document into multiple chunk representations
        
        Args:
            document: Input text document
            
        Returns:
            Dictionary containing different chunk representations
        """
        if not document or not isinstance(document, str):
            return {
                'document_chunks': [],
                'paragraph_chunks': [],
                'semantic_chunks': []
            }
            
        return {
            'document_chunks': self._split_document(document, self.chunk_sizes['document']),
            'paragraph_chunks': self._split_document(document, self.chunk_sizes['paragraph']),
            'semantic_chunks': self._extract_semantic_units(document)
        }