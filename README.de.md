# OpenProdoc Red
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md) | [🇫🇷 Français](README.fr.md) | [🇩🇪 Deutsch](README.de.md) | [🇸🇦 العربية](README.ar.md)

## Cloud-Native Enterprise Content Management System

**OpenProdoc Red** ist eine Kubernetes-bereite Version des OpenProdoc ECM (Enterprise Content Management) Systems. Diese Edition wurde containerisiert und für Cloud-Deployment mit Helm Charts, Docker-Support und produktionsreifer Infrastruktur optimiert.

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
* **REST API aktiviert** - Vollständiger programmatischer Zugriff

### Produktionsbereite Infrastruktur
* **Mehrstufige Docker-Builds** - Optimierte Image-Größen
* **12-Faktor-App-Prinzipien** - Umgebungsbasierte Konfiguration
* **Persistente Volumes** - Sichere Dokument- und Konfigurationsspeicherung
* **Session-Affinität** - Sticky Sessions für Multi-Replica-Deployments
* **Gesundheitsprüfungen** - Kubernetes Readiness und Liveness Probes
* **Sicherheitshärtung** - Non-Root-Container, minimale Berechtigungen

----

## 📋 Kern-ECM-Funktionen

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

### Deployment-Komponenten
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

## 📡 REST API

OpenProdoc Red enthält eine vollständige REST API für programmatischen Zugriff.

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

## 🔄 Migration von klassischem OpenProdoc

OpenProdoc Red behält **volle Kompatibilität** mit bestehenden OpenProdoc-Datenbanken. Die Migration umfasst:

1. **Bestehende Datenbank exportieren** aus klassischem OpenProdoc
2. **In PostgreSQL importieren** in der neuen Umgebung
3. **Dokumentenspeicher kopieren** zum persistenten Volume
4. **Umgebungsvariablen konfigurieren** entsprechend alter Konfiguration
5. **Mit Docker Compose oder Helm deployen**

Die Anwendung erkennt die bestehende Datenbank und überspringt die Erstinstallation.

----

## 📖 Dokumentation

* **[Helm Deployment Guide](docs/HELM_DEPLOYMENT_GUIDE.md)** - Vollständiger Kubernetes-Deployment-Leitfaden
* **[REST API Nutzungshandbuch](docs/api/API_USAGE_GUIDE.md)** - Umfassende API-Referenz
* **[REST API Kurzreferenz](docs/api/API_QUICK_REFERENCE.md)** - Schnelles Befehls-Nachschlagen
* **[Dokumentations-Index](docs/README.md)** - Alle verfügbare Dokumentation

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

**Original OpenProdoc** - Erstellt von Joaquín Hierro
**OpenProdoc Red** - Cloud-native Containerisierung und Kubernetes-Deployment

Dieses Projekt behält volle Kompatibilität mit dem originalen OpenProdoc bei und bietet gleichzeitig moderne Cloud-Deployment-Funktionen.

----

## 📈 Versionsinformationen

* **Chart-Version**: 1.0.0
* **App-Version**: 3.0.3
* **Tomcat**: 9.0.x
* **PostgreSQL**: 15.x (empfohlen)
* **Java**: OpenJDK 11


