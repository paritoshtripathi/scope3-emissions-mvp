"""
Enhanced RAG Pipeline with MOE, TOT, and Graph Integration
"""
from typing import List, Dict, Any, Optional
import os
import logging
from .processors.document_processor import DocumentProcessor
from .embeddings.document_embedder import MultiLevelEmbedder
from .retrieval.multi_vector_retriever import MultiVectorRetriever
from .retrieval.context_augmenter import ContextAugmenter
from .models.inference import InferenceEngine
from .agents.agentic_rag import AgenticRAG, LearningContext
from .agents.moe_router import MoERouter
from .agents.tot_reasoner import ToTReasoner
from .kb.kb_manager import KBManager
from .indexing.faiss_indexes import FAISSIndexManager
from .graph.neo4j_manager import Neo4jManager
from ..config import get_config

class EnhancedRAGPipeline:
    def __init__(self, save_dir: Optional[str] = None):
        """Initialize the enhanced RAG pipeline with all components"""
        try:
            # Initialize sync components first
            self.save_dir = save_dir or os.path.join('models', 'rag')
            self.document_processor = DocumentProcessor()
            self.embedder = MultiLevelEmbedder()
            self.faiss_manager = FAISSIndexManager()
            self.retriever = MultiVectorRetriever()
            self.augmenter = ContextAugmenter()
            
            # Initialize components that need async setup
            self.inference = InferenceEngine()
            self.kb_manager = KBManager()
            self.graph_manager = Neo4jManager(
                uri=os.getenv('NEO4J_URI', 'bolt://neo4j:7687'),
                user=os.getenv('NEO4J_USER', 'neo4j'),
                password=os.getenv('NEO4J_PASSWORD', 'scope3password')
            )
            
            # Expert system components
            self.moe_router = MoERouter()
            self.tot_reasoner = ToTReasoner()
            self.agentic_rag = AgenticRAG()
            
            # Track initialization status
            self.initialization_status = {
                'kb_manager': False,
                'graph_manager': False
            }
            
            logging.info("Enhanced RAG Pipeline base initialization complete")
            
        except Exception as e:
            logging.error(f"Error initializing RAG Pipeline: {e}")
            raise

    async def initialize(self) -> None:
        """Initialize async components with graceful degradation"""
        try:
            # Initialize KB Manager
            try:
                await self.kb_manager.initialize()
                self.initialization_status['kb_manager'] = True
                logging.info("KB Manager initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing KB Manager: {e}")
                self.initialization_status['kb_manager'] = False

            # Initialize Graph Manager
            try:
                await self.graph_manager.initialize()
                self.initialization_status['graph_manager'] = True
                logging.info("Graph Manager initialized successfully")
            except Exception as e:
                logging.error(f"Error initializing Graph Manager: {e}")
                self.initialization_status['graph_manager'] = False

            # Log overall status
            if all(self.initialization_status.values()):
                logging.info("Enhanced RAG Pipeline async initialization complete")
            else:
                failed_components = [k for k, v in self.initialization_status.items() if not v]
                logging.warning(f"Partial initialization - Failed components: {failed_components}")

        except Exception as e:
            logging.error(f"Error in async initialization: {e}")
            # Continue with partial functionality instead of raising

    def process_document(self, content: str) -> Dict[str, Any]:
        """
        Process document synchronously (CPU-bound operations)
        """
        # Process document
        processed = self.document_processor.process(content)
        if not isinstance(processed, dict) or 'content' not in processed or 'chunks' not in processed:
            raise ValueError("Document processor returned invalid format")
        
        # Ensure content is a string and chunks is a list of strings
        doc_content = processed['content']
        if isinstance(doc_content, list):
            doc_content = ' '.join(doc_content)
        
        doc_chunks = processed['chunks']
        if not isinstance(doc_chunks, list):
            doc_chunks = [str(doc_chunks)]
        doc_chunks = [str(chunk) for chunk in doc_chunks]
        
        # Generate embeddings
        embeddings = self.embedder.embed_multi_level(doc_chunks)
        
        return {
            'content': doc_content,
            'chunks': doc_chunks,
            'embeddings': embeddings
        }

    async def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add document to the knowledge base
        Combines sync processing with async storage
        """
        try:
            # Sync processing
            processed = self.process_document(content)
            
            # Add to retriever (sync)
            self.retriever.add_documents(
                chunks=processed['chunks'],
                embeddings=processed['embeddings'],
                metadata=metadata
            )
            
            # Async storage operations
            doc_id = await self.kb_manager.add_document(
                content=processed['content'],
                chunks=processed['chunks'],
                metadata=metadata or {}
            )
            
            # Store relationships (async)
            if metadata and metadata.get('scope3_category'):
                await self._process_scope3_relationships(
                    content,
                    metadata,
                    doc_id
                )
            
            return doc_id
            
        except Exception as e:
            logging.error(f"Error adding document: {e}")
            return str(e)

    def process_query_sync(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query synchronously (CPU-bound operations)
        """
        # Initialize context
        context = context or {}
        context['query'] = query
        options = options or {}
        
        # Process query
        processed_query = self.document_processor.process(query)
        
        # Generate embeddings
        query_embeddings = self.embedder.embed_multi_level(query)
        
        return {
            'processed_query': processed_query,
            'query_embeddings': query_embeddings,
            'context': context,
            'options': options
        }

    async def process_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process query through the pipeline
        Combines sync and async operations
        """
        try:
            # Sync processing first
            processed = self.process_query_sync(query, context, options)
            
            # Async operations
            retrieved_docs = await self.retriever.retrieve(
                query_embeddings=processed['query_embeddings'],
                query=query,
                top_k=(processed['options'] or {}).get('top_k', 5)
            )
            
            augmented_context = await self.augmenter.augment(
                query=query,
                documents=retrieved_docs,
                embeddings=processed['query_embeddings']
            )
            
            # Get graph insights (async)
            graph_insights = await self._get_graph_insights(
                query,
                retrieved_docs
            )
            augmented_context['graph_insights'] = graph_insights
            
            # Expert system operations (async)
            expert_context = await self.moe_router.think({
                **processed['context'],
                **augmented_context
            })
            
            reasoning = await self.tot_reasoner.think({
                'query': query,
                'context': augmented_context,
                'expert_assignments': expert_context.get('expert_assignments', {})
            })
            
            agentic_context = {
                **augmented_context,
                'expert_context': expert_context,
                'reasoning_paths': reasoning.get('thought_paths', []),
                'retrieved_docs': retrieved_docs
            }
            
            agentic_thought = await self.agentic_rag.think(agentic_context)
            agentic_response = await self.agentic_rag.act(agentic_thought)
            
            expert_responses = await self.moe_router.act(expert_context)
            
            final_response = await self._synthesize_response(
                agentic_response,
                expert_responses,
                reasoning
            )
            
            return final_response
            
        except Exception as e:
            logging.error(f"Error in RAG pipeline: {e}")
            return {
                'error': str(e),
                'query': query
            }

    async def _get_graph_insights(
        self,
        query: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get insights from graph database (async)"""
        try:
            # Check Neo4j availability
            if not self.initialization_status['graph_manager'] or not self.graph_manager.is_connected:
                return {
                    'status': 'neo4j_unavailable',
                    'insights': {},
                    'relationships': None
                }

            # Extract categories (sync)
            categories = self._extract_scope3_categories(query, retrieved_docs)
            
            # Get insights (async)
            insights = {}
            for category in categories:
                cat_insights = await self.graph_manager.get_category_insights(
                    category
                )
                
                opportunities = await self.graph_manager.find_reduction_opportunities(
                    category,
                    min_impact=0.1
                )
                
                insights[category] = {
                    'insights': cat_insights,
                    'opportunities': opportunities
                }
            
            graph = await self.graph_manager.get_relationship_graph(depth=2)
            insights['relationships'] = graph
            
            return insights
            
        except Exception as e:
            logging.error(f"Error getting graph insights: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'insights': {},
                'relationships': None
            }

    async def _process_scope3_relationships(
        self,
        content: str,
        metadata: Dict[str, Any],
        doc_id: str
    ) -> None:
        """Process and store relationships (async)"""
        # Skip if Neo4j is not available
        if not self.initialization_status['graph_manager'] or not self.graph_manager.is_connected:
            logging.info("Neo4j not available, skipping relationship processing")
            return

        try:
            category = metadata['scope3_category']
            
            if 'emission_value' in metadata:
                await self.graph_manager.add_emission_source(
                    source_id=doc_id,
                    category=category,
                    properties={
                        'emission_value': metadata['emission_value'],
                        'source': metadata.get('source', 'unknown')
                    }
                )
            
            if metadata.get('is_strategy', False):
                await self.graph_manager.add_reduction_strategy(
                    strategy_id=doc_id,
                    name=metadata.get('strategy_name', ''),
                    categories=[category],
                    properties=metadata
                )
        except Exception as e:
            logging.error(f"Error processing relationships: {e}")
            # Continue without relationships

    async def _synthesize_response(
        self,
        agentic_response: Dict[str, Any],
        expert_responses: Dict[str, Any],
        reasoning: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize final response"""
        return {
            'response': agentic_response.get('response', ''),
            'expert_insights': expert_responses,
            'reasoning_chain': reasoning.get('reasoning_chain', []),
            'confidence': agentic_response.get('confidence', 0.0),
            'metadata': {
                'experts_used': list(expert_responses.keys()),
                'reasoning_paths': reasoning.get('thought_paths', []),
                'sources': agentic_response.get('sources', [])
            }
        }

    def _extract_scope3_categories(
        self,
        query: str,
        docs: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract categories (sync)"""
        categories = set()
        query_lower = query.lower()
        for doc in docs:
            if 'metadata' in doc and 'scope3_category' in doc['metadata']:
                categories.add(doc['metadata']['scope3_category'])
        return list(categories)

    def get_agent_state(self) -> Dict[str, Any]:
        """Get agent state (sync)"""
        return {
            'agentic_rag': self.agentic_rag.get_state(),
            'moe_router': self.moe_router.get_performance_metrics(),
            'tot_reasoner': self.tot_reasoner.get_state()
        }

    def reset_agents(self) -> None:
        """Reset agents (sync)"""
        self.agentic_rag.learning_context = LearningContext()
        self.agentic_rag.retrieval_history = []
        self.agentic_rag.query_refinements = []
        self.moe_router.reload_config()
        self.tot_reasoner = ToTReasoner()

    async def get_kb_stats(self) -> Dict[str, Any]:
        """Get KB stats (combines sync and async)"""
        stats = {
            'kb_stats': self.kb_manager.get_stats(),  # sync
            'vector_stats': self.retriever.get_stats(),  # sync
            'graph_stats': None,
            'status': {
                'kb': True,
                'vector': True,
                'graph': False
            }
        }

        if self.initialization_status['graph_manager'] and self.graph_manager.is_connected:
            try:
                stats['graph_stats'] = await self.graph_manager.get_relationship_graph()
                stats['status']['graph'] = True
            except Exception as e:
                logging.warning(f"Error getting graph stats: {e}")
                stats['graph_error'] = str(e)

        return stats