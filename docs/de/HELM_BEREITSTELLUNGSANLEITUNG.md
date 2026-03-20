# OpenProdoc Helm Chart Bereitstellungsanleitung

## Uebersicht

Diese Anleitung behandelt die Bereitstellung des OpenProdoc Enterprise Content Management Systems mit Helm auf Kubernetes (K3s, K3d oder einem beliebigen Kubernetes-Cluster).


**Chart-Version**: 1.0.0
**App-Version**: 3.0.4

---

## Voraussetzungen

### Erforderliche Werkzeuge

- **Kubernetes-Cluster** (K3s, K3d, minikube oder Cloud-Anbieter)
- **kubectl** - Kubernetes CLI
- **Helm 3.x** - Paketmanager fuer Kubernetes
- **Docker** (optional) - Wird nur fuer den K3d-Image-Import benoetigt

### Erforderliche Datenbank

- **Postgres-Datenbank** Eine Postgres-Instanz ist fuer die Bereitstellung der OpenProdoc-Datenbank erforderlich
- **Datenbankinstanz** Die Postgres-Datenbank muss eine Datenbank fuer die OpenProdoc-Bereitstellung enthalten
- **Datenbank-Administratorbenutzer** Die Postgres-Datenbank muss einen Benutzer mit Administratorberechtigungen fuer die definierte OpenProdoc-Datenbank enthalten

### Voraussetzungen pruefen

```bash
# Check Kubernetes cluster
kubectl cluster-info
kubectl get nodes

# Check Helm version
helm version

```


---

## Installationsmethoden

OpenProdoc kann mit drei Methoden bereitgestellt werden:

1. **Helm Repository** (Empfohlen) - Installation aus dem oeffentlichen Helm Repository
2. **Lokales Chart** - Verwendung von Charts aus diesem Repository
3. **TGZ-Paket** - Herunterladen und Installieren eines gepackten Charts

---

## Schnellstart (Entwicklung)

### Methode 1: Installation aus dem Helm Repository (Empfohlen)

```bash
# Add OpenProdoc Helm repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/

# Update repository index
helm repo update

# Install PostgreSQL from the OpenProdoc repository
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Install OpenProdoc from repository
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin


```

### Methode 2: Installation aus dem lokalen Chart

### 1. PostgreSQL-Datenbank bereitstellen

OpenProdoc erfordert PostgreSQL. Stellen Sie es zuerst bereit:

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

### 2. OpenProdoc bereitstellen

```bash
# Navigate to helm chart directory

# Install OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --namespace default \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

```

### Methode 3: Installation aus dem TGZ-Paket

```bash
# Option A: Download TGZ from Helm repository
helm pull openprodoc/openprodoc --version 1.0.0

# Option B: Download directly from GitHub releases
# curl -LO https://egenillo.github.io/helm-charts/openprodoc-1.0.0.tgz

# Install PostgreSQL from the OpenProdoc repository
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
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

**Vorteile der TGZ-Methode**:
- Kein Hinzufuegen eines Helm Repository erforderlich
- Funktioniert in isolierten Umgebungen ohne Internetzugang (Air-Gapped)
- Einfache Versionskontrolle und Archivierung
- Kann in Artefakt-Repositories gespeichert werden

### 4. Zugriff auf OpenProdoc

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

Fuer den Fernzugriff konfigurieren Sie die Ingress-Parameter in values.yaml vor der Bereitstellung.
---

## Konfiguration

### Struktur der values.yaml

Das Chart verwendet eine hierarchische Konfiguration:

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

### Docker Compose Bereitstellung

Docker Compose bietet eine einfachere Alternative zu Kubernetes fuer lokale Entwicklung und Einzelserver-Bereitstellungen. Die Datei `docker/docker-compose.yml` stellt die vollstaendige Loesung mit allen Komponenten bereit.

#### Bereitgestellte Dienste

| Dienst | Image | Host-Port | Beschreibung |
|---|---|---|---|
| `postgres` | postgres:16-alpine | 5432 | OpenProdoc-Datenbank |
| `core-engine` | openprodoc/core-engine:latest | **8081** | OpenProdoc-Backend + Web-Oberflaeche |
| `pgvector` | pgvector/pgvector:pg16 | (intern) | Vektordatenbank fuer RAG |
| `ollama` | ollama/ollama:0.5.4 | (intern) | LLM- und Embedding-Engine |
| `ollama-pull-models` | curlimages/curl | - | Einmaliger Modell-Downloader |
| `openwebui` | ghcr.io/open-webui/open-webui:main | **8080** | RAG-Oberflaeche |
| `watcher` | openprodoc/openprodoc_rag:1.0.1 | (intern) | Dokument-/Benutzer-/Gruppen-Synchronisation |

#### Schnellstart mit Docker Compose

```bash
# Navigate to docker directory
cd docker/

# Start all services
docker compose up -d

# Monitor startup
docker compose logs -f

# Access the services:
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# OpenWebUI:   http://localhost:8080
```

#### Stoppen und Aufraeumen

```bash
# Stop all services (preserves data)
docker compose stop

# Stop and remove containers (preserves volumes)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

#### Docker Hub Images

Images sind verfuegbar unter:
- `openprodoc/core-engine` - OpenProdoc Core Engine
- `openprodoc/openprodoc_rag` - RAG Watcher Sidecar

**Images manuell herunterladen**:
```bash
docker pull openprodoc/core-engine:latest
docker pull openprodoc/openprodoc_rag:1.0.1
```

#### Wesentliche Unterschiede: Docker Compose vs. Kubernetes

| Merkmal | Docker Compose | Kubernetes (Helm) |
|---|---|---|
| Watcher-Bereitstellung | Separater Container | Sidecar im OpenWebUI-Pod |
| Skalierung | Einzelne Instanz | Multi-Replica mit Hochverfuegbarkeit |
| Geheimnisse | Klartextumgebungsvariablen | Kubernetes Secrets |
| Diensterkennung | Docker DNS | Kubernetes Services |
| Speicher | Docker Volumes | PersistentVolumeClaims |
| Zustandspruefungen | Docker Healthcheck | Liveness/Readiness Probes |
| Init-Container | Einmaliger Dienst | Native Init-Container |
| Ingress | Port-Zuordnung | Traefik/nginx Ingress |

---

## Bereitstellungsszenarien

### Szenario 1: Lokale K3d-Entwicklung (mit Helm Repository)


```bash
# Create K3d cluster
k3d cluster create openprodoc-dev \
  --api-port 6443 \
  --servers 1 \
  --agents 2 \
  --port "8080:80@loadbalancer"

# Add Helm repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo update

# Deploy PostgreSQL from the OpenProdoc repository
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
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


### Szenario 2: Produktionsbereitstellung (mit Helm Repository)

Weitere Details finden Sie in der Anleitung fuer die Produktionsbereitstellung.

```bash
# Create production namespace
kubectl create namespace production

# Add Helm repository
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo update

# Create secrets for sensitive data
kubectl create secret generic openprodoc-secrets \
  --namespace production \
  --from-literal=db-password='YourStrongDBPassword123!' \
  --from-literal=root-password='YourAdminPassword456!' \
  --from-literal=main-key='YourEncryptionKey32CharsLong!'

# Deploy PostgreSQL from the OpenProdoc repository
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
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

**Alternative: Verwendung des TGZ-Pakets fuer isolierte Umgebungen**
```bash
# Download chart TGZ
helm pull openprodoc/openprodoc --version 1.0.0

# Deploy from TGZ
helm install openprodoc openprodoc-1.0.0.tgz \
  --namespace production \
  -f values-production.yaml
```

### Szenario 3: Benutzerdefinierte Storage Class

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
  --set coreEngine.install.rootPassword='YourPasswordRootUser'
```


### Szenario 4: Einzelner Knoten (Minimale Ressourcen)

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
  --set coreEngine.install.rootPassword='YourPasswordRootUser'

```

---

## Helm-Befehlsreferenz

### Repository-Verwaltung

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

### Deinstallation

```bash
# Uninstall release
helm uninstall openprodoc

# Uninstall and delete persistent volumes
helm uninstall openprodoc
kubectl delete pvc openprodoc-storage
```



## Anpassungsbeispiele

### Beispiel 1: Benutzerdefinierte values.yaml

Erstellen Sie `my-values.yaml`:

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

Bereitstellen mit:
```bash
# From Helm repository
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# Or from local chart
helm install openprodoc ./helm/openprodoc -f my-values.yaml
```


---

## Fehlerbehebung

### Pod-Status pruefen

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

### Haeufige Probleme

#### Problem: Pod im CrashLoopBackOff-Zustand

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

#### Problem: Keine Verbindung zur Datenbank moeglich

```bash
# Test database connectivity from pod
kubectl exec -it openprodoc-core-engine-xxx -- bash
pg_isready -h openprodoc-postgresql -p 5432 -U user1

# Check service
kubectl get svc openprodoc-postgresql

# Check network policies
kubectl get networkpolicies
```

#### Problem: PVC wird nicht gebunden

```bash
# Check PVC status
kubectl get pvc

# Check storage classes
kubectl get storageclass

# Describe PVC for events
kubectl describe pvc openprodoc-storage
```

### Skalierung

```bash
# Scale using kubectl
kubectl scale deployment openprodoc-core-engine --replicas=3

# Scale using Helm upgrade
helm upgrade openprodoc ./helm/openprodoc \
  --set coreEngine.replicaCount=3
```



---

## Bewertete Sicherheitspraktiken

### 1. Standardpasswoerter aendern

```bash
# Use Kubernetes secrets
kubectl create secret generic openprodoc-secrets \
  --from-literal=db-password='StrongPassword123!' \
  --from-literal=root-password='AdminPassword456!' \
  --from-literal=main-key='EncryptionKey32CharsHere12345'
```

### 2. Spezifische Image-Tags verwenden

```yaml
coreEngine:
  image:
    tag: "1.0.0"  # NOT "latest"
```

### 3. TLS fuer Ingress aktivieren

```yaml
ingress:
  enabled: true
  tls:
    - secretName: openprodoc-tls
      hosts:
        - openprodoc.yourdomain.com
```

### 4. Ressourcenlimits festlegen

```yaml
coreEngine:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### 5. Nicht-Root-Benutzer verwenden

```yaml
coreEngine:
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
```
