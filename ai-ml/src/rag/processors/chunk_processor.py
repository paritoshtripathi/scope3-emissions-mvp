from typing import List, Dict
import re

class ChunkProcessor:
    def __init__(self, chunk_size: int = 300, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def process_chunks(self, chunks: List[str]) -> List[Dict[str, str]]:
        """
        Process chunks with metadata and cleaning.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of dictionaries containing processed chunks with metadata
        """
        processed_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Clean the chunk
            cleaned_chunk = self._clean_text(chunk)
            
            # Create chunk metadata
            chunk_data = {
                'id': f'chunk_{i}',
                'text': cleaned_chunk,
                'length': len(cleaned_chunk.split()),
                'position': i
            }
            
            processed_chunks.append(chunk_data)
            
        return processed_chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text chunk."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def __repr__(self) -> str:
        return f"ChunkProcessor(chunk_size={self.chunk_size}, overlap={self.overlap})"