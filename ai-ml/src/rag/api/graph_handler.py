"""
Graph operations handler with safe null checks and error handling
"""
from typing import Optional, Dict, Any, Union
from flask import jsonify
from .constants import (
    COMP_NEO4J, ERR_NEO4J_UNAVAILABLE, ERR_GRAPH_NOT_INIT,
    STATUS_SKIPPED, FALLBACK_CATEGORY_DATA, FALLBACK_PATTERNS,
    DEFAULT_DAYS, CODE_NOT_FOUND, ERR_CATEGORY_NOT_FOUND,
    CODE_REL_ERROR, CODE_INSIGHT_ERROR, CODE_PATTERN_ERROR,
    MSG_REL_ADDED
)

class GraphHandler:
    """Handler for safe graph operations with proper error handling"""

    def __init__(self, components, run_async_fn, monitor_operation):
        self.components = components
        self.run_async = run_async_fn
        self.monitor_operation = monitor_operation

    def _get_graph_manager(self) -> Optional[Any]:
        """Safely get graph manager if available"""
        if not self.components.pipeline:
            return None
        return getattr(self.components.pipeline, 'graph_manager', None)

    def _is_neo4j_available(self) -> bool:
        """Check if Neo4j is available"""
        return bool(self.components.status.get(COMP_NEO4J, False))

    def handle_add_relationship(self, data: Dict[str, Any]):
        """Handle adding a relationship with proper error handling"""
        if not self._is_neo4j_available():
            return jsonify({
                "message": ERR_NEO4J_UNAVAILABLE,
                "status": STATUS_SKIPPED
            }), 200

        graph_manager = self._get_graph_manager()
        if not graph_manager:
            return jsonify({
                "message": ERR_GRAPH_NOT_INIT,
                "status": STATUS_SKIPPED
            }), 200

        try:
            with self.monitor_operation("add_relationship"):
                self.run_async(graph_manager.add_category_relationship(
                    category=data['source_category'],
                    related_category=data['target_category'],
                    relationship_type=data['relationship_type'],
                    properties=data.get('properties', {})
                ))
            return {'message': MSG_REL_ADDED}, 201
        except Exception as e:
            return {'code': CODE_REL_ERROR, 'message': str(e)}, 500

    def handle_get_insights(self, category: str):
        """Handle getting insights with proper error handling"""
        if not self._is_neo4j_available():
            return jsonify({
                "message": ERR_NEO4J_UNAVAILABLE,
                "fallback_data": {
                    "category": category,
                    **FALLBACK_CATEGORY_DATA
                }
            }), 200

        graph_manager = self._get_graph_manager()
        if not graph_manager:
            return jsonify({
                "message": ERR_GRAPH_NOT_INIT,
                "fallback_data": {
                    "category": category,
                    **FALLBACK_CATEGORY_DATA
                }
            }), 200

        try:
            with self.monitor_operation("get_insights"):
                insights = self.run_async(graph_manager.get_category_insights(category))
            if not insights:
                return {'code': CODE_NOT_FOUND, 'message': ERR_CATEGORY_NOT_FOUND}, 404
            return jsonify(insights)
        except Exception as e:
            return {'code': CODE_INSIGHT_ERROR, 'message': str(e)}, 500

    def handle_analyze_patterns(self, days: Union[str, int, None] = None):
        """Handle analyzing patterns with proper error handling"""
        if not self._is_neo4j_available():
            return jsonify({
                "message": ERR_NEO4J_UNAVAILABLE,
                "patterns": FALLBACK_PATTERNS
            }), 200

        graph_manager = self._get_graph_manager()
        if not graph_manager:
            return jsonify({
                "message": ERR_GRAPH_NOT_INIT,
                "patterns": FALLBACK_PATTERNS
            }), 200

        try:
            # Convert days to int with fallback to DEFAULT_DAYS
            timeframe_days = DEFAULT_DAYS
            if days is not None:
                try:
                    timeframe_days = int(days)
                except (ValueError, TypeError):
                    return jsonify({
                        "error": "Invalid days parameter",
                        "message": "Days must be a valid integer"
                    }), 400

            with self.monitor_operation("analyze_patterns"):
                patterns = self.run_async(graph_manager.analyze_patterns(
                    timeframe_days=timeframe_days
                ))
            return jsonify(patterns)
        except Exception as e:
            return {'code': CODE_PATTERN_ERROR, 'message': str(e)}, 500