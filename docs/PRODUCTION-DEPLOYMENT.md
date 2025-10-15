# OpenProdoc Production Deployment Guide

This guide provides step-by-step instructions for deploying OpenProdoc to a production Kubernetes cluster.

## Prerequisites

- Kubernetes cluster 1.19+ (tested on 1.24+)
- Helm 3.2.0+
- kubectl configured with cluster access
- Storage class configured (for PersistentVolumes)
- Ingress controller installed (nginx recommended)
- cert-manager (optional, for automatic TLS certificates)
- Container registry (if using private images)


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

```bash
# Check all pods are running
kubectl get pods -n openprodoc

# Expected output:
# NAME                                      READY   STATUS    RESTARTS   AGE
# openprodoc-core-engine-xxxxxxxxxx-xxxxx   1/1     Running   0          5m
# openprodoc-postgresql-0                   1/1     Running   0          5m

# Check services
kubectl get svc -n openprodoc

```

## Step 6: Test Access

```bash
# Get ingress URL
kubectl get ingress -n openprodoc openprodoc -o jsonpath='{.spec.rules[0].host}'

# Access via browser:
# https://openprodoc.yourdomain.com/ProdocWeb2/

# Login credentials:
# Username: root
# Password: <ADMIN_PASSWORD from Step 1>
```

## Production Checklist

- [ ] All passwords are strong and stored securely (password manager, sealed secrets, etc.)
- [ ] Storage classes are configured with appropriate performance characteristics
- [ ] Resource limits are set based on expected load
- [ ] TLS certificates are valid and auto-renewing


## Scaling

### Manual Scaling

```bash
# Scale Web UI
kubectl scale deployment openprodoc-web-ui -n openprodoc --replicas=5

# Or via Helm
helm upgrade openprodoc ./helm/openprodoc \
  -f production-values.yaml \
  --set webUI.replicaCount=5 \
  --namespace openprodoc
```


## Troubleshooting

### Pod not starting

```bash
kubectl describe pod <pod-name> -n openprodoc
kubectl logs <pod-name> -n openprodoc
```

### Database connection issues

```bash
# Test PostgreSQL connectivity
kubectl exec -it -n openprodoc openprodoc-core-engine-xxx -- \
  nc -zv openprodoc-postgresql 5432
```

