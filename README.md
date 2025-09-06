# OpenProdoc Red
----

## Cloud-Native Enterprise Content Management System

**OpenProdoc Red** is a modernized, Kubernetes-ready version of the OpenProdoc ECM (Enterprise Content Management) system. This edition has been completely redesigned for cloud deployment with modern interfaces, updated libraries, and production-grade infrastructure.

----

## 🚀 What's New in OpenProdoc Red

### Cloud-Native Architecture
* **Kubernetes deployment ready** with Helm charts
* **Microservices architecture** with separate API and Web services
* **Container-first design** with Docker support
* **High availability** with horizontal scaling capabilities
* **Production-grade monitoring** with Prometheus metrics and health checks

### Modern Technology Stack
* **Spring Boot 2.7** - Modern Java application framework
* **Maven multi-module** - Professional build system
* **PostgreSQL optimized** - Primary database with connection pooling
* **JSON structured logging** - Cloud-native observability
* **REST API first** - Modern API-driven architecture
* **Thymeleaf templates** - Modern web interface engine

### Enhanced Security & Operations
* **12-factor app compliance** - Environment-based configuration
* **Spring Security integration** - Modern authentication/authorization
* **Health checks & metrics** - Kubernetes-ready monitoring
* **Externalized configuration** - Environment variables and profiles
* **Async logging** - High-performance structured logs

----

## 📋 Core ECM Features (Preserved from OpenProdoc)

* **Multi-platform support** (Linux, Windows, Mac via containers)
* **Multi-database support** with special PostgreSQL optimization
  * PostgreSQL (recommended), MySQL, Oracle, DB2, SQLServer, SQLLite, HSQLDB
* **Multiple authentication methods** (LDAP, Database, OS, Built-in)
* **Flexible document storage**
  * FileSystem, Database BLOB, FTP, URL Reference, Amazon S3
* **Object-oriented metadata** with inheritance support
* **Fine-grained permissions** and delegation capabilities
* **Multi-language support** (English, Spanish, Portuguese, Catalan)
* **Modern web interface** (legacy Swing client still available)
* **Open Source** under GNU AGPL v3

### Document Management Features
* **Thesaurus management** with SKOS-RDF standard support
* **Metadata validation** against thesaurus terms
* **Document import** from Kofax Capture and Abbyy FlexiCapture
* **Automated tasks** with scheduling support
* **Document lifecycle** management with purging
* **Full-text search** with Apache Lucene
* **Reporting system** with export capabilities

----

## 🏗️ Architecture

### Deployment Components
```
┌─────────────────┐    ┌─────────────────┐
│   prodoc-api    │    │   prodoc-web    │
│  (REST API)     │    │ (Web Interface) │
│  Port: 8080     │    │  Port: 8090     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │   PostgreSQL    │
         │   (Database)    │
         └─────────────────┘
```

### Module Structure
* **prodoc-core** - Core document management engine
* **prodoc-api** - REST API service with Spring Boot
* **prodoc-web** - Modern web interface with Thymeleaf
* **Legacy modules** (ProdocSwing, ProdocWeb) - Preserved for compatibility

----

## 🚢 Kubernetes Deployment

### Quick Start with Helm
```bash
# Deploy PostgreSQL
helm install postgres bitnami/postgresql

# Deploy OpenProdoc Red
helm install openprodoc ./helm/openprodoc
```

### Environment Variables
```bash
# Database Configuration
DB_URL=jdbc:postgresql://postgres:5432/openprodoc
DB_USERNAME=openprodoc
DB_PASSWORD=your-secure-password

# Storage Configuration  
STORAGE_TYPE=FILESYSTEM  # or S3
STORAGE_PATH=/app/storage

# Security
JWT_SECRET=your-jwt-secret
AUTH_TYPE=OPD  # or LDAP

# Monitoring
SPRING_PROFILES_ACTIVE=prod
LOG_LEVEL_ROOT=INFO
```

----

## 🛠️ Development & Building

### Prerequisites
* Java 11+
* Maven 3.6+
* Docker
* Kubernetes (k3d/k3s recommended for local development)

### Build Commands
```bash
# Build all modules
mvn clean install

# Run API service locally
cd prodoc-api
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Run Web interface locally  
cd prodoc-web
mvn spring-boot:run -Dspring-boot.run.profiles=dev

# Build Docker images
docker build -t openprodoc-red/api:latest prodoc-api/
docker build -t openprodoc-red/web:latest prodoc-web/
```

----

## 📊 Monitoring & Operations

### Health Checks
* **API Health**: `http://localhost:8080/api/actuator/health`
* **Web Health**: `http://localhost:8090/web/actuator/health`
* **Metrics**: `http://localhost:8080/api/actuator/prometheus`

### Logging
* **Development**: Colored console output
* **Production**: Structured JSON logs for log aggregation
* **Async processing** for high-performance logging

----

## 🔄 Migration from Classic OpenProdoc

OpenProdoc Red maintains **full compatibility** with existing OpenProdoc databases and configurations. Migration involves:

1. **Database schema** - Automatic Flyway migrations
2. **Configuration** - Convert to environment variables
3. **Deployment** - Containerize and deploy to Kubernetes
4. **Integration** - Update client applications to use REST API

----

## 📄 License

OpenProdoc Red is free and open source software licensed under:
* **GNU Affero General Public License v3** (AGPL-3.0)

----

## 🤝 Contributing

This modernization project welcomes contributions for:
* Kubernetes deployment improvements
* Modern UI enhancements  
* Performance optimizations
* Additional cloud provider support
* Documentation and examples

**Original OpenProdoc** - Created by Joaquín Hierro  
**OpenProdoc Red** - Modernization for cloud-native deployment
