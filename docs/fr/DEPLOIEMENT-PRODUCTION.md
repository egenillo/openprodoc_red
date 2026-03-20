# Guide de déploiement en production d'OpenProdoc

Ce guide fournit des instructions étape par étape pour déployer OpenProdoc dans des environnements de production.

## Options de déploiement

| Méthode | Recommandée pour |
|---|---|
| **Docker Compose** | Déploiements sur un seul serveur, petites équipes |
| **Kubernetes (Helm)** | Clusters multi-nœuds, haute disponibilité, entreprise |

## Prérequis

### Pour Kubernetes (Helm)

- Cluster Kubernetes 1.19+ (testé sur 1.24+)
- Helm 3.2.0+
- kubectl configuré avec accès au cluster
- Storage class configurée (pour les PersistentVolumes)
- Ingress controller installé (Traefik ou nginx)
- cert-manager (optionnel, pour les certificats TLS automatiques)
- Registre de conteneurs (si vous utilisez des images privées)

### Pour Docker Compose

- Docker Engine 20.10+ avec Docker Compose v2
- Minimum 16 Go de RAM (Ollama + les modèles LLM sont gourmands en mémoire)
- 100 Go+ d'espace disque (modèles, documents, bases de données)


## Étape 1 : Préparer les secrets

Créez un mot de passe sécurisé et une clé de chiffrement :

```bash
# Generate strong passwords
export OPENPRODOC_ROOT_USER_PASSWORD=$(openssl rand -base64 16)
export ENCRYPTION_KEY=$(openssl rand -base64 32 | cut -c1-32)

echo "Save these credentials securely:"
echo "Openprodocc root user Password: $OPENPRODOC_ADMIN_USER_PASSWORD"
echo "Encryption Key: $ENCRYPTION_KEY"
```

## Étape 2 : Créer le fichier de valeurs de production

Modifiez `production-values.yaml` ou `values.yaml` :

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

## Étape 3 : Installer OpenProdoc

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

## Étape 4 : Attendre l'installation initiale

Le core engine installera automatiquement OpenProdoc au premier démarrage :

```bash
# Watch core engine logs
kubectl logs -f -n openprodoc -l app.kubernetes.io/component=core-engine

# Wait for message: "OpenProdoc installation completed successfully"
```

## Étape 5 : Vérifier le déploiement

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

## Étape 6 : Tester l'accès

### Kubernetes

```bash
# Port forward to access locally
kubectl port-forward svc/openprodoc-core-engine 8081:8080
kubectl port-forward svc/openprodoc-openwebui 8080:8080

# Or if ingress is enabled:
kubectl get ingress -n openprodoc openprodoc -o jsonpath='{.spec.rules[0].host}'
```

### Docker Compose

Les services sont directement accessibles :
- **OpenProdoc** : `http://localhost:8081/ProdocWeb2/`
- **Open WebUI** : `http://localhost:8080`

### Identifiants par défaut

- **OpenProdoc** : Nom d'utilisateur : `root` / Mot de passe : `admin` (à modifier en production)
- **Open WebUI** : Le premier utilisateur inscrit devient administrateur (utilisez `watcher@openprodoc.local` / `12345678`)

## Liste de contrôle pour la production

- [ ] Tous les mots de passe sont robustes et stockés de manière sécurisée (gestionnaire de mots de passe, sealed secrets, etc.)
- [ ] Les storage classes sont configurées avec des caractéristiques de performance appropriées (Kubernetes)
- [ ] Les limites de ressources sont définies en fonction de la charge prévue
- [ ] Les certificats TLS sont valides et se renouvellent automatiquement (Kubernetes avec ingress)
- [ ] Le compte administrateur `watcher@openprodoc.local` est créé dans Open WebUI
- [ ] L'utilisateur `watcher` est créé dans OpenProdoc avec les permissions ACL de lecture appropriées
- [ ] Le jeton SCIM et la clé secrète WebUI ont été modifiés par rapport aux valeurs par défaut
- [ ] Une stratégie de sauvegarde est en place pour les volumes PostgreSQL, pgvector et ollama


## Mise à l'échelle

### Mise à l'échelle manuelle (Kubernetes)

```bash
# Scale Core Engine
kubectl scale deployment openprodoc-core-engine -n openprodoc --replicas=3

# Or via Helm
helm upgrade openprodoc openprodoc/openprodoc \
  -f production-values.yaml \
  --set coreEngine.replicaCount=3 \
  --namespace openprodoc
```

Remarque : Les déploiements Docker Compose exécutent des instances uniques. Pour une mise à l'échelle multi-réplicas, utilisez Kubernetes.


## Dépannage

### Pod qui ne démarre pas (Kubernetes)

```bash
kubectl describe pod <pod-name> -n openprodoc
kubectl logs <pod-name> -n openprodoc
```

### Conteneur qui ne démarre pas (Docker Compose)

```bash
docker compose logs <service-name>
docker inspect openprodoc-<service-name>
```

### Problèmes de connexion à la base de données

```bash
# Kubernetes
kubectl exec -it -n openprodoc openprodoc-core-engine-xxx -- \
  nc -zv openprodoc-postgresql 5432

# Docker Compose
docker compose exec core-engine bash -c "nc -zv postgres 5432"
```

### Échecs d'authentification du watcher

Si les journaux du watcher affichent `authentication failed`, assurez-vous que l'utilisateur administrateur `watcher@openprodoc.local` existe dans Open WebUI. Consultez [RAG_SETUP.md](RAG_SETUP.md#step-4-setup-rag-users) pour les instructions de configuration.
