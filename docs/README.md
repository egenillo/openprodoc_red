# OpenProdoc Red Documentation

This folder contains comprehensive documentation for deploying and using OpenProdoc Red.

---

## Available Documentation

### Deployment Guides

#### [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md)
Complete guide for deploying OpenProdoc on Kubernetes using Helm charts. Covers installation methods (Helm repository, local chart, TGZ package), configuration options, deployment scenarios, troubleshooting, and production best practices. Also includes Docker Compose deployment as an alternative.

#### [PRODUCTION-DEPLOYMENT.md](PRODUCTION-DEPLOYMENT.md)
Step-by-step guide for production deployments. Includes security configuration, secrets management, ingress setup, TLS certificates, monitoring, and backup strategies. Covers both Kubernetes and Docker Compose approaches.

#### [RAG_SETUP.md](RAG_SETUP.md)
Detailed guide for the integrated RAG (Retrieval-Augmented Generation) solution with OpenProdoc. Covers architecture, component configuration (Ollama, pgvector, Open WebUI, Watcher), user/group synchronization, knowledge base organization, and deployment via both Helm and Docker Compose.

---

### API Documentation (`api/` subfolder)

#### [api/API_USAGE_GUIDE.md](api/API_USAGE_GUIDE.md)
Comprehensive REST API reference with detailed endpoint documentation, authentication methods, code examples in multiple languages (Python, JavaScript, Java), and complete workflow examples.

#### [api/API_QUICK_REFERENCE.md](api/API_QUICK_REFERENCE.md)
Quick reference card with all API endpoints in table format, common curl commands, response codes, and query syntax examples for fast lookups.

#### [api/OpenProdoc-API-Collection.json](api/OpenProdoc-API-Collection.json)
Postman collection with pre-configured API requests for testing and development. Import into Postman or similar API testing tools.

#### [api/test-api.sh](api/test-api.sh)
Automated API test script for Linux/Mac environments. Tests authentication, folder operations, document listing, and search functionality.

#### [api/test-api.bat](api/test-api.bat)
Automated API test script for Windows environments. Performs the same tests as the shell script version.

---

## Deployment Options

OpenProdoc supports two deployment methods:

| Method | Best For | Guide |
|---|---|---|
| **Docker Compose** | Local development, single-server deployments | [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md#docker-compose-deployment) |
| **Helm / Kubernetes** | Production, multi-node clusters, HA | [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md#quick-start-development) |

Both methods deploy the full solution: Core Engine, PostgreSQL, Ollama, pgvector, Open WebUI, and RAG Watcher.

## Quick Links

- **Getting Started (Docker Compose)**: See [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md#docker-compose-deployment)
- **Getting Started (Kubernetes)**: See [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md#quick-start-development)
- **RAG Solution Setup**: See [RAG_SETUP.md](RAG_SETUP.md)
- **API Overview**: See [api/API_USAGE_GUIDE.md](api/API_USAGE_GUIDE.md) - Introduction section
- **Production Setup**: See [PRODUCTION-DEPLOYMENT.md](PRODUCTION-DEPLOYMENT.md)
- **API Testing**: Run `./api/test-api.sh` (Linux/Mac) or `api\test-api.bat` (Windows)

