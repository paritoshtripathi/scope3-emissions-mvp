"""
Neo4j Graph Manager for Scope3 Relationship Analysis
"""
from typing import Dict, Any, List, Optional
from neo4j import AsyncGraphDatabase
import logging
from datetime import datetime

class Neo4jManager:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def initialize(self) -> None:
        """Initialize Neo4j schema and setup"""
        await self._init_schema()

    async def _init_schema(self) -> None:
        """Initialize Neo4j schema with constraints and indexes"""
        async with self.driver.session() as session:
            # Create constraints
            await session.run("""
                CREATE CONSTRAINT scope3_category_name IF NOT EXISTS
                FOR (c:Scope3Category) REQUIRE c.name IS UNIQUE
            """)
            
            await session.run("""
                CREATE CONSTRAINT emission_source_id IF NOT EXISTS
                FOR (s:EmissionSource) REQUIRE s.source_id IS UNIQUE
            """)

    async def add_node(self, node_id: str, properties: Dict[str, Any]) -> None:
        """Add a node to the graph"""
        async with self.driver.session() as session:
            await session.run("""
                MERGE (n:Node {id: $node_id})
                SET n += $props
            """, {
                'node_id': node_id,
                'props': properties
            })

    async def update_node(self, node_id: str, properties: Dict[str, Any]) -> None:
        """Update a node's properties"""
        async with self.driver.session() as session:
            await session.run("""
                MATCH (n:Node {id: $node_id})
                SET n += $props
            """, {
                'node_id': node_id,
                'props': properties
            })

    async def delete_node(self, node_id: str) -> None:
        """Delete a node and its relationships"""
        async with self.driver.session() as session:
            await session.run("""
                MATCH (n:Node {id: $node_id})
                DETACH DELETE n
            """, {
                'node_id': node_id
            })

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add a relationship between nodes"""
        async with self.driver.session() as session:
            await session.run("""
                MATCH (s:Node {id: $source_id})
                MATCH (t:Node {id: $target_id})
                MERGE (s)-[r:RELATES_TO {type: $rel_type}]->(t)
                SET r += $props
            """, {
                'source_id': source_id,
                'target_id': target_id,
                'rel_type': relationship_type,
                'props': properties
            })

    async def delete_relationships(self, node_id: str) -> None:
        """Delete all relationships for a node"""
        async with self.driver.session() as session:
            await session.run("""
                MATCH (n:Node {id: $node_id})-[r]-()
                DELETE r
            """, {
                'node_id': node_id
            })

    async def add_category_relationship(
        self,
        category: str,
        related_category: str,
        relationship_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add relationship between Scope3 categories"""
        async with self.driver.session() as session:
            await session.run("""
                MERGE (c1:Scope3Category {name: $cat1})
                MERGE (c2:Scope3Category {name: $cat2})
                MERGE (c1)-[r:RELATES_TO {type: $rel_type}]->(c2)
                SET r += $props
            """, {
                'cat1': category,
                'cat2': related_category,
                'rel_type': relationship_type,
                'props': properties
            })

    async def add_emission_source(
        self,
        source_id: str,
        category: str,
        properties: Dict[str, Any]
    ) -> None:
        """Add emission source with category relationship"""
        async with self.driver.session() as session:
            await session.run("""
                MERGE (s:EmissionSource {source_id: $source_id})
                SET s += $props
                WITH s
                MERGE (c:Scope3Category {name: $category})
                MERGE (s)-[:BELONGS_TO]->(c)
            """, {
                'source_id': source_id,
                'category': category,
                'props': properties
            })

    async def add_reduction_strategy(
        self,
        strategy_id: str,
        name: str,
        categories: List[str],
        properties: Dict[str, Any]
    ) -> None:
        """Add reduction strategy with category relationships"""
        async with self.driver.session() as session:
            await session.run("""
                MERGE (s:ReductionStrategy {strategy_id: $strategy_id})
                SET s.name = $name
                SET s += $props
                WITH s
                UNWIND $categories as cat
                MERGE (c:Scope3Category {name: cat})
                MERGE (s)-[:APPLIES_TO]->(c)
            """, {
                'strategy_id': strategy_id,
                'name': name,
                'categories': categories,
                'props': properties
            })

    async def get_category_insights(self, category: str) -> Dict[str, Any]:
        """Get insights for a specific category"""
        async with self.driver.session() as session:
            result = await session.run("""
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
            """, {'category': category})
            record = await result.single()
            return record['insights']

    async def find_reduction_opportunities(
        self,
        category: str,
        min_impact: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Find reduction opportunities for a category"""
        async with self.driver.session() as session:
            result = await session.run("""
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
            """, {
                'category': category,
                'min_impact': min_impact
            })
            return [record['opportunity'] async for record in result]

    async def analyze_patterns(self, timeframe_days: int = 30) -> List[Dict[str, Any]]:
        """Analyze patterns in emission data"""
        cutoff_date = datetime.now().timestamp() - (timeframe_days * 86400)
        
        async with self.driver.session() as session:
            result = await session.run("""
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
            """, {'cutoff': cutoff_date})
            return [record['pattern'] async for record in result]

    async def get_relationship_graph(self, depth: int = 2) -> Dict[str, Any]:
        """Get relationship graph for visualization"""
        async with self.driver.session() as session:
            result = await session.run("""
                MATCH path = (c1:Scope3Category)-[*1..%d]-(c2:Scope3Category)
                RETURN {
                    nodes: collect(DISTINCT c1.name) + collect(DISTINCT c2.name),
                    relationships: [(r in relationships(path)) | {
                        source: startNode(r).name,
                        target: endNode(r).name,
                        type: type(r)
                    }]
                } as graph
            """ % depth)
            record = await result.single()
            return record['graph']

    async def close(self) -> None:
        """Close Neo4j connection"""
        await self.driver.close()