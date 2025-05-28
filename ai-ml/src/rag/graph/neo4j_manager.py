"""
Neo4j Graph Manager for Scope3 Relationship Analysis
"""
from typing import Dict, Any, List, Optional, cast
from typing_extensions import LiteralString
from neo4j import AsyncGraphDatabase, Query
import logging
from datetime import datetime
from contextlib import asynccontextmanager

class Neo4jManager:
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.is_connected = False
        self.logger = logging.getLogger(__name__)

    def _make_query(self, query_text: str) -> Query:
        """Helper to create a Query object with proper type casting"""
        return Query(cast(LiteralString, query_text))

    @asynccontextmanager
    async def get_session(self):
        """Get a Neo4j session with error handling"""
        if not self.is_connected or not self.driver:
            self.logger.debug("No active Neo4j connection")
            yield None
            return

        session = None
        try:
            session = self.driver.session()
            yield session
        finally:
            if session:
                await session.close()

    async def initialize(self) -> None:
        """Initialize Neo4j schema and setup"""
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection
            async with self.driver.session() as session:
                await session.run(self._make_query("RETURN 1"))
            self.is_connected = True
            await self._init_schema()
            self.logger.info("Neo4j connection established successfully")
        except Exception as e:
            self.is_connected = False
            self.logger.warning(f"Neo4j connection failed: {str(e)}. Operating in fallback mode.")

    async def _init_schema(self) -> None:
        """Initialize Neo4j schema with constraints and indexes"""
        if not self.is_connected:
            return
            
        try:
            async with self.get_session() as session:
                if session:
                    # Create constraints
                    await session.run(self._make_query("""
                        CREATE CONSTRAINT scope3_category_name IF NOT EXISTS
                        FOR (c:Scope3Category) REQUIRE c.name IS UNIQUE
                    """))
                    
                    await session.run(self._make_query("""
                        CREATE CONSTRAINT emission_source_id IF NOT EXISTS
                        FOR (s:EmissionSource) REQUIRE s.source_id IS UNIQUE
                    """))
        except Exception as e:
            self.logger.error(f"Failed to initialize Neo4j schema: {str(e)}")

    async def add_node(self, node_id: str, properties: Dict[str, Any]) -> None:
        """Add a node to the graph"""
        if not self.is_connected:
            self.logger.debug(f"Skipping add_node in fallback mode: {node_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MERGE (n:Node {id: $node_id})
                        SET n += $props
                    """), {
                        'node_id': node_id,
                        'props': properties
                    })
        except Exception as e:
            self.logger.error(f"Failed to add node: {str(e)}")

    async def update_node(self, node_id: str, properties: Dict[str, Any]) -> None:
        """Update a node's properties"""
        if not self.is_connected:
            self.logger.debug(f"Skipping update_node in fallback mode: {node_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MATCH (n:Node {id: $node_id})
                        SET n += $props
                    """), {
                        'node_id': node_id,
                        'props': properties
                    })
        except Exception as e:
            self.logger.error(f"Failed to update node: {str(e)}")

    async def delete_node(self, node_id: str) -> None:
        """Delete a node and its relationships"""
        if not self.is_connected:
            self.logger.debug(f"Skipping delete_node in fallback mode: {node_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MATCH (n:Node {id: $node_id})
                        DETACH DELETE n
                    """), {
                        'node_id': node_id
                    })
        except Exception as e:
            self.logger.error(f"Failed to delete node: {str(e)}")

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add a relationship between nodes"""
        if not self.is_connected:
            self.logger.debug(f"Skipping add_relationship in fallback mode: {source_id} -> {target_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MATCH (s:Node {id: $source_id})
                        MATCH (t:Node {id: $target_id})
                        MERGE (s)-[r:RELATES_TO {type: $rel_type}]->(t)
                        SET r += $props
                    """), {
                        'source_id': source_id,
                        'target_id': target_id,
                        'rel_type': relationship_type,
                        'props': properties
                    })
        except Exception as e:
            self.logger.error(f"Failed to add relationship: {str(e)}")

    async def delete_relationships(self, node_id: str) -> None:
        """Delete all relationships for a node"""
        if not self.is_connected:
            self.logger.debug(f"Skipping delete_relationships in fallback mode: {node_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MATCH (n:Node {id: $node_id})-[r]-()
                        DELETE r
                    """), {
                        'node_id': node_id
                    })
        except Exception as e:
            self.logger.error(f"Failed to delete relationships: {str(e)}")

    async def add_category_relationship(
        self,
        category: str,
        related_category: str,
        relationship_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add relationship between Scope3 categories"""
        if not self.is_connected:
            self.logger.debug(f"Skipping add_category_relationship in fallback mode")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MERGE (c1:Scope3Category {name: $cat1})
                        MERGE (c2:Scope3Category {name: $cat2})
                        MERGE (c1)-[r:RELATES_TO {type: $rel_type}]->(c2)
                        SET r += $props
                    """), {
                        'cat1': category,
                        'cat2': related_category,
                        'rel_type': relationship_type,
                        'props': properties
                    })
        except Exception as e:
            self.logger.error(f"Failed to add category relationship: {str(e)}")

    async def add_emission_source(
        self,
        source_id: str,
        category: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add emission source with category relationship"""
        if not self.is_connected:
            self.logger.debug(f"Skipping add_emission_source in fallback mode: {source_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MERGE (s:EmissionSource {source_id: $source_id})
                        SET s += $props
                        WITH s
                        MERGE (c:Scope3Category {name: $category})
                        MERGE (s)-[:BELONGS_TO]->(c)
                    """), {
                        'source_id': source_id,
                        'category': category,
                        'props': properties
                    })
        except Exception as e:
            self.logger.error(f"Failed to add emission source: {str(e)}")

    async def add_reduction_strategy(
        self,
        strategy_id: str,
        name: str,
        categories: List[str],
        properties: Dict[str, Any]
    ) -> None:
        """Add reduction strategy with category relationships"""
        if not self.is_connected:
            self.logger.debug(f"Skipping add_reduction_strategy in fallback mode: {strategy_id}")
            return

        try:
            async with self.get_session() as session:
                if session:
                    await session.run(self._make_query("""
                        MERGE (s:ReductionStrategy {strategy_id: $strategy_id})
                        SET s.name = $name
                        SET s += $props
                        WITH s
                        UNWIND $categories as cat
                        MERGE (c:Scope3Category {name: cat})
                        MERGE (s)-[:APPLIES_TO]->(c)
                    """), {
                        'strategy_id': strategy_id,
                        'name': name,
                        'categories': categories,
                        'props': properties
                    })
        except Exception as e:
            self.logger.error(f"Failed to add reduction strategy: {str(e)}")

    async def get_category_insights(self, category: str) -> Optional[Dict[str, Any]]:
        """Get insights for a specific category"""
        if not self.is_connected:
            self.logger.debug(f"Skipping get_category_insights in fallback mode")
            return None

        try:
            async with self.get_session() as session:
                if session:
                    result = await session.run(self._make_query("""
                        MATCH (c:Scope3Category {name: $category})
                        OPTIONAL MATCH (c)<-[:BELONGS_TO]-(s:EmissionSource)
                        OPTIONAL MATCH (c)<-[:APPLIES_TO]-(r:ReductionStrategy)
                        OPTIONAL MATCH (c)-[rel:RELATES_TO]-(related:Scope3Category)
                        RETURN {
                            category: c.name,
                            source_count: count(DISTINCT s),
                            strategy_count: count(DISTINCT r),
                            related_categories: collect(DISTINCT related.name),
                            relationships: collect(DISTINCT rel.type)
                        } as insights
                    """), {'category': category})
                    record = await result.single()
                    return record['insights'] if record else None
            return None
        except Exception as e:
            self.logger.error(f"Failed to get category insights: {str(e)}")
            return None

    async def find_reduction_opportunities(
        self,
        category: str,
        min_impact: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Find reduction opportunities for a category"""
        if not self.is_connected:
            self.logger.debug(f"Skipping find_reduction_opportunities in fallback mode")
            return []

        try:
            async with self.get_session() as session:
                if session:
                    result = await session.run(self._make_query("""
                        MATCH (c:Scope3Category {name: $category})
                        MATCH (s:EmissionSource)-[:BELONGS_TO]->(c)
                        MATCH (r:ReductionStrategy)-[:APPLIES_TO]->(c)
                        WHERE s.emission_value >= $min_impact
                        RETURN {
                            source_id: s.source_id,
                            emission_value: s.emission_value,
                            strategy_id: r.strategy_id,
                            strategy_name: r.name,
                            estimated_reduction: r.estimated_reduction
                        } as opportunity
                        ORDER BY s.emission_value DESC
                    """), {
                        'category': category,
                        'min_impact': min_impact
                    })
                    return [record['opportunity'] async for record in result]
            return []
        except Exception as e:
            self.logger.error(f"Failed to find reduction opportunities: {str(e)}")
            return []

    async def analyze_patterns(self, timeframe_days: int = 30) -> List[Dict[str, Any]]:
        """Analyze patterns in emission data"""
        if not self.is_connected:
            self.logger.debug("Skipping analyze_patterns in fallback mode")
            return []

        try:
            cutoff_date = datetime.now().timestamp() - (timeframe_days * 86400)
            async with self.get_session() as session:
                if session:
                    result = await session.run(self._make_query("""
                        MATCH (s:EmissionSource)-[:BELONGS_TO]->(c:Scope3Category)
                        WHERE s.timestamp >= $cutoff
                        WITH c.name as category,
                             collect(s.emission_value) as values,
                             avg(s.emission_value) as avg_emission,
                             count(s) as data_points
                        WHERE data_points >= 3
                        RETURN {
                            category: category,
                            average_emission: avg_emission,
                            trend: CASE 
                                WHEN values[-1] > values[0] THEN 'increasing'
                                WHEN values[-1] < values[0] THEN 'decreasing'
                                ELSE 'stable'
                            END,
                            data_points: data_points
                        } as pattern
                        ORDER BY avg_emission DESC
                    """), {'cutoff': cutoff_date})
                    return [record['pattern'] async for record in result]
            return []
        except Exception as e:
            self.logger.error(f"Failed to analyze patterns: {str(e)}")
            return []

    async def get_relationship_graph(self, depth: int = 2) -> Optional[Dict[str, Any]]:
        """Get relationship graph for visualization"""
        if not self.is_connected:
            self.logger.debug("Skipping get_relationship_graph in fallback mode")
            return None

        try:
            async with self.get_session() as session:
                if session:
                    query_text = f"""
                        MATCH path = (c1:Scope3Category)-[*1..{depth}]-(c2:Scope3Category)
                        RETURN {{
                            nodes: collect(DISTINCT c1.name) + collect(DISTINCT c2.name),
                            relationships: [(r in relationships(path)) | {{
                                source: startNode(r).name,
                                target: endNode(r).name,
                                type: type(r)
                            }}]
                        }} as graph
                    """
                    result = await session.run(self._make_query(query_text))
                    record = await result.single()
                    return record['graph'] if record else None
            return None
        except Exception as e:
            self.logger.error(f"Failed to get relationship graph: {str(e)}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get Neo4j connection status"""
        return {
            "connected": self.is_connected,
            "uri": self.uri
        }

    async def close(self) -> None:
        """Close Neo4j connection"""
        if self.driver:
            try:
                await self.driver.close()
            except Exception as e:
                self.logger.error(f"Error closing Neo4j connection: {str(e)}")
            finally:
                self.is_connected = False
                self.driver = None