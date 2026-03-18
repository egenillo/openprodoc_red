# OpenProdoc RAG Solution Setup Guide

This guide explains how to deploy and use the integrated RAG (Retrieval-Augmented Generation) solution with OpenProdoc.

## Overview

The RAG solution extends OpenProdoc with AI-powered document search and question-answering capabilities. It consists of these main components:

1. **PGVector** - PostgreSQL with vector extension for storing document embeddings
2. **Ollama** - LLM and embedding engine running on CPU
3. **Open WebUI** - User interface and RAG orchestrator
4. **RAG CustomTask** - Native OpenProdoc event handlers that automatically sync documents, folders, users, and groups to Open WebUI

## Architecture

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

The CustomTask runs inside the OpenProdoc JVM — no external sidecar or polling container is needed. Document and folder events trigger HTTP API calls to Open WebUI in real time, and a cron task syncs users and groups every 5 minutes via SCIM.

## Components

### 1. PGVector (Vector Database)

- **Image**: `pgvector/pgvector:pg16`
- **Purpose**: Stores document embeddings for semantic search
- **Storage**: 20Gi by default (configurable)
- **Resources**: 250m CPU, 512Mi RAM (requests)

### 2. Ollama (LLM Engine)

- **Image**: `ollama/ollama:0.5.4`
- **Models**:
  - LLM: `llama3.1:latest` (or `phi3` for lower resource usage)
  - Embeddings: `nomic-embed-text:latest` (lightweight, CPU-optimized)
- **Storage**: 50Gi for models
- **Resources**: 2-4 CPU cores, 4-8Gi RAM

### 3. Open WebUI (RAG Interface)

- **Image**: `ghcr.io/open-webui/open-webui:main`
- **Features**:
  - Chat interface for querying documents
  - Automatic document ingestion from OpenProdoc storage
  - RAG processing with configurable chunk size
- **Storage**: 5Gi for metadata
- **Resources**: 500m-2000m CPU, 1-4Gi RAM

### 4. RAG CustomTask

- **Artifact**: `openprodoc-ragtask.jar` (uploaded into OpenProdoc as a document)
- **Purpose**: Event-driven integration that automatically syncs documents, folders, users, and groups from OpenProdoc to Open WebUI
- **Deployment**: Runs inside the OpenProdoc JVM — no separate container required
- **Tasks**:
  - `RAGEventDoc` — reacts to document INSERT/UPDATE/DELETE events
  - `RAGEventFold` — reacts to folder INSERT/UPDATE/DELETE events
  - `RAGSyncCron` — syncs users and groups to Open WebUI every 5 minutes via SCIM
- **Supported Formats**: pdf, doc, docx, txt, md, rtf, html, json, csv, xml, odt
- **Resources**: Zero additional resources (runs within the core-engine JVM)

## Deployment

### Option A: Docker Compose (Recommended for Development)

The simplest way to deploy the full RAG solution:

```bash
cd docker/

# Start all services
docker compose up -d

# Monitor startup (Ollama model pull can take several minutes)
docker compose logs -f

# Access:
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# Open WebUI:  http://localhost:8080
```

The docker-compose.yml deploys all services with correct startup ordering and health checks. A one-shot `rag-init` container automatically uploads the CustomTask JAR, creates event/cron task definitions, and provisions the watcher admin account in Open WebUI.

### Option B: Kubernetes (Helm)

#### Step 1: Configure Values

Edit `values.yaml` to enable and configure the RAG components:

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

#### Step 2: Adjust Resource Limits

For production deployments, adjust resources based on your cluster capacity:

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

#### Step 3: Deploy

```bash
# Install or upgrade the Helm chart
helm upgrade --install openprodoc ./helm/openprodoc \
  --namespace openprodoc \
  --create-namespace

# Monitor the deployment
kubectl get pods -n openprodoc -w
```

### Step 4: RAG Initialization

The `rag-init` one-shot container (Docker Compose) or Kubernetes Job (Helm) runs automatically after deployment and handles:

1. **Watcher admin account** — Creates `watcher@openprodoc.local` in Open WebUI with admin privileges. This account is used by the CustomTask to manage knowledge bases, files, users, and groups.
2. **JAR upload** — Uploads `openprodoc-ragtask.jar` to OpenProdoc via the REST API.
3. **Task definitions** — Inserts event tasks (document and folder INSERT/UPDATE/DELETE) and a cron task (user/group sync every 5 minutes) into the OpenProdoc database.

The init is **idempotent** — if the tasks already exist, it exits immediately without making changes. This allows safe re-runs on `helm upgrade` or `docker compose up`.

After deployment, you can sign in to Open WebUI with the default watcher admin credentials:

- **Email**: `watcher@openprodoc.local`
- **Password**: `12345678`

These credentials are configurable via `OPENWEBUI_ADMIN_EMAIL` / `OPENWEBUI_ADMIN_PASSWORD` in Docker Compose, or `ragInit.config.watcherEmail` / `ragInit.config.watcherPassword` in Helm values. Change them for production deployments.

#### Automatic user and group synchronization

Once initialized, the `RAGSyncCron` task automatically:
- **Replicates OpenProdoc users** to Open WebUI (every 5 minutes)
- **Replicates OpenProdoc groups** to Open WebUI via SCIM API
- **Assigns users to groups** matching their OpenProdoc group memberships

This means OpenProdoc users can log in to Open WebUI without separate registration.

### Step 5: Verify Deployment

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

### Step 6: User Authentication and Knowledge Base Organization

**Automatic User Replication**: All OpenProdoc users and groups are automatically replicated in the OpenWebUI environment. This means:

- **Seamless Login**: OpenProdoc users can automatically log in to OpenWebUI without any additional setup or registration
- **Single Sign-On**: User credentials are synchronized between OpenProdoc and OpenWebUI
- **Group Membership**: User group associations are maintained in both systems

**Permission-Based Access Control**:

Each user in OpenWebUI will have access to knowledge bases based on their OpenProdoc permissions:

- Users can only access knowledge bases for documents they have permissions to in OpenProdoc
- Access control is enforced at the knowledge base level
- Permissions are inherited from the OpenProdoc ACL system

**Knowledge Base Organization**:

The RAG system creates a one-to-one mapping between OpenProdoc folders and OpenWebUI knowledge bases:

- **Each folder in OpenProdoc generates a separate knowledge base in OpenWebUI**
- Each knowledge base contains the indexed knowledge from all documents within its corresponding OpenProdoc folder
- Users will see only the knowledge bases for folders they have access to
- This folder-based organization makes it easy to manage and query domain-specific document collections

**Example**:

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

This architecture ensures that document security and access control policies defined in OpenProdoc are seamlessly enforced in the RAG system.

## Usage

### Accessing the Services

#### Docker Compose

| Service | URL | Host Port | Container Port |
|---|---|---|---|
| OpenProdoc | `http://localhost:8081/ProdocWeb2/` | 8081 | 8080 |
| OpenProdoc REST API | `http://localhost:8081/ProdocWeb2/APIRest/` | 8081 | 8080 |
| Open WebUI (RAG) | `http://localhost:8082` | 8082 | 8080 |
| PostgreSQL | `localhost:5433` | 5433 | 5432 |

#### Kubernetes

If ingress is enabled, access Open WebUI at `http://localhost/rag` and OpenProdoc at `http://localhost/`.

If ingress is disabled, use port-forwarding:

```bash
kubectl port-forward svc/openprodoc-openwebui 8080:8080
kubectl port-forward svc/openprodoc-core-engine 8081:8080
```

### Querying Knowledge Bases

To use a Knowledge Base in a chat conversation in Open WebUI:

1. Open a new chat in Open WebUI
2. In the message input, type **`#`** — a dropdown will appear listing available Knowledge Bases
3. Select the desired Knowledge Base (e.g., `folder1`)
4. Type your question and send — the LLM will use RAG to search the selected Knowledge Base when generating its answer

You can attach multiple Knowledge Bases to a single conversation by typing `#` again and selecting additional ones.

### How It Works

1. **Document Upload**: When a document is inserted or updated in OpenProdoc, the `RAGEventDoc` CustomTask fires
2. **Ingestion**: The CustomTask uploads the document to Open WebUI's API and adds it to the corresponding Knowledge Base
3. **Processing**: Open WebUI:
   - Splits documents into chunks (default: 1500 chars with 100 char overlap)
   - Generates embeddings using Ollama's `nomic-embed-text` model
   - Stores embeddings in PGVector database
4. **Query**: Users ask questions via the chat interface
5. **Retrieval**: Open WebUI:
   - Generates query embedding
   - Searches PGVector for relevant chunks
   - Provides context to the LLM
6. **Response**: Ollama generates an answer based on retrieved context

### Supported Document Types

The CustomTask automatically processes these file types:
- Text: `.txt`, `.md`, `.rst`, `.rtf`
- Documents: `.pdf`, `.doc`, `.docx`
- Web: `.html`, `.htm`
- Data: `.json`, `.csv`, `.xml`

## Configuration Options

### Changing LLM Models

For better performance on low-resource clusters, use Phi-3:

```yaml
ollama:
  config:
    models:
      llm: "phi3"  # Smaller, faster than llama3:8b
```

### Adjusting RAG Parameters

```yaml
openwebui:
  config:
    rag:
      enabled: true
      chunkSize: 1500      # Size of document chunks
      chunkOverlap: 100    # Overlap between chunks
```

### Storage Configuration

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

## Troubleshooting

### Ollama Models Not Downloading

Check init container logs:

```bash
kubectl logs -n openprodoc <ollama-pod> -c pull-models
```

Models are large (4-8GB each) and may take time to download.

### Documents Not Appearing in Open WebUI

Check that the rag-init completed successfully:

```bash
# Docker Compose
docker compose logs rag-init

# Kubernetes
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init
```

Ensure:
1. The `rag-init` container/job completed without errors
2. The `watcher@openprodoc.local` admin account exists in Open WebUI
3. The CustomTask JAR was uploaded (check OpenProdoc System folder)
4. Event tasks are active (check OpenProdoc Admin → Task Management)
5. Open WebUI is reachable from the core-engine at the configured URL
6. The document MIME type is in the supported list

### PGVector Connection Issues

Check pgvector pod:

```bash
kubectl logs -n openprodoc <pgvector-pod>
kubectl exec -it -n openprodoc <pgvector-pod> -- psql -U rag_user -d rag_vectors
```

Verify the vector extension:

```sql
\dx  -- Should show 'vector' extension
```

### High Resource Usage

For CPU-constrained environments:

1. Switch to smaller models:
   ```yaml
   ollama:
     config:
       models:
         llm: "phi3"  # Instead of llama3:8b
   ```

2. Reduce resource limits:
   ```yaml
   ollama:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. Disable CustomTask init and use manual document upload:
   ```yaml
   ragInit:
     enabled: false
   ```

## Disabling RAG Components

To disable the RAG solution entirely:

```yaml
pgvector:
  enabled: false

ollama:
  enabled: false

openwebui:
  enabled: false
```

## Security Considerations

1. **Secrets**: PGVector password is stored in a Kubernetes secret. Change default password:
   ```yaml
   pgvector:
     config:
       password: "your-secure-password"
   ```

2. **Network Policies**: Consider implementing network policies to restrict pod-to-pod communication

3. **API Authentication**: Configure Open WebUI authentication in production. After rag-init completes, consider setting `ENABLE_SIGNUP=false` and `DEFAULT_USER_ROLE=user` to prevent unauthorized admin accounts.

## Performance Tuning

### For High-Volume Deployments

1. **Increase Ollama Parallelism**:
   ```yaml
   # Set via environment in ollama deployment
   OLLAMA_NUM_PARALLEL: "8"
   ```

2. **Scale PGVector**:
   ```yaml
   pgvector:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. **Enable Caching**: Ollama keeps models in memory based on `OLLAMA_KEEP_ALIVE`

### For Low-Resource Deployments

1. Use Phi-3 model (smaller and faster)
2. Reduce chunk size to process fewer embeddings
3. Disable `ragInit` and use manual document upload via Open WebUI

## Monitoring

Monitor RAG components:

```bash
# Resource usage
kubectl top pods -n openprodoc

# Service status
kubectl get svc -n openprodoc

# Logs
kubectl logs -n openprodoc -l app.kubernetes.io/part-of=openprodoc --tail=100
```

## Further Reading

- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Ollama Model Library](https://ollama.com/library)
- [PGVector Documentation](https://github.com/pgvector/pgvector)
