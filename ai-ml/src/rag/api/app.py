"""
Enhanced RAG API with Swagger documentation
"""
from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
import asyncio
import os
import sys
import time
from typing import Dict, Any
from http import HTTPStatus
from contextlib import contextmanager

from src.rag.rag_pipeline import EnhancedRAGPipeline
from src.rag.models.inference import InferenceEngine
from src.rag.kb.kb_manager import KBManager
from src.config.config_loader import ConfigLoader
from src.monitoring.monitor import Monitor

# Initialize monitoring
monitor = Monitor()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize API with Swagger documentation
api = Api(
    app,
    version='1.0',
    title='Scope3 Enhanced RAG API',
    description='RAG API with MOE, TOT, Neo4j, and FAISS capabilities',
    doc='/api/v1/docs',
    prefix='/api/v1'
)

# Create namespaces
rag_ns = Namespace('rag', description='RAG operations')
agent_ns = Namespace('agent', description='Agent operations')
kb_ns = Namespace('kb', description='Knowledge Base operations')
graph_ns = Namespace('graph', description='Graph operations')
vector_ns = Namespace('vector', description='Vector operations')

# Add namespaces to API
api.add_namespace(rag_ns)
api.add_namespace(agent_ns)
api.add_namespace(kb_ns)
api.add_namespace(graph_ns)
api.add_namespace(vector_ns)

# Initialize components
config_loader = ConfigLoader.get_instance()
config = config_loader.get_config('default')  # Using default config

# Initialize pipeline and other components
def init_components():
    """Initialize all components"""
    global pipeline, inference, kb_manager
    pipeline = EnhancedRAGPipeline()
    inference = InferenceEngine()
    kb_manager = KBManager()
    run_async(pipeline.initialize())
    run_async(kb_manager.initialize())

# Helper function to run async code
def run_async(coro):
    """Helper function to run coroutines in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Initialize components before app starts
init_components()

# Common Models
error_model = api.model('Error', {
    'code': fields.String(required=True, description='Error code'),
    'message': fields.String(required=True, description='Error message')
})

metadata_model = api.model('Metadata', {
    'source': fields.String(description='Source of the document'),
    'timestamp': fields.DateTime(description='Document timestamp'),
    'category': fields.String(description='Scope3 category'),
    'confidence': fields.Float(description='Confidence score')
})

# RAG Models
query_model = api.model('Query', {
    'text': fields.String(required=True, description='Query text'),
    'context': fields.Raw(description='Additional context'),
    'options': fields.Raw(description='Query options')
})

rag_response_model = api.model('RAGResponse', {
    'response': fields.String(required=True, description='Generated response'),
    'sources': fields.List(fields.Raw, description='Source documents'),
    'metadata': fields.Raw(description='Response metadata'),
    'confidence': fields.Float(description='Confidence score')
})

# KB Models
document_model = api.model('Document', {
    'content': fields.String(required=True, description='Document content'),
    'metadata': fields.Nested(metadata_model, description='Document metadata')
})

kb_stats_model = api.model('KBStats', {
    'total_documents': fields.Integer(description='Total documents'),
    'vector_stats': fields.Raw(description='Vector index statistics'),
    'graph_stats': fields.Raw(description='Graph statistics'),
    'last_updated': fields.DateTime(description='Last update timestamp')
})

# Graph Models
relationship_model = api.model('Relationship', {
    'source_category': fields.String(required=True, description='Source category'),
    'target_category': fields.String(required=True, description='Target category'),
    'relationship_type': fields.String(required=True, description='Relationship type'),
    'properties': fields.Raw(description='Relationship properties')
})

insight_model = api.model('CategoryInsight', {
    'category': fields.String(required=True, description='Category name'),
    'source_count': fields.Integer(description='Number of emission sources'),
    'strategy_count': fields.Integer(description='Number of reduction strategies'),
    'related_categories': fields.List(fields.String, description='Related categories'),
    'relationships': fields.List(fields.String, description='Relationship types')
})

pattern_model = api.model('EmissionPattern', {
    'category': fields.String(required=True, description='Category name'),
    'average_emission': fields.Float(description='Average emission value'),
    'trend': fields.String(description='Emission trend'),
    'data_points': fields.Integer(description='Number of data points')
})

# Vector Models
vector_search_model = api.model('VectorSearch', {
    'query_vector': fields.List(fields.Float, description='Query vector'),
    'k': fields.Integer(description='Number of results', default=5),
    'nprobe': fields.Integer(description='Number of clusters to search')
})

vector_result_model = api.model('VectorSearchResult', {
    'id': fields.Integer(description='Vector ID'),
    'distance': fields.Float(description='Distance score'),
    'metadata': fields.Raw(description='Vector metadata')
})

@contextmanager
def monitor_operation(name: str):
    """Context manager for monitoring operations"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        monitor.record_operation(name, duration)

@rag_ns.route('/query')
class RAGQuery(Resource):
    @rag_ns.expect(query_model)
    @rag_ns.response(200, 'Success', rag_response_model)
    @rag_ns.response(400, 'Bad Request', error_model)
    def post(self):
        """Execute RAG query with enhanced capabilities"""
        try:
            data = request.get_json()
            with monitor_operation("rag_query"):
                result = run_async(pipeline.process_query(
                    query=data['text'],
                    context=data.get('context', {}),
                    options=data.get('options', {})
                ))
            return jsonify(result)
        except Exception as e:
            rag_ns.abort(500, code='query_error', message=str(e))

@kb_ns.route('/documents')
class Documents(Resource):
    @kb_ns.expect(document_model)
    @kb_ns.response(201, 'Document added successfully')
    @kb_ns.response(400, 'Bad Request', error_model)
    def post(self):
        """Add document to KB with vector indexing and relationship extraction"""
        try:
            data = request.get_json()
            with monitor_operation("add_document"):
                doc_id = run_async(pipeline.add_document(
                    content=data['content'],
                    metadata=data.get('metadata')
                ))
            return {'message': 'Document added', 'id': doc_id}, 201
        except Exception as e:
            kb_ns.abort(500, code='document_error', message=str(e))

    @kb_ns.response(200, 'Success', fields.List(fields.Nested(document_model)))
    def get(self):
        """Get all documents with metadata"""
        try:
            with monitor_operation("get_documents"):
                docs = run_async(kb_manager.get_documents())
            return jsonify(docs)
        except Exception as e:
            kb_ns.abort(500, code='retrieval_error', message=str(e))

@graph_ns.route('/relationships')
class GraphRelationships(Resource):
    @graph_ns.expect(relationship_model)
    @graph_ns.response(201, 'Relationship added successfully')
    @graph_ns.response(400, 'Bad Request', error_model)
    def post(self):
        """Add relationship between Scope3 categories"""
        try:
            data = request.get_json()
            with monitor_operation("add_relationship"):
                run_async(pipeline.graph_manager.add_category_relationship(
                    category=data['source_category'],
                    related_category=data['target_category'],
                    relationship_type=data['relationship_type'],
                    properties=data.get('properties', {})
                ))
            return {'message': 'Relationship added'}, 201
        except Exception as e:
            graph_ns.abort(500, code='relationship_error', message=str(e))

@graph_ns.route('/insights/<category>')
class CategoryInsights(Resource):
    @graph_ns.response(200, 'Success', insight_model)
    @graph_ns.response(404, 'Category not found', error_model)
    def get(self, category):
        """Get insights for specific Scope3 category"""
        try:
            with monitor_operation("get_insights"):
                insights = run_async(pipeline.graph_manager.get_category_insights(category))
            if not insights:
                graph_ns.abort(404, code='not_found', message='Category not found')
            return jsonify(insights)
        except Exception as e:
            graph_ns.abort(500, code='insight_error', message=str(e))

@graph_ns.route('/patterns')
class EmissionPatterns(Resource):
    @graph_ns.response(200, 'Success', fields.List(fields.Nested(pattern_model)))
    def get(self):
        """Analyze emission patterns across categories"""
        try:
            with monitor_operation("analyze_patterns"):
                patterns = run_async(pipeline.graph_manager.analyze_patterns(
                    timeframe_days=int(request.args.get('days', 30))
                ))
            return jsonify(patterns)
        except Exception as e:
            graph_ns.abort(500, code='pattern_error', message=str(e))

@vector_ns.route('/search')
class VectorSearch(Resource):
    @vector_ns.expect(vector_search_model)
    @vector_ns.response(200, 'Success', fields.List(fields.Nested(vector_result_model)))
    def post(self):
        """Search similar vectors using FAISS"""
        try:
            data = request.get_json()
            with monitor_operation("vector_search"):
                results = pipeline.retriever.search_vectors(
                    query_vector=data['query_vector'],
                    k=data.get('k', 5),
                    nprobe=data.get('nprobe')
                )
            return jsonify(results)
        except Exception as e:
            vector_ns.abort(500, code='search_error', message=str(e))

@kb_ns.route('/stats')
class KBStats(Resource):
    @kb_ns.response(200, 'Success', kb_stats_model)
    def get(self):
        """Get KB statistics including vector and graph metrics"""
        try:
            with monitor_operation("get_stats"):
                stats = run_async(pipeline.get_kb_stats())
            return jsonify(stats)
        except Exception as e:
            kb_ns.abort(500, code='stats_error', message=str(e))

# Add health check endpoint
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "components": {
            "pipeline": pipeline is not None,
            "kb_manager": kb_manager is not None,
            "inference": inference is not None
        }
    }), 200

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=bool(os.getenv('FLASK_DEBUG', True))
    )