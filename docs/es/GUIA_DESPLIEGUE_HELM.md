# Guia de Despliegue con Helm Chart de OpenProdoc

## Descripcion general

Esta guia cubre el despliegue del sistema de gestion de contenido empresarial OpenProdoc usando Helm en Kubernetes (K3s, K3d o cualquier cluster de Kubernetes).


**Chart Version**: 1.0.0
**App Version**: 3.0.4

---

## Requisitos previos

### Herramientas necesarias

- **Cluster de Kubernetes** (K3s, K3d, minikube o proveedor en la nube)
- **kubectl** - CLI de Kubernetes
- **Helm 3.x** - Gestor de paquetes para Kubernetes
- **Docker** (opcional) - Solo necesario para importar imagenes en K3d

### Base de datos requerida

- **Base de datos Postgres** Se requiere una instancia de Postgres para el despliegue de la base de datos de openprodoc
- **Instancia de base de datos** La base de datos Postgres debe contener una base de datos para el despliegue de openprodoc
- **Usuario administrador de base de datos** La base de datos Postgres debe contener un usuario con permisos de administrador para la base de datos definida de openprodoc

### Verificar requisitos previos

```bash
# Check Kubernetes cluster
kubectl cluster-info
kubectl get nodes

# Check Helm version
helm version

```


---

## Metodos de instalacion

OpenProdoc se puede desplegar usando tres metodos:

1. **Repositorio Helm** (Recomendado) - Instalar desde el repositorio publico de Helm
2. **Chart local** - Usar charts de este repositorio
3. **Paquete TGZ** - Descargar e instalar el chart empaquetado

---

## Inicio rapido (Desarrollo)

### Metodo 1: Instalar desde el repositorio Helm (Recomendado)

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

### Metodo 2: Instalar desde chart local

### 1. Desplegar la base de datos PostgreSQL

OpenProdoc requiere PostgreSQL. Desplieguelo primero:

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

### 2. Desplegar OpenProdoc

```bash
# Navigate to helm chart directory

# Install OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --namespace default \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

```

### Metodo 3: Instalar desde paquete TGZ

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

**Ventajas del metodo TGZ**:
- No es necesario agregar el repositorio Helm
- Funciona en entornos sin conexion a internet (air-gapped)
- Facil de versionar y archivar
- Se puede almacenar en repositorios de artefactos

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

Para acceder de forma remota, configure los parametros de ingress en values.yaml antes de desplegar.
---

## Configuracion

### Estructura de values.yaml

El chart utiliza una configuracion jerarquica:

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

### Despliegue con Docker Compose

Docker Compose proporciona una alternativa mas sencilla a Kubernetes para desarrollo local y despliegues en un solo servidor. El archivo `docker/docker-compose.yml` despliega la solucion completa con todos los componentes.

#### Servicios desplegados

| Servicio | Imagen | Puerto del host | Descripcion |
|---|---|---|---|
| `postgres` | postgres:16-alpine | 5432 | Base de datos de OpenProdoc |
| `core-engine` | openprodoc/core-engine:latest | **8081** | Backend + interfaz web de OpenProdoc |
| `pgvector` | pgvector/pgvector:pg16 | (interno) | Base de datos vectorial para RAG |
| `ollama` | ollama/ollama:0.5.4 | (interno) | Motor de LLM y embeddings |
| `ollama-pull-models` | curlimages/curl | - | Descargador de modelos (ejecucion unica) |
| `openwebui` | ghcr.io/open-webui/open-webui:main | **8080** | Interfaz RAG |
| `watcher` | openprodoc/openprodoc_rag:1.0.1 | (interno) | Sincronizacion de documentos/usuarios/grupos |

#### Inicio rapido con Docker Compose

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

#### Detencion y limpieza

```bash
# Stop all services (preserves data)
docker compose stop

# Stop and remove containers (preserves volumes)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

#### Imagenes en Docker Hub

Las imagenes estan disponibles en:
- `openprodoc/core-engine` - OpenProdoc Core Engine
- `openprodoc/openprodoc_rag` - RAG Watcher sidecar

**Descargar imagenes manualmente**:
```bash
docker pull openprodoc/core-engine:latest
docker pull openprodoc/openprodoc_rag:1.0.1
```

#### Diferencias clave: Docker Compose vs Kubernetes

| Caracteristica | Docker Compose | Kubernetes (Helm) |
|---|---|---|
| Despliegue del watcher | Contenedor separado | Sidecar en el pod de OpenWebUI |
| Escalado | Instancia unica | Multi-replica con alta disponibilidad |
| Secretos | Variables de entorno en texto plano | Kubernetes Secrets |
| Descubrimiento de servicios | DNS de Docker | Kubernetes Services |
| Almacenamiento | Volumenes de Docker | PersistentVolumeClaims |
| Comprobaciones de salud | Docker healthcheck | Liveness/readiness probes |
| Contenedores de inicio | Servicio de ejecucion unica | Init containers nativos |
| Ingress | Mapeo de puertos | Traefik/nginx ingress |

---

## Escenarios de despliegue

### Escenario 1: Desarrollo local con K3d (Usando repositorio Helm)


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


### Escenario 2: Despliegue en produccion (Usando repositorio Helm)

Consulte la guia de despliegue en produccion para mas detalles.

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

**Alternativa: Usando paquete TGZ para entornos sin conexion (air-gapped)**
```bash
# Download chart TGZ
helm pull openprodoc/openprodoc --version 1.0.0

# Deploy from TGZ
helm install openprodoc openprodoc-1.0.0.tgz \
  --namespace production \
  -f values-production.yaml
```

### Escenario 3: Clase de almacenamiento personalizada

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


### Escenario 4: Nodo unico (Recursos minimos)

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

## Referencia de comandos Helm

### Gestion de repositorios

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

### Instalacion

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

### Desinstalacion

```bash
# Uninstall release
helm uninstall openprodoc

# Uninstall and delete persistent volumes
helm uninstall openprodoc
kubectl delete pvc openprodoc-storage
```



## Ejemplos de personalizacion

### Ejemplo 1: values.yaml personalizado

Cree `my-values.yaml`:

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

Despliegue con:
```bash
# From Helm repository
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# Or from local chart
helm install openprodoc ./helm/openprodoc -f my-values.yaml
```


---

## Solucion de problemas

### Verificar estado de los pods

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

### Problemas comunes

#### Problema: Pod en CrashLoopBackOff

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

#### Problema: No se puede conectar a la base de datos

```bash
# Test database connectivity from pod
kubectl exec -it openprodoc-core-engine-xxx -- bash
pg_isready -h openprodoc-postgresql -p 5432 -U user1

# Check service
kubectl get svc openprodoc-postgresql

# Check network policies
kubectl get networkpolicies
```

#### Problema: PVC no se vincula

```bash
# Check PVC status
kubectl get pvc

# Check storage classes
kubectl get storageclass

# Describe PVC for events
kubectl describe pvc openprodoc-storage
```

### Escalado

```bash
# Scale using kubectl
kubectl scale deployment openprodoc-core-engine --replicas=3

# Scale using Helm upgrade
helm upgrade openprodoc ./helm/openprodoc \
  --set coreEngine.replicaCount=3
```



---

## Mejores practicas de seguridad

### 1. Cambiar las contrasenas predeterminadas

```bash
# Use Kubernetes secrets
kubectl create secret generic openprodoc-secrets \
  --from-literal=db-password='StrongPassword123!' \
  --from-literal=root-password='AdminPassword456!' \
  --from-literal=main-key='EncryptionKey32CharsHere12345'
```

### 2. Usar etiquetas de imagen especificas

```yaml
coreEngine:
  image:
    tag: "1.0.0"  # NOT "latest"
```

### 3. Habilitar TLS para ingress

```yaml
ingress:
  enabled: true
  tls:
    - secretName: openprodoc-tls
      hosts:
        - openprodoc.yourdomain.com
```

### 4. Limites de recursos

```yaml
coreEngine:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### 5. Usuario no root

```yaml
coreEngine:
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
```
