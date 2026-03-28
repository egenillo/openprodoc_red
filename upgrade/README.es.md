# OpenProdoc Red — Upgrade: Agregar IA/RAG a OpenProdoc Existente
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md)

## Descripcion General

Esta carpeta contiene todo lo necesario para agregar **capacidades de chatbot con IA y RAG (Generacion Aumentada por Recuperacion)** a una **instalacion OpenProdoc existente**, sin reemplazarla ni migrarla.

Si ya tiene OpenProdoc funcionando (Tomcat independiente, maquina virtual o cualquier otra configuracion), puede desplegar solo los contenedores de IA/RAG de OpenProdoc Red junto a el. Su OpenProdoc existente permanece intacto — los nuevos contenedores se conectan a el mediante API REST y base de datos.

### Que se Despliega

| Componente | Proposito | Puerto |
|------------|-----------|--------|
| **Open WebUI** | Interfaz de chatbot RAG | 8082 |
| **Ollama** | Motor de IA/LLM local | 11434 |
| **pgvector** | Base de datos vectorial para embeddings de documentos | (interno) |
| **rag-init** | Inicializador unico (configura tareas y luego finaliza) | - |

### Que NO se Despliega

- No se despliega contenedor de OpenProdoc (ya tiene uno)
- No se despliega contenedor de PostgreSQL para OpenProdoc (ya tiene uno)

----

## Prerequisitos

Antes de comenzar, asegurese de que su OpenProdoc existente cumple estos requisitos:

### 1. API REST Habilitada
La aplicacion web OpenProdoc (`ProdocWeb2`) debe estar desplegada con la API REST (`APIRest`) accesible. Verificar:

```bash
curl http://localhost:8080/ProdocWeb2/APIRest/session
```

### 2. Base de Datos PostgreSQL
Su OpenProdoc debe usar **PostgreSQL** como base de datos. El script rag-init necesita acceso directo a la base de datos para insertar definiciones de tareas. Otras bases de datos (MySQL, Oracle, etc.) no estan soportadas para esta ruta de actualizacion.

### 3. Base de Datos Accesible desde Docker
Los contenedores Docker deben poder alcanzar su PostgreSQL. En la misma maquina:
- **Windows/Mac (Docker Desktop)**: Accesible via `host.docker.internal`
- **Linux**: Accesible via `172.17.0.1` (gateway del bridge Docker)

Si PostgreSQL solo escucha en `localhost`, puede necesitar editar `postgresql.conf`:
```
listen_addresses = '*'
```
Y agregar una linea a `pg_hba.conf`:
```
host    prodoc    user1    172.17.0.0/16    md5
```

### 4. Docker y Docker Compose
Docker Engine y Docker Compose (v2) deben estar instalados.

----

## Inicio Rapido

### Paso 1: Configurar

```bash
# Copiar la configuracion de ejemplo
cp .env.example .env

# Editar .env con los datos de su OpenProdoc
# Como minimo, configurar:
#   OPENPRODOC_URL          - URL de su OpenProdoc
#   OPD_ROOT_USER           - Usuario administrador
#   OPD_ROOT_PASSWORD       - Contrasena de administrador
#   OPD_POSTGRES_HOST       - Host de la base de datos
#   OPD_POSTGRES_PORT       - Puerto de la base de datos
#   OPD_POSTGRES_DB         - Nombre de la base de datos
#   OPD_POSTGRES_USER       - Usuario de la base de datos
#   OPD_POSTGRES_PASSWORD   - Contrasena de la base de datos
```

### Paso 2: Verificar (Opcional pero Recomendado)

```bash
# Ejecutar la verificacion previa de conectividad
./check-openprodoc.sh
```

### Paso 3: Iniciar

```bash
# Linux (auto-detecta GPU)
./start-linux.sh

# Windows
start-windows.bat

# O manualmente
docker compose up -d
```

### Paso 4: Habilitar el Programador de Tareas en OpenProdoc

Agregar estas lineas al archivo `Prodoc.properties` de su OpenProdoc existente:

```properties
PD.TaskCategory=*
PD.TaskSearchFreq=60000
PD.TaskExecFreq=30000
```

Luego **reiniciar su OpenProdoc** (Tomcat o servidor de aplicaciones).

### Paso 5: Verificar

```bash
# Comprobar que la inicializacion se completo
docker compose logs rag-init

# Acceder al chatbot RAG
# Abrir: http://localhost:8082
```

----

## Como Funciona

### Arquitectura

```
Su Maquina Host
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  SU OPENPRODOC EXISTENTE                                 │
│  ├── Tomcat (localhost:8080)                              │
│  │   ├── ProdocWeb2 (Interfaz Web)                       │
│  │   ├── APIRest (API REST)                              │
│  │   └── CustomTask JAR ──── llama ──┐                   │
│  └── PostgreSQL (localhost:5432)      │                   │
│                                      │                   │
│  CONTENEDORES OPENPRODOC RED         │                   │
│  ├── Open WebUI (localhost:8082) ◄───┘                   │
│  ├── Ollama (localhost:11434)                             │
│  └── pgvector (interno)                                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Flujo de Datos

1. **Eventos de documentos**: Cuando se crea/actualiza/elimina un documento en OpenProdoc, el CustomTask JAR (ejecutandose dentro de la JVM de su OpenProdoc) envia el documento a Open WebUI para indexacion RAG.

2. **Sincronizacion de usuarios/grupos**: Una tarea cron replica periodicamente los usuarios y grupos de OpenProdoc a Open WebUI mediante SCIM API, manteniendo los permisos.

3. **Consultas RAG**: Los usuarios interactuan con el chatbot Open WebUI en `http://localhost:8082`. El chatbot usa Ollama para la inferencia de IA y pgvector para la busqueda semantica de documentos.

### Como se Incorpora el JAR de RAG en OpenProdoc

OpenProdoc soporta extensiones personalizadas almacenando archivos JAR como documentos dentro de su propio repositorio (ver [Development with OpenProdoc](https://jhierrot.github.io/openprodoc/Docs/OPD_Development3.0.2.html), seccion 5.3). El contenedor `rag-init` automatiza este proceso:

1. El archivo JAR (`openprodoc-ragtask.jar`) se encuentra en la carpeta `docker/` del repositorio. Docker lo monta como solo lectura en el contenedor `rag-init` en `/jar/openprodoc-ragtask.jar`.

2. El script `rag-init-external.sh` se ejecuta y:
   - **Inicia sesion en su OpenProdoc existente** mediante la API REST (`PUT /ProdocWeb2/APIRest/session`) usando las credenciales del `.env`.
   - **Sube el JAR como un documento** mediante `POST /ProdocWeb2/APIRest/documents`. OpenProdoc lo almacena en su repositorio y devuelve un identificador unico (**PDId**).
   - **Inserta las definiciones de tareas** en la base de datos PostgreSQL de su OpenProdoc mediante SQL directo. Cada definicion de tarea referencia el JAR usando el formato `PDId|paquete.NombreClase` (ej: `1a2b3c4d-5e6f7890|openprodoc.ragtask.RAGEventDoc`). Las definiciones tambien incluyen la URL de Open WebUI y las credenciales como parametros de la tarea.

3. Una vez que el contenedor `rag-init` finaliza (se ejecuta una sola vez y termina), el JAR y las definiciones de tareas quedan almacenados en su OpenProdoc. El paso manual restante es habilitar el **programador de tareas** en `Prodoc.properties` y reiniciar OpenProdoc. Al reiniciar, OpenProdoc lee las definiciones de tareas, **descarga automaticamente el JAR** desde su propio repositorio, lo carga en la JVM y comienza a ejecutar las tareas ante eventos de documentos/carpetas.

**Nota:** Si posteriormente actualiza el JAR (sube una nueva version), debe reiniciar la JVM de nuevo — el classloader de Java mantiene en cache la version cargada previamente.

### Por que OPENWEBUI_HOST_URL es Importante

Las definiciones de tareas almacenadas en la base de datos de su OpenProdoc contienen la URL que el CustomTask JAR usa para alcanzar Open WebUI. Como el JAR se ejecuta **dentro de la JVM de su OpenProdoc** (en el host), ve la red del host — no la red interna de Docker. Por lo tanto:

- `OPENWEBUI_URL=http://openwebui:8080` — Usado solo por el contenedor rag-init (red interna Docker)
- `OPENWEBUI_HOST_URL=http://localhost:8082` — Usado por el CustomTask JAR (red del host)

Si cambia el puerto publicado de Open WebUI, actualice `OPENWEBUI_HOST_URL` consecuentemente.

----

## Referencia de Configuracion

### Variables .env

| Variable | Por defecto | Descripcion |
|----------|-------------|-------------|
| `OPENPRODOC_URL` | `http://host.docker.internal:8080` | URL de su OpenProdoc (desde la perspectiva de Docker) |
| `OPD_ROOT_USER` | `root` | Usuario administrador de OpenProdoc |
| `OPD_ROOT_PASSWORD` | `admin` | Contrasena de administrador de OpenProdoc |
| `OPD_POSTGRES_HOST` | `host.docker.internal` | Host de la base de datos de OpenProdoc |
| `OPD_POSTGRES_PORT` | `5432` | Puerto de la base de datos |
| `OPD_POSTGRES_DB` | `prodoc` | Nombre de la base de datos |
| `OPD_POSTGRES_USER` | `user1` | Usuario de la base de datos |
| `OPD_POSTGRES_PASSWORD` | `pass1` | Contrasena de la base de datos |
| `OPENWEBUI_HOST_URL` | `http://localhost:8082` | URL de Open WebUI vista desde el host |
| `OPENWEBUI_ADMIN_EMAIL` | `watcher@openprodoc.local` | Email del administrador de Open WebUI |
| `OPENWEBUI_ADMIN_PASSWORD` | `12345678` | Contrasena del administrador de Open WebUI |
| `LLM_MODEL` | `llama3.1:latest` | Modelo LLM para Ollama |
| `EMBEDDING_MODEL` | `nomic-embed-text:latest` | Modelo de embeddings para RAG |
| `SYNC_INTERVAL_MINS` | `1` | Frecuencia de sincronizacion de usuarios/grupos (minutos) |

### Configuracion de Prodoc.properties

Estas lineas deben agregarse al `Prodoc.properties` de su OpenProdoc **existente**:

```properties
# Habilitar programador de tareas personalizadas (requerido para integracion RAG)
PD.TaskCategory=*

# Frecuencia de busqueda de nuevas definiciones de tareas (milisegundos)
PD.TaskSearchFreq=60000

# Frecuencia de ejecucion de tareas pendientes (milisegundos)
PD.TaskExecFreq=30000
```

----

## Aceleracion GPU y Seleccion de Imagen Ollama

Ollama puede utilizar una GPU para acelerar significativamente la inferencia del LLM. Se proporcionan scripts de inicio que detectan automaticamente la disponibilidad de GPU y aplican la configuracion correcta de Docker Compose.

### Opciones de Imagen Ollama

| Imagen | Tamano | Caso de uso |
|---|---|---|
| `ollama/ollama:0.18.2` | **~3.86 GB** | Imagen completa con drivers GPU para NVIDIA y AMD. Usar cuando hay GPU disponible. |
| `alpine/ollama:0.18.2` | **~70 MB** | Imagen reducida solo CPU sin drivers GPU. Usar cuando no hay GPU disponible. |

Cuando no se detecta GPU, los scripts de inicio usan automaticamente la imagen ligera `alpine/ollama` mediante el override `docker-compose.cpu-light.yml`, evitando una descarga de 3.86 GB que no aporta beneficio sin GPU.

### Opciones de los Scripts de Inicio

Los scripts aceptan un parametro opcional para forzar un modo especifico:

```bash
./start-linux.sh              # Auto-detectar: GPU → imagen completa, sin GPU → alpine
./start-linux.sh --light      # Forzar alpine/ollama (~70 MB, solo CPU)
./start-linux.sh --cpu        # Forzar ollama/ollama (~3.86 GB, modo CPU, sin override GPU)
./start-linux.sh --nvidia     # Forzar modo NVIDIA GPU
./start-linux.sh --amd        # Forzar modo AMD GPU (solo Linux)
```

```cmd
start-windows.bat             # Auto-detectar: NVIDIA → imagen completa, sin GPU → alpine
start-windows.bat --light     # Forzar alpine/ollama (~70 MB, solo CPU)
start-windows.bat --cpu       # Forzar ollama/ollama (~3.86 GB, modo CPU)
start-windows.bat --nvidia    # Forzar modo NVIDIA GPU
```

### Requisitos Previos para GPU

- **NVIDIA**: Los drivers de NVIDIA y el [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) deben estar instalados en el host. Compatible con Linux y Windows.
- **AMD**: Se requieren GPU y drivers compatibles con ROCm. **Solo Linux** — la imagen Docker `ollama/ollama:0.18.2-rocm` esta disenada especificamente para sistemas Linux con GPUs AMD y no es compatible con Windows ni macOS.

### Override Manual (sin scripts de inicio)

```bash
# GPU NVIDIA
docker compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d

# GPU AMD (solo Linux)
docker compose -f docker-compose.yml -f docker-compose.amd.yml up -d

# CPU-light (alpine/ollama, ~70 MB)
docker compose -f docker-compose.yml -f docker-compose.cpu-light.yml up -d

# CPU estandar (ollama/ollama, ~3.86 GB)
docker compose up -d
```

----

## Servidor MCP (Integracion con Claude)

El servidor MCP es independiente y no necesita Docker. Para usarlo con su OpenProdoc existente:

1. Navegue a la carpeta `MCP/` en el repositorio principal de OpenProdoc Red
2. Configure su Claude Desktop o Claude Code con:

```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["ruta/a/MCP/openprodoc_mcp.py"],
      "env": {
        "OPENPRODOC_BASE_URL": "http://localhost:8080/ProdocWeb2/APIRest",
        "OPENPRODOC_USERNAME": "root",
        "OPENPRODOC_PASSWORD": "su_contrasena"
      }
    }
  }
}
```

Consulte [MCP/README.md](../MCP/README.md) para la guia completa de integracion.

----

## Solucion de Problemas

### rag-init no puede conectar a OpenProdoc

```
ERROR: Could not connect to external OpenProdoc REST API
```

- Verificar que OpenProdoc esta funcionando: `curl http://localhost:8080/ProdocWeb2/`
- En Linux, intentar usar `172.17.0.1` en lugar de `host.docker.internal`
- Comprobar que el puerto coincide con su configuracion de OpenProdoc

### rag-init no puede conectar a PostgreSQL

```
ERROR: External PostgreSQL not ready
```

- Verificar que PostgreSQL esta funcionando: `pg_isready -h localhost -p 5432`
- Comprobar `postgresql.conf` — `listen_addresses` debe incluir la red de Docker
- Comprobar `pg_hba.conf` — la subred de Docker debe estar permitida

### Las tareas no se ejecutan

Despues de agregar la configuracion a `Prodoc.properties` y reiniciar:

1. Comprobar que el JAR se subio: buscar `openprodoc-ragtask.jar` en el RootFolder de OpenProdoc
2. Comprobar definiciones de tareas: `SELECT * FROM pd_tasksdefeven WHERE name LIKE 'RAG_%';`
3. Comprobar logs de errores en los logs de Tomcat de su OpenProdoc (`catalina.out`)

### Open WebUI no es accesible

- Verificar que el contenedor esta funcionando: `docker compose ps`
- Comprobar salud: `curl http://localhost:8082/health`
- Comprobar logs: `docker compose logs openwebui`

----

## Desinstalar

Para eliminar la integracion RAG:

```bash
# Detener y eliminar contenedores y volumenes
docker compose down -v

# Eliminar definiciones de tareas de la base de datos OpenProdoc (opcional)
PGPASSWORD=pass1 psql -h localhost -U user1 -d prodoc -c "
  DELETE FROM pd_tasksdefeven WHERE name LIKE 'RAG_%';
  DELETE FROM pd_tasksdefcron WHERE name LIKE 'RAG_%';
"

# Eliminar configuracion del programador de tareas de Prodoc.properties (opcional)
# Eliminar o comentar estas lineas:
#   PD.TaskCategory=*
#   PD.TaskSearchFreq=60000
#   PD.TaskExecFreq=30000
```

----

## Archivos en Esta Carpeta

| Archivo | Descripcion |
|---------|-------------|
| `docker-compose.yml` | Archivo compose principal (solo contenedores RAG, sin core-engine) |
| `docker-compose.nvidia.yml` | Sobreescritura GPU NVIDIA para Ollama |
| `docker-compose.amd.yml` | Sobreescritura GPU AMD para Ollama (solo Linux) |
| `docker-compose.cpu-light.yml` | Override CPU-light — usa alpine/ollama (~70 MB) en lugar de la imagen completa (~3.86 GB) |
| `.env.example` | Plantilla de configuracion — copiar a `.env` y editar |
| `rag-init-external.sh` | Script de inicializacion para OpenProdoc externo |
| `init-pgvector.sql` | Inicializacion de la base de datos pgvector |
| `start-linux.sh` | Script de inicio con auto-deteccion de GPU (Linux) |
| `start-windows.bat` | Script de inicio con auto-deteccion de GPU (Windows) |
| `check-openprodoc.sh` | Verificacion previa de conectividad |
| `README.md` | Esta documentacion (Ingles) |
| `README.es.md` | Esta documentacion (Espanol) |
