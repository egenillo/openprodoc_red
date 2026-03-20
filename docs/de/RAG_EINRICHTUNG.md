# OpenProdoc RAG-Loesung Einrichtungsanleitung

Diese Anleitung beschreibt, wie die integrierte RAG (Retrieval-Augmented Generation)-Loesung mit OpenProdoc bereitgestellt und verwendet wird.

## Ueberblick

Die RAG-Loesung erweitert OpenProdoc um KI-gestuetzte Dokumentensuche und Frage-Antwort-Funktionen. Sie besteht aus folgenden Hauptkomponenten:

1. **PGVector** - PostgreSQL mit Vector-Erweiterung zur Speicherung von Dokument-Embeddings
2. **Ollama** - LLM- und Embedding-Engine auf CPU-Basis
3. **Open WebUI** - Benutzeroberflaeche und RAG-Orchestrator
4. **RAG CustomTask** - Native OpenProdoc Event-Handler, die Dokumente, Ordner, Benutzer und Gruppen automatisch mit Open WebUI synchronisieren

## Architektur

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

Der CustomTask laeuft innerhalb der OpenProdoc-JVM — es wird kein externer Sidecar oder Polling-Container benoetigt. Dokument- und Ordner-Events loesen HTTP-API-Aufrufe an Open WebUI in Echtzeit aus, und ein Cron-Task synchronisiert Benutzer und Gruppen alle 5 Minuten ueber SCIM.

## Komponenten

### 1. PGVector (Vektordatenbank)

- **Image**: `pgvector/pgvector:pg16`
- **Zweck**: Speichert Dokument-Embeddings fuer die semantische Suche
- **Speicher**: Standardmaessig 20Gi (konfigurierbar)
- **Ressourcen**: 250m CPU, 512Mi RAM (Requests)

### 2. Ollama (LLM-Engine)

- **Image**: `ollama/ollama:0.18.2`
- **Modelle**:
  - LLM: `llama3.1:latest` (oder `phi3` fuer geringeren Ressourcenverbrauch)
  - Embeddings: `nomic-embed-text:latest` (leichtgewichtig, CPU-optimiert)
- **Speicher**: 50Gi fuer Modelle
- **Ressourcen**: 2-4 CPU-Kerne, 4-8Gi RAM

### 3. Open WebUI (RAG-Oberflaeche)

- **Image**: `ghcr.io/open-webui/open-webui:main`
- **Funktionen**:
  - Chat-Oberflaeche zur Abfrage von Dokumenten
  - Automatische Dokumentenaufnahme aus dem OpenProdoc-Speicher
  - RAG-Verarbeitung mit konfigurierbarer Chunk-Groesse
- **Speicher**: 5Gi fuer Metadaten
- **Ressourcen**: 500m-2000m CPU, 1-4Gi RAM

### 4. RAG CustomTask

- **Artefakt**: `openprodoc-ragtask.jar` (wird als Dokument in OpenProdoc hochgeladen)
- **Zweck**: Ereignisgesteuerte Integration, die Dokumente, Ordner, Benutzer und Gruppen automatisch von OpenProdoc nach Open WebUI synchronisiert
- **Bereitstellung**: Laeuft innerhalb der OpenProdoc-JVM — kein separater Container erforderlich
- **Tasks**:
  - `RAGEventDoc` — reagiert auf Dokument-INSERT/UPDATE/DELETE-Ereignisse
  - `RAGEventFold` — reagiert auf Ordner-INSERT/UPDATE/DELETE-Ereignisse
  - `RAGSyncCron` — synchronisiert Benutzer und Gruppen alle 5 Minuten ueber SCIM mit Open WebUI
- **Unterstuetzte Formate**: pdf, doc, docx, txt, md, rtf, html, json, csv, xml, odt
- **Ressourcen**: Keine zusaetzlichen Ressourcen (laeuft innerhalb der Core-Engine-JVM)

## Bereitstellung

### Option A: Docker Compose (Empfohlen fuer die Entwicklung)

Der einfachste Weg, die vollstaendige RAG-Loesung bereitzustellen:

```bash
cd docker/

# Alle Dienste starten
docker compose up -d

# Startvorgang ueberwachen (Ollama-Modell-Download kann mehrere Minuten dauern)
docker compose logs -f

# Zugriff:
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# Open WebUI:  http://localhost:8080
```

Die docker-compose.yml stellt alle Dienste mit korrekter Startreihenfolge und Health Checks bereit. Ein einmaliger `rag-init`-Container laedt automatisch die CustomTask-JAR hoch, erstellt Event-/Cron-Task-Definitionen und richtet das Watcher-Admin-Konto in Open WebUI ein.

**Hinweis:** Beim ersten Start laedt der `ollama-pull-models`-Container das LLM-Modell (~4-5 GB) und das Embedding-Modell herunter. Dies kann je nach Internetverbindung mehrere Minuten dauern. Den Fortschritt koennen Sie mit `docker logs -f openprodoc-model-puller` verfolgen. Sobald der Download abgeschlossen ist, erscheinen die Modelle in Open WebUI und stehen zur Auswahl bereit.

#### Modelle konfigurieren

Die LLM- und Embedding-Modelle sind ueber Umgebungsvariablen konfigurierbar:

| Variable | Standard | Beschreibung |
|---|---|---|
| `LLM_MODEL` | `llama3.1:latest` | LLM-Modell fuer Chat |
| `EMBEDDING_MODEL` | `nomic-embed-text:latest` | Embedding-Modell fuer RAG |

Sie koennen diese auf verschiedene Arten ueberschreiben:

**Inline:**
```bash
LLM_MODEL=phi3 EMBEDDING_MODEL=nomic-embed-text:latest docker compose up -d
```

**Mit einer `.env`-Datei** im `docker/`-Ordner:
```
LLM_MODEL=phi3
EMBEDDING_MODEL=nomic-embed-text:latest
```

**Export:**
```bash
export LLM_MODEL=phi3
docker compose up -d
```

Wenn nichts gesetzt ist, werden die Standardwerte (`llama3.1:latest` und `nomic-embed-text:latest`) verwendet.

#### GPU-Unterstuetzung fuer Ollama

Ollama kann eine GPU nutzen, um die LLM-Inferenz erheblich zu beschleunigen. Startskripte werden bereitgestellt, die die GPU-Verfuegbarkeit automatisch erkennen und die richtige Docker Compose-Konfiguration anwenden:

| Plattform | Skript | GPU-Unterstuetzung |
|---|---|---|
| Linux | `./start-linux.sh` | NVIDIA und AMD (automatisch erkannt) |
| Windows | `start-windows.bat` | Nur NVIDIA |
| macOS | Nicht noetig — verwenden Sie direkt `docker compose up -d` | Keine (Docker Desktop laeuft in einer VM, kein GPU-Passthrough) |

**Linux:**

```bash
cd docker/
chmod +x start-linux.sh
./start-linux.sh
```

Das Skript erkennt NVIDIA-GPUs ueber `nvidia-smi` und AMD-GPUs ueber `/dev/kfd` und startet dann Docker Compose mit der entsprechenden Override-Datei (`docker-compose.nvidia.yml` oder `docker-compose.amd.yml`). Wenn keine GPU gefunden wird, startet es im reinen CPU-Modus.

**Voraussetzungen fuer die GPU-Nutzung:**
- **NVIDIA**: NVIDIA-Treiber und das [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) muessen auf dem Host installiert sein. Unterstuetzt unter Linux und Windows.
- **AMD**: ROCm-kompatible GPU und Treiber muessen installiert sein. **Nur Linux** — das Docker-Image `ollama/ollama:0.18.2-rocm` ist speziell fuer Linux-Systeme mit AMD-GPUs konzipiert und wird unter Windows oder macOS nicht unterstuetzt.

**Windows:**

```cmd
cd docker
start-windows.bat
```

Das Skript prueft ueber `nvidia-smi` auf NVIDIA-GPUs. Unter Windows wird GPU-Passthrough in Docker Desktop offiziell nur fuer NVIDIA-GPUs mit dem WSL2-Backend unterstuetzt. Es gibt kein spezialisiertes Docker-Image fuer ROCm-Beschleunigung unter Windows.

**Windows mit AMD-GPU:** Wenn Sie eine AMD Radeon GPU unter Windows haben, wird empfohlen, Ollama nativ zu installieren anstatt Docker zu verwenden:

1. Laden Sie `OllamaSetup.exe` von der [offiziellen Ollama-Website](https://ollama.com/download) herunter
2. Stellen Sie sicher, dass die neuesten AMD-Treiber installiert sind
3. Ollama erkennt Ihre kompatible Radeon-Karte automatisch
4. Konfigurieren Sie die `OLLAMA_BASE_URL` im Docker Compose `openwebui`-Dienst so, dass sie auf Ihre native Ollama-Instanz zeigt (z.B. `http://host.docker.internal:11434`) anstatt auf die containerisierte Version

**macOS:**

Es wird kein Startskript benoetigt. Docker Desktop fuer Mac fuehrt Container in einer Linux-VM aus, daher sind weder NVIDIA-, AMD- noch Apple Silicon-GPUs aus Containern zugaenglich. Fuehren Sie einfach aus:

```bash
cd docker/
docker compose up -d
```

#### Stoppen und Datenpersistenz

**Wichtig:** Seien Sie vorsichtig mit dem `-v`-Flag beim Stoppen von Diensten:

| Befehl | Auswirkung |
|---|---|
| `docker compose stop` | Stoppt Container. Kein Datenverlust. |
| `docker compose down` | Stoppt und entfernt Container und Netzwerke. **Volumes (Daten) bleiben erhalten.** |
| `docker compose down -v` | Stoppt und entfernt Container, Netzwerke **und alle Volumes. Alle Daten gehen verloren.** |

Die Verwendung von `docker compose down -v` zerstoert die folgenden benannten Volumes und alle darin enthaltenen Daten:

- **`postgres-data`** — OpenProdoc-Datenbank (Dokumenten-Metadaten, Benutzer, Konfiguration)
- **`openprodoc-storage`** — Im Dateisystem gespeicherte Dokumentdateien
- **`pgvector-data`** — RAG-Vektor-Embeddings
- **`ollama-data`** — Heruntergeladene LLM-Modelle (~4-5 GB)
- **`openwebui-data`** — Open WebUI-Einstellungen und Benutzerkonten

Verwenden Sie `docker compose down` (ohne `-v`), um alles sicher zu stoppen und Ihre Daten zu behalten.

### Option B: Kubernetes (Helm)

#### Schritt 1: Werte konfigurieren

Bearbeiten Sie `values.yaml`, um die RAG-Komponenten zu aktivieren und zu konfigurieren:

```yaml
# RAG-Komponenten aktivieren
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

#### Schritt 2: Ressourcenlimits anpassen

Passen Sie fuer Produktionsbereitstellungen die Ressourcen basierend auf Ihrer Cluster-Kapazitaet an:

```yaml
ollama:
  resources:
    limits:
      cpu: 4000m      # 4 Kerne empfohlen
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

#### Schritt 3: Bereitstellen

```bash
# Helm Chart installieren oder aktualisieren
helm upgrade --install openprodoc ./helm/openprodoc \
  --namespace openprodoc \
  --create-namespace

# Bereitstellung ueberwachen
kubectl get pods -n openprodoc -w
```

### Schritt 4: RAG-Initialisierung

Der einmalige `rag-init`-Container (Docker Compose) oder Kubernetes Job (Helm) wird nach der Bereitstellung automatisch ausgefuehrt und uebernimmt:

1. **Watcher-Admin-Konto** — Erstellt `watcher@openprodoc.local` in Open WebUI mit Administratorrechten. Dieses Konto wird vom CustomTask zur Verwaltung von Knowledge Bases, Dateien, Benutzern und Gruppen verwendet.
2. **JAR-Upload** — Laedt `openprodoc-ragtask.jar` ueber die REST-API in OpenProdoc hoch.
3. **Task-Definitionen** — Fuegt Event-Tasks (Dokument- und Ordner-INSERT/UPDATE/DELETE) und einen Cron-Task (Benutzer-/Gruppen-Synchronisation alle 5 Minuten) in die OpenProdoc-Datenbank ein.

Die Initialisierung ist **idempotent** — wenn die Tasks bereits existieren, wird sie sofort beendet, ohne Aenderungen vorzunehmen. Dies ermoeglicht sichere Wiederholungen bei `helm upgrade` oder `docker compose up`.

Nach der Bereitstellung koennen Sie sich mit den Standard-Watcher-Admin-Zugangsdaten bei Open WebUI anmelden:

- **E-Mail**: `watcher@openprodoc.local`
- **Passwort**: `12345678`

Diese Zugangsdaten sind ueber `OPENWEBUI_ADMIN_EMAIL` / `OPENWEBUI_ADMIN_PASSWORD` in Docker Compose oder `ragInit.config.watcherEmail` / `ragInit.config.watcherPassword` in Helm-Werten konfigurierbar. Aendern Sie diese fuer Produktionsbereitstellungen.

#### Automatische Benutzer- und Gruppensynchronisation

Nach der Initialisierung fuehrt der `RAGSyncCron`-Task automatisch folgende Aktionen durch:
- **Repliziert OpenProdoc-Benutzer** nach Open WebUI (alle 5 Minuten)
- **Repliziert OpenProdoc-Gruppen** ueber die SCIM-API nach Open WebUI
- **Weist Benutzer Gruppen zu**, die ihren OpenProdoc-Gruppenmitgliedschaften entsprechen

Das bedeutet, dass sich OpenProdoc-Benutzer ohne separate Registrierung bei Open WebUI anmelden koennen.

### Schritt 5: Bereitstellung ueberpruefen

#### Docker Compose

```bash
# Pruefen, ob alle Dienste laufen
docker compose ps

# Erwartet: alle Dienste "Up" oder "Up (healthy)"

# Pruefen, ob Ollama-Modelle heruntergeladen wurden
docker compose logs ollama-pull-models

# Pruefen, ob rag-init erfolgreich abgeschlossen wurde
docker compose logs rag-init

# Zugriff testen
curl -s http://localhost:8081/ProdocWeb2/ | head -5   # OpenProdoc
curl -s http://localhost:8080/health                    # Open WebUI
```

#### Kubernetes

```bash
# Pruefen, ob alle Pods laufen
kubectl get pods -n openprodoc

# Erwartete Ausgabe sollte zeigen:
# - openprodoc-core-engine-xxx (Running)
# - openprodoc-pgvector-xxx (Running)
# - openprodoc-ollama-xxx (Running)
# - openprodoc-openwebui-xxx (Running)

# Pruefen, ob der rag-init Job abgeschlossen ist
kubectl get jobs -n openprodoc
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init

# Pruefen, ob Ollama-Modelle heruntergeladen wurden
kubectl logs -n openprodoc -l app.kubernetes.io/component=ollama -c pull-models
```

### Schritt 6: Benutzerauthentifizierung und Knowledge Base-Organisation

**Automatische Benutzerreplikation**: Alle OpenProdoc-Benutzer und -Gruppen werden automatisch in der OpenWebUI-Umgebung repliziert. Das bedeutet:

- **Nahtlose Anmeldung**: OpenProdoc-Benutzer koennen sich automatisch bei OpenWebUI anmelden, ohne zusaetzliche Einrichtung oder Registrierung
- **Single Sign-On**: Benutzer-Zugangsdaten werden zwischen OpenProdoc und OpenWebUI synchronisiert
- **Gruppenmitgliedschaft**: Benutzer-Gruppen-Zuordnungen werden in beiden Systemen beibehalten

**Berechtigungsbasierte Zugriffskontrolle**:

Jeder Benutzer in OpenWebUI hat Zugriff auf Knowledge Bases basierend auf seinen OpenProdoc-Berechtigungen:

- Benutzer koennen nur auf Knowledge Bases fuer Dokumente zugreifen, fuer die sie in OpenProdoc Berechtigungen haben
- Die Zugriffskontrolle wird auf Knowledge Base-Ebene durchgesetzt
- Berechtigungen werden vom OpenProdoc-ACL-System uebernommen

**Knowledge Base-Organisation**:

Das RAG-System erstellt eine Eins-zu-eins-Zuordnung zwischen OpenProdoc-Ordnern und OpenWebUI Knowledge Bases:

- **Jeder Ordner in OpenProdoc erzeugt eine separate Knowledge Base in OpenWebUI**
- Jede Knowledge Base enthaelt das indexierte Wissen aller Dokumente innerhalb des entsprechenden OpenProdoc-Ordners
- Benutzer sehen nur die Knowledge Bases fuer Ordner, auf die sie Zugriff haben
- Diese ordnerbasierte Organisation erleichtert die Verwaltung und Abfrage fachspezifischer Dokumentensammlungen

**Beispiel**:

```
OpenProdoc-Struktur:
├── Engineering/          → Knowledge Base: "Engineering"
│   ├── specs.pdf
│   └── designs.doc
├── Marketing/            → Knowledge Base: "Marketing"
│   ├── campaigns.pptx
│   └── analytics.xlsx
└── HR/                   → Knowledge Base: "HR"
    ├── policies.pdf
    └── handbook.doc

Benutzer mit Zugriff auf die Ordner "Engineering" und "Marketing":
- Kann sich automatisch bei OpenWebUI anmelden
- Sieht 2 Knowledge Bases: "Engineering" und "Marketing"
- Kann die Knowledge Base "HR" nicht sehen oder darauf zugreifen
```

Diese Architektur stellt sicher, dass die in OpenProdoc definierten Dokumentensicherheits- und Zugriffskontrollrichtlinien nahtlos im RAG-System durchgesetzt werden.

## Verwendung

### Zugriff auf die Dienste

#### Docker Compose

| Dienst | URL | Host-Port | Container-Port |
|---|---|---|---|
| OpenProdoc | `http://localhost:8081/ProdocWeb2/` | 8081 | 8080 |
| OpenProdoc REST API | `http://localhost:8081/ProdocWeb2/APIRest/` | 8081 | 8080 |
| Open WebUI (RAG) | `http://localhost:8082` | 8082 | 8080 |
| PostgreSQL | `localhost:5433` | 5433 | 5432 |

#### Kubernetes

Wenn ingress aktiviert ist, erreichen Sie Open WebUI unter `http://localhost/rag` und OpenProdoc unter `http://localhost/`.

Wenn ingress deaktiviert ist, verwenden Sie Port-Forwarding:

```bash
kubectl port-forward svc/openprodoc-openwebui 8080:8080
kubectl port-forward svc/openprodoc-core-engine 8081:8080
```

### Knowledge Bases abfragen

Um eine Knowledge Base in einem Chat-Gespraech in Open WebUI zu verwenden:

1. Oeffnen Sie einen neuen Chat in Open WebUI
2. Geben Sie im Nachrichtenfeld **`#`** ein — ein Dropdown erscheint mit den verfuegbaren Knowledge Bases
3. Waehlen Sie die gewuenschte Knowledge Base aus (z.B. `folder1`)
4. Geben Sie Ihre Frage ein und senden Sie sie — das LLM verwendet RAG, um die ausgewaehlte Knowledge Base bei der Antwortgenerierung zu durchsuchen

Sie koennen mehrere Knowledge Bases an ein einzelnes Gespraech anhaengen, indem Sie erneut `#` eingeben und weitere auswaehlen.

### So funktioniert es

1. **Dokument-Upload**: Wenn ein Dokument in OpenProdoc eingefuegt oder aktualisiert wird, wird der `RAGEventDoc` CustomTask ausgeloest
2. **Aufnahme**: Der CustomTask laedt das Dokument ueber die API von Open WebUI hoch und fuegt es der entsprechenden Knowledge Base hinzu
3. **Verarbeitung**: Open WebUI:
   - Teilt Dokumente in Chunks auf (Standard: 1500 Zeichen mit 100 Zeichen Ueberlappung)
   - Erzeugt Embeddings mit dem `nomic-embed-text`-Modell von Ollama
   - Speichert Embeddings in der PGVector-Datenbank
4. **Abfrage**: Benutzer stellen Fragen ueber die Chat-Oberflaeche
5. **Abruf**: Open WebUI:
   - Erzeugt ein Abfrage-Embedding
   - Durchsucht PGVector nach relevanten Chunks
   - Stellt dem LLM den Kontext bereit
6. **Antwort**: Ollama generiert eine Antwort basierend auf dem abgerufenen Kontext

### Unterstuetzte Dokumenttypen

Der CustomTask verarbeitet automatisch die folgenden Dateitypen:
- Text: `.txt`, `.md`, `.rst`, `.rtf`
- Dokumente: `.pdf`, `.doc`, `.docx`
- Web: `.html`, `.htm`
- Daten: `.json`, `.csv`, `.xml`

## Konfigurationsoptionen

### LLM-Modelle aendern

Fuer bessere Leistung auf ressourcenarmen Clustern verwenden Sie Phi-3:

```yaml
ollama:
  config:
    models:
      llm: "phi3"  # Kleiner, schneller als llama3:8b
```

### RAG-Parameter anpassen

```yaml
openwebui:
  config:
    rag:
      enabled: true
      chunkSize: 1500      # Groesse der Dokument-Chunks
      chunkOverlap: 100    # Ueberlappung zwischen Chunks
```

### Speicherkonfiguration

```yaml
pgvector:
  persistence:
    size: 20Gi  # Anpassen basierend auf dem erwarteten Dokumentenvolumen

ollama:
  persistence:
    size: 50Gi  # Modelle benoetigen ~10-20GB pro Modell

openwebui:
  persistence:
    size: 5Gi   # Metadaten und Konfiguration
```

## Fehlerbehebung

### Ollama-Modelle werden nicht heruntergeladen

Init-Container-Logs pruefen:

```bash
kubectl logs -n openprodoc <ollama-pod> -c pull-models
```

Modelle sind gross (jeweils 4-8GB) und der Download kann einige Zeit dauern.

### Dokumente erscheinen nicht in Open WebUI

Pruefen Sie, ob rag-init erfolgreich abgeschlossen wurde:

```bash
# Docker Compose
docker compose logs rag-init

# Kubernetes
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init
```

Stellen Sie sicher, dass:
1. Der `rag-init`-Container/Job ohne Fehler abgeschlossen wurde
2. Das Admin-Konto `watcher@openprodoc.local` in Open WebUI existiert
3. Die CustomTask-JAR hochgeladen wurde (pruefen Sie den OpenProdoc-Systemordner)
4. Event-Tasks aktiv sind (pruefen Sie OpenProdoc Admin → Task-Verwaltung)
5. Open WebUI von der Core-Engine unter der konfigurierten URL erreichbar ist
6. Der MIME-Typ des Dokuments in der Liste der unterstuetzten Typen enthalten ist

### PGVector-Verbindungsprobleme

PGVector-Pod pruefen:

```bash
kubectl logs -n openprodoc <pgvector-pod>
kubectl exec -it -n openprodoc <pgvector-pod> -- psql -U rag_user -d rag_vectors
```

Vector-Erweiterung ueberpruefen:

```sql
\dx  -- Sollte die 'vector'-Erweiterung anzeigen
```

### Hoher Ressourcenverbrauch

Fuer CPU-eingeschraenkte Umgebungen:

1. Auf kleinere Modelle wechseln:
   ```yaml
   ollama:
     config:
       models:
         llm: "phi3"  # Anstelle von llama3:8b
   ```

2. Ressourcenlimits reduzieren:
   ```yaml
   ollama:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. CustomTask-Init deaktivieren und manuellen Dokument-Upload verwenden:
   ```yaml
   ragInit:
     enabled: false
   ```

## RAG-Komponenten deaktivieren

Um die RAG-Loesung vollstaendig zu deaktivieren:

```yaml
pgvector:
  enabled: false

ollama:
  enabled: false

openwebui:
  enabled: false
```

## Sicherheitshinweise

1. **Secrets**: Das PGVector-Passwort wird in einem Kubernetes Secret gespeichert. Aendern Sie das Standardpasswort:
   ```yaml
   pgvector:
     config:
       password: "your-secure-password"
   ```

2. **Network Policies**: Erwaegen Sie die Implementierung von Network Policies zur Einschraenkung der Pod-zu-Pod-Kommunikation

3. **API-Authentifizierung**: Konfigurieren Sie die Open WebUI-Authentifizierung in der Produktion. Nachdem rag-init abgeschlossen ist, sollten Sie `ENABLE_SIGNUP=false` und `DEFAULT_USER_ROLE=user` setzen, um unautorisierte Admin-Konten zu verhindern.

## Leistungsoptimierung

### Fuer Bereitstellungen mit hohem Volumen

1. **Ollama-Parallelitaet erhoehen**:
   ```yaml
   # Ueber Umgebungsvariable im Ollama-Deployment setzen
   OLLAMA_NUM_PARALLEL: "8"
   ```

2. **PGVector skalieren**:
   ```yaml
   pgvector:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. **Caching aktivieren**: Ollama haelt Modelle im Speicher basierend auf `OLLAMA_KEEP_ALIVE`

### Fuer ressourcenarme Bereitstellungen

1. Phi-3-Modell verwenden (kleiner und schneller)
2. Chunk-Groesse reduzieren, um weniger Embeddings zu verarbeiten
3. `ragInit` deaktivieren und manuellen Dokument-Upload ueber Open WebUI verwenden

## Ueberwachung

RAG-Komponenten ueberwachen:

```bash
# Ressourcenverbrauch
kubectl top pods -n openprodoc

# Dienststatus
kubectl get svc -n openprodoc

# Logs
kubectl logs -n openprodoc -l app.kubernetes.io/part-of=openprodoc --tail=100
```

## Weiterfuehrende Informationen

- [Open WebUI Dokumentation](https://docs.openwebui.com/)
- [Ollama Model Library](https://ollama.com/library)
- [PGVector Dokumentation](https://github.com/pgvector/pgvector)
