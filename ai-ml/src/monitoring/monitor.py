"""
Monitoring system for RAG implementation
"""
import time
import psutil
import logging
from typing import Dict, Any
import json
import os
from datetime import datetime

class Monitor:
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure logging
        self.setup_logging()
        
        # Initialize metrics
        self.metrics = {
            'processing_times': [],
            'memory_usage': [],
            'document_count': 0,
            'query_count': 0,
            'errors': []
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.log_dir, f'rag_{datetime.now().strftime("%Y%m%d")}.log')
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('RAGMonitor')
    
    def log_processing_time(self, operation: str, time_taken: float):
        """Log processing time for an operation"""
        self.metrics['processing_times'].append({
            'operation': operation,
            'time': time_taken,
            'timestamp': datetime.now().isoformat()
        })
        self.logger.info(f"{operation} took {time_taken:.2f} seconds")
    
    def log_memory_usage(self):
        """Log current memory usage"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        self.metrics['memory_usage'].append({
            'memory_mb': memory_mb,
            'timestamp': datetime.now().isoformat()
        })
        self.logger.info(f"Memory usage: {memory_mb:.2f} MB")
    
    def log_error(self, error_type: str, details: str):
        """Log error information"""
        self.metrics['errors'].append({
            'type': error_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self.logger.error(f"{error_type}: {details}")
    
    def increment_counter(self, counter_type: str):
        """Increment a counter"""
        if counter_type in ['document_count', 'query_count']:
            self.metrics[counter_type] += 1
            self.logger.info(f"{counter_type} increased to {self.metrics[counter_type]}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            'current_stats': {
                'total_documents': self.metrics['document_count'],
                'total_queries': self.metrics['query_count'],
                'error_count': len(self.metrics['errors']),
                'avg_processing_time': self._calculate_avg_processing_time(),
                'current_memory_usage': self._get_current_memory_usage()
            },
            'detailed_metrics': self.metrics
        }
    
    def _calculate_avg_processing_time(self) -> float:
        """Calculate average processing time"""
        times = [record['time'] for record in self.metrics['processing_times']]
        return sum(times) / len(times) if times else 0
    
    def _get_current_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        if self.metrics['memory_usage']:
            return self.metrics['memory_usage'][-1]['memory_mb']
        return 0
    
    def save_metrics(self):
        """Save metrics to file"""
        metrics_file = os.path.join(self.log_dir, 'rag_metrics.json')
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        self.logger.info("Metrics saved to file")

    def record_operation(self, operation_name: str, duration: float):
        """Record an operation's duration and log it"""
        self.log_processing_time(operation_name, duration)
        self.log_memory_usage()
        if operation_name == 'add_document':
            self.increment_counter('document_count')
        elif operation_name == 'rag_query':
            self.increment_counter('query_count')

# Initialize global monitor
monitor = Monitor()