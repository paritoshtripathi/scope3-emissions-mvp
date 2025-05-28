"""
Enhanced RAG API with Full Pipeline Capabilities and Swagger Documentation
"""
from flask import Flask, request, g
from flask_cors import CORS
from flask_restx import Api, Resource, fields
import logging
from pathlib import Path
from werkzeug.utils import secure_filename
import requests
import asyncio
from functools import wraps
from datetime import datetime
from typing import Dict, Any, Optional, Union, Tuple, List, cast

# Import RAG components
from ..rag_pipeline import EnhancedRAGPipeline
from ..processors.document_processor import DocumentProcessor
from ..embeddings.document_embedder import MultiLevelEmbedder
from ..retrieval.multi_vector_retriever import MultiVectorRetriever
from ..kb.kb_manager import KBManager
from ..kb.quality_assessor import QualityAssessor
from ..agents.conversation_expert import ConversationExpert
from ..utils.document_reader import DocumentReader

# Import Swagger models
from .swagger_config import (
    api, rag_ns, kb_ns,
    query_model, query_response,
    document_model, quality_metrics,
    success_response, error_response, health_response,
    file_upload_parser
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize API with Swagger
api.init_app(app)

# Initialize components
rag_pipeline = EnhancedRAGPipeline()
kb_manager = KBManager()
doc_processor = DocumentProcessor()
embedder = MultiLevelEmbedder()
retriever = MultiVectorRetriever()
doc_reader = DocumentReader()
conversation_expert = ConversationExpert()

# Initialize quality assessor with required components
quality_assessor = QualityAssessor(
    kb_manager=kb_manager,
    retriever=retriever,
    embedder=embedder
)

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent.parent.parent.parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize RAG Pipeline on startup
@app.before_request
def initialize_pipeline():
    """Initialize the RAG pipeline if not already initialized"""
    if not hasattr(g, '_pipeline_initialized'):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(rag_pipeline.initialize())
        g._pipeline_initialized = True
        logger.info("RAG Pipeline initialized")

# RAG System Endpoints
@rag_ns.route('/health')
class RagHealth(Resource):
    @rag_ns.doc('check_rag_health')
    @rag_ns.response(200, 'Success', health_response)
    def get(self):
        """Check RAG service health"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            stats = loop.run_until_complete(rag_pipeline.get_kb_stats())
            return {
                'status': 'healthy',
                'version': '1.0',
                'components': {
                    'kb_manager': stats['status']['kb'],
                    'vector_store': stats['status']['vector'],
                    'graph_db': stats['status']['graph']
                }
            }
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500

@rag_ns.route('/query')
class RagQuery(Resource):
    @rag_ns.doc('query_rag_system')
    @rag_ns.expect(query_model)
    @rag_ns.response(200, 'Success', query_response)
    def post(self):
        """Query RAG system"""
        try:
            data = request.get_json()
            query = data['text']
            context = data.get('context', {})
            options = data.get('options', {})

            # Add query to context
            context['query'] = query

            try:
                # Try RAG pipeline first
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(rag_pipeline.process_query(
                    query=query,
                    context=context,
                    options=options
                ))

                # If RAG pipeline fails or returns no response, use conversation expert
                if response.get('error') or not response.get('response'):
                    logger.info("Using conversation expert for response")
                    
                    # First let conversation expert think about the query
                    conversation_thought = loop.run_until_complete(
                        conversation_expert.think({
                            'query': query,
                            'context': context,
                            'previous_response': response,
                            'error': response.get('error')
                        })
                    )
                    
                    # Then let it act based on its analysis
                    conversation_response = loop.run_until_complete(
                        conversation_expert.act(conversation_thought)
                    )
                    
                    # Use conversation expert's response
                    response = {
                        'response': conversation_response.get('response', ''),
                        'confidence': conversation_response.get('confidence', 0.0),
                        'metadata': {
                            'source': 'conversation_expert',
                            'experts_used': conversation_response.get('route_to_experts', []),
                            'context': conversation_response.get('context_enhancement', {}),
                            'processing_type': conversation_response.get('processing_type', 'conversation')
                        }
                    }

                # Ensure consistent response format
                return {
                    'answer': response.get('response', ''),
                    'confidence': response.get('confidence', 0.0),
                    'sources': response.get('metadata', {}).get('sources', []),
                    'metadata': {
                        'experts_used': response.get('metadata', {}).get('experts_used', []),
                        'reasoning_paths': response.get('metadata', {}).get('reasoning_chain', []),
                        'context': response.get('metadata', {}).get('context', {}),
                        'processing_type': response.get('metadata', {}).get('processing_type', '')
                    }
                }

            except Exception as e:
                logger.error(f"Error processing query: {e}")
                # Use conversation expert for error handling
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Let conversation expert think about the error
                error_thought = loop.run_until_complete(
                    conversation_expert.think({
                        'query': query,
                        'context': context,
                        'error': str(e),
                        'error_type': 'processing_error'
                    })
                )
                
                # Get error response
                error_response = loop.run_until_complete(
                    conversation_expert.act(error_thought)
                )
                
                return {
                    'answer': error_response.get('response', ''),
                    'confidence': error_response.get('confidence', 0.0),
                    'sources': [],
                    'metadata': {
                        'experts_used': ['conversation_expert'],
                        'error_handled': True,
                        'context': error_response.get('context_enhancement', {}),
                        'processing_type': 'error_handling'
                    }
                }

        except Exception as e:
            logger.error(f"Error in query endpoint: {e}")
            return {'error': str(e)}, 500

# Knowledge Base Management Endpoints
@kb_ns.route('/documents')
class Documents(Resource):
    @kb_ns.doc('upload_document')
    @kb_ns.expect(file_upload_parser)
    @kb_ns.response(201, 'Success', success_response)
    @kb_ns.response(400, 'Validation Error', error_response)
    @kb_ns.response(500, 'Internal Server Error', error_response)
    def post(self):
        """Upload and process a document"""
        try:
            if 'file' not in request.files:
                return {'error': 'No file part'}, 400
            
            file = request.files['file']
            if not file or file.filename == '':
                return {'error': 'No selected file'}, 400
                
            if file and allowed_file(file.filename or ''):
                filename = secure_filename(file.filename or '')
                filepath = UPLOAD_FOLDER / filename
                file.save(str(filepath))
                
                content = doc_reader.read_file(filepath)
                if not content:
                    return {'error': 'Could not read file content'}, 400
                    
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                doc_id = loop.run_until_complete(rag_pipeline.add_document(
                    content=content,
                    metadata={
                        'filename': filename,
                        'source': 'upload',
                        'type': filepath.suffix[1:]
                    }
                ))
                
                return {'message': 'Document processed successfully', 'doc_id': doc_id}, 201
            return {'error': 'Invalid file type'}, 400
        except Exception as e:
            return {'error': str(e)}, 500

    @kb_ns.doc('get_documents')
    @kb_ns.response(200, 'Success', document_model)
    def get(self):
        """Get all documents"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            docs = loop.run_until_complete(kb_manager.get_documents())
            return docs
        except Exception as e:
            return {'error': str(e)}, 500

@kb_ns.route('/documents/<string:doc_id>')
class DocumentOperations(Resource):
    @kb_ns.doc('get_document')
    @kb_ns.response(200, 'Success', document_model)
    @kb_ns.response(404, 'Not Found', error_response)
    def get(self, doc_id):
        """Get a specific document"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            doc = loop.run_until_complete(kb_manager.get_document(doc_id))
            if not doc:
                return {'error': 'Document not found'}, 404
            return doc
        except Exception as e:
            return {'error': str(e)}, 500

    @kb_ns.doc('delete_document')
    @kb_ns.response(204, 'Document deleted')
    @kb_ns.response(404, 'Not Found', error_response)
    def delete(self, doc_id):
        """Delete a document"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(kb_manager.delete_document(doc_id))
            if not success:
                return {'error': 'Document not found'}, 404
            return '', 204
        except Exception as e:
            return {'error': str(e)}, 500

@kb_ns.route('/quality')
class Quality(Resource):
    @kb_ns.doc('assess_quality')
    @kb_ns.response(200, 'Success', quality_metrics)
    @kb_ns.response(500, 'Internal Server Error', error_response)
    def get(self):
        """Assess knowledge base quality"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            metrics = loop.run_until_complete(quality_assessor.assess_quality())
            return metrics
        except Exception as e:
            return {'error': str(e)}, 500

def create_app():
    """Create and configure the Flask application"""
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)