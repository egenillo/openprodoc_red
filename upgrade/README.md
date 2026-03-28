# OpenProdoc Red — Upgrade: Add AI/RAG to Existing OpenProdoc
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md)

## Overview

This folder contains everything needed to add **AI chatbot and RAG (Retrieval-Augmented Generation) capabilities** to an **existing OpenProdoc installation**, without replacing or migrating it.

If you already have OpenProdoc running (standalone Tomcat, VM, or any other setup), you can deploy only the AI/RAG containers from OpenProdoc Red alongside it. Your existing OpenProdoc stays untouched — the new containers connect to it via REST API and database.

### What Gets Deployed

| Component | Purpose | Port |
|-----------|---------|------|
| **Open WebUI** | RAG chatbot interface | 8082 |
| **Ollama** | Local AI/LLM engine | 11434 |
| **pgvector** | Vector database for document embeddings | (internal) |
| **rag-init** | One-shot initializer (configures tasks, then exits) | - |

### What Does NOT Get Deployed

- No OpenProdoc container (you already have one)
- No PostgreSQL container for OpenProdoc (you already have one)

----

## Prerequisites

Before starting, ensure your existing OpenProdoc meets these requirements:

### 1. REST API Enabled
The OpenProdoc web application (`ProdocWeb2`) must be deployed with the REST API (`APIRest`) accessible. Test it:

```bash
curl http://localhost:8080/ProdocWeb2/APIRest/session
```

### 2. PostgreSQL Database
Your OpenProdoc must use **PostgreSQL** as its database. The rag-init script needs direct database access to insert task definitions. Other databases (MySQL, Oracle, etc.) are not supported for this upgrade path.

### 3. Database Accessible from Docker
Docker containers must be able to reach your PostgreSQL. On the same machine:
- **Windows/Mac (Docker Desktop)**: Accessible via `host.docker.internal`
- **Linux**: Accessible via `172.17.0.1` (Docker bridge gateway)

If PostgreSQL only listens on `localhost`, you may need to edit `postgresql.conf`:
```
listen_addresses = '*'
```
And add a line to `pg_hba.conf`:
```
host    prodoc    user1    172.17.0.0/16    md5
```

### 4. Docker and Docker Compose
Docker Engine and Docker Compose (v2) must be installed.

----

## Quick Start

### Step 1: Configure

```bash
# Copy the example configuration
cp .env.example .env

# Edit .env with your OpenProdoc details
# At minimum, set:
#   OPENPRODOC_URL          - Your OpenProdoc URL
#   OPD_ROOT_USER           - Admin username
#   OPD_ROOT_PASSWORD       - Admin password
#   OPD_POSTGRES_HOST       - Database host
#   OPD_POSTGRES_PORT       - Database port
#   OPD_POSTGRES_DB         - Database name
#   OPD_POSTGRES_USER       - Database user
#   OPD_POSTGRES_PASSWORD   - Database password
```

### Step 2: Verify (Optional but Recommended)

```bash
# Run the pre-flight check to verify connectivity
./check-openprodoc.sh
```

### Step 3: Start

```bash
# Linux (auto-detects GPU)
./start-linux.sh

# Windows
start-windows.bat

# Or manually
docker compose up -d
```

### Step 4: Enable Task Scheduler in OpenProdoc

Add these lines to your existing OpenProdoc's `Prodoc.properties` file:

```properties
PD.TaskCategory=*
PD.TaskSearchFreq=60000
PD.TaskExecFreq=30000
```

Then **restart your OpenProdoc** (Tomcat or application server).

### Step 5: Verify

```bash
# Check initialization completed
docker compose logs rag-init

# Access the RAG chatbot
# Open: http://localhost:8082
```

----

## How It Works

### Architecture

```
Your Host Machine
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  YOUR EXISTING OPENPRODOC                                │
│  ├── Tomcat (localhost:8080)                              │
│  │   ├── ProdocWeb2 (Web UI)                             │
│  │   ├── APIRest (REST API)                              │
│  │   └── CustomTask JAR ──── calls ──┐                   │
│  └── PostgreSQL (localhost:5432)      │                   │
│                                      │                   │
│  OPENPRODOC RED CONTAINERS           │                   │
│  ├── Open WebUI (localhost:8082) ◄───┘                   │
│  ├── Ollama (localhost:11434)                             │
│  └── pgvector (internal)                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document events**: When you create/update/delete a document in OpenProdoc, the CustomTask JAR (running inside your OpenProdoc's JVM) sends the document to Open WebUI for RAG indexing.

2. **User/group sync**: A cron task periodically replicates OpenProdoc users and groups to Open WebUI via SCIM API, maintaining permissions.

3. **RAG queries**: Users interact with the Open WebUI chatbot at `http://localhost:8082`. The chatbot uses Ollama for AI inference and pgvector for semantic document search.

### How the RAG Task JAR is Incorporated into OpenProdoc

OpenProdoc supports custom extensions by storing JAR files as documents inside its own repository (see [Development with OpenProdoc](https://jhierrot.github.io/openprodoc/Docs/OPD_Development3.0.2.html), section 5.3). The `rag-init` container automates this process:

1. The JAR file (`openprodoc-ragtask.jar`) lives in the `docker/` folder of the repository. Docker mounts it read-only into the `rag-init` container at `/jar/openprodoc-ragtask.jar`.

2. The `rag-init-external.sh` script runs and:
   - **Logs into your existing OpenProdoc** via the REST API (`PUT /ProdocWeb2/APIRest/session`) using the credentials from `.env`.
   - **Uploads the JAR as a document** via `POST /ProdocWeb2/APIRest/documents`. OpenProdoc stores it in its repository and returns a unique identifier (**PDId**).
   - **Inserts task definitions** into your OpenProdoc's PostgreSQL database via direct SQL. Each task definition references the JAR using the format `PDId|package.ClassName` (e.g., `1a2b3c4d-5e6f7890|openprodoc.ragtask.RAGEventDoc`). The definitions also include the Open WebUI URL and credentials as task parameters.

3. After the `rag-init` container finishes (it runs once and exits), the JAR and task definitions are stored in your OpenProdoc. The remaining manual step is enabling the **task scheduler** in `Prodoc.properties` and restarting OpenProdoc. On restart, OpenProdoc reads the task definitions, **automatically downloads the JAR** from its own repository, loads it into the JVM, and begins executing tasks on document/folder events.

**Note:** If you later update the JAR (upload a new version), you must restart the JVM again — Java's classloader caches the previously loaded version.

### Why OPENWEBUI_HOST_URL Matters

The task definitions stored in your OpenProdoc database contain the URL that the CustomTask JAR uses to reach Open WebUI. Since the JAR runs **inside your OpenProdoc's JVM** (on the host), it sees the host network — not Docker's internal network. Therefore:

- `OPENWEBUI_URL=http://openwebui:8080` — Used only by the rag-init container (Docker internal)
- `OPENWEBUI_HOST_URL=http://localhost:8082` — Used by the CustomTask JAR (host network)

If you change the Open WebUI published port, update `OPENWEBUI_HOST_URL` accordingly.

----

## Configuration Reference

### .env Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENPRODOC_URL` | `http://host.docker.internal:8080` | Your OpenProdoc URL (from Docker's perspective) |
| `OPD_ROOT_USER` | `root` | OpenProdoc admin username |
| `OPD_ROOT_PASSWORD` | `admin` | OpenProdoc admin password |
| `OPD_POSTGRES_HOST` | `host.docker.internal` | OpenProdoc database host |
| `OPD_POSTGRES_PORT` | `5432` | OpenProdoc database port |
| `OPD_POSTGRES_DB` | `prodoc` | OpenProdoc database name |
| `OPD_POSTGRES_USER` | `user1` | Database user |
| `OPD_POSTGRES_PASSWORD` | `pass1` | Database password |
| `OPENWEBUI_HOST_URL` | `http://localhost:8082` | Open WebUI URL as seen from the host |
| `OPENWEBUI_ADMIN_EMAIL` | `watcher@openprodoc.local` | Open WebUI admin email |
| `OPENWEBUI_ADMIN_PASSWORD` | `12345678` | Open WebUI admin password |
| `LLM_MODEL` | `llama3.1:latest` | LLM model for Ollama |
| `EMBEDDING_MODEL` | `nomic-embed-text:latest` | Embedding model for RAG |
| `SYNC_INTERVAL_MINS` | `1` | User/group sync frequency (minutes) |

### Prodoc.properties Settings

These must be added to your **existing** OpenProdoc's `Prodoc.properties`:

```properties
# Enable custom task scheduler (required for RAG integration)
PD.TaskCategory=*

# How often to search for new task definitions (milliseconds)
PD.TaskSearchFreq=60000

# How often to execute pending tasks (milliseconds)
PD.TaskExecFreq=30000
```

----

## GPU Acceleration and Ollama Image Selection

Ollama can use a GPU to significantly speed up LLM inference. Start scripts are provided to auto-detect GPU availability and apply the correct Docker Compose configuration.

### Ollama Image Options

| Image | Size | Use case |
|---|---|---|
| `ollama/ollama:0.18.2` | **~3.86 GB** | Full image with GPU drivers for NVIDIA and AMD. Use when GPU is available. |
| `alpine/ollama:0.18.2` | **~70 MB** | Stripped-down CPU-only image with no GPU drivers. Use when no GPU is available. |

When no GPU is detected, the start scripts automatically use the lightweight `alpine/ollama` image via the `docker-compose.cpu-light.yml` override, avoiding a 3.86 GB download that provides no benefit without a GPU.

### Start Script Options

The scripts accept an optional parameter to force a specific mode:

```bash
./start-linux.sh              # Auto-detect: GPU → full image, no GPU → alpine
./start-linux.sh --light      # Force alpine/ollama (~70 MB, CPU-only)
./start-linux.sh --cpu        # Force ollama/ollama (~3.86 GB, CPU mode, no GPU override)
./start-linux.sh --nvidia     # Force NVIDIA GPU mode
./start-linux.sh --amd        # Force AMD GPU mode (Linux only)
```

```cmd
start-windows.bat             # Auto-detect: NVIDIA → full image, no GPU → alpine
start-windows.bat --light     # Force alpine/ollama (~70 MB, CPU-only)
start-windows.bat --cpu       # Force ollama/ollama (~3.86 GB, CPU mode)
start-windows.bat --nvidia    # Force NVIDIA GPU mode
```

### GPU Prerequisites

- **NVIDIA**: NVIDIA drivers and [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) must be installed on the host. Supported on Linux and Windows.
- **AMD**: ROCm-compatible GPU and drivers must be installed. **Linux only** — the `ollama/ollama:0.18.2-rocm` Docker image is specifically designed for Linux systems with AMD GPUs and is not supported on Windows or macOS.

### Manual Override (without start scripts)

```bash
# NVIDIA GPU
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d

# AMD GPU (Linux only)
docker compose -f docker-compose.yml -f docker-compose.amd.yml up -d

# CPU-light (alpine/ollama, ~70 MB)
docker compose -f docker-compose.yml -f docker-compose.cpu-light.yml up -d

# CPU standard (ollama/ollama, ~3.86 GB)
docker compose up -d
```

----

## MCP Server (Claude Integration)

The MCP server is independent and does not need Docker. To use it with your existing OpenProdoc:

1. Navigate to the `MCP/` folder in the main OpenProdoc Red repository
2. Configure your Claude Desktop or Claude Code with:

```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["path/to/MCP/openprodoc_mcp.py"],
      "env": {
        "OPENPRODOC_BASE_URL": "http://localhost:8080/ProdocWeb2/APIRest",
        "OPENPRODOC_USERNAME": "root",
        "OPENPRODOC_PASSWORD": "your_password"
      }
    }
  }
}
```

See [MCP/README.md](../MCP/README.md) for the complete integration guide.

----

## Troubleshooting

### rag-init fails to connect to OpenProdoc

```
ERROR: Could not connect to external OpenProdoc REST API
```

- Verify OpenProdoc is running: `curl http://localhost:8080/ProdocWeb2/`
- On Linux, try using `172.17.0.1` instead of `host.docker.internal`
- Check that the port matches your OpenProdoc configuration

### rag-init fails to connect to PostgreSQL

```
ERROR: External PostgreSQL not ready
```

- Verify PostgreSQL is running: `pg_isready -h localhost -p 5432`
- Check `postgresql.conf` — `listen_addresses` must include Docker's network
- Check `pg_hba.conf` — Docker subnet must be allowed

### Tasks are not executing

After adding settings to `Prodoc.properties` and restarting:

1. Check that the JAR was uploaded: look for `openprodoc-ragtask.jar` in OpenProdoc's RootFolder
2. Check task definitions: `SELECT * FROM pd_tasksdefeven WHERE name LIKE 'RAG_%';`
3. Check logs for errors in your OpenProdoc's Tomcat logs (`catalina.out`)

### Open WebUI not accessible

- Verify container is running: `docker compose ps`
- Check health: `curl http://localhost:8082/health`
- Check logs: `docker compose logs openwebui`

----

## Uninstall

To remove the RAG integration:

```bash
# Stop and remove containers and volumes
docker compose down -v

# Remove task definitions from OpenProdoc database (optional)
PGPASSWORD=pass1 psql -h localhost -U user1 -d prodoc -c "
  DELETE FROM pd_tasksdefeven WHERE name LIKE 'RAG_%';
  DELETE FROM pd_tasksdefcron WHERE name LIKE 'RAG_%';
"

# Remove task scheduler settings from Prodoc.properties (optional)
# Delete or comment out these lines:
#   PD.TaskCategory=*
#   PD.TaskSearchFreq=60000
#   PD.TaskExecFreq=30000
```

----

## Files in This Folder

| File | Description |
|------|-------------|
| `docker-compose.yml` | Main compose file (RAG containers only, no core-engine) |
| `docker-compose.nvidia.yml` | NVIDIA GPU override for Ollama |
| `docker-compose.amd.yml` | AMD GPU override for Ollama (Linux only) |
| `docker-compose.cpu-light.yml` | CPU-light override — uses alpine/ollama (~70 MB) instead of full image (~3.86 GB) |
| `.env.example` | Configuration template — copy to `.env` and edit |
| `rag-init-external.sh` | Initialization script for external OpenProdoc |
| `init-pgvector.sql` | pgvector database initialization |
| `start-linux.sh` | Start script with GPU auto-detection (Linux) |
| `start-windows.bat` | Start script with GPU auto-detection (Windows) |
| `check-openprodoc.sh` | Pre-flight connectivity check |
| `README.md` | This documentation (English) |
| `README.es.md` | This documentation (Spanish) |
