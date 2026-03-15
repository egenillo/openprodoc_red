# OpenProdoc Production Deployment Guide

This guide provides step-by-step instructions for deploying OpenProdoc to production environments.

## Deployment Options

| Method | Best For |
|---|---|
| **Docker Compose** | Single-server deployments, small teams |
| **Kubernetes (Helm)** | Multi-node clusters, high availability, enterprise |

## Prerequisites

### For Kubernetes (Helm)

- Kubernetes cluster 1.19+ (tested on 1.24+)
- Helm 3.2.0+
- kubectl configured with cluster access
- Storage class configured (for PersistentVolumes)
- Ingress controller installed (Traefik or nginx)
- cert-manager (optional, for automatic TLS certificates)
- Container registry (if using private images)

### For Docker Compose

- Docker Engine 20.10+ with Docker Compose v2
- Minimum 16GB RAM (Ollama + LLM models are memory-intensive)
- 100GB+ disk space (models, documents, databases)


## Step 1: Prepare Secrets

Create a secure password and encryption key:

```bash
# Generate strong passwords
export OPENPRODOC_ROOT_USER_PASSWORD=$(openssl rand -base64 16)
export ENCRYPTION_KEY=$(openssl rand -base64 32 | cut -c1-32)

echo "Save these credentials securely:"
echo "Openprodocc root user Password: $OPENPRODOC_ADMIN_USER_PASSWORD"
echo "Encryption Key: $ENCRYPTION_KEY"
```

## Step 2: Create Production Values File

Edit `production-values.yaml` or `values.yaml`:

```yaml

coreEngine:
  image:
    registry: ""  # Leave empty for local registry or specify your registry
    tag: "latest"  # Change to specific version tag in production
  config:
    database:
      user: user1   # Change to specific admin Postgres user
      password: pass1  # Change to specific password for admin Postgres user
    install:
      rootPassword: "admin"  # "REPLACE_WITH_OPENPRODOC_ROOT_USER_PASSWORD
      defaultLang: "EN"  # Change to your specific language
      mainKey: "uthfytnbh84kflh06fhru"    #  REPLACE_WITH_ENCRYPTION_KEY

```

## Step 3: Install OpenProdoc

```bash
# Create namespace
kubectl create namespace openprodoc

# Install with Helm
helm install openprodoc ./helm/openprodoc \
  -f production-values.yaml \
  --namespace openprodoc

# Monitor installation
kubectl get pods -n openprodoc -w
```

## Step 4: Wait for Initial Installation

The core engine will automatically install OpenProdoc on first startup:

```bash
# Watch core engine logs
kubectl logs -f -n openprodoc -l app.kubernetes.io/component=core-engine

# Wait for message: "OpenProdoc installation completed successfully"
```

## Step 5: Verify Deployment

### Kubernetes

```bash
# Check all pods are running
kubectl get pods -n openprodoc

# Expected output:
# NAME                                      READY   STATUS    RESTARTS   AGE
# openprodoc-core-engine-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# openprodoc-postgresql-0                   1/1     Running   0          5m
# openprodoc-ollama-xxxxxxxxxx-xxxxx        1/1     Running   0          5m
# openprodoc-pgvector-xxxxxxxxxx-xxxxx      1/1     Running   0          5m
# openprodoc-openwebui-xxxxxxxxxx-xxxxx     2/2     Running   0          5m

# Check services
kubectl get svc -n openprodoc
```

### Docker Compose

```bash
docker compose ps
# All services should show "Up" or "Up (healthy)"
```

## Step 6: Test Access

### Kubernetes

```bash
# Port forward to access locally
kubectl port-forward svc/openprodoc-core-engine 8081:8080
kubectl port-forward svc/openprodoc-openwebui 8080:8080

# Or if ingress is enabled:
kubectl get ingress -n openprodoc openprodoc -o jsonpath='{.spec.rules[0].host}'
```

### Docker Compose

Services are directly accessible:
- **OpenProdoc**: `http://localhost:8081/ProdocWeb2/`
- **Open WebUI**: `http://localhost:8080`

### Default Credentials

- **OpenProdoc**: Username: `root` / Password: `admin` (change in production)
- **Open WebUI**: First user to register becomes admin (use `watcher@openprodoc.local` / `12345678`)

## Production Checklist

- [ ] All passwords are strong and stored securely (password manager, sealed secrets, etc.)
- [ ] Storage classes are configured with appropriate performance characteristics (Kubernetes)
- [ ] Resource limits are set based on expected load
- [ ] TLS certificates are valid and auto-renewing (Kubernetes with ingress)
- [ ] The `watcher@openprodoc.local` admin account is created in Open WebUI
- [ ] The `watcher` user is created in OpenProdoc with appropriate READ ACL permissions
- [ ] SCIM token and WebUI secret key are changed from defaults
- [ ] Backup strategy is in place for PostgreSQL, pgvector, and ollama volumes


## Scaling

### Manual Scaling (Kubernetes)

```bash
# Scale Core Engine
kubectl scale deployment openprodoc-core-engine -n openprodoc --replicas=3

# Or via Helm
helm upgrade openprodoc openprodoc/openprodoc \
  -f production-values.yaml \
  --set coreEngine.replicaCount=3 \
  --namespace openprodoc
```

Note: Docker Compose deployments run single instances. For multi-replica scaling, use Kubernetes.


## Troubleshooting

### Pod not starting (Kubernetes)

```bash
kubectl describe pod <pod-name> -n openprodoc
kubectl logs <pod-name> -n openprodoc
```

### Container not starting (Docker Compose)

```bash
docker compose logs <service-name>
docker inspect openprodoc-<service-name>
```

### Database connection issues

```bash
# Kubernetes
kubectl exec -it -n openprodoc openprodoc-core-engine-xxx -- \
  nc -zv openprodoc-postgresql 5432

# Docker Compose
docker compose exec core-engine bash -c "nc -zv postgres 5432"
```

### Watcher authentication failures

If the watcher logs show `authentication failed`, ensure the `watcher@openprodoc.local` admin user exists in Open WebUI. See [RAG_SETUP.md](RAG_SETUP.md#step-4-setup-rag-users) for setup instructions.

