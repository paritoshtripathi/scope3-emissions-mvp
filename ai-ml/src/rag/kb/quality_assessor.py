"""
Knowledge Base Quality Assessment
"""
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
import logging
from numpy.typing import NDArray

from ..kb.kb_manager import KBManager
from ..retrieval.multi_vector_retriever import MultiVectorRetriever
from ..embeddings.document_embedder import MultiLevelEmbedder

logger = logging.getLogger(__name__)

class QualityAssessor:
    def __init__(
        self,
        kb_manager: KBManager,
        retriever: MultiVectorRetriever,
        embedder: MultiLevelEmbedder
    ):
        self.kb_manager = kb_manager
        self.retriever = retriever
        self.embedder = embedder

    async def assess_quality(self) -> Dict[str, Any]:
        """
        Assess the quality of the knowledge base using multiple metrics
        """
        try:
            # Get all documents and chunks
            docs = await self.kb_manager.get_documents()
            stats = self.kb_manager.get_stats()
            
            if not docs:
                return self._get_empty_metrics()

            # Calculate individual metrics
            coverage_metrics = self._assess_coverage(docs, stats)
            consistency_metrics = await self._assess_consistency(docs)
            relevance_metrics = self._assess_relevance(docs)
            diversity_metrics = self._assess_diversity(docs)
            
            # Combine all metrics
            scores = [
                coverage_metrics['coverage_score'],
                consistency_metrics['consistency_score'],
                relevance_metrics['relevance_score'],
                diversity_metrics['diversity_score']
            ]
            
            return {
                **coverage_metrics,
                **consistency_metrics,
                **relevance_metrics,
                **diversity_metrics,
                'overall_score': self._calculate_overall_score(scores)
            }
            
        except Exception as e:
            logger.error(f"Error assessing KB quality: {e}")
            return self._get_empty_metrics()

    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'coverage_score': 0.0,
            'coverage_metrics': {},
            'consistency_score': 0.0,
            'consistency_metrics': {},
            'relevance_score': 0.0,
            'relevance_metrics': {},
            'diversity_score': 0.0,
            'diversity_metrics': {},
            'overall_score': 0.0
        }

    def _assess_coverage(
        self,
        docs: List[Dict[str, Any]],
        stats: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Assess knowledge base coverage
        """
        # Document count score
        doc_count = stats.get('document_count', 0)
        doc_score = min(1.0, doc_count / 10)  # Assume 10 docs is full coverage
        
        # Chunk density score
        chunk_count = stats.get('chunk_count', 0)
        avg_chunks_per_doc = chunk_count / doc_count if doc_count > 0 else 0
        chunk_score = min(1.0, avg_chunks_per_doc / 20)  # Assume 20 chunks/doc is ideal
        
        # Category coverage
        categories = set(doc.get('metadata', {}).get('category', '') for doc in docs)
        category_score = min(1.0, len(categories) / 5)  # Assume 5 categories is full coverage
        
        # Combined score
        scores = np.array([doc_score, chunk_score, category_score])
        coverage_score = float(np.mean(scores))
        
        return {
            'coverage_score': coverage_score,
            'coverage_metrics': {
                'document_coverage': float(doc_score),
                'chunk_density': float(chunk_score),
                'category_coverage': float(category_score),
                'total_documents': doc_count,
                'total_chunks': chunk_count,
                'avg_chunks_per_doc': float(avg_chunks_per_doc),
                'categories': list(categories)
            }
        }

    async def _assess_consistency(
        self,
        docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess knowledge base consistency
        """
        try:
            # Metadata consistency
            metadata_fields = ['source', 'type', 'category']
            metadata_completeness = []
            
            for doc in docs:
                metadata = doc.get('metadata', {})
                fields_present = sum(1 for field in metadata_fields if field in metadata)
                metadata_completeness.append(fields_present / len(metadata_fields))
            
            metadata_score = float(np.mean(np.array(metadata_completeness))) if metadata_completeness else 0
            
            # Content similarity check
            chunk_similarities = []
            for doc in docs:
                chunks = doc.get('chunks', [])
                if len(chunks) > 1:
                    embeddings = np.array(self.embedder.embed_multi_level(chunks))
                    sim_matrix = cosine_similarity(embeddings)
                    # Get average similarity excluding self-similarity
                    np.fill_diagonal(sim_matrix, 0)
                    chunk_similarities.append(float(sim_matrix.mean()))
            
            similarity_score = float(np.mean(np.array(chunk_similarities))) if chunk_similarities else 0
            
            # Version consistency
            version_counts = Counter(doc.get('current_version') for doc in docs)
            version_score = 1.0 if len(version_counts) == 1 else 0.5
            
            # Combined score
            scores = np.array([metadata_score, similarity_score, version_score])
            consistency_score = float(np.mean(scores))
            
            return {
                'consistency_score': consistency_score,
                'consistency_metrics': {
                    'metadata_consistency': float(metadata_score),
                    'content_similarity': float(similarity_score),
                    'version_consistency': float(version_score),
                    'metadata_completeness': float(np.mean(np.array(metadata_completeness))),
                    'version_distribution': dict(version_counts)
                }
            }
            
        except Exception as e:
            logger.error(f"Error assessing consistency: {e}")
            return {
                'consistency_score': 0.0,
                'consistency_metrics': {}
            }

    def _assess_relevance(
        self,
        docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess knowledge base relevance
        """
        try:
            # Source credibility
            source_scores = {
                'upload': 0.8,
                'url': 0.6,
                'api': 0.7
            }
            
            source_ratings = []
            for doc in docs:
                source = doc.get('metadata', {}).get('source', '')
                source_ratings.append(source_scores.get(source, 0.5))
            
            source_score = float(np.mean(np.array(source_ratings))) if source_ratings else 0
            
            # Content type relevance
            type_scores = {
                'pdf': 0.9,
                'txt': 0.7,
                'doc': 0.8,
                'docx': 0.8
            }
            
            type_ratings = []
            for doc in docs:
                doc_type = doc.get('metadata', {}).get('type', '')
                type_ratings.append(type_scores.get(doc_type, 0.5))
            
            type_score = float(np.mean(np.array(type_ratings))) if type_ratings else 0
            
            # Combined score
            scores = np.array([source_score, type_score])
            relevance_score = float(np.mean(scores))
            
            return {
                'relevance_score': relevance_score,
                'relevance_metrics': {
                    'source_credibility': float(source_score),
                    'content_type_relevance': float(type_score),
                    'source_distribution': dict(Counter(
                        doc.get('metadata', {}).get('source', '') for doc in docs
                    )),
                    'type_distribution': dict(Counter(
                        doc.get('metadata', {}).get('type', '') for doc in docs
                    ))
                }
            }
            
        except Exception as e:
            logger.error(f"Error assessing relevance: {e}")
            return {
                'relevance_score': 0.0,
                'relevance_metrics': {}
            }

    def _assess_diversity(
        self,
        docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess knowledge base diversity
        """
        try:
            # Category diversity
            categories = [doc.get('metadata', {}).get('category', '') for doc in docs]
            category_counts = Counter(categories)
            category_entropy = self._calculate_entropy(list(category_counts.values()))
            
            # Content length diversity
            lengths = [len(doc.get('content', '')) for doc in docs]
            lengths_array = np.array(lengths)
            length_variance = float(np.var(lengths_array)) if lengths else 0
            length_score = min(1.0, length_variance / 1000000)  # Normalize variance
            
            # Source diversity
            sources = [doc.get('metadata', {}).get('source', '') for doc in docs]
            source_counts = Counter(sources)
            source_entropy = self._calculate_entropy(list(source_counts.values()))
            
            # Combined score
            scores = np.array([category_entropy, length_score, source_entropy])
            diversity_score = float(np.mean(scores))
            
            return {
                'diversity_score': diversity_score,
                'diversity_metrics': {
                    'category_diversity': float(category_entropy),
                    'length_diversity': float(length_score),
                    'source_diversity': float(source_entropy),
                    'category_distribution': dict(category_counts),
                    'source_distribution': dict(source_counts),
                    'length_stats': {
                        'mean': float(np.mean(lengths_array)),
                        'std': float(np.std(lengths_array)),
                        'min': min(lengths),
                        'max': max(lengths)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error assessing diversity: {e}")
            return {
                'diversity_score': 0.0,
                'diversity_metrics': {}
            }

    def _calculate_entropy(self, counts: List[int]) -> float:
        """Calculate normalized entropy of a distribution"""
        if not counts or sum(counts) == 0:
            return 0.0
        
        counts_array = np.array(counts)
        probs = counts_array / counts_array.sum()
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        max_entropy = np.log2(len(counts))
        
        return float(entropy / max_entropy if max_entropy > 0 else 0)

    def _calculate_overall_score(self, scores: List[float]) -> float:
        """Calculate weighted overall quality score"""
        weights = np.array([0.3, 0.25, 0.25, 0.2])  # Coverage, Consistency, Relevance, Diversity
        scores_array = np.array(scores)
        return float(np.average(scores_array, weights=weights))