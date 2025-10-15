# OpenProdoc Red Documentation

This folder contains documentation for the OpenProdoc Red Kubernetes deployment.

## Available Documentation

### 📚 [API Usage Guide](API_USAGE_GUIDE.md)
Comprehensive guide covering:
- Complete API endpoint reference
- Authentication and session management
- Folders, Documents, and Thesauri APIs
- Code examples in Python, JavaScript, and Java
- Troubleshooting and security best practices
- Full workflow examples

**Best for**: Learning the API from scratch, understanding all features, integration development

### ⚡ [API Quick Reference](API_QUICK_REFERENCE.md)
Quick reference guide with:
- All endpoints in table format
- Common curl commands
- Response codes and formats
- Query syntax examples
- Quick copy-paste examples

**Best for**: Quick lookups, daily development work, command-line operations

## Quick Start

### 1. Access the API

If running in Kubernetes, first set up port forwarding:

```bash
export KUBECONFIG="C:\datos\claude\openprodoc_red2\kubeconfig.yaml"
kubectl port-forward -n default svc/openprodoc-core-engine 8080:8080
```

### 2. Login and Get Token

```bash
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d '{"Name":"root","Password":"admin"}'
```

Save the returned token:
```bash
export TOKEN="<your-token-here>"
```

### 3. Test the API

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

## API Base URL

- **Local/Port-forward**: `http://localhost:8080/ProdocWeb2/APIRest/`
- **Internal Cluster**: `http://openprodoc-core-engine.default.svc.cluster.local:8080/ProdocWeb2/APIRest/`
- **Ingress** (when enabled): `http://<your-domain>/ProdocWeb2/APIRest/`

## Default Credentials

- **Username**: `root`
- **Password**: `admin`

⚠️ **Important**: Change these credentials in production!

## Key Features

- ✅ RESTful JSON API
- ✅ JWT token-based authentication
- ✅ Document upload/download
- ✅ Folder hierarchy management
- ✅ Search and query capabilities
- ✅ Version control (checkout/checkin)
- ✅ Thesaurus management
- ✅ Session management

## Architecture

```
┌─────────────────────────────────────────┐
│         Client Application              │
│   (curl, Python, JavaScript, Java)      │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON
               │
┌──────────────▼──────────────────────────┐
│      OpenProdoc REST API                │
│   http://host:8080/ProdocWeb2/APIRest/  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    OpenProdoc Core Engine (Tomcat)      │
│         - Document Management           │
│         - Folder Operations             │
│         - Version Control               │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼──────┐
│ PostgreSQL │    │ File System │
│  Database  │    │   Storage   │
└────────────┘    └─────────────┘
```

## Kubernetes Deployment

The OpenProdoc system runs in Kubernetes with:
- **2 replicas** of core-engine for high availability
- **Session affinity** enabled (ClientIP-based, 3 hours timeout)
- **Persistent volumes** for document storage and configuration
- **PostgreSQL** database for metadata
- **Service type**: ClusterIP (internal access)

## Testing Checklist

✅ Login endpoint working
✅ Token authentication working
✅ Get folder by path working
✅ List subfolders working
✅ List documents in folder working
✅ Logout working
✅ JWT token expiration handled
✅ Error responses formatted correctly

## Support and Resources

- **Full Documentation**: See [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)
- **Quick Reference**: See [API_QUICK_REFERENCE.md](API_QUICK_REFERENCE.md)
- **Source Code**: `C:\datos\claude\openprodoc\ProdocWeb2\src\java\APIRest\`
- **Helm Charts**: `C:\datos\claude\openprodoc_red2\helm\openprodoc\`

## Version

- **OpenProdoc Version**: 3.0.3
- **API Version**: REST API v1
- **Documentation Last Updated**: October 2025

## Need Help?

1. Check the [API Usage Guide](API_USAGE_GUIDE.md) for detailed examples
2. Review the [Quick Reference](API_QUICK_REFERENCE.md) for common commands
3. Check pod logs: `kubectl logs -n default <pod-name>`
4. Verify service status: `kubectl get pods,svc -n default`

---

**Happy Coding! 🚀**
