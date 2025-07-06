# Enterprise Reporting Platform - Deployment Guide

This guide will help you deploy and configure the complete enterprise reporting platform with all microservices.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- At least 8GB RAM available for containers
- OpenAI API key (optional, for LLM features)

## Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd enterprise-reporting-platform
   chmod +x scripts/start.sh
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   nano .env
   ```

3. **Start Platform**
   ```bash
   ./scripts/start.sh
   ```

## Detailed Setup

### 1. Environment Configuration

Edit the `.env` file with your specific configuration:

```bash
# Essential configuration
OPENAI_API_KEY=your-openai-api-key-here

# Database (default values work for local development)
POSTGRES_DB=enterprise_reporting
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Keycloak admin credentials
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=admin123
```

### 2. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Keycloak Configuration

After starting the platform, configure Keycloak for authentication:

1. **Access Keycloak Admin Console**
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin123`

2. **Create Realm**
   - Click "Master" dropdown → "Create Realm"
   - Realm name: `enterprise-reporting`
   - Click "Create"

3. **Create Client**
   - Go to "Clients" → "Create client"
   - Client ID: `reporting-app`
   - Client type: `OpenID Connect`
   - Click "Next"
   - Client authentication: `OFF` (public client)
   - Valid redirect URIs: `http://localhost:3000/*`
   - Web origins: `http://localhost:3000`
   - Click "Save"

4. **Create Test User**
   - Go to "Users" → "Create new user"
   - Username: `testuser`
   - Email: `test@company.com`
   - First/Last name: `Test User`
   - Click "Create"
   - Go to "Credentials" tab → "Set password"
   - Password: `password123`
   - Temporary: `OFF`

### 4. Verify Installation

1. **Check Service Health**
   ```bash
   # API Gateway
   curl http://localhost:8000/health
   
   # LLM Service
   curl http://localhost:8001/health
   
   # Analytics Service
   curl http://localhost:4000/cubejs-api/v1/meta
   ```

2. **Access Applications**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Keycloak Admin: http://localhost:8080

## Platform Features

### 1. Dashboard and Reports

- **Access**: Log in through the frontend at http://localhost:3000
- **Features**:
  - Pre-built report catalog organized by categories
  - Interactive charts and visualizations
  - Mobile-responsive design
  - Real-time data updates

### 2. Natural Language Queries

- **Access**: AI Query interface in the main dashboard
- **Usage**:
  ```
  Example queries:
  - "Show me total sales for this month"
  - "What are the top 5 products by revenue?"
  - "How many customers do we have by region?"
  ```
- **Configuration**: Requires OpenAI API key in environment variables

### 3. Analytics API

- **Cube.js Integration**: Advanced OLAP capabilities
- **Endpoints**: http://localhost:4000/cubejs-api/v1/
- **Features**:
  - Pre-aggregated data cubes
  - Real-time analytics
  - Multi-dimensional analysis

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │  LLM Service    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Analytics      │    │  Auth Service   │
                       │  (Cube.js)      │    │  (Keycloak)     │
                       │  Port: 4000     │    │  Port: 8080     │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │ (PostgreSQL)    │
                       │  Port: 5432     │
                       └─────────────────┘
```

## Sample Data

The platform comes with sample business data including:
- Sales transactions
- Customer information
- Product catalog
- Sample reports and dashboards

## Development

### Local Development Setup

1. **API Gateway Development**
   ```bash
   cd api-gateway
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8000
   ```

2. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **LLM Service Development**
   ```bash
   cd llm-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8001
   ```

### Testing

1. **API Testing**
   ```bash
   # Test authentication
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/auth/me
   
   # Test report execution
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/reports
   
   # Test LLM query
   curl -X POST -H "Content-Type: application/json" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -d '{"query": "show total sales"}' \
        http://localhost:8000/llm/query
   ```

## Production Deployment

### Environment Variables for Production

```bash
# Security
JWT_SECRET=your-production-jwt-secret
API_SECRET=your-production-api-secret

# Database
DATABASE_URL=postgresql://user:password@production-db:5432/enterprise_reporting

# External services
KEYCLOAK_URL=https://your-keycloak-domain.com
OPENAI_API_KEY=your-production-openai-key

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_KEYCLOAK_URL=https://your-keycloak-domain.com
```

### Production Considerations

1. **Security**
   - Use strong passwords and secrets
   - Enable HTTPS/TLS
   - Configure proper CORS policies
   - Set up network isolation

2. **Scaling**
   - Use container orchestration (Kubernetes)
   - Set up load balancers
   - Configure horizontal pod autoscaling
   - Use managed database services

3. **Monitoring**
   - Set up application monitoring
   - Configure log aggregation
   - Health checks and alerting
   - Performance monitoring

## Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   # Check logs
   docker-compose logs [service-name]
   
   # Restart specific service
   docker-compose restart [service-name]
   ```

2. **Authentication issues**
   - Verify Keycloak configuration
   - Check client settings and redirect URIs
   - Ensure realm and client names match

3. **Database connection issues**
   ```bash
   # Check PostgreSQL logs
   docker-compose logs postgres
   
   # Connect to database
   docker-compose exec postgres psql -U postgres -d enterprise_reporting
   ```

4. **LLM service issues**
   - Verify OpenAI API key is set
   - Check LLM service logs
   - Test with simple queries first

### Performance Optimization

1. **Database**
   - Configure connection pooling
   - Add appropriate indexes
   - Regular maintenance and vacuuming

2. **Caching**
   - Enable Redis for session caching
   - Configure Cube.js pre-aggregations
   - Frontend caching strategies

3. **Resource Allocation**
   - Adjust Docker memory limits
   - CPU allocation per service
   - Monitor resource usage

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review service logs for error messages
3. Verify configuration settings
4. Check network connectivity between services

## Next Steps

After successful deployment:
1. Create additional users in Keycloak
2. Configure custom reports and dashboards
3. Set up monitoring and alerting
4. Plan for scaling and high availability
5. Regular backup procedures