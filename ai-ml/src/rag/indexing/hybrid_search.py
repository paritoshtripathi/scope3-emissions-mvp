"""
Hybrid Search Implementation with Enhanced Query Processing
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import logging
from src.rag.retrieval.query_expander import QueryExpander, ExpandedQuery
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

@dataclass
class SearchResult:
    doc_id: str
    score: float
    metadata: Dict[str, Any]
    match_details: Dict[str, Any]

class HybridSearchEngine:
    def __init__(self):
        """Initialize hybrid searcher with multiple search strategies"""
        self.query_expander = QueryExpander()
        self.stop_words = set(stopwords.words('english'))
        
        # Default weights for hybrid scoring
        self.weights = {
            'semantic': 0.6,
            'keyword': 0.2,
            'metadata': 0.2
        }
        
        # Metadata field importance
        self.metadata_importance = {
            'scope3_category': 1.0,
            'emission_type': 0.8,
            'calculation_method': 0.7
        }

    async def search(
        self,
        query: str,
        index_manager: Any,
        top_k: int = 5,
        context: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform hybrid search with query expansion
        
        Args:
            query: Original search query
            index_manager: Index manager instance
            top_k: Number of results to return
            context: Optional search context
            
        Returns:
            List of search results with scores
        """
        try:
            # 1. Expand query
            expanded = await self.query_expander.expand_query(query, context)
            
            # 2. Perform semantic search for each expanded query
            semantic_results = await self._semantic_search(
                expanded,
                index_manager,
                top_k * 2  # Get more results for reranking
            )
            
            # 3. Perform keyword matching
            keyword_results = self._keyword_search(
                expanded.original,
                index_manager,
                top_k * 2
            )
            
            # 4. Combine and rerank results
            final_results = self._hybrid_ranking(
                semantic_results,
                keyword_results,
                expanded,
                top_k
            )
            
            # 5. Add match details
            for result in final_results:
                result.match_details = {
                    'query_expansion': expanded.metadata,
                    'matched_terms': self._get_matched_terms(
                        expanded.original,
                        result.metadata.get('content', '')
                    )
                }
            
            return final_results[:top_k]
            
        except Exception as e:
            logging.error(f"Error in hybrid search: {e}")
            return await self._semantic_search(
                ExpandedQuery(
                    original=query,
                    expanded=[query],
                    weights=[1.0],
                    metadata={}
                ),
                index_manager,
                top_k
            )

    def _keyword_search(
        self,
        query: str,
        index_manager: Any,
        top_k: int
    ) -> List[SearchResult]:
        """Perform keyword-based search"""
        terms = set(self._clean_text(query))
        results = []
        
        for doc in index_manager.get_all_documents():
            content = doc.get('content', '')
            doc_terms = set(self._clean_text(content))
            
            # Calculate TF-IDF style score
            matches = terms.intersection(doc_terms)
            if matches:
                score = len(matches) / len(terms)
                # Boost score based on term frequency
                term_freq = sum(content.lower().count(term.lower()) for term in matches)
                score *= (1 + np.log1p(term_freq))
                
                results.append(SearchResult(
                    doc_id=doc['id'],
                    score=score,
                    metadata=doc,
                    match_details={'matched_terms': list(matches)}
                ))
                
        return sorted(results, key=lambda x: x.score, reverse=True)[:top_k]

    def _hybrid_ranking(
        self,
        semantic_results: List[SearchResult],
        keyword_results: List[SearchResult],
        expanded: ExpandedQuery,
        top_k: int
    ) -> List[SearchResult]:
        """Combine and rerank results using multiple signals"""
        doc_scores = {}
        
        # Combine semantic and keyword scores
        for result in semantic_results:
            doc_scores[result.doc_id] = {
                'score': result.score * self.weights['semantic'],
                'metadata': result.metadata,
                'signals': {'semantic': result.score}
            }
            
        for result in keyword_results:
            if result.doc_id in doc_scores:
                doc_scores[result.doc_id]['score'] += (
                    result.score * self.weights['keyword']
                )
                doc_scores[result.doc_id]['signals']['keyword'] = result.score
            else:
                doc_scores[result.doc_id] = {
                    'score': result.score * self.weights['keyword'],
                    'metadata': result.metadata,
                    'signals': {'keyword': result.score}
                }
                
        # Add metadata scoring
        for doc_id, data in doc_scores.items():
            metadata_score = self._calculate_metadata_score(
                data['metadata'],
                expanded
            )
            data['score'] += metadata_score * self.weights['metadata']
            data['signals']['metadata'] = metadata_score
            
        # Create final results
        final_results = [
            SearchResult(
                doc_id=doc_id,
                score=data['score'],
                metadata=data['metadata'],
                match_details={'signals': data['signals']}
            )
            for doc_id, data in doc_scores.items()
        ]
        
        return sorted(
            final_results,
            key=lambda x: x.score,
            reverse=True
        )[:top_k]

    def _clean_text(self, text: str) -> List[str]:
        """Clean and tokenize text"""
        tokens = word_tokenize(text.lower())
        return [
            token for token in tokens
            if token not in self.stop_words and token.isalnum()
        ]

    async def _semantic_search(
        self,
        expanded: ExpandedQuery,
        index_manager: Any,
        top_k: int
    ) -> List[SearchResult]:
        """Perform semantic search using expanded queries"""
        all_results = []
        
        # Search for each expanded query variant
        for query, weight in zip(expanded.expanded, expanded.weights):
            # Get embeddings for the query
            query_embedding = self.query_expander.model.encode([query])[0]
            
            # Search across all index levels
            for level in ['document', 'chunk', 'semantic']:
                if hasattr(index_manager.indexes, level):
                    distances, indices, metadata = await index_manager.indexes[level].search(
                        query_embedding,
                        k=top_k,
                        nprobe=10  # Increase search scope
                    )
                    
                    # Convert distances to similarity scores and apply weights
                    for dist, meta in zip(distances, metadata):
                        similarity = 1.0 / (1.0 + dist)  # Convert distance to similarity
                        score = similarity * weight * index_manager.weights[level]
                        
                        result = SearchResult(
                            doc_id=meta.get('doc_id', ''),
                            score=score,
                            metadata=meta,
                            match_details={
                                'query_variant': query,
                                'level': level,
                                'raw_score': similarity
                            }
                        )
                        all_results.append(result)
        
        # Combine results for same documents
        combined_results = {}
        for result in all_results:
            if result.doc_id not in combined_results:
                combined_results[result.doc_id] = result
            else:
                # Take max score across query variants and levels
                if result.score > combined_results[result.doc_id].score:
                    combined_results[result.doc_id] = result
        
        return sorted(
            combined_results.values(),
            key=lambda x: x.score,
            reverse=True
        )[:top_k]

    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract semantically meaningful terms from text"""
        # Clean and tokenize
        tokens = self._clean_text(text)
        
        # Get term frequencies
        term_freq = {}
        for token in tokens:
            term_freq[token] = term_freq.get(token, 0) + 1
            
        # Filter by frequency and length
        key_terms = [
            term for term in term_freq
            if term_freq[term] >= 1 and len(term) >= 3
        ]
        
        return key_terms

    def _find_semantic_clusters(
        self,
        terms: List[str],
        embeddings: np.ndarray,
        n_clusters: int = 3
    ) -> List[List[str]]:
        """Group terms into semantic clusters"""
        if len(terms) < n_clusters:
            return [terms]
            
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        
        # Group terms by cluster
        term_clusters: List[List[str]] = [[] for _ in range(n_clusters)]
        for term, cluster_id in zip(terms, clusters):
            term_clusters[cluster_id].append(term)
            
        return term_clusters

    def _find_shared_concepts(
        self,
        doc_content: str,
        query_terms: List[str]
    ) -> Dict[str, float]:
        """Find shared semantic concepts between document and query"""
        # Get document terms
        doc_terms = self._extract_key_terms(doc_content)
        
        # Calculate term overlap scores
        concept_scores = {}
        for q_term in query_terms:
            for d_term in doc_terms:
                if q_term == d_term:
                    concept_scores[q_term] = 1.0
                else:
                    # Use semantic similarity for non-exact matches
                    similarity = cosine_similarity(
                        [self.query_expander.model.encode([q_term])[0]],
                        [self.query_expander.model.encode([d_term])[0]]
                    )[0][0]
                    if similarity > 0.7:  # Threshold for semantic similarity
                        concept_scores[f"{q_term}-{d_term}"] = similarity
                        
        return concept_scores

    def _get_matched_terms(self, query: str, content: str) -> Dict[str, Any]:
        """Get detailed term matching information"""
        query_terms = self._extract_key_terms(query)
        doc_terms = self._extract_key_terms(content)
        
        matches = {
            'exact': [],
            'semantic': [],
            'shared_concepts': {}
        }
        
        # Find exact matches
        matches['exact'] = list(set(query_terms) & set(doc_terms))
        
        # Find semantic matches
        shared_concepts = self._find_shared_concepts(content, query_terms)
        matches['shared_concepts'] = shared_concepts
        
        # Get semantic matches above threshold
        semantic_matches = [
            (term_pair.split('-')[0], term_pair.split('-')[1], score)
            for term_pair, score in shared_concepts.items()
            if '-' in term_pair and score > 0.7
        ]
        matches['semantic'] = semantic_matches
        
        return matches

    def _calculate_metadata_score(
        self,
        metadata: Dict[str, Any],
        expanded: ExpandedQuery
    ) -> float:
        """Calculate score based on metadata matching"""
        score = 0.0
        
        for field, importance in self.metadata_importance.items():
            if field in metadata and field in expanded.metadata:
                if metadata[field] == expanded.metadata[field]:
                    score += importance
                else:
                    # Check for semantic similarity in field values
                    field_similarity = cosine_similarity(
                        [self.query_expander.model.encode([str(metadata[field])])[0]],
                        [self.query_expander.model.encode([str(expanded.metadata[field])])[0]]
                    )[0][0]
                    score += importance * field_similarity
                    
        return score / sum(self.metadata_importance.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the hybrid search engine"""
        return {
            'weights': self.weights,
            'metadata_importance': self.metadata_importance,
            'query_expander_stats': self.query_expander.get_expansion_stats()
        }