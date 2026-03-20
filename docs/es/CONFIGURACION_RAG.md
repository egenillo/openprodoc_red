# Guia de configuracion de la solucion RAG de OpenProdoc

Esta guia explica como desplegar y utilizar la solucion integrada de RAG (Retrieval-Augmented Generation) con OpenProdoc.

## Descripcion general

La solucion RAG extiende OpenProdoc con capacidades de busqueda de documentos y respuesta a preguntas potenciadas por IA. Consta de los siguientes componentes principales:

1. **PGVector** - PostgreSQL con extension vectorial para almacenar embeddings de documentos
2. **Ollama** - Motor de LLM y embeddings ejecutandose en CPU
3. **Open WebUI** - Interfaz de usuario y orquestador RAG
4. **RAG CustomTask** - Manejadores de eventos nativos de OpenProdoc que sincronizan automaticamente documentos, carpetas, usuarios y grupos con Open WebUI

## Arquitectura

```
┌──────────────────────────────┐
│  OpenProdoc Core Engine      │
│  ┌────────────────────────┐  │
│  │  RAG CustomTask (JAR)  │  │
│  │  • Doc events (INS/UPD/DEL)
│  │  • Folder events       │  │
│  │  • User/Group sync     │  │
│  └───────────┬────────────┘  │
└──────────────┼───────────────┘
               │ HTTP API calls
               ▼
        ┌─────────────┐
        │  Open WebUI  │
        │  (RAG UI)    │
        └──────┬───────┘
               │
       ┌───────┴───────┐
       ▼               ▼
 ┌──────────┐    ┌──────────┐
 │  Ollama  │    │ PGVector │
 │  (LLM)   │    │ (Vectors)│
 └──────────┘    └──────────┘
```

El CustomTask se ejecuta dentro de la JVM de OpenProdoc — no se necesita ningun sidecar externo ni contenedor de sondeo. Los eventos de documentos y carpetas activan llamadas HTTP API a Open WebUI en tiempo real, y una tarea cron sincroniza usuarios y grupos cada 5 minutos mediante SCIM.

## Componentes

### 1. PGVector (Base de datos vectorial)

- **Imagen**: `pgvector/pgvector:pg16`
- **Proposito**: Almacena embeddings de documentos para busqueda semantica
- **Almacenamiento**: 20Gi por defecto (configurable)
- **Recursos**: 250m CPU, 512Mi RAM (solicitudes)

### 2. Ollama (Motor LLM)

- **Imagen**: `ollama/ollama:0.18.2`
- **Modelos**:
  - LLM: `llama3.1:latest` (o `phi3` para menor uso de recursos)
  - Embeddings: `nomic-embed-text:latest` (ligero, optimizado para CPU)
- **Almacenamiento**: 50Gi para modelos
- **Recursos**: 2-4 nucleos de CPU, 4-8Gi RAM

### 3. Open WebUI (Interfaz RAG)

- **Imagen**: `ghcr.io/open-webui/open-webui:main`
- **Caracteristicas**:
  - Interfaz de chat para consultar documentos
  - Ingesta automatica de documentos desde el almacenamiento de OpenProdoc
  - Procesamiento RAG con tamano de fragmento configurable
- **Almacenamiento**: 5Gi para metadatos
- **Recursos**: 500m-2000m CPU, 1-4Gi RAM

### 4. RAG CustomTask

- **Artefacto**: `openprodoc-ragtask.jar` (subido a OpenProdoc como documento)
- **Proposito**: Integracion basada en eventos que sincroniza automaticamente documentos, carpetas, usuarios y grupos de OpenProdoc a Open WebUI
- **Despliegue**: Se ejecuta dentro de la JVM de OpenProdoc — no requiere contenedor separado
- **Tareas**:
  - `RAGEventDoc` — reacciona a eventos de documento INSERT/UPDATE/DELETE
  - `RAGEventFold` — reacciona a eventos de carpeta INSERT/UPDATE/DELETE
  - `RAGSyncCron` — sincroniza usuarios y grupos con Open WebUI cada 5 minutos mediante SCIM
- **Formatos soportados**: pdf, doc, docx, txt, md, rtf, html, json, csv, xml, odt
- **Recursos**: Cero recursos adicionales (se ejecuta dentro de la JVM del core-engine)

## Despliegue

### Opcion A: Docker Compose (Recomendado para desarrollo)

La forma mas sencilla de desplegar la solucion RAG completa:

```bash
cd docker/

# Iniciar todos los servicios
docker compose up -d

# Monitorear el arranque (la descarga de modelos de Ollama puede tardar varios minutos)
docker compose logs -f

# Acceso:
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# Open WebUI:  http://localhost:8080
```

El archivo docker-compose.yml despliega todos los servicios con el orden de arranque correcto y health checks. Un contenedor de ejecucion unica `rag-init` sube automaticamente el JAR del CustomTask, crea las definiciones de tareas de eventos/cron y aprovisiona la cuenta de administracion watcher en Open WebUI.

**Nota:** En el primer arranque, el contenedor `ollama-pull-models` descarga el modelo LLM (~4-5 GB) y el modelo de embeddings. Esto puede tardar varios minutos dependiendo de su conexion a internet. Puede monitorear el progreso con `docker logs -f openprodoc-model-puller`. Una vez completada la descarga, los modelos apareceran en Open WebUI y estaran disponibles para su seleccion.

#### Configuracion de modelos

Los modelos de LLM y embeddings son configurables mediante variables de entorno:

| Variable | Valor por defecto | Descripcion |
|---|---|---|
| `LLM_MODEL` | `llama3.1:latest` | Modelo LLM para chat |
| `EMBEDDING_MODEL` | `nomic-embed-text:latest` | Modelo de embeddings para RAG |

Puede sobreescribirlos de varias formas:

**En linea:**
```bash
LLM_MODEL=phi3 EMBEDDING_MODEL=nomic-embed-text:latest docker compose up -d
```

**Con un archivo `.env`** en la carpeta `docker/`:
```
LLM_MODEL=phi3
EMBEDDING_MODEL=nomic-embed-text:latest
```

**Exportacion:**
```bash
export LLM_MODEL=phi3
docker compose up -d
```

Si no se configuran, se usan los valores por defecto (`llama3.1:latest` y `nomic-embed-text:latest`).

#### Soporte de GPU para Ollama

Ollama puede utilizar una GPU para acelerar significativamente la inferencia del LLM. Se proporcionan scripts de inicio que detectan automaticamente la disponibilidad de GPU y aplican la configuracion correcta de Docker Compose:

| Plataforma | Script | Soporte de GPU |
|---|---|---|
| Linux | `./start-linux.sh` | NVIDIA y AMD (deteccion automatica) |
| Windows | `start-windows.bat` | Solo NVIDIA |
| macOS | No necesario — use `docker compose up -d` directamente | Ninguno (Docker Desktop se ejecuta en una VM, sin passthrough de GPU) |

**Linux:**

```bash
cd docker/
chmod +x start-linux.sh
./start-linux.sh
```

El script detecta GPUs NVIDIA mediante `nvidia-smi` y GPUs AMD mediante `/dev/kfd`, y luego lanza Docker Compose con el archivo de sobreescritura apropiado (`docker-compose.nvidia.yml` o `docker-compose.amd.yml`). Si no se encuentra ninguna GPU, inicia en modo solo CPU.

**Requisitos previos para el uso de GPU:**
- **NVIDIA**: Los drivers de NVIDIA y el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) deben estar instalados en el host. Compatible con Linux y Windows.
- **AMD**: Se requieren GPU y drivers compatibles con ROCm. **Solo Linux** — la imagen Docker `ollama/ollama:0.18.2-rocm` esta disenada especificamente para sistemas Linux con GPUs AMD y no es compatible con Windows ni macOS.

**Windows:**

```cmd
cd docker
start-windows.bat
```

El script verifica la presencia de GPUs NVIDIA mediante `nvidia-smi`. En Windows, el passthrough de GPU en Docker Desktop solo esta oficialmente soportado para GPUs NVIDIA usando el backend WSL2. No existe una imagen Docker especializada para aceleracion ROCm en Windows.

**Windows con GPU AMD:** Si tiene una GPU AMD Radeon en Windows, el enfoque recomendado es instalar Ollama de forma nativa en lugar de usar Docker:

1. Descargue `OllamaSetup.exe` desde el [sitio web oficial de Ollama](https://ollama.com/download)
2. Asegurese de tener los drivers AMD mas recientes instalados
3. Ollama detectara automaticamente su tarjeta Radeon compatible
4. Configure la variable `OLLAMA_BASE_URL` en el servicio `openwebui` de Docker Compose para que apunte a su instancia nativa de Ollama (por ejemplo, `http://host.docker.internal:11434`) en lugar de la contenedorizada

**macOS:**

No se necesita script de inicio. Docker Desktop para Mac ejecuta los contenedores dentro de una VM Linux, por lo que ni las GPUs NVIDIA, AMD ni Apple Silicon son accesibles desde los contenedores. Simplemente ejecute:

```bash
cd docker/
docker compose up -d
```

#### Detencion y persistencia de datos

**Importante:** Tenga cuidado con la opcion `-v` al detener los servicios:

| Comando | Efecto |
|---|---|
| `docker compose stop` | Detiene los contenedores. Sin perdida de datos. |
| `docker compose down` | Detiene y elimina contenedores y redes. **Los volumenes (datos) se preservan.** |
| `docker compose down -v` | Detiene y elimina contenedores, redes **y todos los volumenes. Se pierden todos los datos.** |

Usar `docker compose down -v` destruye los siguientes volumenes con nombre y todos sus datos:

- **`postgres-data`** — Base de datos de OpenProdoc (metadatos de documentos, usuarios, configuracion)
- **`openprodoc-storage`** — Archivos de documentos almacenados en el sistema de archivos
- **`pgvector-data`** — Embeddings vectoriales de RAG
- **`ollama-data`** — Modelos LLM descargados (~4-5 GB)
- **`openwebui-data`** — Configuracion de Open WebUI y cuentas de usuario

Use `docker compose down` (sin `-v`) para detener todo de forma segura manteniendo sus datos intactos.

### Opcion B: Kubernetes (Helm)

#### Paso 1: Configurar valores

Edite `values.yaml` para habilitar y configurar los componentes RAG:

```yaml
# Enable RAG components
pgvector:
  enabled: true

ollama:
  enabled: true
  config:
    models:
      llm: "llama3.1:latest"  # or "phi3" for smaller deployments
      embedding: "nomic-embed-text:latest"

openwebui:
  enabled: true

ragInit:
  enabled: true
```

#### Paso 2: Ajustar limites de recursos

Para despliegues en produccion, ajuste los recursos segun la capacidad de su cluster:

```yaml
ollama:
  resources:
    limits:
      cpu: 4000m      # 4 cores recommended
      memory: 8Gi
    requests:
      cpu: 2000m
      memory: 4Gi

openwebui:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 1Gi
```

#### Paso 3: Desplegar

```bash
# Install or upgrade the Helm chart
helm upgrade --install openprodoc ./helm/openprodoc \
  --namespace openprodoc \
  --create-namespace

# Monitor the deployment
kubectl get pods -n openprodoc -w
```

### Paso 4: Inicializacion de RAG

El contenedor de ejecucion unica `rag-init` (Docker Compose) o Job de Kubernetes (Helm) se ejecuta automaticamente despues del despliegue y se encarga de:

1. **Cuenta de administracion watcher** — Crea `watcher@openprodoc.local` en Open WebUI con privilegios de administrador. Esta cuenta es utilizada por el CustomTask para gestionar knowledge bases, archivos, usuarios y grupos.
2. **Subida del JAR** — Sube `openprodoc-ragtask.jar` a OpenProdoc mediante la API REST.
3. **Definiciones de tareas** — Inserta tareas de eventos (INSERT/UPDATE/DELETE de documentos y carpetas) y una tarea cron (sincronizacion de usuarios/grupos cada 5 minutos) en la base de datos de OpenProdoc.

La inicializacion es **idempotente** — si las tareas ya existen, finaliza inmediatamente sin realizar cambios. Esto permite re-ejecuciones seguras en `helm upgrade` o `docker compose up`.

Despues del despliegue, puede iniciar sesion en Open WebUI con las credenciales predeterminadas del administrador watcher:

- **Email**: `watcher@openprodoc.local`
- **Contrasena**: `12345678`

Estas credenciales son configurables mediante `OPENWEBUI_ADMIN_EMAIL` / `OPENWEBUI_ADMIN_PASSWORD` en Docker Compose, o `ragInit.config.watcherEmail` / `ragInit.config.watcherPassword` en los valores de Helm. Cambielas para despliegues en produccion.

#### Sincronizacion automatica de usuarios y grupos

Una vez inicializada, la tarea `RAGSyncCron` automaticamente:
- **Replica los usuarios de OpenProdoc** en Open WebUI (cada 5 minutos)
- **Replica los grupos de OpenProdoc** en Open WebUI mediante la API SCIM
- **Asigna usuarios a grupos** que coincidan con sus membresías de grupos en OpenProdoc

Esto significa que los usuarios de OpenProdoc pueden iniciar sesion en Open WebUI sin necesidad de registro separado.

### Paso 5: Verificar el despliegue

#### Docker Compose

```bash
# Check all services are running
docker compose ps

# Expected: all services "Up" or "Up (healthy)"

# Check Ollama models are downloaded
docker compose logs ollama-pull-models

# Check rag-init completed successfully
docker compose logs rag-init

# Test access
curl -s http://localhost:8081/ProdocWeb2/ | head -5   # OpenProdoc
curl -s http://localhost:8080/health                    # Open WebUI
```

#### Kubernetes

```bash
# Check all pods are running
kubectl get pods -n openprodoc

# Expected output should show:
# - openprodoc-core-engine-xxx (Running)
# - openprodoc-pgvector-xxx (Running)
# - openprodoc-ollama-xxx (Running)
# - openprodoc-openwebui-xxx (Running)

# Check rag-init job completed
kubectl get jobs -n openprodoc
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init

# Check Ollama models are downloaded
kubectl logs -n openprodoc -l app.kubernetes.io/component=ollama -c pull-models
```

### Paso 6: Autenticacion de usuarios y organizacion de Knowledge Bases

**Replicacion automatica de usuarios**: Todos los usuarios y grupos de OpenProdoc se replican automaticamente en el entorno de OpenWebUI. Esto significa:

- **Inicio de sesion transparente**: Los usuarios de OpenProdoc pueden iniciar sesion automaticamente en OpenWebUI sin ninguna configuracion ni registro adicional
- **Single Sign-On**: Las credenciales de usuario se sincronizan entre OpenProdoc y OpenWebUI
- **Membresia de grupos**: Las asociaciones de grupos de usuario se mantienen en ambos sistemas

**Control de acceso basado en permisos**:

Cada usuario en OpenWebUI tendra acceso a knowledge bases segun sus permisos en OpenProdoc:

- Los usuarios solo pueden acceder a knowledge bases de documentos para los que tienen permisos en OpenProdoc
- El control de acceso se aplica a nivel de knowledge base
- Los permisos se heredan del sistema ACL de OpenProdoc

**Organizacion de Knowledge Bases**:

El sistema RAG crea un mapeo uno a uno entre las carpetas de OpenProdoc y las knowledge bases de OpenWebUI:

- **Cada carpeta en OpenProdoc genera una knowledge base separada en OpenWebUI**
- Cada knowledge base contiene el conocimiento indexado de todos los documentos dentro de su carpeta correspondiente en OpenProdoc
- Los usuarios solo veran las knowledge bases de las carpetas a las que tienen acceso
- Esta organizacion basada en carpetas facilita la gestion y consulta de colecciones de documentos especificas por dominio

**Ejemplo**:

```
OpenProdoc Structure:
├── Engineering/          → Knowledge Base: "Engineering"
│   ├── specs.pdf
│   └── designs.doc
├── Marketing/            → Knowledge Base: "Marketing"
│   ├── campaigns.pptx
│   └── analytics.xlsx
└── HR/                   → Knowledge Base: "HR"
    ├── policies.pdf
    └── handbook.doc

User with access to "Engineering" and "Marketing" folders:
- Can log in to OpenWebUI automatically
- Sees 2 knowledge bases: "Engineering" and "Marketing"
- Cannot see or access "HR" knowledge base
```

Esta arquitectura garantiza que las politicas de seguridad documental y control de acceso definidas en OpenProdoc se apliquen de forma transparente en el sistema RAG.

## Uso

### Acceso a los servicios

#### Docker Compose

| Servicio | URL | Puerto del host | Puerto del contenedor |
|---|---|---|---|
| OpenProdoc | `http://localhost:8081/ProdocWeb2/` | 8081 | 8080 |
| OpenProdoc REST API | `http://localhost:8081/ProdocWeb2/APIRest/` | 8081 | 8080 |
| Open WebUI (RAG) | `http://localhost:8082` | 8082 | 8080 |
| PostgreSQL | `localhost:5433` | 5433 | 5432 |

#### Kubernetes

Si ingress esta habilitado, acceda a Open WebUI en `http://localhost/rag` y a OpenProdoc en `http://localhost/`.

Si ingress esta deshabilitado, use port-forwarding:

```bash
kubectl port-forward svc/openprodoc-openwebui 8080:8080
kubectl port-forward svc/openprodoc-core-engine 8081:8080
```

### Consulta de Knowledge Bases

Para usar una Knowledge Base en una conversacion de chat en Open WebUI:

1. Abra un nuevo chat en Open WebUI
2. En el campo de mensaje, escriba **`#`** — aparecera un desplegable listando las Knowledge Bases disponibles
3. Seleccione la Knowledge Base deseada (por ejemplo, `folder1`)
4. Escriba su pregunta y envie — el LLM usara RAG para buscar en la Knowledge Base seleccionada al generar su respuesta

Puede adjuntar multiples Knowledge Bases a una sola conversacion escribiendo `#` nuevamente y seleccionando Knowledge Bases adicionales.

### Como funciona

1. **Subida de documentos**: Cuando un documento se inserta o actualiza en OpenProdoc, se activa el CustomTask `RAGEventDoc`
2. **Ingesta**: El CustomTask sube el documento a la API de Open WebUI y lo agrega a la Knowledge Base correspondiente
3. **Procesamiento**: Open WebUI:
   - Divide los documentos en fragmentos (por defecto: 1500 caracteres con 100 caracteres de solapamiento)
   - Genera embeddings usando el modelo `nomic-embed-text` de Ollama
   - Almacena los embeddings en la base de datos PGVector
4. **Consulta**: Los usuarios hacen preguntas a traves de la interfaz de chat
5. **Recuperacion**: Open WebUI:
   - Genera el embedding de la consulta
   - Busca en PGVector los fragmentos relevantes
   - Proporciona contexto al LLM
6. **Respuesta**: Ollama genera una respuesta basada en el contexto recuperado

### Tipos de documentos soportados

El CustomTask procesa automaticamente estos tipos de archivo:
- Texto: `.txt`, `.md`, `.rst`, `.rtf`
- Documentos: `.pdf`, `.doc`, `.docx`
- Web: `.html`, `.htm`
- Datos: `.json`, `.csv`, `.xml`

## Opciones de configuracion

### Cambiar modelos LLM

Para mejor rendimiento en clusters con recursos limitados, use Phi-3:

```yaml
ollama:
  config:
    models:
      llm: "phi3"  # Smaller, faster than llama3:8b
```

### Ajustar parametros RAG

```yaml
openwebui:
  config:
    rag:
      enabled: true
      chunkSize: 1500      # Size of document chunks
      chunkOverlap: 100    # Overlap between chunks
```

### Configuracion de almacenamiento

```yaml
pgvector:
  persistence:
    size: 20Gi  # Adjust based on expected document volume

ollama:
  persistence:
    size: 50Gi  # Models require ~10-20GB per model

openwebui:
  persistence:
    size: 5Gi   # Metadata and configuration
```

## Solucion de problemas

### Los modelos de Ollama no se descargan

Verifique los logs del contenedor de inicializacion:

```bash
kubectl logs -n openprodoc <ollama-pod> -c pull-models
```

Los modelos son grandes (4-8GB cada uno) y pueden tardar en descargarse.

### Los documentos no aparecen en Open WebUI

Verifique que rag-init se completo exitosamente:

```bash
# Docker Compose
docker compose logs rag-init

# Kubernetes
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init
```

Asegurese de que:
1. El contenedor/job `rag-init` se completo sin errores
2. La cuenta de administracion `watcher@openprodoc.local` existe en Open WebUI
3. El JAR del CustomTask fue subido (verifique la carpeta System de OpenProdoc)
4. Las tareas de eventos estan activas (verifique en OpenProdoc Admin → Task Management)
5. Open WebUI es accesible desde el core-engine en la URL configurada
6. El tipo MIME del documento esta en la lista de formatos soportados

### Problemas de conexion con PGVector

Verifique el pod de pgvector:

```bash
kubectl logs -n openprodoc <pgvector-pod>
kubectl exec -it -n openprodoc <pgvector-pod> -- psql -U rag_user -d rag_vectors
```

Verifique la extension vectorial:

```sql
\dx  -- Should show 'vector' extension
```

### Alto uso de recursos

Para entornos con restricciones de CPU:

1. Cambie a modelos mas pequenos:
   ```yaml
   ollama:
     config:
       models:
         llm: "phi3"  # Instead of llama3:8b
   ```

2. Reduzca los limites de recursos:
   ```yaml
   ollama:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. Deshabilite la inicializacion del CustomTask y use la subida manual de documentos:
   ```yaml
   ragInit:
     enabled: false
   ```

## Deshabilitar componentes RAG

Para deshabilitar la solucion RAG completamente:

```yaml
pgvector:
  enabled: false

ollama:
  enabled: false

openwebui:
  enabled: false
```

## Consideraciones de seguridad

1. **Secretos**: La contrasena de PGVector se almacena en un secret de Kubernetes. Cambie la contrasena predeterminada:
   ```yaml
   pgvector:
     config:
       password: "your-secure-password"
   ```

2. **Network Policies**: Considere implementar network policies para restringir la comunicacion entre pods

3. **Autenticacion de API**: Configure la autenticacion de Open WebUI en produccion. Despues de que rag-init se complete, considere establecer `ENABLE_SIGNUP=false` y `DEFAULT_USER_ROLE=user` para evitar cuentas de administrador no autorizadas.

## Ajuste de rendimiento

### Para despliegues de alto volumen

1. **Aumentar el paralelismo de Ollama**:
   ```yaml
   # Set via environment in ollama deployment
   OLLAMA_NUM_PARALLEL: "8"
   ```

2. **Escalar PGVector**:
   ```yaml
   pgvector:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. **Habilitar cache**: Ollama mantiene los modelos en memoria segun `OLLAMA_KEEP_ALIVE`

### Para despliegues con recursos limitados

1. Use el modelo Phi-3 (mas pequeno y rapido)
2. Reduzca el tamano de fragmento para procesar menos embeddings
3. Deshabilite `ragInit` y use la subida manual de documentos mediante Open WebUI

## Monitoreo

Monitoree los componentes RAG:

```bash
# Resource usage
kubectl top pods -n openprodoc

# Service status
kubectl get svc -n openprodoc

# Logs
kubectl logs -n openprodoc -l app.kubernetes.io/part-of=openprodoc --tail=100
```

## Lectura adicional

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Ollama Model Library](https://ollama.com/library)
- [PGVector Documentation](https://github.com/pgvector/pgvector)
