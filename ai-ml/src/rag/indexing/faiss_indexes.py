"""
FAISS Index Implementation for Enhanced Vector Search
"""
import numpy as np
import faiss
import pickle
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import os
import logging

@dataclass
class IndexMetadata:
    dimension: int
    index_type: str
    total_vectors: int
    last_updated: str
    index_path: str

class FAISSIndexManager:
    def __init__(
        self,
        dimension: int = 768,  # Default for many transformers
        index_type: str = "IVFFlat",  # IVFFlat for better speed/accuracy trade-off
        nlist: int = 100,  # Number of clusters for IVF
        storage_dir: str = "models/faiss_index"
    ):
        self.dimension = dimension
        self.index_type = index_type
        self.nlist = nlist
        self.storage_dir = storage_dir
        self.index = None
        self.metadata = None
        self.id_to_metadata = {}  # Map vector IDs to document metadata
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize or load index
        self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize FAISS index with appropriate configuration"""
        if self._load_existing_index():
            logging.info("Loaded existing FAISS index")
            return

        # Quantizer for IVF
        quantizer = faiss.IndexFlatL2(self.dimension)
        
        if self.index_type == "IVFFlat":
            # IVFFlat index - good balance of speed and accuracy
            self.index = faiss.IndexIVFFlat(
                quantizer, 
                self.dimension,
                self.nlist,
                faiss.METRIC_L2
            )
        elif self.index_type == "IVFPQ":
            # IVFPQ index - better memory efficiency
            self.index = faiss.IndexIVFPQ(
                quantizer,
                self.dimension,
                self.nlist,
                8,  # M = number of sub-quantizers
                8   # nbits = bits per sub-quantizer
            )
        else:
            # Flat index - exact search, slower but most accurate
            self.index = faiss.IndexFlatL2(self.dimension)

        # Initialize metadata
        self.metadata = IndexMetadata(
            dimension=self.dimension,
            index_type=self.index_type,
            total_vectors=0,
            last_updated=self._get_timestamp(),
            index_path=os.path.join(self.storage_dir, "faiss.index")
        )

    def _load_existing_index(self) -> bool:
        """Load existing index if available"""
        index_path = os.path.join(self.storage_dir, "faiss.index")
        metadata_path = os.path.join(self.storage_dir, "metadata.pkl")
        
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            try:
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    self.metadata, self.id_to_metadata = pickle.load(f)
                return True
            except Exception as e:
                logging.error(f"Error loading index: {e}")
                return False
        return False

    def _save_index(self) -> None:
        """Save index and metadata"""
        try:
            # Update metadata
            self.metadata.total_vectors = self.index.ntotal
            self.metadata.last_updated = self._get_timestamp()
            
            # Save index
            faiss.write_index(
                self.index,
                os.path.join(self.storage_dir, "faiss.index")
            )
            
            # Save metadata
            with open(os.path.join(self.storage_dir, "metadata.pkl"), 'wb') as f:
                pickle.dump((self.metadata, self.id_to_metadata), f)
                
        except Exception as e:
            logging.error(f"Error saving index: {e}")
            raise

    def add_vectors(
        self,
        vectors: np.ndarray,
        metadata: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add vectors to the index
        
        Args:
            vectors: numpy array of vectors to add
            metadata: list of metadata dicts for each vector
            
        Returns:
            List of assigned vector IDs
        """
        if not self.index.is_trained and hasattr(self.index, 'train'):
            self.index.train(vectors)

        # Generate IDs for new vectors
        start_id = self.index.ntotal
        ids = np.arange(start_id, start_id + len(vectors))
        
        # Add vectors to index
        self.index.add_with_ids(vectors, ids)
        
        # Store metadata
        for id_, meta in zip(ids, metadata):
            self.id_to_metadata[int(id_)] = meta
            
        # Save updated index
        self._save_index()
        
        return ids.tolist()

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
        nprobe: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Search for similar vectors
        
        Args:
            query_vector: Vector to search for
            k: Number of results to return
            nprobe: Number of clusters to search (IVF only)
            
        Returns:
            Tuple of (distances, indices, metadata)
        """
        if nprobe and hasattr(self.index, 'nprobe'):
            original_nprobe = self.index.nprobe
            self.index.nprobe = nprobe

        # Reshape query if needed
        if len(query_vector.shape) == 1:
            query_vector = query_vector.reshape(1, -1)

        # Perform search
        distances, indices = self.index.search(query_vector, k)
        
        # Get metadata for results
        metadata = [
            self.id_to_metadata.get(int(idx), {})
            for idx in indices[0]
        ]

        # Reset nprobe if changed
        if nprobe and hasattr(self.index, 'nprobe'):
            self.index.nprobe = original_nprobe

        return distances[0], indices[0], metadata

    def remove_vectors(self, ids: List[int]) -> None:
        """Remove vectors from index"""
        if hasattr(self.index, 'remove_ids'):
            self.index.remove_ids(np.array(ids))
            
            # Remove metadata
            for id_ in ids:
                self.id_to_metadata.pop(id_, None)
                
            # Save updated index
            self._save_index()
        else:
            raise NotImplementedError("Removal not supported for this index type")

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "last_updated": self.metadata.last_updated if self.metadata else None,
            "memory_usage": self._estimate_memory_usage()
        }

    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of index in bytes"""
        if self.index_type == "IVFFlat":
            # Rough estimation for IVFFlat
            return (
                self.index.ntotal * self.dimension * 4 +  # Vector storage
                self.nlist * self.dimension * 4           # Centroids
            )
        elif self.index_type == "IVFPQ":
            # Rough estimation for IVFPQ
            return (
                self.index.ntotal * 8 +                   # Compressed vectors
                self.nlist * self.dimension * 4           # Centroids
            )
        else:
            # Flat index
            return self.index.ntotal * self.dimension * 4

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()