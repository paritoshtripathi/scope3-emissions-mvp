import os
import logging
from src.rag.api.app import app

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 5000))
        logger.info(f"Starting Flask app on port {port}")
        logger.info(f"Debug mode: {os.getenv('FLASK_DEBUG', True)}")
        logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
        
        app.run(
            host='0.0.0.0',
            port=port,
            debug=bool(os.getenv('FLASK_DEBUG', True))
        )
    except Exception as e:
        logger.error(f"Failed to start Flask app: {e}", exc_info=True)
        raise