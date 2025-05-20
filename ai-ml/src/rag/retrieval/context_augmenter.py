"""
Context Augmenter for Enhanced Document Understanding
"""
from typing import List, Dict, Any, Optional
import numpy as np
from src.rag.indexing.hybrid_search import HybridSearchEngine as HybridSearcher  # Alias for backward compatibility

class ContextAugmenter:
    def __init__(self):
        """Initialize context augmenter"""
        self.hybrid_searcher = HybridSearcher()
        
        # Augmentation strategies
        self.strategies = {
            'semantic_expansion': self._semantic_expansion,
            'cross_reference': self._cross_reference,
            'temporal_context': self._temporal_context,
            'scope3_specific': self._scope3_augmentation
        }
        
        # Context weights
        self.weights = {
            'semantic': 0.4,
            'reference': 0.3,
            'temporal': 0.1,
            'scope3': 0.2
        }

    async def augment(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """
        Augment retrieved documents with additional context
        
        Args:
            query: Original query
            documents: Retrieved documents
            embeddings: Query embeddings at different levels
            
        Returns:
            Augmented context
        """
        augmented_context = {
            'original_query': query,
            'documents': documents,
            'augmentations': {}
        }
        
        # Apply each augmentation strategy
        for strategy_name, strategy_func in self.strategies.items():
            try:
                augmented = await strategy_func(
                    query,
                    documents,
                    embeddings
                )
                augmented_context['augmentations'][strategy_name] = augmented
            except Exception as e:
                augmented_context['augmentations'][strategy_name] = {
                    'error': str(e)
                }
                
        # Combine augmentations
        augmented_context['combined'] = self._combine_augmentations(
            augmented_context['augmentations']
        )
        
        return augmented_context

    async def _semantic_expansion(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Expand context with semantic relationships"""
        semantic_context = {
            'related_concepts': [],
            'key_terms': [],
            'semantic_clusters': []
        }
        
        # Extract key terms from documents
        doc_texts = [doc.get('content', '') for doc in documents]
        key_terms = self.hybrid_searcher.extract_key_terms(doc_texts)
        
        # Find semantic clusters
        if 'semantic' in embeddings:
            clusters = self.hybrid_searcher.find_semantic_clusters(
                embeddings['semantic']
            )
            semantic_context['semantic_clusters'] = clusters
            
        semantic_context['key_terms'] = key_terms
        return semantic_context

    async def _cross_reference(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Find cross-references between documents"""
        references = {
            'internal_refs': [],
            'document_links': [],
            'shared_concepts': []
        }
        
        # Find shared concepts across documents
        for i, doc1 in enumerate(documents):
            for j, doc2 in enumerate(documents[i+1:], i+1):
                shared = self.hybrid_searcher.find_shared_concepts(
                    doc1.get('content', ''),
                    doc2.get('content', '')
                )
                if shared:
                    references['shared_concepts'].append({
                        'doc1_id': doc1.get('doc_id'),
                        'doc2_id': doc2.get('doc_id'),
                        'concepts': shared
                    })
                    
        return references

    async def _temporal_context(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Add temporal context to documents"""
        temporal = {
            'timeline': [],
            'temporal_order': [],
            'relevance_decay': []
        }
        
        # Sort documents by timestamp if available
        dated_docs = [
            doc for doc in documents
            if 'timestamp' in doc.get('metadata', {})
        ]
        if dated_docs:
            temporal['temporal_order'] = sorted(
                dated_docs,
                key=lambda x: x['metadata']['timestamp']
            )
            
        return temporal

    async def _scope3_augmentation(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        embeddings: Dict[str, np.ndarray]
    ) -> Dict[str, Any]:
        """Add Scope3-specific context"""
        scope3_context = {
            'categories': [],
            'emission_factors': [],
            'calculation_context': [],
            'related_strategies': []
        }
        
        # Extract Scope3 categories
        for doc in documents:
            metadata = doc.get('metadata', {})
            if 'scope3_category' in metadata:
                if metadata['scope3_category'] not in scope3_context['categories']:
                    scope3_context['categories'].append(
                        metadata['scope3_category']
                    )
                    
            # Extract emission factors
            if 'emission_value' in metadata:
                scope3_context['emission_factors'].append({
                    'category': metadata.get('scope3_category'),
                    'value': metadata['emission_value'],
                    'unit': metadata.get('unit', 'tCO2e')
                })
                
        return scope3_context

    def _combine_augmentations(
        self,
        augmentations: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Combine different augmentation results"""
        combined = {
            'enhanced_context': {},
            'key_insights': [],
            'relationships': []
        }
        
        # Combine semantic expansions
        if 'semantic_expansion' in augmentations:
            combined['enhanced_context']['semantic'] = {
                'terms': augmentations['semantic_expansion'].get('key_terms', []),
                'clusters': augmentations['semantic_expansion'].get(
                    'semantic_clusters',
                    []
                )
            }
            
        # Add cross-references
        if 'cross_reference' in augmentations:
            combined['relationships'].extend(
                augmentations['cross_reference'].get('shared_concepts', [])
            )
            
        # Add temporal context
        if 'temporal_context' in augmentations:
            combined['enhanced_context']['temporal'] = {
                'order': augmentations['temporal_context'].get(
                    'temporal_order',
                    []
                )
            }
            
        # Add Scope3 context
        if 'scope3_specific' in augmentations:
            combined['enhanced_context']['scope3'] = {
                'categories': augmentations['scope3_specific'].get(
                    'categories',
                    []
                ),
                'factors': augmentations['scope3_specific'].get(
                    'emission_factors',
                    []
                )
            }
            
        return combined