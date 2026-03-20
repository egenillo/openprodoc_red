# Guide de deploiement du Helm Chart OpenProdoc

## Presentation

Ce guide couvre le deploiement du systeme de gestion de contenu d'entreprise OpenProdoc en utilisant Helm sur Kubernetes (K3s, K3d ou tout cluster Kubernetes).


**Version du Chart** : 1.0.0
**Version de l'application** : 3.0.4

---

## Prerequis

### Outils requis

- **Cluster Kubernetes** (K3s, K3d, minikube ou fournisseur cloud)
- **kubectl** - CLI Kubernetes
- **Helm 3.x** - Gestionnaire de paquets pour Kubernetes
- **Docker** (optionnel) - Necessaire uniquement pour l'import d'images K3d

### Base de donnees requise

- **Base de donnees Postgres** Une instance Postgres est requise pour le deploiement de la base de donnees openprodoc
- **Instance de base de donnees** La base Postgres doit contenir une base de donnees pour le deploiement d'openprodoc
- **Utilisateur administrateur de la base** La base Postgres doit contenir un utilisateur avec les permissions d'administration pour la base de donnees definie pour openprodoc

### Verification des prerequis

```bash
# Check Kubernetes cluster
kubectl cluster-info
kubectl get nodes

# Check Helm version
helm version

```


---

## Methodes d'installation

OpenProdoc peut etre deploye selon trois methodes :

1. **Depot Helm** (Recommande) - Installation depuis le depot Helm public
2. **Chart local** - Utilisation des charts de ce depot
3. **Paquet TGZ** - Telechargement et installation du chart empaquete

---

## Demarrage rapide (Developpement)

### Methode 1 : Installation depuis le depot Helm (Recommande)

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

### Methode 2 : Installation depuis un chart local

### 1. Deployer la base de donnees PostgreSQL

OpenProdoc necessite PostgreSQL. Deployez-le en premier :

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

### 2. Deployer OpenProdoc

```bash
# Navigate to helm chart directory

# Install OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --namespace default \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

```

### Methode 3 : Installation depuis un paquet TGZ

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

**Avantages de la methode TGZ** :
- Pas besoin d'ajouter un depot Helm
- Fonctionne dans des environnements isoles (air-gapped)
- Facile a versionner et archiver
- Peut etre stocke dans des depots d'artefacts

### 4. Acceder a OpenProdoc

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

Pour un acces distant, configurez les parametres ingress dans values.yaml avant le deploiement.
---

## Configuration

### Structure de values.yaml

Le chart utilise une configuration hierarchique :

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

### Deploiement avec Docker Compose

Docker Compose offre une alternative plus simple a Kubernetes pour le developpement local et les deploiements sur serveur unique. Le fichier `docker/docker-compose.yml` deploie la solution complete avec tous les composants.

#### Services deployes

| Service | Image | Port hote | Description |
|---|---|---|---|
| `postgres` | postgres:16-alpine | 5432 | Base de donnees OpenProdoc |
| `core-engine` | openprodoc/core-engine:latest | **8081** | Backend + interface web OpenProdoc |
| `pgvector` | pgvector/pgvector:pg16 | (interne) | Base de donnees vectorielle pour RAG |
| `ollama` | ollama/ollama:0.5.4 | (interne) | Moteur LLM et d'embeddings |
| `ollama-pull-models` | curlimages/curl | - | Telechargeur de modeles ponctuel |
| `openwebui` | ghcr.io/open-webui/open-webui:main | **8080** | Interface RAG |
| `watcher` | openprodoc/openprodoc_rag:1.0.1 | (interne) | Synchronisation documents/utilisateurs/groupes |

#### Demarrage rapide avec Docker Compose

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

#### Arret et nettoyage

```bash
# Stop all services (preserves data)
docker compose stop

# Stop and remove containers (preserves volumes)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

#### Images Docker Hub

Les images sont disponibles sur :
- `openprodoc/core-engine` - OpenProdoc Core Engine
- `openprodoc/openprodoc_rag` - Sidecar RAG Watcher

**Telecharger les images manuellement** :
```bash
docker pull openprodoc/core-engine:latest
docker pull openprodoc/openprodoc_rag:1.0.1
```

#### Differences cles : Docker Compose vs Kubernetes

| Fonctionnalite | Docker Compose | Kubernetes (Helm) |
|---|---|---|
| Deploiement du Watcher | Conteneur separe | Sidecar dans le pod OpenWebUI |
| Mise a l'echelle | Instance unique | Multi-replicas avec haute disponibilite |
| Secrets | Variables d'environnement en texte clair | Kubernetes Secrets |
| Decouverte de services | DNS Docker | Kubernetes Services |
| Stockage | Volumes Docker | PersistentVolumeClaims |
| Verifications de sante | Docker healthcheck | Sondes liveness/readiness |
| Conteneurs d'initialisation | Service ponctuel | Conteneurs init natifs |
| Ingress | Mappage de ports | Traefik/nginx ingress |

---

## Scenarios de deploiement

### Scenario 1 : Developpement local K3d (avec depot Helm)


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


### Scenario 2 : Deploiement en production (avec depot Helm)

Consultez le guide de deploiement en production pour plus de details.

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

**Alternative : Utilisation d'un paquet TGZ pour un environnement isole**
```bash
# Download chart TGZ
helm pull openprodoc/openprodoc --version 1.0.0

# Deploy from TGZ
helm install openprodoc openprodoc-1.0.0.tgz \
  --namespace production \
  -f values-production.yaml
```

### Scenario 3 : Classe de stockage personnalisee

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


### Scenario 4 : Noeud unique (ressources minimales)

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

## Reference des commandes Helm

### Gestion du depot

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

### Desinstallation

```bash
# Uninstall release
helm uninstall openprodoc

# Uninstall and delete persistent volumes
helm uninstall openprodoc
kubectl delete pvc openprodoc-storage
```



## Exemples de personnalisation

### Exemple 1 : Fichier values.yaml personnalise

Creez un fichier `my-values.yaml` :

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

Deployez avec :
```bash
# From Helm repository
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# Or from local chart
helm install openprodoc ./helm/openprodoc -f my-values.yaml
```


---

## Depannage

### Verifier l'etat des pods

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

### Problemes courants

#### Probleme : Pod en CrashLoopBackOff

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

#### Probleme : Impossible de se connecter a la base de donnees

```bash
# Test database connectivity from pod
kubectl exec -it openprodoc-core-engine-xxx -- bash
pg_isready -h openprodoc-postgresql -p 5432 -U user1

# Check service
kubectl get svc openprodoc-postgresql

# Check network policies
kubectl get networkpolicies
```

#### Probleme : PVC non lie

```bash
# Check PVC status
kubectl get pvc

# Check storage classes
kubectl get storageclass

# Describe PVC for events
kubectl describe pvc openprodoc-storage
```

### Mise a l'echelle

```bash
# Scale using kubectl
kubectl scale deployment openprodoc-core-engine --replicas=3

# Scale using Helm upgrade
helm upgrade openprodoc ./helm/openprodoc \
  --set coreEngine.replicaCount=3
```



---

## Bonnes pratiques de securite

### 1. Modifier les mots de passe par defaut

```bash
# Use Kubernetes secrets
kubectl create secret generic openprodoc-secrets \
  --from-literal=db-password='StrongPassword123!' \
  --from-literal=root-password='AdminPassword456!' \
  --from-literal=main-key='EncryptionKey32CharsHere12345'
```

### 2. Utiliser des tags d'image specifiques

```yaml
coreEngine:
  image:
    tag: "1.0.0"  # NOT "latest"
```

### 3. Activer TLS pour l'ingress

```yaml
ingress:
  enabled: true
  tls:
    - secretName: openprodoc-tls
      hosts:
        - openprodoc.yourdomain.com
```

### 4. Limites de ressources

```yaml
coreEngine:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### 5. Utilisateur non-root

```yaml
coreEngine:
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
```
