# Scope3 RAG System

Advanced Retrieval-Augmented Generation system for Scope3 emissions analysis and ESG insights.

## Features

- 🤖 Advanced Agentic RAG with Tree of Thoughts reasoning
- 🧠 Mixture of Experts for domain-specific knowledge
- 🔍 Hybrid vector search with FAISS
- 📊 Real-time monitoring and metrics
- 🔄 Swagger API documentation

## Directory Structure

```
ai-ml/
├── src/                    # Source code
│   ├── rag/               # RAG implementation
│   │   ├── agents/       # Expert agents
│   │   ├── api/         # REST API
│   │   ├── embeddings/  # Embedding generation
│   │   ├── indexing/    # Vector storage
│   │   ├── models/     # Core models
│   │   ├── processors/ # Document processing
│   │   ├── retrieval/  # Retrieval system
│   │   └── scripts/    # Utility scripts
│   ├── config/          # Configuration
│   └── monitoring/      # System monitoring
├── tests/                # Test suite
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── scripts/             # Development scripts
│   └── windows/       # Windows scripts
├── kb/                  # Knowledge base
└── models/             # Model storage
```

## Quick Start

### 1. Setup Environment

```batch
# Clone repository
git clone <repository-url>
cd ai-ml

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -e .
```

### 2. Configure Environment

```batch
# Copy environment template
copy .env.example .env

# Edit .env with your settings:
# - API keys
# - Model configurations
# - Environment settings
```

### 3. Validate Setup

```batch
# Run setup validation
scripts\windows\validate.bat

# Fix common issues if needed
scripts\windows\fix_common_issues.bat
```

### 4. Run Tests

```batch
# Run test suite
scripts\windows\run_tests.bat
```

### 5. Start Development Server

```batch
# Start the API server
python main.py
```

Access the API:
- API Endpoints: http://localhost:5000
- Swagger UI: http://localhost:5000/docs
- Metrics: http://localhost:5000/metrics

## Development

### Available Scripts

- `validate.bat`: Validate environment setup
- `cleanup.bat`: Clean project structure
- `verify_paths.bat`: Verify import paths
- `fix_common_issues.bat`: Fix common setup issues
- `run_tests.bat`: Run test suite

### Adding New Features

1. Create feature branch:
```batch
git checkout -b feature/your-feature
```

2. Implement changes following the structure:
- Add agents in src/rag/agents/
- Add models in src/rag/models/
- Add tests in tests/unit/ or tests/integration/

3. Validate changes:
```batch
scripts\windows\validate.bat
scripts\windows\run_tests.bat
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions focused
- Write tests for new features

## API Documentation

### Core Endpoints

1. Document Processing
```bash
POST /documents/process
Content-Type: multipart/form-data
```

2. Chat Interface
```bash
POST /chat
Content-Type: application/json
{
    "message": "What are the main sources of Scope 3 emissions?",
    "context": {}
}
```

3. System Metrics
```bash
GET /metrics
```

### Response Format

```json
{
    "answer": "Detailed answer...",
    "reasoning": {
        "path": [
            {
                "type": "query_analysis",
                "content": "Analysis...",
                "confidence": 0.95
            }
        ],
        "confidence": 0.92
    },
    "expert_insights": {
        "recommendations": [
            {
                "expert": "EmissionsExpert",
                "response": "Expert insight...",
                "confidence": 0.88
            }
        ]
    },
    "sources": [
        {
            "document": "scope3_guidelines.pdf",
            "relevance": 0.95
        }
    ]
}
```

## Monitoring

- Real-time metrics via Prometheus
- System health monitoring
- Performance tracking
- Error logging

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Run tests and validation
5. Submit pull request

## License

[License details here]