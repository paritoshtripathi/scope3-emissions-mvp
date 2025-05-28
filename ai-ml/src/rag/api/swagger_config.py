"""
Swagger configuration for Scope3 RAG API
"""
from flask_restx import Api, Namespace, fields

# Create API with Swagger UI
api = Api(
    title='Scope3 RAG API',
    version='1.0',
    description='RAG API for Scope3 Emissions Analysis',
    doc='/',
    prefix='/api'
)

# Create namespaces
rag_ns = Namespace('rag', description='RAG query and management')
kb_ns = Namespace('kb', description='Knowledge Base operations')

# Add namespaces to API
api.add_namespace(rag_ns)
api.add_namespace(kb_ns)

# Query Models
query_model = api.model('Query', {
    'text': fields.String(required=True, description='Query text', example='What are the main sources of scope 3 emissions?'),
    'context': fields.Raw(description='Additional context for the query', example={'category': 'purchased_goods'}),
    'options': fields.Raw(description='Query options', example={'use_moe': True, 'max_tokens': 250})
})

query_response = api.model('QueryResponse', {
    'answer': fields.String(required=True, description='Generated response'),
    'confidence': fields.Float(description='Response confidence score'),
    'sources': fields.List(fields.String, description='Source documents used'),
    'metadata': fields.Raw(description='Additional response metadata')
})

# Document Models
document_metadata = api.model('DocumentMetadata', {
    'scope3_category': fields.String(example='Purchased Goods and Services'),
    'source': fields.String(example='Supplier Report'),
    'timestamp': fields.DateTime,
    'confidence': fields.Float
})

document_model = api.model('Document', {
    'doc_id': fields.String(description='Document ID'),
    'content': fields.String(description='Document content'),
    'metadata': fields.Nested(document_metadata),
    'chunks': fields.List(fields.String)
})

# Quality Assessment Models
quality_metrics = api.model('QualityMetrics', {
    'completeness': fields.Float(example=0.85, description='Knowledge base completeness score'),
    'consistency': fields.Float(example=0.92, description='Data consistency score'),
    'relevance': fields.Float(example=0.78, description='Content relevance score'),
    'coverage': fields.Raw(description='Category coverage statistics'),
    'recommendations': fields.List(fields.String, description='Improvement recommendations')
})

# Response Models
success_response = api.model('SuccessResponse', {
    'message': fields.String(required=True, description='Success message'),
    'data': fields.Raw(description='Response data')
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(required=True, description='Error message'),
    'details': fields.Raw(description='Error details')
})

health_response = api.model('HealthResponse', {
    'status': fields.String(required=True, example='healthy', description='API health status'),
    'version': fields.String(required=True, example='1.0', description='API version'),
    'components': fields.Raw(required=True, description='Component statuses', example={
        'kb_manager': True,
        'vector_store': True,
        'graph_db': True
    })
})

# File Upload Parser
file_upload_parser = api.parser()
file_upload_parser.add_argument(
    'file',
    location='files',
    type='FileStorage',
    required=True,
    help='Document file to upload (PDF, DOCX, TXT)'
)