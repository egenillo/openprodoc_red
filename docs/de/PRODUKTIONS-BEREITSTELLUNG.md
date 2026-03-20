# OpenProdoc Produktionsbereitstellungsanleitung

Diese Anleitung bietet schrittweise Anweisungen fuer die Bereitstellung von OpenProdoc in Produktionsumgebungen.

## Bereitstellungsoptionen

| Methode | Geeignet fuer |
|---|---|
| **Docker Compose** | Einzelserver-Bereitstellungen, kleine Teams |
| **Kubernetes (Helm)** | Multi-Node-Cluster, Hochverfuegbarkeit, Unternehmen |

## Voraussetzungen

### Fuer Kubernetes (Helm)

- Kubernetes Cluster 1.19+ (getestet mit 1.24+)
- Helm 3.2.0+
- kubectl mit konfiguriertem Clusterzugriff
- Storage Class konfiguriert (fuer PersistentVolumes)
- Ingress Controller installiert (Traefik oder nginx)
- cert-manager (optional, fuer automatische TLS-Zertifikate)
- Container Registry (bei Verwendung privater Images)

### Fuer Docker Compose

- Docker Engine 20.10+ mit Docker Compose v2
- Mindestens 16GB RAM (Ollama + LLM-Modelle sind speicherintensiv)
- 100GB+ Speicherplatz (Modelle, Dokumente, Datenbanken)


## Schritt 1: Geheimnisse vorbereiten

Erstellen Sie ein sicheres Passwort und einen Verschluesselungsschluessel:

```bash
# Generate strong passwords
export OPENPRODOC_ROOT_USER_PASSWORD=$(openssl rand -base64 16)
export ENCRYPTION_KEY=$(openssl rand -base64 32 | cut -c1-32)

echo "Save these credentials securely:"
echo "Openprodocc root user Password: $OPENPRODOC_ADMIN_USER_PASSWORD"
echo "Encryption Key: $ENCRYPTION_KEY"
```

## Schritt 2: Produktionswerte-Datei erstellen

Bearbeiten Sie `production-values.yaml` oder `values.yaml`:

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

## Schritt 3: OpenProdoc installieren

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

## Schritt 4: Auf die Erstinstallation warten

Die Core Engine installiert OpenProdoc beim ersten Start automatisch:

```bash
# Watch core engine logs
kubectl logs -f -n openprodoc -l app.kubernetes.io/component=core-engine

# Wait for message: "OpenProdoc installation completed successfully"
```

## Schritt 5: Bereitstellung ueberpruefen

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

## Schritt 6: Zugriff testen

### Kubernetes

```bash
# Port forward to access locally
kubectl port-forward svc/openprodoc-core-engine 8081:8080
kubectl port-forward svc/openprodoc-openwebui 8080:8080

# Or if ingress is enabled:
kubectl get ingress -n openprodoc openprodoc -o jsonpath='{.spec.rules[0].host}'
```

### Docker Compose

Die Dienste sind direkt erreichbar:
- **OpenProdoc**: `http://localhost:8081/ProdocWeb2/`
- **Open WebUI**: `http://localhost:8080`

### Standard-Anmeldedaten

- **OpenProdoc**: Benutzername: `root` / Passwort: `admin` (in der Produktion aendern)
- **Open WebUI**: Der erste registrierte Benutzer wird Administrator (verwenden Sie `watcher@openprodoc.local` / `12345678`)

## Produktions-Checkliste

- [ ] Alle Passwoerter sind stark und sicher gespeichert (Passwort-Manager, Sealed Secrets usw.)
- [ ] Storage Classes sind mit geeigneten Leistungsmerkmalen konfiguriert (Kubernetes)
- [ ] Ressourcenlimits sind basierend auf der erwarteten Last festgelegt
- [ ] TLS-Zertifikate sind gueltig und werden automatisch erneuert (Kubernetes mit Ingress)
- [ ] Das Administratorkonto `watcher@openprodoc.local` wurde in Open WebUI erstellt
- [ ] Der Benutzer `watcher` wurde in OpenProdoc mit entsprechenden READ-ACL-Berechtigungen erstellt
- [ ] SCIM-Token und WebUI Secret Key wurden von den Standardwerten geaendert
- [ ] Eine Backup-Strategie fuer PostgreSQL-, pgvector- und Ollama-Volumes ist vorhanden


## Skalierung

### Manuelle Skalierung (Kubernetes)

```bash
# Scale Core Engine
kubectl scale deployment openprodoc-core-engine -n openprodoc --replicas=3

# Or via Helm
helm upgrade openprodoc openprodoc/openprodoc \
  -f production-values.yaml \
  --set coreEngine.replicaCount=3 \
  --namespace openprodoc
```

Hinweis: Docker Compose-Bereitstellungen laufen als Einzelinstanzen. Fuer die Skalierung mit mehreren Replikaten verwenden Sie Kubernetes.


## Fehlerbehebung

### Pod startet nicht (Kubernetes)

```bash
kubectl describe pod <pod-name> -n openprodoc
kubectl logs <pod-name> -n openprodoc
```

### Container startet nicht (Docker Compose)

```bash
docker compose logs <service-name>
docker inspect openprodoc-<service-name>
```

### Datenbankverbindungsprobleme

```bash
# Kubernetes
kubectl exec -it -n openprodoc openprodoc-core-engine-xxx -- \
  nc -zv openprodoc-postgresql 5432

# Docker Compose
docker compose exec core-engine bash -c "nc -zv postgres 5432"
```

### Watcher-Authentifizierungsfehler

Wenn die Watcher-Logs `authentication failed` anzeigen, stellen Sie sicher, dass der Administratorbenutzer `watcher@openprodoc.local` in Open WebUI existiert. Siehe [RAG_SETUP.md](RAG_SETUP.md#step-4-setup-rag-users) fuer Einrichtungsanweisungen.
