# OpenProdoc Red Documentation

This folder contains comprehensive documentation for deploying and using OpenProdoc Red.

---

## 📚 Available Documentation

### Deployment Guides

#### [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md)
Complete guide for deploying OpenProdoc on Kubernetes using Helm charts. Covers installation methods (Helm repository, local chart, TGZ package), configuration options, deployment scenarios, troubleshooting, and production best practices.

#### [PRODUCTION-DEPLOYMENT.md](PRODUCTION-DEPLOYMENT.md)
Step-by-step guide for production deployments. Includes security configuration, secrets management, ingress setup, TLS certificates, monitoring, and backup strategies.

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

## Quick Links

- **Getting Started**: See [HELM_DEPLOYMENT_GUIDE.md](HELM_DEPLOYMENT_GUIDE.md) - Quick Start section
- **API Overview**: See [api/API_USAGE_GUIDE.md](api/API_USAGE_GUIDE.md) - Introduction section
- **Production Setup**: See [PRODUCTION-DEPLOYMENT.md](PRODUCTION-DEPLOYMENT.md)
- **API Testing**: Run `./api/test-api.sh` (Linux/Mac) or `api\test-api.bat` (Windows)

