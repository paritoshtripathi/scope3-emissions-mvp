"""
Constants for API messages and labels
"""

# Status Messages
STATUS_HEALTHY = "healthy"
STATUS_DEGRADED = "degraded"
STATUS_SKIPPED = "skipped"

# Error Messages
ERR_PIPELINE_NOT_INIT = "Pipeline not initialized"
ERR_KB_NOT_INIT = "KB Manager not initialized"
ERR_GRAPH_NOT_INIT = "Graph manager not available"
ERR_NEO4J_UNAVAILABLE = "Neo4j service unavailable"
ERR_SERVICE_UNAVAILABLE = "Service unavailable"
ERR_CATEGORY_NOT_FOUND = "Category not found"

# Success Messages
MSG_DOC_ADDED = "Document added"
MSG_REL_ADDED = "Relationship added"
MSG_HEALTHY = "All components healthy"
MSG_DEGRADED = "Some components are in degraded state"

# Error Codes
CODE_NOT_FOUND = "not_found"
CODE_QUERY_ERROR = "query_error"
CODE_DOC_ERROR = "document_error"
CODE_RETRIEVAL_ERROR = "retrieval_error"
CODE_REL_ERROR = "relationship_error"
CODE_INSIGHT_ERROR = "insight_error"
CODE_PATTERN_ERROR = "pattern_error"
CODE_SEARCH_ERROR = "search_error"
CODE_STATS_ERROR = "stats_error"

# Default Values
DEFAULT_DAYS = 30
DEFAULT_TOP_K = 5

# Component Names
COMP_PIPELINE = "pipeline"
COMP_INFERENCE = "inference"
COMP_KB_MANAGER = "kb_manager"
COMP_NEO4J = "neo4j"

# Operation Names
OP_RAG_QUERY = "rag_query"
OP_ADD_DOC = "add_document"
OP_GET_DOCS = "get_documents"
OP_ADD_REL = "add_relationship"
OP_GET_INSIGHTS = "get_insights"
OP_ANALYZE_PATTERNS = "analyze_patterns"
OP_VECTOR_SEARCH = "vector_search"
OP_GET_STATS = "get_stats"

# Fallback Data
FALLBACK_CATEGORY_DATA = {
    "source_count": 0,
    "strategy_count": 0,
    "related_categories": [],
    "relationships": []
}

FALLBACK_PATTERNS = []