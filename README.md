# OpenProdoc Red
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md) | [🇫🇷 Français](README.fr.md) | [🇩🇪 Deutsch](README.de.md) | [🇸🇦 العربية](README.ar.md)

## Cloud-Native Document Management System

**OpenProdoc Red** is a Kubernetes-ready version of the OpenProdoc DMS (Document Management System). This edition has been containerized and optimized for cloud deployment with Helm charts, Docker support, and production-grade infrastructure.

----

## 🚀 What's New in OpenProdoc Red

### Cloud-Native Architecture
* **Kubernetes deployment ready** with Helm charts
* **Container-first design** with Docker and Docker Compose support
* **High availability** with horizontal scaling capabilities and session affinity
* **PostgreSQL optimized** for cloud database deployments
* **Environment-based configuration** with externalized settings

### Modern Deployment Stack
* **Tomcat 9 with OpenJDK 11** - Stable application server
* **PostgreSQL 15** - Modern database with optimizations
* **Helm charts** - Production-ready Kubernetes deployments
* **Docker Compose** - Easy local development setup
* **REST API enabled** - Full programmatic access

### Production-Ready Infrastructure
* **Multi-stage Docker builds** - Optimized image sizes
* **12-factor app principles** - Environment-based configuration
* **Persistent volumes** - Secure document and configuration storage
* **Session affinity** - Sticky sessions for multi-replica deployments
* **Health checks** - Kubernetes readiness and liveness probes
* **Security hardening** - Non-root containers, minimal permissions

### AI Integration with Model Context Protocol (MCP)
* **MCP Server included** - Native support for AI assistant integration
* **Claude Desktop & Claude Code ready** - Seamless integration with Anthropic's AI tools
* **Comprehensive API coverage** - Full CRUD operations for folders, documents, and thesaurus
* **Natural language interface** - Manage documents using conversational commands
* **Dual response formats** - Markdown for humans, JSON for machines
* **Automatic authentication** - Environment-based credential management
* **See [MCP/README.md](MCP/README.md)** for complete integration guide

----

## 📋 Core ECM Features

* **Multi-platform support** (Linux, Windows, Mac via containers)
* **Multi-database support** with PostgreSQL optimization
  * PostgreSQL (recommended), MySQL, Oracle, DB2, SQLServer, SQLLite, HSQLDB
* **Multiple authentication methods** (LDAP, Database, OS, Built-in)
* **Flexible document storage**
  * FileSystem (default), Database BLOB, FTP, URL Reference, Amazon S3
* **Object-oriented metadata** with inheritance support
* **Fine-grained permissions** and delegation capabilities
* **Multi-language support** (English, Spanish, Portuguese, Catalan)
* **Web interface** (ProdocWeb2)
* **REST API** for programmatic access
* **Open Source** under GNU AGPL v3

### Document Management Features
* **Thesaurus management** with SKOS-RDF standard support
* **Metadata validation** against thesaurus terms
* **Version control** with checkout/checkin workflow
* **Document lifecycle** management with purging
* **Full-text search** with Apache Lucene
* **Folder hierarchy** with permissions inheritance
* **Document import/export** capabilities

----

## 🏗️ Architecture

### Deployment Components
```
┌─────────────────────────────────────┐
│      OpenProdoc Core Engine         │
│      (Tomcat 9 + ProdocWeb2)        │
│         Port: 8080                  │
│   ┌──────────────────────────┐      │
│   │  Web UI: /ProdocWeb2/    │      │
│   │  REST API: /APIRest/     │      │
│   └──────────────────────────┘      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼────────┐
│ PostgreSQL │    │  File Storage │
│  Database  │    │    Volume     │
└────────────┘    └───────────────┘
```

### Storage Architecture
* **Database (PostgreSQL)** - Metadata, users, permissions, configuration
* **File System Volume** - Document binaries, configurable encryption
* **Persistent Volumes** - Kubernetes-managed storage for data persistence

----

## 🚢 Quick Start

### Docker Compose (Recommended for Development)

```bash
# Clone repository
Clone the repository https://github.com/egenillo/openprodoc_red in your local environment

# Start services
docker-compose up -d

# Wait for startup (2-3 minutes for initial installation)
docker-compose logs -f core-engine

# Access application
# Web UI: http://localhost:8080/ProdocWeb2/
# REST API: http://localhost:8080/ProdocWeb2/APIRest/

# Default credentials
# Username: root
# Password: admin
```

### Kubernetes Deployment

```bash

# Deploy PostgreSQL
helm install openprodoc-postgresql ./helm/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Deploy OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# Local access via port-forward
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# Access application
# Web UI: http://localhost:8080/ProdocWeb2/
# REST API: http://localhost:8080/ProdocWeb2/APIRest/
```

See [Helm Deployment Guide](docs/HELM_DEPLOYMENT_GUIDE.md) for detailed instructions.

----

## 📡 REST API

OpenProdoc Red includes a full REST API for programmatic access.

### Quick Example

```bash
# Login
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d "{\"Name\":\"root\",\"Password\":\"admin\"}"

# Returns JWT token
{"Res":"OK","Token":"eyJhbGci..."}

# Use token for authenticated requests
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

### Available Endpoints

* **Session Management** - Login, logout
* **Folders API** - Create, read, update, delete folders
* **Documents API** - Upload, download, search documents
* **Thesauri API** - Manage controlled vocabularies

**Documentation**:
* [REST API Usage Guide](docs/api/API_USAGE_GUIDE.md) - Complete reference with examples
* [REST API Quick Reference](docs/api/API_QUICK_REFERENCE.md) - Command cheat sheet
* [Postman Collection](docs/api/OpenProdoc-API-Collection.json) - Import into API testing tools

**Test Scripts**:
* Linux/Mac: `./docs/api/test-api.sh`
* Windows: `docs/api/test-api.bat`

----

## 🛠️ Configuration

### Environment Variables

OpenProdoc Red uses environment variables for configuration:

```bash
# Database Configuration
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=prodoc
DB_USER=prodoc
DB_PASSWORD=your-secure-password
DB_JDBC_CLASS=org.postgresql.Driver
DB_JDBC_URL_TEMPLATE=jdbc:postgresql://{HOST}:{PORT}/{DATABASE}

# Installation Settings
INSTALL_ON_STARTUP=true
ROOT_PASSWORD=admin
DEFAULT_LANG=EN
TIMESTAMP_FORMAT="dd/MM/yyyy HH:mm:ss"
DATE_FORMAT="dd/MM/yyyy"
MAIN_KEY=uthfytnbh84kflh06fhru  # Document encryption key

# Repository Configuration
REPO_NAME=Reposit
REPO_ENCRYPT=False
REPO_URL=/storage/OPD/
REPO_TYPE=FS  # FileSystem storage
REPO_USER=
REPO_PASSWORD=
REPO_PARAM=

# JDBC Driver
JDBC_DRIVER_PATH=./lib/postgresql-42.3.8.jar
```

### Kubernetes Configuration

Helm values.yaml provides comprehensive configuration options:

```yaml
coreEngine:
  replicaCount: 2  # High availability

  service:
    type: ClusterIP
    port: 8080
    sessionAffinity:
      enabled: true  # Sticky sessions
      timeoutSeconds: 10800  # 3 hours

  persistence:
    enabled: true
    size: 100Gi
    mountPath: /storage/OPD

  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 2Gi
```

See [values.yaml](helm/openprodoc/values.yaml) for all options.

----

## 📊 Monitoring & Operations

### Health Checks

```bash
# Check application health (web UI)
curl http://localhost:8080/ProdocWeb2/

# Check REST API
curl http://localhost:8080/ProdocWeb2/APIRest/session

# Kubernetes pod status
kubectl get pods
kubectl logs -f <pod-name>
```

----

## 🔒 Security

### Default Security Settings

* **Non-root containers** - Runs as user 1000
* **Minimal capabilities** - Drops all unnecessary Linux capabilities
* **Read-only root filesystem** - Disabled (required for Tomcat work directories)
* **No privilege escalation** - Enforced via security context

### Production Security Checklist

- [ ] Change default admin password (`ROOT_PASSWORD`)
- [ ] Change database password (`DB_PASSWORD`)
- [ ] Change document encryption key (`MAIN_KEY`)
- [ ] Use specific image tags (not `latest`)
- [ ] Enable TLS/HTTPS via Ingress
- [ ] Configure network policies
- [ ] Set resource limits
- [ ] Enable audit logging
- [ ] Regular security updates
- [ ] Backup strategy in place

----

## 🔄 Migration from Classic OpenProdoc

OpenProdoc Red maintains **full compatibility** with existing OpenProdoc databases. Migration involves:

1. **Export existing database** from classic OpenProdoc
2. **Import into PostgreSQL** in the new environment
3. **Copy document storage** to persistent volume
4. **Configure environment variables** matching old configuration
5. **Deploy using Docker Compose or Helm**

The application will detect the existing database and skip initial installation.

----

## 📖 Documentation

* **[Helm Deployment Guide](docs/HELM_DEPLOYMENT_GUIDE.md)** - Complete Kubernetes deployment guide
* **[REST API Usage Guide](docs/api/API_USAGE_GUIDE.md)** - Comprehensive API reference
* **[REST API Quick Reference](docs/api/API_QUICK_REFERENCE.md)** - Quick command lookup
* **[Documentation Index](docs/README.md)** - All available documentation


----

## 📄 License

OpenProdoc Red is free and open source software licensed under:
* **GNU Affero General Public License v3** (AGPL-3.0)

This license ensures that any modifications or network services using this software remain open source.

----

## 🤝 Contributing

Contributions welcome for:
* Kubernetes deployment improvements
* Documentation and examples
* Performance optimizations
* Bug fixes and testing
* Additional storage backends
* Cloud provider integrations

----

## 📞 Support

* **Documentation**: See `docs/` folder
* **Issues**: Report bugs and feature requests
* **Original OpenProdoc**: https://jhierrot.github.io/openprodoc/
* **License**:  AGPL-3.0 license

----

## 🙏 Acknowledgments

**Original OpenProdoc** - Created by Joaquín Hierro
**OpenProdoc Red** - Cloud-native containerization and Kubernetes deployment

This project maintains full compatibility with the original OpenProdoc while providing modern cloud deployment capabilities.

----

## 📈 Version Information

* **Chart Version**: 1.0.0
* **App Version**: 3.0.3
* **Tomcat**: 9.0.x
* **PostgreSQL**: 15.x (recommended)
* **Java**: OpenJDK 11


