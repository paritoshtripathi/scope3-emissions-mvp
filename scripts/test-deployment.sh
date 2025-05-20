#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "Testing Scope 3 RAG Deployment"
echo "============================="

# Test PostgreSQL
echo -n "Testing PostgreSQL connection... "
if pg_isready -h localhost -p 5432; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}Failed${NC}"
    exit 1
fi

# Test RAG API
echo -n "Testing RAG API health... "
if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}Failed${NC}"
    exit 1
fi

# Test Backend
echo -n "Testing Backend health... "
if curl -s http://localhost:3000/health | grep -q "ok"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}Failed${NC}"
    exit 1
fi

# Test Frontend
echo -n "Testing Frontend server... "
if curl -s http://localhost:4200 | grep -q "<!DOCTYPE html>"; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}Failed${NC}"
    exit 1
fi

# Test RAG Processing
echo "Testing RAG document processing..."
curl -X POST -H "Content-Type: application/json" -d '{
  "documents": [{
    "text": "Scope 3 emissions test document",
    "metadata": {
      "category": "test",
      "source": "deployment-test"
    }
  }]
}' http://localhost:5000/process-documents

# Test RAG Query
echo "Testing RAG query..."
curl -X POST -H "Content-Type: application/json" -d '{
  "query": "What are Scope 3 emissions?",
  "top_k": 1
}' http://localhost:5000/query

echo -e "\n${GREEN}All tests completed successfully!${NC}"