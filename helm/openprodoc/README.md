# OpenProdoc Helm Chart

Production-ready Helm chart for deploying OpenProdoc ECM (Enterprise Content Management) system on Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure
- Ingress controller (nginx, traefik, etc.) if ingress is enabled
- cert-manager (optional, for TLS certificates)

## Features

- **High Availability**: Multiple Web UI replicas with anti-affinity rules
- **Auto-scaling**: HPA for Web UI based on CPU/Memory metrics
- **Security**: Network policies, pod security contexts, secret management
- **Persistence**: PVCs for document storage and configurations
- **Monitoring**: ServiceMonitor support for Prometheus
- **Production-ready**: Resource limits, probes, PodDisruptionBudgets
- **Flexible**: Support for Direct and Remote connection modes

## Installation

### 1. Add Repository (if published)

```bash
helm repo add openprodoc https://charts.openprodoc.org
helm repo update
```

### 2. Create Production Values File

Create a `my-values.yaml` file with your production settings:

```yaml
# REQUIRED: Set PostgreSQL password
postgresql:
  auth:
    password: "YOUR_STRONG_PASSWORD_HERE"

# REQUIRED: Set core engine configuration
coreEngine:
  image:
    tag: "1.0.0"  # Use specific version

  config:
    database:
      password: "YOUR_STRONG_PASSWORD_HERE"  # Must match postgresql password

    install:
      rootPassword: "YOUR_ADMIN_PASSWORD"
      mainKey: "YOUR_ENCRYPTION_KEY_32CHARS"

  persistence:
    size: 500Gi  # Adjust based on needs
    storageClass: "your-storage-class"

# REQUIRED: Set web UI configuration
webUI:
  image:
    tag: "1.0.0"  # Use specific version

  replicaCount: 3

  database:
    password: "ENCODED_PASSWORD"  # Get from database after first install

  persistence:
    storageClass: "your-storage-class"

# REQUIRED: Set ingress domain
ingress:
  enabled: true
  hosts:
    - host: openprodoc.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: openprodoc-web-ui
              port:
                number: 8080
  tls:
    - secretName: openprodoc-tls
      hosts:
        - openprodoc.yourdomain.com
```

### 3. Install the Chart

```bash
# First installation
helm install openprodoc ./helm/openprodoc \
  -f my-values.yaml \
  --namespace openprodoc \
  --create-namespace

# Monitor installation
kubectl get pods -n openprodoc -w
```

### 4. Get Encoded Password (First Install Only)

After the core engine completes installation:

```bash
# Get encoded password from database
kubectl exec -n openprodoc openprodoc-postgresql-0 -- \
  psql -U prodoc -d prodoc \
  -c "SELECT password FROM pd_users WHERE name='root';"

# Update my-values.yaml with the encoded password
# Then upgrade:
helm upgrade openprodoc ./helm/openprodoc \
  -f my-values.yaml \
  --namespace openprodoc
```

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `postgresql.auth.password` | PostgreSQL password | `""` (required) |
| `coreEngine.image.repository` | Core engine image | `openprodoc/core-engine` |
| `coreEngine.image.tag` | Core engine image tag | `latest` |
| `coreEngine.config.database.password` | Database password | `""` (required) |
| `coreEngine.config.install.rootPassword` | Admin password | `""` (required) |
| `coreEngine.config.install.mainKey` | Encryption key | `""` (required) |
| `coreEngine.persistence.size` | Document storage size | `100Gi` |
| `webUI.image.repository` | Web UI image | `openprodoc-red/web-ui` |
| `webUI.image.tag` | Web UI image tag | `latest` |
| `webUI.replicaCount` | Number of Web UI replicas | `2` |
| `webUI.database.password` | Encoded database password | `""` (required) |
| `webUI.autoscaling.enabled` | Enable HPA | `true` |
| `webUI.autoscaling.minReplicas` | Minimum replicas | `2` |
| `webUI.autoscaling.maxReplicas` | Maximum replicas | `10` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `nginx` |
| `ingress.hosts` | Ingress hosts | `[]` (required) |

### Connection Modes

The Web UI supports two connection modes:

#### Direct Mode (Default - Production Recommended)
Web UI connects directly to PostgreSQL database:

```yaml
webUI:
  connectionMode: Direct
  database:
    password: "ENCODED_PASSWORD"  # Use encoded password from database
```

#### Remote Mode
Web UI connects to Core Engine via HTTP:

```yaml
webUI:
  connectionMode: Remote
  remoteCore:
    host: openprodoc-core-engine
    port: 8080
    context: ProdocWeb2
```

### Resource Configuration

Production resource recommendations:

```yaml
postgresql:
  primary:
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 2000m
        memory: 4Gi

coreEngine:
  resources:
    requests:
      cpu: 1000m
      memory: 4Gi
    limits:
      cpu: 4000m
      memory: 8Gi

webUI:
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi
```

### Storage Configuration

```yaml
coreEngine:
  persistence:
    enabled: true
    storageClass: "fast-ssd"  # Use fast storage for documents
    size: 500Gi
    accessModes:
      - ReadWriteOnce

postgresql:
  primary:
    persistence:
      enabled: true
      storageClass: "fast-ssd"  # Use fast storage for database
      size: 50Gi
```

### Security Configuration

```yaml
# Enable network policies
networkPolicy:
  enabled: true

# Pod security contexts
coreEngine:
  podSecurityContext:
    fsGroup: 1000
    runAsNonRoot: true
    runAsUser: 1000

  securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop:
        - ALL
    readOnlyRootFilesystem: false
```

## Upgrading

```bash
# Upgrade to new version
helm upgrade openprodoc ./helm/openprodoc \
  -f my-values.yaml \
  --namespace openprodoc

# Upgrade with new values
helm upgrade openprodoc ./helm/openprodoc \
  -f my-values.yaml \
  --set webUI.replicaCount=5 \
  --namespace openprodoc
```

## Uninstallation

```bash
# Uninstall release (keeps PVCs)
helm uninstall openprodoc --namespace openprodoc

# Delete PVCs (WARNING: This deletes all data)
kubectl delete pvc -n openprodoc --all

# Delete namespace
kubectl delete namespace openprodoc
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n openprodoc
kubectl describe pod <pod-name> -n openprodoc
```

### View Logs

```bash
# Core engine logs
kubectl logs -n openprodoc -l app.kubernetes.io/component=core-engine

# Web UI logs
kubectl logs -n openprodoc -l app.kubernetes.io/component=web-ui

# PostgreSQL logs
kubectl logs -n openprodoc -l app.kubernetes.io/name=postgresql
```

### Database Access

```bash
# Connect to PostgreSQL
kubectl exec -it -n openprodoc openprodoc-postgresql-0 -- \
  psql -U prodoc -d prodoc

# Check tables
kubectl exec -n openprodoc openprodoc-postgresql-0 -- \
  psql -U prodoc -d prodoc -c "\dt"
```

### Common Issues

**Issue**: Web UI shows "For input string" error
**Solution**: Ensure you're using the ENCODED password from the database, not plain text

**Issue**: Core engine fails to install
**Solution**: Check PostgreSQL connectivity and credentials

**Issue**: Cannot access via ingress
**Solution**: Verify ingress controller is running and DNS is configured

## Production Checklist

- [ ] Use specific image tags (not `latest`)
- [ ] Set strong passwords for all secrets
- [ ] Configure proper storage classes
- [ ] Set appropriate resource limits
- [ ] Enable TLS/SSL for ingress
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerts
- [ ] Configure network policies
- [ ] Review and adjust autoscaling settings
- [ ] Test disaster recovery procedures

## Backup and Restore

### Backup

```bash
# Backup PostgreSQL
kubectl exec -n openprodoc openprodoc-postgresql-0 -- \
  pg_dump -U prodoc prodoc > openprodoc-backup.sql

# Backup documents (requires access to PV)
kubectl exec -n openprodoc <core-engine-pod> -- \
  tar czf /tmp/documents.tar.gz /storage/OPD/
kubectl cp openprodoc/<core-engine-pod>:/tmp/documents.tar.gz ./documents.tar.gz
```

### Restore

```bash
# Restore PostgreSQL
kubectl exec -i -n openprodoc openprodoc-postgresql-0 -- \
  psql -U prodoc prodoc < openprodoc-backup.sql

# Restore documents
kubectl cp ./documents.tar.gz openprodoc/<core-engine-pod>:/tmp/documents.tar.gz
kubectl exec -n openprodoc <core-engine-pod> -- \
  tar xzf /tmp/documents.tar.gz -C /
```

## Monitoring

Enable Prometheus monitoring:

```yaml
monitoring:
  serviceMonitor:
    enabled: true
    interval: 30s
```

Enable Grafana dashboard:

```yaml
monitoring:
  grafanaDashboard:
    enabled: true
```

## Support

- GitHub Issues: https://github.com/yourusername/openprodoc-red/issues
- OpenProdoc Official: http://openprodoc.org
- Documentation: https://github.com/yourusername/openprodoc-red

## License

This Helm chart is released under the AGPL-3.0 License. See LICENSE file for details.
