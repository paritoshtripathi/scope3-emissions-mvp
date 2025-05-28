"""
Multi-Vector Retriever with Hybrid Search Capabilities
"""
from typing import List, Dict, Any, Optional, Tuple
import uuid
try:
    import numpy as np
except ImportError:
    raise ImportError(
        "numpy is required for MultiVectorRetriever. "
        "Install it with 'pip install numpy'"
    )
from src.rag.indexing.faiss_indexes import FAISSIndexManager
from src.rag.indexing.hybrid_search import HybridSearchEngine

class MultiVectorRetriever:
    def __init__(self):
        """Initialize multi-vector retriever with multiple indexes"""
        # Initialize indexes for different levels
        self.indexes = {
            'document': FAISSIndexManager(dimension=768, index_type="IVFFlat"),
            'chunk': FAISSIndexManager(dimension=384, index_type="IVFFlat"),
            'semantic': FAISSIndexManager(dimension=768, index_type="IVFFlat")
        }
        
        # Initialize hybrid searcher
        self.hybrid_searcher = HybridSearchEngine()
        
        # Retrieval weights for different levels
        self.weights = {
            'document': 0.3,
            'chunk': 0.5,
            'semantic': 0.2
        }
        
        # Document metadata storage
        self.doc_metadata = {}

    async def retrieve(
        self,
        query_embeddings: Dict[str, np.ndarray],
        query: str,
        top_k: int = 5,
        strategy: str = 'weighted',
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve documents using multi-level embeddings"""
        # Use hybrid search for enhanced retrieval
        hybrid_results = await self.hybrid_searcher.search(
            query=query,
            index_manager=self,
            top_k=top_k,
            context=context
        )
        
        # Get results from each level with expanded context
        level_results = {}
        for level, embedding in query_embeddings.items():
            distances, indices, metadata = await self._search_with_context(
                embedding=embedding,
                level=level,
                k=top_k,
                context=context
            )
            level_results[level] = {
                'distances': distances,
                'indices': indices,
                'metadata': metadata
            }
            
        # Combine results based on strategy
        if strategy == 'weighted':
            results = self._weighted_combination(level_results, top_k)
        else:  # ensemble
            results = self._ensemble_combination(level_results, top_k)
            
        # Add document metadata
        for result in results:
            doc_id = result['metadata'].get('doc_id')
            if doc_id and doc_id in self.doc_metadata:
                result['metadata'].update(self.doc_metadata[doc_id])
                
        return results

    def add_documents(
        self,
        chunks: List[str],
        embeddings: Dict[str, np.ndarray],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Add documents to all indexes"""
        doc_ids = []
        metadata = metadata or {}
        
        # Use existing doc_id from metadata or generate a new one
        doc_id = metadata.get('doc_id') or f"doc_{uuid.uuid4().hex[:8]}"
        metadata['doc_id'] = doc_id
        
        # Add to each level's index
        for level, level_embeddings in embeddings.items():
            chunk_metadata = [
                {
                    'chunk_id': f"{doc_id}_chunk_{i}",
                    'doc_id': doc_id,
                    **metadata
                }
                for i in range(len(chunks))
            ]
            
            ids = self.indexes[level].add_vectors(
                level_embeddings,
                chunk_metadata
            )
            doc_ids.extend(ids)
            
        # Store document metadata
        self.doc_metadata[doc_id] = metadata
        
        return doc_ids

    def _weighted_combination(
        self,
        level_results: Dict[str, Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Combine results using weighted scores"""
        # Normalize distances and apply weights
        all_scores = {}
        for level, results in level_results.items():
            weight = self.weights[level]
            for i, (distance, idx, meta) in enumerate(zip(
                results['distances'],
                results['indices'],
                results['metadata']
            )):
                doc_id = meta.get('doc_id')
                if not doc_id:
                    continue
                    
                score = 1 - (distance / np.max(results['distances']))
                weighted_score = score * weight
                
                if doc_id in all_scores:
                    all_scores[doc_id]['score'] += weighted_score
                else:
                    all_scores[doc_id] = {
                        'score': weighted_score,
                        'metadata': meta
                    }
                    
        # Sort by combined score
        sorted_results = sorted(
            all_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        return [
            {
                'doc_id': doc_id,
                'score': data['score'],
                'metadata': data['metadata']
            }
            for doc_id, data in sorted_results[:top_k]
        ]

    def _ensemble_combination(
        self,
        level_results: Dict[str, Dict[str, Any]],
        top_k: int
    ) -> List[Dict[str, Any]]:
        """Combine results using ensemble voting"""
        # Count document appearances
        doc_votes = {}
        for level, results in level_results.items():
            for i, (distance, idx, meta) in enumerate(zip(
                results['distances'],
                results['indices'],
                results['metadata']
            )):
                doc_id = meta.get('doc_id')
                if not doc_id:
                    continue
                    
                score = 1 - (distance / np.max(results['distances']))
                
                if doc_id in doc_votes:
                    doc_votes[doc_id]['votes'] += 1
                    doc_votes[doc_id]['score'] += score
                else:
                    doc_votes[doc_id] = {
                        'votes': 1,
                        'score': score,
                        'metadata': meta
                    }
                    
        # Sort by votes, then score
        sorted_results = sorted(
            doc_votes.items(),
            key=lambda x: (x[1]['votes'], x[1]['score']),
            reverse=True
        )
        
        return [
            {
                'doc_id': doc_id,
                'score': data['score'] / data['votes'],
                'votes': data['votes'],
                'metadata': data['metadata']
            }
            for doc_id, data in sorted_results[:top_k]
        ]

    async def _search_with_context(
        self,
        embedding: np.ndarray,
        level: str,
        k: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """Perform context-aware search at a specific level"""
        # Get base results
        distances, indices, metadata = self.indexes[level].search(
            embedding,
            k=k,
            nprobe=10
        )
        
        if context:
            # Apply context-based filtering
            filtered_indices = []
            filtered_distances = []
            filtered_metadata = []
            
            for i, (dist, idx, meta) in enumerate(zip(distances, indices, metadata)):
                relevance_score = self._calculate_context_relevance(
                    meta,
                    context
                )
                
                if relevance_score > 0:
                    # Adjust distance based on context relevance
                    adjusted_dist = dist * (1 - relevance_score * 0.3)
                    filtered_distances.append(adjusted_dist)
                    filtered_indices.append(idx)
                    filtered_metadata.append(meta)
            
            if filtered_indices:
                return (
                    np.array(filtered_distances),
                    np.array(filtered_indices),
                    filtered_metadata
                )
        
        return distances, indices, metadata

    def _calculate_context_relevance(
        self,
        metadata: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score based on context"""
        score = 0.0
        
        # Check category match
        if 'scope3_category' in context and 'scope3_category' in metadata:
            if context['scope3_category'] == metadata['scope3_category']:
                score += 0.5
                
        # Check temporal relevance
        if 'year' in context and 'year' in metadata:
            year_diff = abs(context['year'] - metadata['year'])
            if year_diff == 0:
                score += 0.3
            elif year_diff <= 2:
                score += 0.2
                
        # Check methodology match
        if 'methodology' in context and 'methodology' in metadata:
            if context['methodology'] == metadata['methodology']:
                score += 0.2
                
        return min(score, 1.0)

    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics"""
        return {
            'index_stats': {
                level: index.get_stats()
                for level, index in self.indexes.items()
            },
            'total_documents': len(self.doc_metadata),
            'weights': self.weights,
            'hybrid_stats': self.hybrid_searcher.get_stats()
        }

    def search_vectors(
        self,
        query_vector: List[float],
        k: int = 5,
        nprobe: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors using FAISS"""
        # Convert query vector to numpy array
        query_array = np.array(query_vector, dtype=np.float32).reshape(1, -1)
        
        # Search in document-level index
        distances, indices, metadata = self.indexes['document'].search(
            query_array,
            k=k,
            nprobe=nprobe or 10
        )
        
        # Format results
        results = []
        for i, (dist, idx, meta) in enumerate(zip(
            distances[0],  # First row since we only have one query
            indices[0],
            metadata
        )):
            doc_id = meta.get('doc_id')
            if not doc_id:
                continue
                
            result = {
                'id': int(idx),
                'distance': float(dist),
                'metadata': meta
            }
            # Add document metadata if available
            if doc_id in self.doc_metadata:
                result['metadata'].update(self.doc_metadata[doc_id])
            results.append(result)
            
        return results