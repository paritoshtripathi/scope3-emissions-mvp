"""
Utility functions for API operations
"""
from typing import Optional, Any, Callable
from contextlib import contextmanager
import time
from flask import jsonify
from .constants import (
    ERR_GRAPH_NOT_INIT,
    STATUS_SKIPPED,
    FALLBACK_PATTERNS,
    FALLBACK_CATEGORY_DATA
)

def get_graph_manager_safely(components) -> Optional[Any]:
    """Safely get graph manager if available"""
    if not components.pipeline:
        return None
    return getattr(components.pipeline, 'graph_manager', None)

def handle_graph_operation_error(operation_name: str, error: Exception) -> tuple:
    """Handle graph operation errors consistently"""
    if operation_name == "add_relationship":
        return jsonify({
            "message": ERR_GRAPH_NOT_INIT,
            "status": STATUS_SKIPPED
        }), 200
    elif operation_name == "get_insights":
        return jsonify({
            "message": ERR_GRAPH_NOT_INIT,
            "fallback_data": FALLBACK_CATEGORY_DATA
        }), 200
    elif operation_name == "analyze_patterns":
        return jsonify({
            "message": ERR_GRAPH_NOT_INIT,
            "patterns": FALLBACK_PATTERNS
        }), 200
    else:
        return jsonify({
            "error": str(error),
            "message": ERR_GRAPH_NOT_INIT
        }), 500

@contextmanager
def create_monitor_operation(monitor):
    """Create a monitor operation context manager"""
    def monitor_operation(name: str):
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            monitor.record_operation(name, duration)
    return monitor_operation