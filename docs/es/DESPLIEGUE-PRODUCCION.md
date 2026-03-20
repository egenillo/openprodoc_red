# Guia de despliegue en produccion de OpenProdoc

Esta guia proporciona instrucciones paso a paso para desplegar OpenProdoc en entornos de produccion.

## Opciones de despliegue

| Metodo | Recomendado para |
|---|---|
| **Docker Compose** | Despliegues en un solo servidor, equipos pequenos |
| **Kubernetes (Helm)** | Clusters multi-nodo, alta disponibilidad, entornos empresariales |

## Requisitos previos

### Para Kubernetes (Helm)

- Cluster de Kubernetes 1.19+ (probado en 1.24+)
- Helm 3.2.0+
- kubectl configurado con acceso al cluster
- Storage class configurada (para PersistentVolumes)
- Ingress controller instalado (Traefik o nginx)
- cert-manager (opcional, para certificados TLS automaticos)
- Registro de contenedores (si se utilizan imagenes privadas)

### Para Docker Compose

- Docker Engine 20.10+ con Docker Compose v2
- Minimo 16GB de RAM (Ollama + modelos LLM consumen mucha memoria)
- 100GB+ de espacio en disco (modelos, documentos, bases de datos)


## Paso 1: Preparar los secretos

Cree una contrasena segura y una clave de cifrado:

```bash
# Generate strong passwords
export OPENPRODOC_ROOT_USER_PASSWORD=$(openssl rand -base64 16)
export ENCRYPTION_KEY=$(openssl rand -base64 32 | cut -c1-32)

echo "Save these credentials securely:"
echo "Openprodocc root user Password: $OPENPRODOC_ADMIN_USER_PASSWORD"
echo "Encryption Key: $ENCRYPTION_KEY"
```

## Paso 2: Crear el archivo de valores para produccion

Edite `production-values.yaml` o `values.yaml`:

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

## Paso 3: Instalar OpenProdoc

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

## Paso 4: Esperar a la instalacion inicial

El core engine instalara automaticamente OpenProdoc en el primer arranque:

```bash
# Watch core engine logs
kubectl logs -f -n openprodoc -l app.kubernetes.io/component=core-engine

# Wait for message: "OpenProdoc installation completed successfully"
```

## Paso 5: Verificar el despliegue

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

## Paso 6: Probar el acceso

### Kubernetes

```bash
# Port forward to access locally
kubectl port-forward svc/openprodoc-core-engine 8081:8080
kubectl port-forward svc/openprodoc-openwebui 8080:8080

# Or if ingress is enabled:
kubectl get ingress -n openprodoc openprodoc -o jsonpath='{.spec.rules[0].host}'
```

### Docker Compose

Los servicios son accesibles directamente:
- **OpenProdoc**: `http://localhost:8081/ProdocWeb2/`
- **Open WebUI**: `http://localhost:8080`

### Credenciales por defecto

- **OpenProdoc**: Usuario: `root` / Contrasena: `admin` (cambiar en produccion)
- **Open WebUI**: El primer usuario en registrarse se convierte en administrador (usar `watcher@openprodoc.local` / `12345678`)

## Lista de verificacion para produccion

- [ ] Todas las contrasenas son seguras y estan almacenadas de forma segura (gestor de contrasenas, sealed secrets, etc.)
- [ ] Las storage classes estan configuradas con las caracteristicas de rendimiento adecuadas (Kubernetes)
- [ ] Los limites de recursos estan establecidos segun la carga esperada
- [ ] Los certificados TLS son validos y se renuevan automaticamente (Kubernetes con ingress)
- [ ] La cuenta de administrador `watcher@openprodoc.local` esta creada en Open WebUI
- [ ] El usuario `watcher` esta creado en OpenProdoc con los permisos ACL de lectura apropiados
- [ ] El token SCIM y la clave secreta de WebUI se han cambiado respecto a los valores por defecto
- [ ] Existe una estrategia de respaldo para los volumenes de PostgreSQL, pgvector y ollama


## Escalado

### Escalado manual (Kubernetes)

```bash
# Scale Core Engine
kubectl scale deployment openprodoc-core-engine -n openprodoc --replicas=3

# Or via Helm
helm upgrade openprodoc openprodoc/openprodoc \
  -f production-values.yaml \
  --set coreEngine.replicaCount=3 \
  --namespace openprodoc
```

Nota: Los despliegues con Docker Compose ejecutan instancias unicas. Para escalado con multiples replicas, utilice Kubernetes.


## Solucion de problemas

### Pod que no arranca (Kubernetes)

```bash
kubectl describe pod <pod-name> -n openprodoc
kubectl logs <pod-name> -n openprodoc
```

### Contenedor que no arranca (Docker Compose)

```bash
docker compose logs <service-name>
docker inspect openprodoc-<service-name>
```

### Problemas de conexion a la base de datos

```bash
# Kubernetes
kubectl exec -it -n openprodoc openprodoc-core-engine-xxx -- \
  nc -zv openprodoc-postgresql 5432

# Docker Compose
docker compose exec core-engine bash -c "nc -zv postgres 5432"
```

### Fallos de autenticacion del watcher

Si los logs del watcher muestran `authentication failed`, asegurese de que el usuario administrador `watcher@openprodoc.local` existe en Open WebUI. Consulte [RAG_SETUP.md](RAG_SETUP.md#step-4-setup-rag-users) para las instrucciones de configuracion.
