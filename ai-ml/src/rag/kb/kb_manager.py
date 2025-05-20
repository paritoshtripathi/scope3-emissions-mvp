"""
Enhanced Knowledge Base Manager with Versioning and Deduplication
"""
from typing import Dict, Any, List, Optional, Set, Tuple
import hashlib
import json
from datetime import datetime
import logging
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import networkx as nx
import os
from src.rag.graph.neo4j_manager import Neo4jManager

@dataclass
class DocumentVersion:
    version_id: str
    content_hash: str
    timestamp: str
    changes: Dict[str, Any]
    metadata: Dict[str, Any]

@dataclass
class Document:
    doc_id: str
    content: str
    chunks: List[str]
    metadata: Dict[str, Any]
    current_version: DocumentVersion
    version_history: List[DocumentVersion]

class KBManager:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize KB manager with versioning support"""
        self.db_path = db_path or 'kb_store.db'
        
        # Initialize Neo4j connection with environment variables
        self.graph_manager = Neo4jManager(
            uri=os.getenv('NEO4J_URI', 'bolt://neo4j:7687'),
            user=os.getenv('NEO4J_USER', 'neo4j'),
            password=os.getenv('NEO4J_PASSWORD', 'scope3password')
        )
        
        # Initialize SQLite database
        self._init_database()
        
        # Cache for document hashes
        self.content_hashes: Dict[str, str] = {}
        
        # Deduplication settings
        self.dedup_threshold = 0.9
        
        # Version tracking
        self.version_counter = 0
        
        logging.info("KBManager initialized with versioning support")

    async def initialize(self) -> None:
        """Initialize async components"""
        await self.graph_manager.initialize()

    def _init_database(self) -> None:
        """Initialize SQLite database with versioning tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    content TEXT,
                    metadata TEXT,
                    current_version TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS versions (
                    version_id TEXT PRIMARY KEY,
                    doc_id TEXT,
                    content_hash TEXT,
                    timestamp TEXT,
                    changes TEXT,
                    metadata TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents (doc_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT,
                    content TEXT,
                    embedding TEXT,
                    metadata TEXT,
                    FOREIGN KEY (doc_id) REFERENCES documents (doc_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    source_id TEXT,
                    target_id TEXT,
                    relationship_type TEXT,
                    metadata TEXT,
                    PRIMARY KEY (source_id, target_id, relationship_type)
                )
            """)

    async def add_document(
        self,
        content: str,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Add document with versioning and deduplication
        
        Args:
            content: Document content
            chunks: Processed chunks
            metadata: Document metadata
            
        Returns:
            Document ID
        """
        try:
            # Generate content hash
            content_hash = self._generate_hash(content)
            
            # Check for duplicates
            duplicate_id = await self._check_duplicate(content_hash, content)
            if duplicate_id:
                # Update existing document
                return await self.update_document(
                    duplicate_id,
                    content,
                    chunks,
                    metadata
                )
            
            # Create new document
            doc_id = f"doc_{len(self.content_hashes)}"
            version_id = self._generate_version_id()
            
            # Create version record
            version = DocumentVersion(
                version_id=version_id,
                content_hash=content_hash,
                timestamp=datetime.now().isoformat(),
                changes={'type': 'creation'},
                metadata=metadata
            )
            
            # Store document and version
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO documents VALUES (?, ?, ?, ?)",
                    (
                        doc_id,
                        content,
                        json.dumps(metadata),
                        version_id
                    )
                )
                
                conn.execute(
                    "INSERT INTO versions VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        version_id,
                        doc_id,
                        content_hash,
                        version.timestamp,
                        json.dumps(version.changes),
                        json.dumps(version.metadata)
                    )
                )
                
                # Store chunks
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    conn.execute(
                        "INSERT INTO chunks VALUES (?, ?, ?, ?, ?)",
                        (
                            chunk_id,
                            doc_id,
                            chunk,
                            "",  # embedding stored separately
                            json.dumps(metadata)
                        )
                    )
            
            # Update cache
            self.content_hashes[doc_id] = content_hash
            
            # Add to knowledge graph
            await self._add_to_graph(doc_id, content, metadata)
            
            return doc_id
            
        except Exception as e:
            logging.error(f"Error adding document: {e}")
            raise

    async def update_document(
        self,
        doc_id: str,
        content: str,
        chunks: List[str],
        metadata: Dict[str, Any]
    ) -> str:
        """Update document with new version"""
        try:
            # Generate new content hash
            new_hash = self._generate_hash(content)
            
            # Get current version
            current = await self.get_document(doc_id)
            if not current:
                raise ValueError(f"Document {doc_id} not found")
                
            # Check if content actually changed
            if new_hash == current.current_version.content_hash:
                return doc_id
                
            # Create new version
            version_id = self._generate_version_id()
            version = DocumentVersion(
                version_id=version_id,
                content_hash=new_hash,
                timestamp=datetime.now().isoformat(),
                changes=self._calculate_changes(
                    current.content,
                    content
                ),
                metadata=metadata
            )
            
            # Update database
            with sqlite3.connect(self.db_path) as conn:
                # Update document
                conn.execute(
                    """
                    UPDATE documents 
                    SET content = ?, metadata = ?, current_version = ?
                    WHERE doc_id = ?
                    """,
                    (content, json.dumps(metadata), version_id, doc_id)
                )
                
                # Add version
                conn.execute(
                    "INSERT INTO versions VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        version_id,
                        doc_id,
                        new_hash,
                        version.timestamp,
                        json.dumps(version.changes),
                        json.dumps(version.metadata)
                    )
                )
                
                # Update chunks
                conn.execute(
                    "DELETE FROM chunks WHERE doc_id = ?",
                    (doc_id,)
                )
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{i}"
                    conn.execute(
                        "INSERT INTO chunks VALUES (?, ?, ?, ?, ?)",
                        (
                            chunk_id,
                            doc_id,
                            chunk,
                            "",  # embedding stored separately
                            json.dumps(metadata)
                        )
                    )
            
            # Update cache
            self.content_hashes[doc_id] = new_hash
            
            # Update knowledge graph
            await self._update_graph(doc_id, content, metadata)
            
            return doc_id
            
        except Exception as e:
            logging.error(f"Error updating document: {e}")
            raise

    async def get_document(
        self,
        doc_id: str,
        version_id: Optional[str] = None
    ) -> Optional[Document]:
        """Get document with optional version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get document
                doc_row = conn.execute(
                    "SELECT * FROM documents WHERE doc_id = ?",
                    (doc_id,)
                ).fetchone()
                
                if not doc_row:
                    return None
                    
                # Get version history
                versions = conn.execute(
                    "SELECT * FROM versions WHERE doc_id = ?",
                    (doc_id,)
                ).fetchall()
                
                # Get chunks
                chunks = [
                    row[2] for row in conn.execute(
                        "SELECT * FROM chunks WHERE doc_id = ?",
                        (doc_id,)
                    ).fetchall()
                ]
                
                # Convert to Document object
                version_history = [
                    DocumentVersion(
                        version_id=v[0],
                        content_hash=v[2],
                        timestamp=v[3],
                        changes=json.loads(v[4]),
                        metadata=json.loads(v[5])
                    )
                    for v in versions
                ]
                
                # Get specified or current version
                target_version = version_id or doc_row[3]
                current_version = next(
                    v for v in version_history
                    if v.version_id == target_version
                )
                
                return Document(
                    doc_id=doc_id,
                    content=doc_row[1],
                    chunks=chunks,
                    metadata=json.loads(doc_row[2]),
                    current_version=current_version,
                    version_history=version_history
                )
                
        except Exception as e:
            logging.error(f"Error getting document: {e}")
            return None

    async def delete_document(self, doc_id: str) -> bool:
        """Delete document and its versions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete document and related records
                conn.execute("DELETE FROM documents WHERE doc_id = ?", (doc_id,))
                conn.execute("DELETE FROM versions WHERE doc_id = ?", (doc_id,))
                conn.execute("DELETE FROM chunks WHERE doc_id = ?", (doc_id,))
                conn.execute(
                    """
                    DELETE FROM relationships 
                    WHERE source_id = ? OR target_id = ?
                    """,
                    (doc_id, doc_id)
                )
            
            # Remove from cache
            self.content_hashes.pop(doc_id, None)
            
            # Remove from knowledge graph
            await self.graph_manager.delete_node(doc_id)
            
            return True
            
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            return False

    def _generate_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.sha256(content.encode()).hexdigest()

    def _generate_version_id(self) -> str:
        """Generate unique version ID"""
        self.version_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"v{timestamp}_{self.version_counter}"

    async def _check_duplicate(
        self,
        content_hash: str,
        content: str
    ) -> Optional[str]:
        """Check for duplicate documents"""
        # First check exact hash matches
        for doc_id, hash_value in self.content_hashes.items():
            if hash_value == content_hash:
                return doc_id
                
        # Then check for near-duplicates
        try:
            similar_docs = await self._find_similar_documents(content)
            if similar_docs:
                return similar_docs[0][0]  # Return most similar doc_id
                
        except Exception as e:
            logging.warning(f"Error checking near-duplicates: {e}")
            
        return None

    async def _find_similar_documents(
        self,
        content: str
    ) -> List[Tuple[str, float]]:
        """Find similar documents using embeddings"""
        # Implementation depends on embedding strategy
        # For now, return empty list
        return []

    def _calculate_changes(
        self,
        old_content: str,
        new_content: str
    ) -> Dict[str, Any]:
        """Calculate changes between versions"""
        # Simple change detection for now
        return {
            'type': 'update',
            'timestamp': datetime.now().isoformat(),
            'size_change': len(new_content) - len(old_content)
        }

    async def _add_to_graph(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Add document to knowledge graph"""
        # Add document node
        await self.graph_manager.add_node(
            doc_id,
            {
                'type': 'document',
                'metadata': metadata
            }
        )
        
        # Extract and add relationships
        relationships = self._extract_relationships(content, metadata)
        for rel in relationships:
            await self.graph_manager.add_relationship(
                source_id=doc_id,
                target_id=rel['target'],
                relationship_type=rel['type'],
                properties=rel['properties']
            )

    async def _update_graph(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Update document in knowledge graph"""
        # Update node properties
        await self.graph_manager.update_node(
            doc_id,
            {
                'type': 'document',
                'metadata': metadata,
                'last_updated': datetime.now().isoformat()
            }
        )
        
        # Update relationships
        await self.graph_manager.delete_relationships(doc_id)
        relationships = self._extract_relationships(content, metadata)
        for rel in relationships:
            await self.graph_manager.add_relationship(
                source_id=doc_id,
                target_id=rel['target'],
                relationship_type=rel['type'],
                properties=rel['properties']
            )

    def _extract_relationships(
        self,
        content: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract relationships from content"""
        relationships = []
        
        # Add category relationship
        if 'scope3_category' in metadata:
            relationships.append({
                'target': f"category_{metadata['scope3_category']}",
                'type': 'belongs_to',
                'properties': {
                    'confidence': 1.0
                }
            })
            
        # Add methodology relationship
        if 'methodology' in metadata:
            relationships.append({
                'target': f"methodology_{metadata['methodology']}",
                'type': 'uses',
                'properties': {
                    'confidence': 1.0
                }
            })
            
        return relationships

    def get_stats(self) -> Dict[str, Any]:
        """Get KB statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                doc_count = conn.execute(
                    "SELECT COUNT(*) FROM documents"
                ).fetchone()[0]
                
                version_count = conn.execute(
                    "SELECT COUNT(*) FROM versions"
                ).fetchone()[0]
                
                chunk_count = conn.execute(
                    "SELECT COUNT(*) FROM chunks"
                ).fetchone()[0]
                
                relationship_count = conn.execute(
                    "SELECT COUNT(*) FROM relationships"
                ).fetchone()[0]
                
            return {
                'document_count': doc_count,
                'version_count': version_count,
                'chunk_count': chunk_count,
                'relationship_count': relationship_count,
                'cache_size': len(self.content_hashes)
            }
            
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {}

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.graph_manager.close()
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

    async def get_documents(self) -> List[Dict[str, Any]]:
        """Get all documents with metadata"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT d.doc_id, d.content, d.metadata, d.current_version,
                           GROUP_CONCAT(c.content) as chunks
                    FROM documents d
                    LEFT JOIN chunks c ON d.doc_id = c.doc_id
                    GROUP BY d.doc_id
                    """
                )
                
                documents = []
                for row in cursor:
                    doc = {
                        'doc_id': row[0],
                        'content': row[1],
                        'metadata': json.loads(row[2]),
                        'version': row[3],
                        'chunks': row[4].split(',') if row[4] else []
                    }
                    documents.append(doc)
                return documents
                
        except Exception as e:
            logging.error(f"Error getting documents: {e}")
            return []