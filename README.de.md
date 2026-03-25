# OpenProdoc Red
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md) | [🇫🇷 Français](README.fr.md) | [🇩🇪 Deutsch](README.de.md) | [🇸🇦 العربية](README.ar.md)

## Dokumentenmanagement in der Cloud oder Container-Plattformen

**OpenProdoc Red** ist eine [Docker](https://de.wikipedia.org/wiki/Docker_(Software))-Container-Paketierung des [OpenProdoc](https://jhierrot.github.io/openprodoc/) Dokumentenmanagementsystems, integriert mit Containern für **Künstliche Intelligenz (KI)**, die eine Interaktion mit dem Dokumenten-Repository über einen fortschrittlichen Chatbot ermöglichen. Darüber hinaus ermöglicht das entwickelte Projekt die Einbeziehung von Informationen aus dem Dokumenten-Repository zur **Personalisierung der Antworten** ([RAG](https://de.wikipedia.org/wiki/Retrieval_Augmented_Generation)), und das alles **ohne die Notwendigkeit, Informationen im Internet zu veröffentlichen**, unter Verwendung lokaler KI-Engines.

Die Verwendung von Containern ermöglicht die Bereitstellung in **produktiven und hoch skalierbaren Umgebungen** unter Verwendung von Plattformen wie [Kubernetes](https://de.wikipedia.org/wiki/Kubernetes). Je nach Bedarf **kann jede einzelne Komponente separat skaliert werden**.

----

## 🚀 Neues in OpenProdoc Red

### Cloud-Native Architektur
* **Kubernetes-Deployment bereit** mit Helm Charts
* **Container-First-Design** mit Docker und Docker Compose Support
* **Hochverfügbarkeit** mit horizontalen Skalierungsmöglichkeiten und Session-Affinität
* **PostgreSQL-optimiert** für Cloud-Datenbank-Deployments
* **Umgebungsbasierte Konfiguration** mit externalisierten Einstellungen

### Moderner Deployment-Stack
* **Tomcat 9 mit OpenJDK 11** - Stabiler Applikationsserver
* **PostgreSQL 15** - Moderne Datenbank mit Optimierungen
* **Helm Charts** - Produktionsbereite Kubernetes-Deployments
* **Docker Compose** - Einfaches lokales Entwicklungs-Setup


### Produktionsbereite Infrastruktur
* **Mehrstufige Docker-Builds** - Optimierte Image-Größen
* **12-Faktor-App-Prinzipien** - Umgebungsbasierte Konfiguration
* **Persistente Volumes** - Sichere Dokument- und Konfigurationsspeicherung
* **Session-Affinität** - Sticky Sessions für Multi-Replica-Deployments
* **Gesundheitsprüfungen** - Kubernetes Readiness und Liveness Probes
* **Sicherheitshärtung** - Non-Root-Container, minimale Berechtigungen

### KI-Integration mit Model Context Protocol (MCP)
* **MCP-Server enthalten** - Native Unterstützung für KI-Assistenten-Integration
* **Bereit für Claude Desktop & Claude Code** - Nahtlose Integration mit Anthropics KI-Tools
* **Umfassende API-Abdeckung** - Vollständige CRUD-Operationen für Ordner, Dokumente und Thesaurus
* **Natürlichsprachige Schnittstelle** - Verwalten Sie Dokumente mit konversationellen Befehlen
* **Duale Antwortformate** - Markdown für Menschen, JSON für Maschinen
* **Automatische Authentifizierung** - Umgebungsbasierte Anmeldeinformationsverwaltung
* **Siehe [MCP/README.md](MCP/README.md)** für den vollständigen Integrationsleitfaden

### Integriertes RAG-System (Retrieval-Augmented Generation)
* **KI-gestützte Dokumentensuche** - Semantische Suche mit natürlichsprachigen Abfragen
* **Frage-Antwort-Funktionen** - Stellen Sie Fragen und erhalten Sie Antworten aus Ihren Dokumenten
* **Automatische Dokumentenaufnahme** - Neue Dokumente werden automatisch für RAG indiziert
* **Wissensdatenbank pro Ordner** - Jeder OpenProdoc-Ordner wird zu einer separaten Wissensdatenbank
* **Berechtigungsbasierter Zugriff** - Benutzer greifen nur auf Wissensdatenbanken für berechtigte Dokumente zu
* **Nahtlose Authentifizierung** - OpenProdoc-Benutzer melden sich automatisch bei der OpenWebUI-Oberfläche an
* **Native ereignisgesteuerte Integration** - Der externe Watcher-Container wurde durch ein CustomTask-JAR ersetzt, das in der OpenProdoc-JVM läuft und in Echtzeit auf Dokument- und Ordnerereignisse reagiert, ohne zusätzliche Container
* **Automatische Benutzer- und Gruppensynchronisation** - Ein integrierter Cron-Task repliziert OpenProdoc-Benutzer und -Gruppen nach Open WebUI und bewahrt dabei Gruppenmitgliedschaften und Berechtigungen
* **Produktionsreifer Stack** - Enthält PGVector, Ollama (CPU-optimiert) und Open WebUI
* **Siehe [docs/RAG_SETUP.md](docs/RAG_SETUP.md)** für den Deployment-Leitfaden

----

## 📋 OpenProdoc-Funktionen

### Technische Merkmale
* **Multi-Plattform-Unterstützung** (Linux, Windows, Mac via Container)
* **Multi-Datenbank-Unterstützung** mit PostgreSQL-Optimierung
  * PostgreSQL (empfohlen), MySQL, Oracle, DB2, SQLServer, SQLLite, HSQLDB
* **Mehrere Authentifizierungsmethoden** (LDAP, Datenbank, OS, Integriert)
* **Flexible Dokumentenspeicherung**
  * Dateisystem (Standard), Datenbank-BLOB, FTP, URL-Referenz, Amazon S3
* **Objektorientierte Metadaten** mit Vererbungsunterstützung
* **Feinkörnige Berechtigungen** und Delegierungsmöglichkeiten
* **Mehrsprachige Unterstützung** (Englisch, Spanisch, Portugiesisch, Katalanisch)
* **Web-Oberfläche** (ProdocWeb2)
* **REST API** für programmatischen Zugriff
* **Open Source** unter GNU AGPL v3

### Dokumentenverwaltungsfunktionen
* **Thesaurus-Verwaltung** mit SKOS-RDF-Standard-Unterstützung
* **Metadaten-Validierung** gegen Thesaurus-Begriffe
* **Versionskontrolle** mit Checkout/Checkin-Workflow
* **Dokumentenlebenszyklus**-Verwaltung mit Bereinigung
* **Volltextsuche** mit Apache Lucene
* **Ordnerhierarchie** mit Berechtigungsvererbung
* **Dokument-Import/Export**-Funktionen

----

## 🏗️ Architektur

### OpenProdoc Red Deployment-Komponenten
```
┌─────────────────────────────────────┐
│      OpenProdoc Core Engine         │
│      (Tomcat 9 + ProdocWeb2)        │
│         Port: 8080                  │
│   ┌──────────────────────────┐      │
│   │  Web UI: /ProdocWeb2/    │      │
│   │  REST API: /APIRest/     │      │
│   └──────────────────────────┘      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼────────┐
│ PostgreSQL │    │ Dateispeicher │
│  Datenbank │    │    Volume     │
└────────────┘    └───────────────┘
```

### Speicherarchitektur
* **Datenbank (PostgreSQL)** - Metadaten, Benutzer, Berechtigungen, Konfiguration
* **Dateisystem-Volume** - Dokument-Binärdateien, konfigurierbare Verschlüsselung
* **Persistente Volumes** - Kubernetes-verwaltete Speicherung für Datenpersistenz

Obwohl die Hauptelemente der OpenProdoc Red Architektur vorgegeben sind (wie die Datenbank), bleiben andere Elemente der [Standard-OpenProdoc-Architektur](https://jhierrot.github.io/openprodoc/help/EN/Architect.html) verfügbar, wie die Authentifizierungsalternativen oder die Speicherung bestimmter Dokumenttypen in anderen Repositories.

----

## 🚢 Schnellstart

### Docker Compose (Empfohlen für Entwicklung)

```bash
# Repository klonen
Klonen Sie das Repository https://github.com/egenillo/openprodoc_red in Ihre lokale Umgebung

# Services starten
docker-compose up -d

# Auf Start warten (2-3 Minuten für Erstinstallation)
docker-compose logs -f core-engine

# Auf Anwendung zugreifen
# Web UI: http://localhost:8080/ProdocWeb2/
# REST API: http://localhost:8080/ProdocWeb2/APIRest/

# Standard-Anmeldedaten
# Benutzername: root
# Passwort: admin
```

### Kubernetes-Deployment

```bash

# PostgreSQL deployen
helm install openprodoc-postgresql ./helm/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# OpenProdoc deployen
helm install openprodoc ./helm/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# Lokaler Zugriff via Port-Forward
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# Auf Anwendung zugreifen
# Web UI: http://localhost:8080/ProdocWeb2/
# REST API: http://localhost:8080/ProdocWeb2/APIRest/
```

Siehe [Helm Deployment Guide](docs/HELM_DEPLOYMENT_GUIDE.md) für detaillierte Anweisungen.

----

## 📡 Entwicklung und OpenProdoc REST API

OpenProdoc enthält eine vollständige REST API, die ebenfalls in den Containern dieses Projekts veröffentlicht wird, um die Entwicklung und Integration zu erleichtern.

### Schnelles Beispiel

```bash
# Anmelden
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d "{\"Name\":\"root\",\"Password\":\"admin\"}"

# Gibt JWT-Token zurück
{"Res":"OK","Token":"eyJhbGci..."}

# Token für authentifizierte Anfragen verwenden
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

### Verfügbare Endpoints

* **Session-Management** - Login, Logout
* **Ordner-API** - Ordner erstellen, lesen, aktualisieren, löschen
* **Dokumente-API** - Dokumente hochladen, herunterladen, suchen
* **Thesaurus-API** - Kontrollierte Vokabulare verwalten

**Dokumentation**:
* [REST API Nutzungshandbuch](docs/api/API_USAGE_GUIDE.md) - Vollständige Referenz mit Beispielen
* [REST API Kurzreferenz](docs/api/API_QUICK_REFERENCE.md) - Befehls-Cheatsheet
* [Postman Collection](docs/api/OpenProdoc-API-Collection.json) - Importieren in API-Test-Tools

**Test-Skripte**:
* Linux/Mac: `./docs/api/test-api.sh`
* Windows: `docs/api/test-api.bat`

**Weitere Entwicklungsoptionen**:

Neben der REST API verfügt **OpenProdoc über eine Java API und die Möglichkeit, Entwicklungen und Integrationen durchzuführen, die ALLE Funktionen umfassen, einschließlich der Administration**.

Die vollständige OpenProdoc-Entwicklungsdokumentation (Java, REST, erweiterte Konfiguration, etc.) ist verfügbar unter: [Development SDK](https://jhierrot.github.io/openprodoc/Docs/OPD_Development3.0.2.html)


----

## 🛠️ Konfiguration

### Umgebungsvariablen

OpenProdoc Red verwendet Umgebungsvariablen für die Konfiguration:

```bash
# Datenbank-Konfiguration
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=prodoc
DB_USER=prodoc
DB_PASSWORD=ihr-sicheres-passwort
DB_JDBC_CLASS=org.postgresql.Driver
DB_JDBC_URL_TEMPLATE=jdbc:postgresql://{HOST}:{PORT}/{DATABASE}

# Installations-Einstellungen
INSTALL_ON_STARTUP=true
ROOT_PASSWORD=admin
DEFAULT_LANG=EN
TIMESTAMP_FORMAT="dd/MM/yyyy HH:mm:ss"
DATE_FORMAT="dd/MM/yyyy"
MAIN_KEY=uthfytnbh84kflh06fhru  # Dokument-Verschlüsselungsschlüssel

# Repository-Konfiguration
REPO_NAME=Reposit
REPO_ENCRYPT=False
REPO_URL=/storage/OPD/
REPO_TYPE=FS  # Dateisystem-Speicherung
REPO_USER=
REPO_PASSWORD=
REPO_PARAM=

# JDBC-Treiber
JDBC_DRIVER_PATH=./lib/postgresql-42.3.8.jar
```

### Kubernetes-Konfiguration

Die Helm values.yaml bietet umfassende Konfigurationsoptionen:

```yaml
coreEngine:
  replicaCount: 2  # Hochverfügbarkeit

  service:
    type: ClusterIP
    port: 8080
    sessionAffinity:
      enabled: true  # Sticky Sessions
      timeoutSeconds: 10800  # 3 Stunden

  persistence:
    enabled: true
    size: 100Gi
    mountPath: /storage/OPD

  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 500m
      memory: 2Gi
```

Siehe [values.yaml](helm/openprodoc/values.yaml) für alle Optionen.

----

## 📊 Überwachung und Betrieb

### Gesundheitsprüfungen

```bash
# Anwendungsgesundheit prüfen (Web UI)
curl http://localhost:8080/ProdocWeb2/

# REST API prüfen
curl http://localhost:8080/ProdocWeb2/APIRest/session

# Kubernetes Pod-Status
kubectl get pods
kubectl logs -f <pod-name>
```

----

## 🔒 Sicherheit

### Standard-Sicherheitseinstellungen

* **Non-Root-Container** - Läuft als Benutzer 1000
* **Minimale Capabilities** - Entfernt alle unnötigen Linux-Capabilities
* **Schreibgeschütztes Root-Dateisystem** - Deaktiviert (erforderlich für Tomcat-Arbeitsverzeichnisse)
* **Keine Privilegieneskalation** - Durchgesetzt via Sicherheitskontext

### Produktions-Sicherheits-Checkliste

- [ ] Standard-Admin-Passwort ändern (`ROOT_PASSWORD`)
- [ ] Datenbank-Passwort ändern (`DB_PASSWORD`)
- [ ] Dokument-Verschlüsselungsschlüssel ändern (`MAIN_KEY`)
- [ ] Spezifische Image-Tags verwenden (nicht `latest`)
- [ ] TLS/HTTPS via Ingress aktivieren
- [ ] Netzwerk-Richtlinien konfigurieren
- [ ] Ressourcenlimits setzen
- [ ] Audit-Logging aktivieren
- [ ] Regelmäßige Sicherheitsupdates
- [ ] Backup-Strategie implementiert

----

## 🔄 Migration von bestehenden OpenProdoc-Installationen

OpenProdoc Red behält das OpenProdoc-Datenmodell bei. Wenn die verwendete Datenbank PostgreSQL ist, ist **die Kompatibilität vollständig** und die Migration umfasst:

1. **Bestehende Datenbank exportieren** aus OpenProdoc
2. **In PostgreSQL importieren** in der neuen Umgebung
3. **Dokumentenspeicher kopieren** zum persistenten Volume
4. **Umgebungsvariablen konfigurieren** entsprechend alter Konfiguration
5. **Mit Docker Compose oder Helm deployen**

Die Anwendung erkennt die bestehende Datenbank und überspringt die Erstinstallation.


**Wenn die bestehende Installation eine andere Datenbank verwendet, ist die Migration ebenfalls möglich, wenn auch etwas komplexer.**

Die Empfehlung wäre, die Definitionen (Benutzer, Gruppen, Dokumenttypen, Aufgaben, etc.) über die Administrationsoptionen zu exportieren und dann mit dem OpenProdoc Swing-Thick-Client (siehe Architekturoptionen) ganze Ordnerzweige in ein Dateisystem zu exportieren und in die neue Umgebung zu importieren, ebenfalls mit dem Thick-Client.

----

## 📖 Dokumentation

* **[Helm Deployment Guide](docs/HELM_DEPLOYMENT_GUIDE.md)** - Vollständiger Kubernetes-Deployment-Leitfaden
* **[REST API Nutzungshandbuch](docs/api/API_USAGE_GUIDE.md)** - Umfassende API-Referenz
* **[REST API Kurzreferenz](docs/api/API_QUICK_REFERENCE.md)** - Schnelles Befehls-Nachschlagen
* **[Dokumentations-Index](docs/README.md)** - Alle verfügbare Dokumentation
* **[OpenProdoc Online-Hilfe](https://jhierrot.github.io/openprodoc/help/EN/HelpIndex.html)** - OpenProdoc-Hilfe auch im Hilfe-Menü nach der Installation verfügbar.
* **[Detailliertes OpenProdoc-Handbuch](https://jhierrot.github.io/openprodoc/Docs/Introducci%C3%B3nG.D.OpenProdoc.html)** - Ein PDF-Dokument, das schrittweise alle Funktionen von OpenProdoc erklärt, einschließlich Administration und Konfiguration.

----

## 🧪 Tests

### Automatisierte API-Tests

```bash
# Linux/Mac
./docs/api/test-api.sh

# Windows
docs\api\test-api.bat
```

### Manuelle Tests

1. Web UI aufrufen: http://localhost:8080/ProdocWeb2/
2. Anmelden mit `root` / `admin`
3. Ordner erstellen und Dokumente hochladen
4. REST API mit bereitgestellten Skripten testen

----

## 📄 Lizenz

OpenProdoc Red ist freie und Open-Source-Software lizenziert unter:
* **GNU Affero General Public License v3** (AGPL-3.0)

Diese Lizenz stellt sicher, dass alle Modifikationen oder Netzwerkdienste, die diese Software verwenden, Open Source bleiben.

----

## 🤝 Beiträge

Beiträge willkommen für:
* Kubernetes-Deployment-Verbesserungen
* Dokumentation und Beispiele
* Performance-Optimierungen
* Fehlerbehebungen und Tests
* Zusätzliche Speicher-Backends
* Cloud-Provider-Integrationen

----

## 📞 Support

* **Dokumentation**: Siehe `docs/`-Ordner
* **Probleme**: Fehler und Feature-Anfragen melden
* **Original OpenProdoc**: https://jhierrot.github.io/openprodoc/
* **Lizenz**: AGPL-3.0-Lizenz

----

## 🙏 Danksagungen

**OpenProdoc** - Erstellt von Joaquín Hierro

**OpenProdoc Red** - Cloud-native Containerisierung, Fähigkeiten der künstlichen Intelligenz und Kubernetes-Deployment

Dieses Projekt behält volle Kompatibilität mit dem originalen OpenProdoc bei und bietet gleichzeitig moderne Cloud-Deployment-Funktionen.

----

## 📈 Versionsinformationen

* **Chart-Version**: 1.0.0
* **App-Version**: 3.0.3
* **Tomcat**: 9.0.x
* **PostgreSQL**: 15.x (empfohlen)
* **Java**: OpenJDK 11


