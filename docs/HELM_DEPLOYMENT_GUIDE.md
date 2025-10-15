# OpenProdoc Helm Chart Deployment Guide

## Overview

This guide covers deploying OpenProdoc Enterprise Content Management system using Helm on Kubernetes (K3s, K3d, or any Kubernetes cluster).


**Chart Version**: 1.0.0
**App Version**: 3.0.4

---

## Prerequisites

### Required Tools

- **Kubernetes cluster** (K3s, K3d, minikube, or cloud provider)
- **kubectl** - Kubernetes CLI
- **Helm 3.x** - Package manager for Kubernetes
- **Docker** (optional) - Only needed for K3d image import

### Required Database

- **Postgres Database** A Postgres instance is required for openprodoc database deployment
- **Database instance** Postgres DB must contain a database for openprodoc deployment
- **Database admin user** Postgres DB must contain a user with admin permissions for the openprodoc defined database 

### Check Prerequisites

```bash
# Check Kubernetes cluster
kubectl cluster-info
kubectl get nodes

# Check Helm version
helm version

```

---

## Installation Methods

OpenProdoc can be deployed using three methods:

1. **Helm Repository** (Recommended) - Install from public Helm repository
2. **Local Chart** - Use charts from this repository
3. **TGZ Package** - Download and install packaged chart

---

## Quick Start (Development)

### Method 1: Install from Helm Repository (Recommended)

```bash
# Add OpenProdoc Helm repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/

# Update repository index
helm repo update

# Install PostgreSQL (if needed)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install openprodoc-postgresql bitnami/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Install OpenProdoc from repository
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin
  

```

### Method 2: Install from Local Chart

### 1. Deploy PostgreSQL Database

OpenProdoc requires PostgreSQL. Deploy it first:

```bash
# Add PostgreSQL namespace (optional)
kubectl create namespace openprodoc

# Install PostgreSQL using the included chart
helm install openprodoc-postgresql ./helm/postgresql \
  --namespace default \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

```

### 2. Deploy OpenProdoc

```bash
# Navigate to helm chart directory

# Install OpenProdoc
helm install openprodoc ./openprodoc \
  --namespace default \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

```

### Method 3: Install from TGZ Package

```bash
# Option A: Download TGZ from Helm repository
helm pull openprodoc/openprodoc --version 1.0.0

# Option B: Download directly from GitHub releases
# curl -LO https://egenillo.github.io/helm-charts/openprodoc-1.0.0.tgz

# Install PostgreSQL (if needed)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install openprodoc-postgresql bitnami/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Install from TGZ file
helm install openprodoc openprodoc-1.0.0.tgz \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# Or with custom values file
helm install openprodoc openprodoc-1.0.0.tgz \
  -f my-values.yaml

# Watch deployment
kubectl get pods -w
```

**Advantages of TGZ method**:
- No need to add Helm repository
- Works in air-gapped environments
- Easy to version control and archive
- Can be stored in artifact repositories

### 4. Access OpenProdoc

```bash
# Port forward to access locally the application
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# Access in browser in local:
# Web UI: http://localhost:8080/ProdocWeb2/
# REST API: http://localhost:8080/ProdocWeb2/APIRest/

# Default credentials:
# Username: root
# Password: admin
```

To access remotely configure the Ingress parameters in values.yaml before deploying 
---

## Configuration

### values.yaml Structure

The chart uses a hierarchical configuration:

```yaml
coreEngine:           # Core application settings
  replicaCount: 2     # Number of instances
  image:              # Docker image configuration
  service:            # Kubernetes service
  config:             # Application configuration
    database:         # PostgreSQL connection
    install:          # Initial installation
    repository:       # Document storage
  persistence:        # Persistent volumes
  resources:          # CPU/Memory limits
```

### Docker deployment

####  Docker information

**Docker Hub**: Images are available at `openprodoc/core-engine`

**Pull image manually**:
```bash
docker pull openprodoc/core-engine:latest:latest
```


---

## Deployment Scenarios

### Scenario 1: Local K3d Development (Using Helm Repository)


```bash
# Create K3d cluster
k3d cluster create openprodoc-dev \
  --api-port 6443 \
  --servers 1 \
  --agents 2 \
  --port "8080:80@loadbalancer"

# Add Helm repositories
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Deploy PostgreSQL
helm install openprodoc-postgresql bitnami/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Deploy OpenProdoc from repository
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# Access via port-forward
kubectl port-forward svc/openprodoc-core-engine 8080:8080
```


### Scenario 2: Production Deployment (Using Helm Repository)

Check Production deployment guide for details.

```bash
# Create production namespace
kubectl create namespace production

# Add Helm repositories
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Create secrets for sensitive data
kubectl create secret generic openprodoc-secrets \
  --namespace production \
  --from-literal=db-password='YourStrongDBPassword123!' \
  --from-literal=root-password='YourAdminPassword456!' \
  --from-literal=main-key='YourEncryptionKey32CharsLong!'

# Deploy PostgreSQL
helm install openprodoc-postgresql bitnami/postgresql \
  --namespace production \
  --set auth.username=prodoc \
  --set auth.password='YourStrongDBPassword123!' \
  --set auth.database=prodoc

# Deploy with production values from repository
helm install openprodoc openprodoc/openprodoc \
  --namespace production \
  --version 1.0.0 \
  --set coreEngine.image.tag=1.0.0 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=openprodoc.yourdomain.com

# Monitor deployment
kubectl get pods -n production -w
```

**Alternative: Using TGZ package for air-gapped environment**
```bash
# Download chart TGZ
helm pull openprodoc/openprodoc --version 1.0.0

# Deploy from TGZ
helm install openprodoc openprodoc-1.0.0.tgz \
  --namespace production \
  -f values-production.yaml
```

### Scenario 3: Custom Storage Class

```bash
# Add repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo update

# Deploy with specific storage class from repository
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.persistence.storageClass=fast-ssd \
  --set coreEngine.persistence.size=500Gi \
  --set coreEngine.config.database.user='YourAdminDBUser' \
  --set coreEngine.config.database.password='YourPasswordDBUser' \
  --set coreEngine.install.rootPassword=ad'YourPasswordRootUser' \
  --set coreEngine.config.database.password=pass1
```


### Scenario 4: Single Node (Minimal Resources)

```bash
# Minimal deployment for testing from repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.replicaCount=1 \
  --set coreEngine.resources.limits.cpu=1000m \
  --set coreEngine.resources.limits.memory=2Gi \
  --set coreEngine.persistence.size=10Gi \
  --set coreEngine.config.database.user='YourAdminDBUser' \
  --set coreEngine.config.database.password='YourPasswordDBUser' \
  --set coreEngine.install.rootPassword=ad'YourPasswordRootUser' 

```

---

## Helm Commands Reference

### Repository Management

```bash
# Add OpenProdoc Helm repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/

# Update repository index
helm repo update

# Search for available charts and versions
helm search repo openprodoc
helm search repo openprodoc --versions

# Show chart information
helm show chart openprodoc/openprodoc
helm show values openprodoc/openprodoc
helm show readme openprodoc/openprodoc

# Download chart without installing
helm pull openprodoc/openprodoc
helm pull openprodoc/openprodoc --version 1.0.0
helm pull openprodoc/openprodoc --untar

# Remove repository
helm repo remove openprodoc
```

### Installation

```bash
# Install from Helm repository (recommended)
helm install openprodoc openprodoc/openprodoc

# Install from local chart directory
helm install openprodoc ./helm/openprodoc

# Install from TGZ file
helm install openprodoc openprodoc-1.0.0.tgz

# Install with custom values file
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# Install specific version from repository
helm install openprodoc openprodoc/openprodoc --version 1.0.0

# Install in specific namespace
helm install openprodoc openprodoc/openprodoc \
  --namespace prod \
  --create-namespace

# Dry-run to see what would be deployed
helm install openprodoc openprodoc/openprodoc --dry-run --debug
```

### Uninstall

```bash
# Uninstall release
helm uninstall openprodoc

# Uninstall and delete persistent volumes
helm uninstall openprodoc
kubectl delete pvc openprodoc-storage 
```



## Customization Examples

### Example 1: Custom values.yaml

Create `my-values.yaml`:

```yaml
coreEngine:
  replicaCount: 3

  image:
    tag: "1.0.0"

  config:
    database:
      host: postgres.database.svc.cluster.local
      password: "securePassword123"

    install:
      rootPassword: "AdminPass456"
      defaultLang: "ES"

  persistence:
    size: 200Gi
    storageClass: "fast-storage"

  resources:
    limits:
      cpu: 4000m
      memory: 8Gi
    requests:
      cpu: 1000m
      memory: 4Gi

ingress:
  enabled: true
  hosts:
    - host: docs.mycompany.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: openprodoc-tls
      hosts:
        - docs.mycompany.com
```

Deploy with:
```bash
# From Helm repository
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# Or from local chart
helm install openprodoc ./helm/openprodoc -f my-values.yaml
```


---

## Troubleshooting

### Check Pod Status

```bash
# Get pods
kubectl get pods -l app.kubernetes.io/name=openprodoc

# Describe pod
kubectl describe pod openprodoc-core-engine-xxx

# Check logs
kubectl logs -f openprodoc-core-engine-xxx

# Check previous container logs (if crashed)
kubectl logs openprodoc-core-engine-xxx --previous
```

### Common Issues

#### Issue: Pod in CrashLoopBackOff

```bash
# Check logs
kubectl logs openprodoc-core-engine-xxx

# Common causes:
# 1. Database not ready - check PostgreSQL
kubectl get pods -l app.kubernetes.io/name=postgresql

# 2. Wrong database credentials
kubectl get secret openprodoc-secrets -o yaml

# 3. Image pull error
kubectl describe pod openprodoc-core-engine-xxx | grep -A 5 Events
```

#### Issue: Cannot connect to database

```bash
# Test database connectivity from pod
kubectl exec -it openprodoc-core-engine-xxx -- bash
pg_isready -h openprodoc-postgresql -p 5432 -U user1

# Check service
kubectl get svc openprodoc-postgresql

# Check network policies
kubectl get networkpolicies
```

#### Issue: PVC not binding

```bash
# Check PVC status
kubectl get pvc

# Check storage classes
kubectl get storageclass

# Describe PVC for events
kubectl describe pvc openprodoc-storage
```

### Scaling

```bash
# Scale using kubectl
kubectl scale deployment openprodoc-core-engine --replicas=3

# Scale using Helm upgrade
helm upgrade openprodoc ./helm/openprodoc \
  --set coreEngine.replicaCount=3
```



---

## Security Best Practices

### 1. Change Default Passwords

```bash
# Use Kubernetes secrets
kubectl create secret generic openprodoc-secrets \
  --from-literal=db-password='StrongPassword123!' \
  --from-literal=root-password='AdminPassword456!' \
  --from-literal=main-key='EncryptionKey32CharsHere12345'
```

### 2. Use Specific Image Tags

```yaml
coreEngine:
  image:
    tag: "1.0.0"  # NOT "latest"
```

### 3. Enable TLS for Ingress

```yaml
ingress:
  enabled: true
  tls:
    - secretName: openprodoc-tls
      hosts:
        - openprodoc.yourdomain.com
```

### 4. Resource Limits

```yaml
coreEngine:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### 5. Non-root User

```yaml
coreEngine:
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
```


