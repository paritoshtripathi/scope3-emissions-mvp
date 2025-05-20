"""
Query Expansion Module for Enhanced Search
"""
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class ExpandedQuery:
    original: str
    expanded: List[str]
    weights: List[float]
    metadata: Dict[str, Any]

class QueryExpander:
    def __init__(self):
        """Initialize query expander with semantic models"""
        self.model = SentenceTransformer('BAAI/bge-large-en-v1.5')
        self.expansion_cache = {}
        self.term_embeddings = {}
        
    async def expand_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExpandedQuery:
        """
        Expand query with semantic variations
        
        Args:
            query: Original query
            context: Optional context for domain-specific expansion
            
        Returns:
            Expanded query with weights
        """
        # Check cache
        if query in self.expansion_cache:
            return self.expansion_cache[query]
            
        # Base expansion
        expanded = [query]
        weights = [1.0]
        metadata: Dict[str, Any] = {}
        
        # Get query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Extract key phrases
        key_phrases = self._extract_key_phrases(query)
        
        # Generate variations
        for phrase in key_phrases:
            variations = self._generate_variations(phrase, context or {})
            expanded.extend(variations)
            
            # Calculate semantic similarity for weights
            var_embeddings = self.model.encode(variations)
            similarities = cosine_similarity([query_embedding], var_embeddings)[0]
            weights.extend(similarities.tolist())
            
        # Normalize weights
        total_weight = sum(weights)
        weights = [w/total_weight for w in weights]
        
        # Add metadata
        metadata['key_phrases'] = key_phrases
        if context:
            metadata.update(context)
            
        result = ExpandedQuery(
            original=query,
            expanded=expanded,
            weights=weights,
            metadata=metadata
        )
        
        # Cache result
        self.expansion_cache[query] = result
        
        return result
        
    def get_semantic_terms(self, text: str) -> Set[str]:
        """
        Get semantically important terms from text
        
        Args:
            text: Input text
            
        Returns:
            Set of semantic terms
        """
        # Extract terms
        terms = set(text.lower().split())
        
        # Get embeddings for terms
        term_embeddings = self.model.encode(list(terms))
        
        # Store embeddings for later use
        for term, embedding in zip(terms, term_embeddings):
            self.term_embeddings[term] = embedding
            
        return terms
        
    def are_terms_related(self, term1: str, term2: str, threshold: float = 0.7) -> bool:
        """
        Check if two terms are semantically related
        
        Args:
            term1: First term
            term2: Second term
            threshold: Similarity threshold
            
        Returns:
            True if terms are related
        """
        # Get embeddings
        if term1 not in self.term_embeddings:
            self.term_embeddings[term1] = self.model.encode([term1])[0]
        if term2 not in self.term_embeddings:
            self.term_embeddings[term2] = self.model.encode([term2])[0]
            
        # Calculate similarity
        similarity = cosine_similarity(
            [self.term_embeddings[term1]],
            [self.term_embeddings[term2]]
        )[0][0]
        
        return similarity >= threshold
        
    def get_term_similarity(self, term1: str, term2: str) -> float:
        """
        Get semantic similarity between terms
        
        Args:
            term1: First term
            term2: Second term
            
        Returns:
            Similarity score
        """
        # Get embeddings
        if term1 not in self.term_embeddings:
            self.term_embeddings[term1] = self.model.encode([term1])[0]
        if term2 not in self.term_embeddings:
            self.term_embeddings[term2] = self.model.encode([term2])[0]
            
        # Calculate similarity
        similarity = cosine_similarity(
            [self.term_embeddings[term1]],
            [self.term_embeddings[term2]]
        )[0][0]
        
        return float(similarity)
        
    def get_expansion_stats(self) -> Dict[str, Any]:
        """Get statistics about query expansion"""
        stats: Dict[str, Any] = {
            'cache_size': len(self.expansion_cache),
            'term_embeddings': len(self.term_embeddings)
        }
        return stats
        
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        # Simple phrase extraction
        words = text.lower().split()
        phrases = []
        
        # Single words
        phrases.extend(words)
        
        # Bigrams
        for i in range(len(words)-1):
            phrases.append(f"{words[i]} {words[i+1]}")
            
        return phrases
        
    def _generate_variations(
        self,
        phrase: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate variations of a phrase"""
        variations = []
        
        # Add base phrase
        variations.append(phrase)
        
        # Add context-specific variations
        if 'domain' in context:
            variations.append(f"{context['domain']} {phrase}")
            
        # Add scope3-specific variations if relevant
        if 'scope3' in phrase.lower():
            variations.extend([
                f"scope 3 {phrase}",
                f"scope three {phrase}",
                f"indirect emissions {phrase}"
            ])
            
        return variations