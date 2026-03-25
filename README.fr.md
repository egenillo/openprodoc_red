# OpenProdoc Red
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md) | [🇫🇷 Français](README.fr.md) | [🇩🇪 Deutsch](README.de.md) | [🇸🇦 العربية](README.ar.md)

## Gestion Documentaire dans le Cloud ou Plateformes de Conteneurs

**OpenProdoc Red** est un empaquetage en conteneurs [Docker](https://fr.wikipedia.org/wiki/Docker_(logiciel)) du Système de Gestion Documentaire [OpenProdoc](https://jhierrot.github.io/openprodoc/) intégré avec des conteneurs orientés vers l'**Intelligence Artificielle (IA)** qui permettent d'interagir avec le référentiel documentaire au moyen d'un chatbot avancé. De plus, le projet développé permet d'inclure les informations du référentiel de documents pour **personnaliser les réponses** ([RAG](https://fr.wikipedia.org/wiki/G%C3%A9n%C3%A9ration_augment%C3%A9e_de_r%C3%A9cup%C3%A9ration)), le tout **sans avoir besoin de publier les informations sur Internet**, en utilisant des moteurs d'IA locaux.

L'utilisation de conteneurs permet le déploiement dans des **environnements productifs et hautement évolutifs** en utilisant des plateformes telles que [Kubernetes](https://fr.wikipedia.org/wiki/Kubernetes). Selon les besoins, **chaque composant peut être mis à l'échelle séparément**.

----

## 🚀 Nouveautés dans OpenProdoc Red

### Architecture Cloud Native
* **Prêt pour le déploiement Kubernetes** avec Helm charts
* **Conception axée sur les conteneurs** avec support Docker et Docker Compose
* **Haute disponibilité** avec capacités de mise à l'échelle horizontale et affinité de session
* **Optimisé pour PostgreSQL** pour les déploiements de bases de données cloud
* **Configuration basée sur l'environnement** avec paramètres externalisés

### Stack de Déploiement Moderne
* **Tomcat 9 avec OpenJDK 11** - Serveur d'applications stable
* **PostgreSQL 15** - Base de données moderne avec optimisations
* **Helm charts** - Déploiements Kubernetes prêts pour la production
* **Docker Compose** - Configuration facile pour le développement local


### Infrastructure Prête pour la Production
* **Builds Docker multi-étapes** - Tailles d'images optimisées
* **Principes d'application 12-factor** - Configuration basée sur l'environnement
* **Volumes persistants** - Stockage sécurisé des documents et de la configuration
* **Affinité de session** - Sessions persistantes pour les déploiements multi-répliques
* **Vérifications de santé** - Sondes de préparation et de vivacité Kubernetes
* **Durcissement de la sécurité** - Conteneurs sans root, permissions minimales

### Intégration IA avec Model Context Protocol (MCP)
* **Serveur MCP inclus** - Support natif pour l'intégration d'assistants IA
* **Prêt pour Claude Desktop & Claude Code** - Intégration transparente avec les outils IA d'Anthropic
* **Couverture API complète** - Opérations CRUD complètes pour dossiers, documents et thésaurus
* **Interface en langage naturel** - Gérez les documents avec des commandes conversationnelles
* **Formats de réponse doubles** - Markdown pour les humains, JSON pour les machines
* **Authentification automatique** - Gestion des identifiants basée sur l'environnement
* **Voir [MCP/README.md](MCP/README.md)** pour le guide d'intégration complet

### Système RAG Intégré (Génération Augmentée par Récupération)
* **Recherche de documents par IA** - Recherche sémantique avec requêtes en langage naturel
* **Capacités de questions-réponses** - Posez des questions et obtenez des réponses de vos documents
* **Ingestion automatique de documents** - Les nouveaux documents sont automatiquement indexés pour RAG
* **Base de connaissances par dossier** - Chaque dossier OpenProdoc devient une base de connaissances distincte
* **Accès basé sur les permissions** - Les utilisateurs accèdent uniquement aux bases de connaissances des documents autorisés
* **Authentification transparente** - Les utilisateurs OpenProdoc se connectent automatiquement à l'interface OpenWebUI
* **Intégration native événementielle** - Le conteneur watcher externe a été remplacé par un CustomTask JAR qui s'exécute dans la JVM d'OpenProdoc, réagissant aux événements de documents et dossiers en temps réel sans conteneurs supplémentaires
* **Synchronisation automatique des utilisateurs et groupes** - Une tâche cron intégrée réplique les utilisateurs et groupes d'OpenProdoc vers Open WebUI, en préservant les appartenances aux groupes et les permissions
* **Stack de niveau production** - Inclut PGVector, Ollama (optimisé CPU) et Open WebUI
* **Voir [docs/RAG_SETUP.md](docs/RAG_SETUP.md)** pour le guide de déploiement

----

## 📋 Fonctionnalités OpenProdoc

### Caractéristiques Techniques
* **Support multiplateforme** (Linux, Windows, Mac via conteneurs)
* **Support multi-bases de données** avec optimisation PostgreSQL
  * PostgreSQL (recommandé), MySQL, Oracle, DB2, SQLServer, SQLLite, HSQLDB
* **Méthodes d'authentification multiples** (LDAP, Base de données, OS, Intégré)
* **Stockage flexible des documents**
  * Système de fichiers (par défaut), BLOB de base de données, FTP, Référence URL, Amazon S3
* **Métadonnées orientées objet** avec support d'héritage
* **Permissions granulaires** et capacités de délégation
* **Support multilingue** (Anglais, Espagnol, Portugais, Catalan)
* **Interface web** (ProdocWeb2)
* **API REST** pour l'accès programmatique
* **Open Source** sous GNU AGPL v3

### Fonctionnalités de Gestion Documentaire
* **Gestion de thésaurus** avec support du standard SKOS-RDF
* **Validation des métadonnées** par rapport aux termes du thésaurus
* **Contrôle de version** avec workflow checkout/checkin
* **Gestion du cycle de vie** des documents avec purge
* **Recherche en texte intégral** avec Apache Lucene
* **Hiérarchie de dossiers** avec héritage des permissions
* **Capacités d'import/export** de documents

----

## 🏗️ Architecture

### Composants de Déploiement OpenProdoc Red
```
┌─────────────────────────────────────┐
│      OpenProdoc Core Engine         │
│      (Tomcat 9 + ProdocWeb2)        │
│         Port: 8080                  │
│   ┌──────────────────────────┐      │
│   │  UI Web: /ProdocWeb2/    │      │
│   │  API REST: /APIRest/     │      │
│   └──────────────────────────┘      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼────────┐
│ PostgreSQL │    │  Stockage de  │
│Base Données│    │    Fichiers   │
└────────────┘    └───────────────┘
```

### Architecture de Stockage
* **Base de données (PostgreSQL)** - Métadonnées, utilisateurs, permissions, configuration
* **Volume du système de fichiers** - Binaires des documents, chiffrement configurable
* **Volumes persistants** - Stockage géré par Kubernetes pour la persistance des données

Bien que les éléments principaux de l'Architecture d'OpenProdoc Red soient prédéfinis (comme la base de données), d'autres éléments de l'[Architecture Standard d'OpenProdoc](https://jhierrot.github.io/openprodoc/help/FR/Architect.html) restent disponibles, comme les alternatives d'authentification ou le stockage de certains types de documents dans d'autres référentiels.

----

## 🚢 Démarrage Rapide

### Docker Compose (Recommandé pour le Développement)

```bash
# Cloner le dépôt
Clonez le dépôt https://github.com/egenillo/openprodoc_red dans votre environnement local

# Démarrer les services
docker-compose up -d

# Attendre le démarrage (2-3 minutes pour l'installation initiale)
docker-compose logs -f core-engine

# Accéder à l'application
# UI Web: http://localhost:8080/ProdocWeb2/
# API REST: http://localhost:8080/ProdocWeb2/APIRest/

# Identifiants par défaut
# Utilisateur: root
# Mot de passe: admin
```

### Déploiement Kubernetes

```bash

# Déployer PostgreSQL
helm install openprodoc-postgresql ./helm/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Déployer OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# Accès local via port-forward
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# Accéder à l'application
# UI Web: http://localhost:8080/ProdocWeb2/
# API REST: http://localhost:8080/ProdocWeb2/APIRest/
```

Consultez le [Guide de Déploiement Helm](docs/HELM_DEPLOYMENT_GUIDE.md) pour des instructions détaillées.

----

## 📡 Développement et API REST OpenProdoc

OpenProdoc inclut une API REST complète qui est également publiée dans les conteneurs de ce projet pour faciliter le développement et l'intégration.

### Exemple Rapide

```bash
# Connexion
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d "{\"Name\":\"root\",\"Password\":\"admin\"}"

# Retourne un token JWT
{"Res":"OK","Token":"eyJhbGci..."}

# Utiliser le token pour les requêtes authentifiées
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

### Points de Terminaison Disponibles

* **Gestion de session** - Connexion, déconnexion
* **API des dossiers** - Créer, lire, mettre à jour, supprimer des dossiers
* **API des documents** - Téléverser, télécharger, rechercher des documents
* **API des thésaurus** - Gérer les vocabulaires contrôlés

**Documentation**:
* [Guide d'Utilisation de l'API REST](docs/api/API_USAGE_GUIDE.md) - Référence complète avec exemples
* [Référence Rapide de l'API REST](docs/api/API_QUICK_REFERENCE.md) - Aide-mémoire des commandes
* [Collection Postman](docs/api/OpenProdoc-API-Collection.json) - À importer dans les outils de test d'API

**Scripts de Test**:
* Linux/Mac: `./docs/api/test-api.sh`
* Windows: `docs/api/test-api.bat`

**Autres options de développement**:

En plus de l'API REST, **OpenProdoc dispose d'une API Java et de la possibilité de réaliser des développements et intégrations incluant TOUTES les fonctions, y compris l'administration**.

La documentation complète de développement OpenProdoc (Java, REST, configuration avancée, etc.) est disponible sur: [Development SDK](https://jhierrot.github.io/openprodoc/Docs/OPD_Development3.0.2.html)


----

## 🛠️ Configuration

### Variables d'Environnement

OpenProdoc Red utilise des variables d'environnement pour la configuration:

```bash
# Configuration de la Base de Données
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=prodoc
DB_USER=prodoc
DB_PASSWORD=votre-mot-de-passe-securise
DB_JDBC_CLASS=org.postgresql.Driver
DB_JDBC_URL_TEMPLATE=jdbc:postgresql://{HOST}:{PORT}/{DATABASE}

# Paramètres d'Installation
INSTALL_ON_STARTUP=true
ROOT_PASSWORD=admin
DEFAULT_LANG=EN
TIMESTAMP_FORMAT="dd/MM/yyyy HH:mm:ss"
DATE_FORMAT="dd/MM/yyyy"
MAIN_KEY=uthfytnbh84kflh06fhru  # Clé de chiffrement des documents

# Configuration du Dépôt
REPO_NAME=Reposit
REPO_ENCRYPT=False
REPO_URL=/storage/OPD/
REPO_TYPE=FS  # Stockage sur système de fichiers
REPO_USER=
REPO_PASSWORD=
REPO_PARAM=

# Pilote JDBC
JDBC_DRIVER_PATH=./lib/postgresql-42.3.8.jar
```

### Configuration Kubernetes

Le fichier Helm values.yaml fournit des options de configuration complètes:

```yaml
coreEngine:
  replicaCount: 2  # Haute disponibilité

  service:
    type: ClusterIP
    port: 8080
    sessionAffinity:
      enabled: true  # Sessions persistantes
      timeoutSeconds: 10800  # 3 heures

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

Consultez [values.yaml](helm/openprodoc/values.yaml) pour toutes les options.

----

## 📊 Surveillance et Opérations

### Vérifications de Santé

```bash
# Vérifier la santé de l'application (UI web)
curl http://localhost:8080/ProdocWeb2/

# Vérifier l'API REST
curl http://localhost:8080/ProdocWeb2/APIRest/session

# État du pod Kubernetes
kubectl get pods
kubectl logs -f <nom-du-pod>
```

----

## 🔒 Sécurité

### Paramètres de Sécurité par Défaut

* **Conteneurs sans root** - S'exécute en tant qu'utilisateur 1000
* **Capacités minimales** - Supprime toutes les capacités Linux inutiles
* **Système de fichiers racine en lecture seule** - Désactivé (requis pour les répertoires de travail Tomcat)
* **Pas d'escalade de privilèges** - Appliqué via le contexte de sécurité

### Liste de Vérification de Sécurité en Production

- [ ] Changer le mot de passe administrateur par défaut (`ROOT_PASSWORD`)
- [ ] Changer le mot de passe de la base de données (`DB_PASSWORD`)
- [ ] Changer la clé de chiffrement des documents (`MAIN_KEY`)
- [ ] Utiliser des tags d'image spécifiques (pas `latest`)
- [ ] Activer TLS/HTTPS via Ingress
- [ ] Configurer les politiques réseau
- [ ] Définir les limites de ressources
- [ ] Activer la journalisation d'audit
- [ ] Mises à jour de sécurité régulières
- [ ] Stratégie de sauvegarde en place

----

## 🔄 Migration depuis des Installations OpenProdoc Existantes

OpenProdoc Red maintient le modèle de données d'OpenProdoc. Si la base de données utilisée est PostgreSQL, **la compatibilité est totale** et la migration implique:

1. **Exporter la base de données existante** depuis OpenProdoc
2. **Importer dans PostgreSQL** dans le nouvel environnement
3. **Copier le stockage des documents** vers le volume persistant
4. **Configurer les variables d'environnement** correspondant à l'ancienne configuration
5. **Déployer en utilisant Docker Compose ou Helm**

L'application détectera la base de données existante et ignorera l'installation initiale.


**Si l'installation existante utilise une autre base de données, la migration est également possible, bien qu'un peu plus complexe.**

La recommandation serait d'exporter les définitions (Utilisateurs, Groupes, Types documentaires, Tâches, etc.) depuis les options d'administration, puis en utilisant le client lourd Swing d'OpenProdoc (voir les options d'architecture), d'exporter les branches entières de dossiers vers un système de fichiers et de les importer dans le nouvel environnement, également avec le client lourd.

----

## 📖 Documentation

* **[Guide de Déploiement Helm](docs/HELM_DEPLOYMENT_GUIDE.md)** - Guide complet de déploiement Kubernetes
* **[Guide d'Utilisation de l'API REST](docs/api/API_USAGE_GUIDE.md)** - Référence complète de l'API
* **[Référence Rapide de l'API REST](docs/api/API_QUICK_REFERENCE.md)** - Recherche rapide de commandes
* **[Index de Documentation](docs/README.md)** - Toute la documentation disponible
* **[Aide en Ligne OpenProdoc](https://jhierrot.github.io/openprodoc/help/FR/HelpIndex.html)** - Aide d'OpenProdoc également disponible dans le menu Aide après l'installation.
* **[Manuel Détaillé d'OpenProdoc](https://jhierrot.github.io/openprodoc/Docs/Introducci%C3%B3nG.D.OpenProdoc.html)** - Un document PDF expliquant progressivement toutes les fonctions d'OpenProdoc, y compris l'administration et la configuration.

----

## 🧪 Tests

### Tests Automatisés de l'API

```bash
# Linux/Mac
./docs/api/test-api.sh

# Windows
docs\api\test-api.bat
```

### Tests Manuels

1. Accéder à l'UI web: http://localhost:8080/ProdocWeb2/
2. Se connecter avec `root` / `admin`
3. Créer des dossiers et téléverser des documents
4. Tester l'API REST avec les scripts fournis

----

## 📄 Licence

OpenProdoc Red est un logiciel libre et open source sous licence:
* **GNU Affero General Public License v3** (AGPL-3.0)

Cette licence garantit que toute modification ou service réseau utilisant ce logiciel reste open source.

----

## 🤝 Contributions

Contributions bienvenues pour:
* Améliorations du déploiement Kubernetes
* Documentation et exemples
* Optimisations de performance
* Corrections de bugs et tests
* Backends de stockage supplémentaires
* Intégrations avec les fournisseurs cloud

----

## 📞 Support

* **Documentation**: Voir le dossier `docs/`
* **Problèmes**: Signaler les bugs et les demandes de fonctionnalités
* **OpenProdoc Original**: https://jhierrot.github.io/openprodoc/
* **Licence**: Licence AGPL-3.0

----

## 🙏 Remerciements

**OpenProdoc** - Créé par Joaquín Hierro

**OpenProdoc Red** - Conteneurisation cloud native, capacités d'intelligence artificielle et déploiement Kubernetes

Ce projet maintient une compatibilité totale avec l'OpenProdoc original tout en fournissant des capacités modernes de déploiement cloud.

----

## 📈 Informations de Version

* **Version du Chart**: 1.0.0
* **Version de l'Application**: 3.0.3
* **Tomcat**: 9.0.x
* **PostgreSQL**: 15.x (recommandé)
* **Java**: OpenJDK 11


