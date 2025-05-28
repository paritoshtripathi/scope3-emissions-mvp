"""
Knowledge Base Initialization Script
"""
import os
import logging
import asyncio
from pathlib import Path
import json
import uuid

from ..kb.kb_manager import KBManager
from ..processors.document_processor import DocumentProcessor
from ..utils.document_reader import DocumentReader
from ..embeddings.document_embedder import MultiLevelEmbedder
from ..retrieval.multi_vector_retriever import MultiVectorRetriever

# Global components for state persistence
kb_manager = KBManager()
doc_processor = DocumentProcessor()
embedder = MultiLevelEmbedder()
retriever = MultiVectorRetriever()

async def process_document(content: str, metadata: dict) -> bool:
    """Process a single document and add to KB"""
    if not content or not content.strip():
        logging.warning(f"Empty content for document: {metadata.get('source', 'unknown')}")
        return False

    try:
        # Process content
        processed = doc_processor.process(content)
        if not processed or not processed.get('chunks'):
            logging.warning(f"No chunks generated for document: {metadata.get('source', 'unknown')}")
            return False

        # Generate embeddings
        embeddings = embedder.embed_multi_level(processed['chunks'])
        
        # Add to both KB and retriever
        await kb_manager.add_document(
            content=content,
            chunks=processed['chunks'],
            metadata=metadata
        )
        retriever.add_documents(
            chunks=processed['chunks'],
            embeddings=embeddings,
            metadata=metadata
        )
        logging.info(f"Added document with ID: {metadata['doc_id']}")
        return True
    except Exception as e:
        logging.error(f"Error processing document {metadata.get('source', 'unknown')}: {e}")
        return False

async def init_knowledge_base() -> bool:
    """Initialize knowledge base with scope3 documents"""
    try:
        # Get KB directory path
        kb_dir = Path(__file__).parent.parent.parent.parent / 'kb'
        
        # First load combined knowledge
        combined_path = kb_dir / 'combined_scope3_knowledge.txt'
        if combined_path.exists():
            logging.info("Loading combined scope3 knowledge...")
            content = DocumentReader.read_text(combined_path)
            if content:
                doc_id = f"doc_{uuid.uuid4().hex[:8]}"
                metadata = {
                    'doc_id': doc_id,
                    'type': 'base_knowledge',
                    'source': 'combined_scope3_knowledge',
                    'category': 'general'
                }
                await process_document(content, metadata)
        
        # Load category documents
        for pdf_file in kb_dir.glob('Category*.pdf'):
            logging.info(f"Loading {pdf_file.name}...")
            
            # Extract category from filename
            category = pdf_file.stem.split('-')[1].strip()
            
            # Read PDF content
            content = DocumentReader.read_pdf(pdf_file)
            if content:
                doc_id = f"doc_{uuid.uuid4().hex[:8]}"
                metadata = {
                    'doc_id': doc_id,
                    'type': 'category_guide',
                    'source': pdf_file.name,
                    'category': category,
                    'scope3_category': category.lower().replace(' ', '_')
                }
                await process_document(content, metadata)
            else:
                logging.warning(f"Could not read content from {pdf_file}")
        
        # Load additional documents
        additional_docs = [
            ('Imp-1-Scope3_Calculation_Guidance.pdf', 'calculation_guidance'),
            ('Intro_GHGP_Tech.pdf', 'technical_intro'),
            ('SBT_Value_Chain_Report-1.pdf', 'value_chain'),
            ('Scope-3-Proposals-Summary-Draft.pdf', 'proposals')
        ]
        
        for filename, doc_type in additional_docs:
            file_path = kb_dir / filename
            if file_path.exists():
                logging.info(f"Loading {filename}...")
                
                # Read document content
                content = DocumentReader.read_file(file_path)
                if content:
                    doc_id = f"doc_{uuid.uuid4().hex[:8]}"
                    metadata = {
                        'doc_id': doc_id,
                        'type': doc_type,
                        'source': filename,
                        'category': 'general'
                    }
                    await process_document(content, metadata)
                else:
                    logging.warning(f"Could not read content from {filename}")
        
        # Log KB stats
        kb_stats = kb_manager.get_stats()
        retriever_stats = retriever.get_stats()
        logging.info(f"Knowledge base initialized with stats: {json.dumps(kb_stats, indent=2)}")
        logging.info(f"Retriever initialized with stats: {json.dumps(retriever_stats, indent=2)}")
        
        # Verify initialization
        docs = await kb_manager.get_documents()
        logging.info(f"Loaded {len(docs)} documents into knowledge base")
        
        # Run verification
        return await verify_kb_initialization()
        
    except Exception as e:
        logging.error(f"Error initializing knowledge base: {e}")
        return False

async def verify_kb_initialization() -> bool:
    """Verify knowledge base is properly initialized"""
    try:
        kb_stats = kb_manager.get_stats()
        retriever_stats = retriever.get_stats()
        
        # Check if documents are loaded in KB
        if kb_stats.get('document_count', 0) == 0:
            logging.error("No documents found in knowledge base")
            return False
            
        # Check if chunks are created in KB
        if kb_stats.get('chunk_count', 0) == 0:
            logging.error("No chunks found in knowledge base")
            return False
            
        # Check if documents are loaded in retriever
        if retriever_stats.get('total_documents', 0) == 0:
            logging.error("No documents found in retriever")
            return False
            
        logging.info("Knowledge base verification successful")
        logging.info(f"KB Stats: {json.dumps(kb_stats, indent=2)}")
        logging.info(f"Retriever Stats: {json.dumps(retriever_stats, indent=2)}")
        return True
        
    except Exception as e:
        logging.error(f"Error verifying knowledge base: {e}")
        return False

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    success = asyncio.run(init_knowledge_base())
    exit(0 if success else 1)