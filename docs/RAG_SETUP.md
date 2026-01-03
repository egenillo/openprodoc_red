# OpenProdoc RAG Solution Setup Guide

This guide explains how to deploy and use the integrated RAG (Retrieval-Augmented Generation) solution with OpenProdoc.

## Overview

The RAG solution extends OpenProdoc with AI-powered document search and question-answering capabilities. It consists of three main components:

1. **PGVector** - PostgreSQL with vector extension for storing document embeddings
2. **Ollama** - LLM and embedding engine running on CPU
3. **Open WebUI** - User interface and RAG orchestrator with automatic document ingestion

## Architecture

```
┌─────────────────┐
│  OpenProdoc     │
│  Core Engine    │
└────────┬────────┘
         │
         │ Shared PVC (Read-Only)
         │
         ▼
┌─────────────────────────────────────┐
│  Open WebUI Pod                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │  Open WebUI  │  │   Watcher   │ │
│  │   (Main)     │  │  (Sidecar)  │ │
│  └──────┬───────┘  └──────┬──────┘ │
└─────────┼──────────────────┼────────┘
          │                  │
          │                  │ Monitors & Ingests
          ▼                  ▼
    ┌─────────┐        ┌──────────┐
    │ Ollama  │        │ PGVector │
    │  (LLM)  │        │ (Vectors)│
    └─────────┘        └──────────┘
```

## Components

### 1. PGVector (Vector Database)

- **Image**: `pgvector/pgvector:pg16`
- **Purpose**: Stores document embeddings for semantic search
- **Storage**: 20Gi by default (configurable)
- **Resources**: 250m CPU, 512Mi RAM (requests)

### 2. Ollama (LLM Engine)

- **Image**: `ollama/ollama:latest`
- **Models**:
  - LLM: `llama3:8b` (or `phi3` for lower resource usage)
  - Embeddings: `all-minilm` (lightweight, CPU-optimized)
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

### 4. Watcher Sidecar

- **Purpose**: Monitors OpenProdoc storage and automatically ingests new documents
- **Supported Formats**: txt, md, pdf, doc, docx, html, json, csv, xml
- **Resources**: 100m-200m CPU, 128-256Mi RAM

## Deployment

### Step 1: Configure Values

Edit `values.yaml` to enable and configure the RAG components:

```yaml
# Enable RAG components
pgvector:
  enabled: true

ollama:
  enabled: true
  config:
    models:
      llm: "llama3:8b"  # or "phi3" for smaller deployments
      embedding: "all-minilm"

openwebui:
  enabled: true
  watcher:
    enabled: true
```

### Step 2: Adjust Resource Limits

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

### Step 3: Deploy

```bash
# Install or upgrade the Helm chart
helm upgrade --install openprodoc ./helm/openprodoc \
  --namespace openprodoc \
  --create-namespace

# Monitor the deployment
kubectl get pods -n openprodoc -w
```

### Step 4: Setup RAG users

The first time you access to OpenWebUI interface you will be requested to create the admin user.

**IMPORTANT**: After deployment, you must create a user called `watcher` in OpenProdoc.

The RAG system will only index and process documents that the `watcher` user has READ access to. This provides fine-grained control over which documents are available for AI-powered search and question-answering.

To create the watcher user:

1. Log in to OpenProdoc with administrator credentials
2. Navigate to user management
3. Create a new user with username: `watcher`
4. Add the `watcher` user with READ permissions to the ACL associated with the folders/files you want to include in the RAG system
5. Ensure the user has appropriate access levels for your use case

**Access Control**: Only documents where the `watcher` user has READ permissions in the ACL will be:
- Monitored by the watcher sidecar
- Ingested into the RAG system
- Available for semantic search and AI queries

This ensures document-level security is maintained in the RAG solution.

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n openprodoc

# Expected output should show:
# - openprodoc-core-engine-xxx (Running)
# - openprodoc-pgvector-xxx (Running)
# - openprodoc-ollama-xxx (Running)
# - openprodoc-openwebui-xxx (Running)

# Check Ollama models are downloaded
kubectl logs -n openprodoc -l app.kubernetes.io/component=ollama -c pull-models

# Check watcher is monitoring
kubectl logs -n openprodoc -l app.kubernetes.io/component=openwebui -c watcher
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

### Accessing the RAG Interface

If ingress is enabled, access Open WebUI at:

```
http://localhost/rag
```

If ingress is disabled, use port-forwarding:

```bash
kubectl port-forward -n openprodoc svc/openprodoc-openwebui 8080:8080
```

Then access: `http://localhost:8080`

### How It Works

1. **Document Upload**: Documents added to OpenProdoc storage are automatically detected by the watcher sidecar
2. **Ingestion**: The watcher sends documents to Open WebUI's API
3. **Processing**: Open WebUI:
   - Splits documents into chunks (default: 1500 chars with 100 char overlap)
   - Generates embeddings using Ollama's `all-minilm` model
   - Stores embeddings in PGVector database
4. **Query**: Users ask questions via the chat interface
5. **Retrieval**: Open WebUI:
   - Generates query embedding
   - Searches PGVector for relevant chunks
   - Provides context to the LLM
6. **Response**: Ollama generates an answer based on retrieved context

### Supported Document Types

The watcher automatically processes these file types:
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

### Watcher Configuration

```yaml
openwebui:
  watcher:
    config:
      pollInterval: 30  # How often to check for new files (seconds)
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

### Watcher Not Ingesting Documents

Check watcher logs:

```bash
kubectl logs -n openprodoc <openwebui-pod> -c watcher
```

Ensure:
1. OpenProdoc PVC is mounted correctly
2. File types are supported
3. Open WebUI API is accessible

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

3. Disable watcher if manual ingestion is acceptable:
   ```yaml
   openwebui:
     watcher:
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

3. **Read-Only Mount**: The watcher mounts OpenProdoc storage as read-only for safety

4. **API Authentication**: Configure Open WebUI authentication in production

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
3. Increase watcher poll interval to reduce CPU usage
4. Disable watcher and use manual document upload

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
