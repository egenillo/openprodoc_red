# Guide de configuration de la solution RAG OpenProdoc

Ce guide explique comment deployer et utiliser la solution RAG (Retrieval-Augmented Generation) integree avec OpenProdoc.

## Vue d'ensemble

La solution RAG etend OpenProdoc avec des capacites de recherche documentaire et de questions-reponses alimentees par l'IA. Elle se compose des elements principaux suivants :

1. **PGVector** - PostgreSQL avec l'extension vector pour stocker les embeddings de documents
2. **Ollama** - Moteur LLM et d'embedding fonctionnant sur CPU
3. **Open WebUI** - Interface utilisateur et orchestrateur RAG
4. **RAG CustomTask** - Gestionnaires d'evenements natifs d'OpenProdoc qui synchronisent automatiquement les documents, dossiers, utilisateurs et groupes vers Open WebUI

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

Le CustomTask s'execute au sein de la JVM d'OpenProdoc — aucun sidecar externe ni conteneur de polling n'est necessaire. Les evenements de documents et de dossiers declenchent des appels HTTP API vers Open WebUI en temps reel, et une tache cron synchronise les utilisateurs et les groupes toutes les 5 minutes via SCIM.

## Composants

### 1. PGVector (Base de donnees vectorielle)

- **Image** : `pgvector/pgvector:pg16`
- **Objectif** : Stocke les embeddings de documents pour la recherche semantique
- **Stockage** : 20Gi par defaut (configurable)
- **Ressources** : 250m CPU, 512Mi RAM (requests)

### 2. Ollama (Moteur LLM)

- **Image** : `ollama/ollama:0.18.2`
- **Modeles** :
  - LLM : `llama3.1:latest` (ou `phi3` pour une consommation de ressources reduite)
  - Embeddings : `nomic-embed-text:latest` (leger, optimise pour CPU)
- **Stockage** : 50Gi pour les modeles
- **Ressources** : 2-4 coeurs CPU, 4-8Gi RAM

### 3. Open WebUI (Interface RAG)

- **Image** : `ghcr.io/open-webui/open-webui:main`
- **Fonctionnalites** :
  - Interface de chat pour interroger les documents
  - Ingestion automatique des documents depuis le stockage OpenProdoc
  - Traitement RAG avec taille de chunk configurable
- **Stockage** : 5Gi pour les metadonnees
- **Ressources** : 500m-2000m CPU, 1-4Gi RAM

### 4. RAG CustomTask

- **Artefact** : `openprodoc-ragtask.jar` (televerse dans OpenProdoc en tant que document)
- **Objectif** : Integration pilotee par evenements qui synchronise automatiquement les documents, dossiers, utilisateurs et groupes d'OpenProdoc vers Open WebUI
- **Deploiement** : S'execute au sein de la JVM d'OpenProdoc — aucun conteneur separe requis
- **Taches** :
  - `RAGEventDoc` — reagit aux evenements INSERT/UPDATE/DELETE de documents
  - `RAGEventFold` — reagit aux evenements INSERT/UPDATE/DELETE de dossiers
  - `RAGSyncCron` — synchronise les utilisateurs et groupes vers Open WebUI toutes les 5 minutes via SCIM
- **Formats supportes** : pdf, doc, docx, txt, md, rtf, html, json, csv, xml, odt
- **Ressources** : Aucune ressource supplementaire (s'execute au sein de la JVM du core-engine)

## Deploiement

### Option A : Docker Compose (recommande pour le developpement)

La facon la plus simple de deployer la solution RAG complete :

```bash
cd docker/

# Demarrer tous les services
docker compose up -d

# Surveiller le demarrage (le telechargement du modele Ollama peut prendre plusieurs minutes)
docker compose logs -f

# Acces :
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# Open WebUI:  http://localhost:8080
```

Le fichier docker-compose.yml deploie tous les services avec un ordre de demarrage correct et des health checks. Un conteneur ephemere `rag-init` televerse automatiquement le JAR du CustomTask, cree les definitions de taches evenementielles et cron, et provisionne le compte administrateur watcher dans Open WebUI.

**Remarque :** Au premier demarrage, le conteneur `ollama-pull-models` telecharge le modele LLM (~4-5 Go) et le modele d'embedding. Cela peut prendre plusieurs minutes selon votre connexion internet. Vous pouvez suivre la progression avec `docker logs -f openprodoc-model-puller`. Une fois le telechargement termine, les modeles apparaitront dans Open WebUI et seront disponibles pour la selection.

#### Configuration des modeles

Les modeles LLM et d'embedding sont configurables via des variables d'environnement :

| Variable | Valeur par defaut | Description |
|---|---|---|
| `LLM_MODEL` | `llama3.1:latest` | Modele LLM pour le chat |
| `EMBEDDING_MODEL` | `nomic-embed-text:latest` | Modele d'embedding pour le RAG |

Vous pouvez les modifier de plusieurs facons :

**En ligne :**
```bash
LLM_MODEL=phi3 EMBEDDING_MODEL=nomic-embed-text:latest docker compose up -d
```

**Avec un fichier `.env`** dans le dossier `docker/` :
```
LLM_MODEL=phi3
EMBEDDING_MODEL=nomic-embed-text:latest
```

**Export :**
```bash
export LLM_MODEL=phi3
docker compose up -d
```

Si elles ne sont pas definies, les valeurs par defaut (`llama3.1:latest` et `nomic-embed-text:latest`) sont utilisees.

#### Support GPU pour Ollama

Ollama peut utiliser un GPU pour accelerer considerablement l'inference LLM. Des scripts de demarrage sont fournis pour detecter automatiquement la disponibilite du GPU et appliquer la configuration Docker Compose appropriee :

| Plateforme | Script | Support GPU |
|---|---|---|
| Linux | `./start-linux.sh` | NVIDIA et AMD (detection automatique) |
| Windows | `start-windows.bat` | NVIDIA uniquement |
| macOS | Non necessaire — utilisez `docker compose up -d` directement | Aucun (Docker Desktop s'execute dans une VM, pas de passthrough GPU) |

**Linux :**

```bash
cd docker/
chmod +x start-linux.sh
./start-linux.sh
```

Le script detecte les GPU NVIDIA via `nvidia-smi` et les GPU AMD via `/dev/kfd`, puis lance Docker Compose avec le fichier override approprie (`docker-compose.nvidia.yml` ou `docker-compose.amd.yml`). Si aucun GPU n'est detecte, il demarre en mode CPU uniquement.

**Prerequis pour l'utilisation du GPU :**
- **NVIDIA** : Les pilotes NVIDIA et le [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) doivent etre installes sur l'hote. Supporte sur Linux et Windows.
- **AMD** : Un GPU compatible ROCm et ses pilotes doivent etre installes. **Linux uniquement** — l'image Docker `ollama/ollama:0.18.2-rocm` est specifiquement concue pour les systemes Linux avec GPU AMD et n'est pas supportee sur Windows ou macOS.

**Windows :**

```cmd
cd docker
start-windows.bat
```

Le script verifie la presence de GPU NVIDIA via `nvidia-smi`. Sur Windows, le passthrough GPU de Docker Desktop n'est officiellement supporte que pour les GPU NVIDIA utilisant le backend WSL2. Il n'existe pas d'image Docker specialisee pour l'acceleration ROCm sur Windows.

**Windows avec GPU AMD :** Si vous disposez d'un GPU AMD Radeon sur Windows, l'approche recommandee est d'installer Ollama nativement au lieu d'utiliser Docker :

1. Telechargez `OllamaSetup.exe` depuis le [site officiel d'Ollama](https://ollama.com/download)
2. Assurez-vous d'avoir les derniers pilotes AMD installes
3. Ollama detectera automatiquement votre carte Radeon compatible
4. Configurez `OLLAMA_BASE_URL` dans le service `openwebui` du Docker Compose pour pointer vers votre instance Ollama native (par ex. `http://host.docker.internal:11434`) au lieu de l'instance conteneurisee

**macOS :**

Aucun script de demarrage n'est necessaire. Docker Desktop pour Mac execute les conteneurs dans une VM Linux, donc ni les GPU NVIDIA, AMD, ni Apple Silicon ne sont accessibles depuis les conteneurs. Executez simplement :

```bash
cd docker/
docker compose up -d
```

#### Arret et persistance des donnees

**Important :** Soyez prudent avec l'option `-v` lors de l'arret des services :

| Commande | Effet |
|---|---|
| `docker compose stop` | Arrete les conteneurs. Aucune perte de donnees. |
| `docker compose down` | Arrete et supprime les conteneurs et reseaux. **Les volumes (donnees) sont preserves.** |
| `docker compose down -v` | Arrete et supprime les conteneurs, reseaux **et tous les volumes. Toutes les donnees sont perdues.** |

L'utilisation de `docker compose down -v` detruit les volumes nommes suivants et toutes leurs donnees :

- **`postgres-data`** — Base de donnees OpenProdoc (metadonnees des documents, utilisateurs, configuration)
- **`openprodoc-storage`** — Fichiers de documents stockes sur le systeme de fichiers
- **`pgvector-data`** — Embeddings vectoriels RAG
- **`ollama-data`** — Modeles LLM telecharges (~4-5 Go)
- **`openwebui-data`** — Parametres et comptes utilisateurs d'Open WebUI

Utilisez `docker compose down` (sans `-v`) pour tout arreter en securite tout en conservant vos donnees intactes.

### Option B : Kubernetes (Helm)

#### Etape 1 : Configurer les valeurs

Editez `values.yaml` pour activer et configurer les composants RAG :

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

#### Etape 2 : Ajuster les limites de ressources

Pour les deploiements en production, ajustez les ressources en fonction de la capacite de votre cluster :

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

#### Etape 3 : Deployer

```bash
# Install or upgrade the Helm chart
helm upgrade --install openprodoc ./helm/openprodoc \
  --namespace openprodoc \
  --create-namespace

# Monitor the deployment
kubectl get pods -n openprodoc -w
```

### Etape 4 : Initialisation du RAG

Le conteneur ephemere `rag-init` (Docker Compose) ou le Job Kubernetes (Helm) s'execute automatiquement apres le deploiement et gere :

1. **Compte administrateur watcher** — Cree `watcher@openprodoc.local` dans Open WebUI avec des privileges administrateur. Ce compte est utilise par le CustomTask pour gerer les Knowledge Bases, fichiers, utilisateurs et groupes.
2. **Telechargement du JAR** — Televerse `openprodoc-ragtask.jar` dans OpenProdoc via l'API REST.
3. **Definitions des taches** — Insere les taches evenementielles (INSERT/UPDATE/DELETE de documents et dossiers) et une tache cron (synchronisation utilisateurs/groupes toutes les 5 minutes) dans la base de donnees OpenProdoc.

L'initialisation est **idempotente** — si les taches existent deja, elle se termine immediatement sans effectuer de modifications. Cela permet des re-executions securisees lors de `helm upgrade` ou `docker compose up`.

Apres le deploiement, vous pouvez vous connecter a Open WebUI avec les identifiants par defaut du compte administrateur watcher :

- **Email** : `watcher@openprodoc.local`
- **Mot de passe** : `12345678`

Ces identifiants sont configurables via `OPENWEBUI_ADMIN_EMAIL` / `OPENWEBUI_ADMIN_PASSWORD` dans Docker Compose, ou `ragInit.config.watcherEmail` / `ragInit.config.watcherPassword` dans les valeurs Helm. Modifiez-les pour les deploiements en production.

#### Synchronisation automatique des utilisateurs et des groupes

Une fois initialise, la tache `RAGSyncCron` effectue automatiquement :
- **La replication des utilisateurs OpenProdoc** vers Open WebUI (toutes les 5 minutes)
- **La replication des groupes OpenProdoc** vers Open WebUI via l'API SCIM
- **L'assignation des utilisateurs aux groupes** correspondant a leurs appartenances aux groupes OpenProdoc

Cela signifie que les utilisateurs d'OpenProdoc peuvent se connecter a Open WebUI sans inscription separee.

### Etape 5 : Verifier le deploiement

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

### Etape 6 : Authentification des utilisateurs et organisation des Knowledge Bases

**Replication automatique des utilisateurs** : Tous les utilisateurs et groupes d'OpenProdoc sont automatiquement repliques dans l'environnement OpenWebUI. Cela signifie :

- **Connexion transparente** : Les utilisateurs d'OpenProdoc peuvent se connecter automatiquement a OpenWebUI sans aucune configuration ni inscription supplementaire
- **Authentification unique** : Les identifiants des utilisateurs sont synchronises entre OpenProdoc et OpenWebUI
- **Appartenance aux groupes** : Les associations de groupes des utilisateurs sont maintenues dans les deux systemes

**Controle d'acces base sur les permissions** :

Chaque utilisateur dans OpenWebUI aura acces aux Knowledge Bases en fonction de ses permissions OpenProdoc :

- Les utilisateurs ne peuvent acceder qu'aux Knowledge Bases correspondant aux documents pour lesquels ils ont des permissions dans OpenProdoc
- Le controle d'acces est applique au niveau des Knowledge Bases
- Les permissions sont heritees du systeme ACL d'OpenProdoc

**Organisation des Knowledge Bases** :

Le systeme RAG cree une correspondance un-a-un entre les dossiers OpenProdoc et les Knowledge Bases OpenWebUI :

- **Chaque dossier dans OpenProdoc genere une Knowledge Base distincte dans OpenWebUI**
- Chaque Knowledge Base contient les connaissances indexees de tous les documents de son dossier OpenProdoc correspondant
- Les utilisateurs ne verront que les Knowledge Bases des dossiers auxquels ils ont acces
- Cette organisation par dossiers facilite la gestion et l'interrogation de collections de documents specifiques a un domaine

**Exemple** :

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

Cette architecture garantit que les politiques de securite documentaire et de controle d'acces definies dans OpenProdoc sont appliquees de maniere transparente dans le systeme RAG.

## Utilisation

### Acceder aux services

#### Docker Compose

| Service | URL | Port hote | Port conteneur |
|---|---|---|---|
| OpenProdoc | `http://localhost:8081/ProdocWeb2/` | 8081 | 8080 |
| OpenProdoc REST API | `http://localhost:8081/ProdocWeb2/APIRest/` | 8081 | 8080 |
| Open WebUI (RAG) | `http://localhost:8082` | 8082 | 8080 |
| PostgreSQL | `localhost:5433` | 5433 | 5432 |

#### Kubernetes

Si ingress est active, accedez a Open WebUI a `http://localhost/rag` et a OpenProdoc a `http://localhost/`.

Si ingress est desactive, utilisez le port-forwarding :

```bash
kubectl port-forward svc/openprodoc-openwebui 8080:8080
kubectl port-forward svc/openprodoc-core-engine 8081:8080
```

### Interroger les Knowledge Bases

Pour utiliser une Knowledge Base dans une conversation de chat dans Open WebUI :

1. Ouvrez un nouveau chat dans Open WebUI
2. Dans le champ de saisie, tapez **`#`** — un menu deroulant apparaitra listant les Knowledge Bases disponibles
3. Selectionnez la Knowledge Base souhaitee (par ex. `folder1`)
4. Tapez votre question et envoyez — le LLM utilisera le RAG pour rechercher dans la Knowledge Base selectionnee lors de la generation de sa reponse

Vous pouvez attacher plusieurs Knowledge Bases a une seule conversation en tapant `#` a nouveau et en selectionnant des Knowledge Bases supplementaires.

### Comment ca fonctionne

1. **Telechargement de document** : Lorsqu'un document est insere ou mis a jour dans OpenProdoc, le CustomTask `RAGEventDoc` se declenche
2. **Ingestion** : Le CustomTask televerse le document vers l'API d'Open WebUI et l'ajoute a la Knowledge Base correspondante
3. **Traitement** : Open WebUI :
   - Decoupe les documents en chunks (par defaut : 1500 caracteres avec 100 caracteres de chevauchement)
   - Genere les embeddings en utilisant le modele `nomic-embed-text` d'Ollama
   - Stocke les embeddings dans la base de donnees PGVector
4. **Requete** : Les utilisateurs posent des questions via l'interface de chat
5. **Recuperation** : Open WebUI :
   - Genere l'embedding de la requete
   - Recherche dans PGVector les chunks pertinents
   - Fournit le contexte au LLM
6. **Reponse** : Ollama genere une reponse basee sur le contexte recupere

### Types de documents supportes

Le CustomTask traite automatiquement ces types de fichiers :
- Texte : `.txt`, `.md`, `.rst`, `.rtf`
- Documents : `.pdf`, `.doc`, `.docx`
- Web : `.html`, `.htm`
- Donnees : `.json`, `.csv`, `.xml`

## Options de configuration

### Changer les modeles LLM

Pour de meilleures performances sur les clusters a faibles ressources, utilisez Phi-3 :

```yaml
ollama:
  config:
    models:
      llm: "phi3"  # Smaller, faster than llama3:8b
```

### Ajuster les parametres RAG

```yaml
openwebui:
  config:
    rag:
      enabled: true
      chunkSize: 1500      # Size of document chunks
      chunkOverlap: 100    # Overlap between chunks
```

### Configuration du stockage

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

## Depannage

### Les modeles Ollama ne se telechargent pas

Verifiez les logs du conteneur d'initialisation :

```bash
kubectl logs -n openprodoc <ollama-pod> -c pull-models
```

Les modeles sont volumineux (4-8 Go chacun) et peuvent prendre du temps a telecharger.

### Les documents n'apparaissent pas dans Open WebUI

Verifiez que le rag-init s'est termine avec succes :

```bash
# Docker Compose
docker compose logs rag-init

# Kubernetes
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init
```

Assurez-vous que :
1. Le conteneur/job `rag-init` s'est termine sans erreurs
2. Le compte administrateur `watcher@openprodoc.local` existe dans Open WebUI
3. Le JAR du CustomTask a ete televerse (verifiez le dossier Systeme d'OpenProdoc)
4. Les taches evenementielles sont actives (verifiez OpenProdoc Admin → Gestion des taches)
5. Open WebUI est accessible depuis le core-engine a l'URL configuree
6. Le type MIME du document est dans la liste des formats supportes

### Problemes de connexion PGVector

Verifiez le pod pgvector :

```bash
kubectl logs -n openprodoc <pgvector-pod>
kubectl exec -it -n openprodoc <pgvector-pod> -- psql -U rag_user -d rag_vectors
```

Verifiez l'extension vector :

```sql
\dx  -- Should show 'vector' extension
```

### Utilisation elevee des ressources

Pour les environnements a CPU limite :

1. Passez a des modeles plus petits :
   ```yaml
   ollama:
     config:
       models:
         llm: "phi3"  # Instead of llama3:8b
   ```

2. Reduisez les limites de ressources :
   ```yaml
   ollama:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. Desactivez l'initialisation du CustomTask et utilisez le telechargement manuel de documents :
   ```yaml
   ragInit:
     enabled: false
   ```

## Desactiver les composants RAG

Pour desactiver entierement la solution RAG :

```yaml
pgvector:
  enabled: false

ollama:
  enabled: false

openwebui:
  enabled: false
```

## Considerations de securite

1. **Secrets** : Le mot de passe PGVector est stocke dans un secret Kubernetes. Changez le mot de passe par defaut :
   ```yaml
   pgvector:
     config:
       password: "your-secure-password"
   ```

2. **Network Policies** : Envisagez d'implementer des network policies pour restreindre la communication entre pods

3. **Authentification API** : Configurez l'authentification d'Open WebUI en production. Apres la completion du rag-init, envisagez de definir `ENABLE_SIGNUP=false` et `DEFAULT_USER_ROLE=user` pour empecher la creation de comptes administrateur non autorises.

## Optimisation des performances

### Pour les deploiements a haut volume

1. **Augmenter le parallelisme d'Ollama** :
   ```yaml
   # Set via environment in ollama deployment
   OLLAMA_NUM_PARALLEL: "8"
   ```

2. **Redimensionner PGVector** :
   ```yaml
   pgvector:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. **Activer le cache** : Ollama garde les modeles en memoire en fonction de `OLLAMA_KEEP_ALIVE`

### Pour les deploiements a faibles ressources

1. Utilisez le modele Phi-3 (plus petit et plus rapide)
2. Reduisez la taille des chunks pour traiter moins d'embeddings
3. Desactivez `ragInit` et utilisez le telechargement manuel de documents via Open WebUI

## Surveillance

Surveillez les composants RAG :

```bash
# Resource usage
kubectl top pods -n openprodoc

# Service status
kubectl get svc -n openprodoc

# Logs
kubectl logs -n openprodoc -l app.kubernetes.io/part-of=openprodoc --tail=100
```

## Lectures complementaires

- [Documentation Open WebUI](https://docs.openwebui.com/)
- [Bibliotheque de modeles Ollama](https://ollama.com/library)
- [Documentation PGVector](https://github.com/pgvector/pgvector)
