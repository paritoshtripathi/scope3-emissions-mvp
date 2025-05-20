# Scope 3 RAG System Deployment Guide

## Prerequisites

- Docker and Docker Compose
- PostgreSQL client (for monitoring)
- curl (for testing)

## Environment Setup

1. Create necessary environment files:

```bash
# .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
NODE_ENV=development
```

2. Ensure directory structure:
```
.
├── ai-ml/
│   ├── models/
│   ├── kb/
│   └── ...
├── backend/
│   ├── src/
│   └── uploads/
├── frontend/
└── database/
    └── postgres/
        ├── data/
        └── migrations/
```

## Deployment Steps

1. Build and start services:
```bash
docker-compose up --build
```

2. Run database migrations:
```bash
docker-compose exec postgres psql -U postgres -d scope3_db -f /docker-entrypoint-initdb.d/migrations/007_add_rag_support.sql
```

3. Verify deployment:
```bash
./scripts/test-deployment.sh
```

## Service URLs

- Frontend: http://localhost:4200
- Backend API: http://localhost:3000
- RAG API: http://localhost:5000
- PostgreSQL: localhost:5432

## Monitoring

1. Check service status:
```bash
docker-compose ps
```

2. View logs:
```bash
docker-compose logs -f [service_name]
```

3. Monitor RAG processing:
```bash
docker-compose exec postgres psql -U postgres -d scope3_db -c "SELECT * FROM ingestion_log WHERE rag_processed = true;"
```

## Troubleshooting

1. If RAG API fails:
   - Check model downloads
   - Verify GPU availability
   - Check memory usage

2. If database connection fails:
   - Verify PostgreSQL is running
   - Check connection strings
   - Verify migrations

3. If file processing fails:
   - Check upload directory permissions
   - Verify file formats
   - Check available disk space

## Backup and Recovery

1. Backup database:
```bash
docker-compose exec postgres pg_dump -U postgres scope3_db > backup.sql
```

2. Backup RAG models:
```bash
tar -czf models_backup.tar.gz ai-ml/models/
```

## Performance Optimization

1. RAG System:
   - Adjust chunk sizes in config
   - Monitor memory usage
   - Consider GPU acceleration

2. Database:
   - Monitor query performance
   - Adjust PostgreSQL settings
   - Review indexes

## Security Considerations

1. Environment Variables:
   - Use secure passwords
   - Rotate credentials regularly
   - Don't commit .env files

2. Network Security:
   - Configure firewalls
   - Use HTTPS in production
   - Implement rate limiting

## Production Deployment

Additional steps for production:

1. SSL/TLS Setup
2. Load Balancing
3. Monitoring Setup
4. Backup Automation
5. CI/CD Integration

## Support

For issues:
1. Check logs
2. Review documentation
3. Contact support team