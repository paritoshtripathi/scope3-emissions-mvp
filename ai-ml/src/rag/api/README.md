# RAG API Documentation

## Deployment

### Using Docker

1. Build and run using docker-compose:
```bash
cd ai-ml
docker-compose up --build
```

2. The API will be available at:
   - API Endpoints: `http://localhost:5000`
   - Swagger UI: `http://localhost:5000/docs`

### Manual Deployment

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the API:
```bash
python -m flask run --host=0.0.0.0 --port=5000
```

## API Documentation

### Swagger UI
The complete API documentation is available through Swagger UI at `/docs` endpoint. This provides:
- Interactive API documentation
- Request/response examples
- Try-it-out functionality
- Schema definitions

### Available Endpoints

1. Health Check
   - GET `/health`
   - Check system health and configuration

2. Document Processing
   - POST `/documents/process`
   - Upload and process documents
   - Supports PDF and text files
   - Optional category classification

3. Chat Interface
   - POST `/chat`
   - Send queries to the RAG system
   - Receives reasoned responses with expert insights

4. System Metrics
   - GET `/metrics`
   - Monitor system performance and usage

## Example Usage

### Using Swagger UI

1. Navigate to `http://localhost:5000/docs`
2. Explore available endpoints
3. Use the "Try it out" button to test endpoints
4. View detailed request/response schemas

### Example Queries

The chat endpoint accepts queries like:

```json
{
  "message": "What are the main categories of Scope 3 emissions?",
  "context": {
    "focus": "supply_chain",
    "detail_level": "detailed"
  }
}
```

Response includes:
- Detailed answer
- Reasoning path
- Expert insights
- Source documents

## Response Format

All responses follow standard formats with proper HTTP status codes:

- Success (200): Properly formatted response
- Bad Request (400): Invalid input
- Error (500): Processing error with details

## Monitoring

The system provides detailed metrics through the `/metrics` endpoint:
- Request counts
- Processing times
- Memory usage
- Error rates

## Error Handling

All endpoints include proper error handling with detailed messages and appropriate HTTP status codes.