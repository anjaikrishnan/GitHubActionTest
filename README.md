# Enterprise Reporting & Visualization Platform

A comprehensive enterprise reporting platform with natural language querying capabilities, built using microservices architecture.

## Features

- 📊 **Interactive Dashboards**: Dynamic charts and visualizations
- 🗂️ **Report Catalog**: Menu-driven report selection
- 🤖 **LLM-Powered Queries**: Natural language to SQL conversion
- 📱 **Mobile Responsive**: Works seamlessly on all devices
- 🔐 **Enterprise Security**: Keycloak integration for authentication
- 🏗️ **Microservices**: Scalable, modular architecture

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │  LLM Service    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Analytics      │    │  Auth Service   │
                       │  (Cube.js)      │    │  (Keycloak)     │
                       └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │ (PostgreSQL)    │
                       └─────────────────┘
```

## Services

- **frontend/**: Next.js React application
- **api-gateway/**: FastAPI main backend service
- **llm-service/**: Natural language query processing
- **analytics-service/**: Cube.js for data modeling
- **keycloak/**: Authentication and authorization
- **database/**: PostgreSQL database

## Quick Start

```bash
# Clone and setup
git clone <repository>
cd enterprise-reporting-platform

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# API: http://localhost:8000
# Keycloak: http://localhost:8080
```

## Technology Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Analytics**: Cube.js
- **Authentication**: Keycloak
- **Database**: PostgreSQL
- **LLM Integration**: OpenAI GPT/Local LLM
- **Containerization**: Docker, Docker Compose

## Development Setup

1. Install Docker and Docker Compose
2. Clone the repository
3. Run `docker-compose up -d`
4. Access services at their respective ports

## Environment Variables

See `.env.example` for required environment variables.