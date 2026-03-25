# OpenProdoc Red
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md) | [🇫🇷 Français](README.fr.md) | [🇩🇪 Deutsch](README.de.md) | [🇸🇦 العربية](README.ar.md)

## Gestión Documental en la Nube o Plataformas de Contenedores

**OpenProdoc Red** es un empaquetado en contenedores [Docker](https://es.wikipedia.org/wiki/Docker_(software)) del Gestor Documental [OpenProdoc](https://jhierrot.github.io/openprodoc/) integrado con contenedores orientados a **Inteligencia Artificial (IA)** que permiten interactuar con el repositorio Documental por medio de un chatbot avanzado. Además, el proyecto desarrollado permite incluir la información del repositorio de documentos para **personalizar las respuestas** ([RAG](https://es.wikipedia.org/wiki/Generaci%C3%B3n_aumentada_por_recuperaci%C3%B3n)) todo ello **sin necesidad de publicar la información en Internet**, usando motores locales de IA.

El uso de contenedores permite el despliegue en **entornos productivos y muy escalables** usando plataformas como [Kubernetes](https://es.wikipedia.org/wiki/Kubernetes). De acuerdo a las necesidades **puede escalarse cada uno de los componentes por separado**.

----

## 🚀 Novedades en OpenProdoc Red

### Arquitectura Nativa en la Nube
* **Listo para despliegue en Kubernetes** con Helm charts
* **Diseño centrado en contenedores** con soporte para Docker y Docker Compose
* **Alta disponibilidad** con capacidad de escalado horizontal y afinidad de sesión
* **Optimizado para PostgreSQL** para despliegues de bases de datos en la nube
* **Configuración basada en entorno** con configuraciones externalizadas

### Stack de Despliegue Moderno
* **Tomcat 9 con OpenJDK 11** - Servidor de aplicaciones estable
* **PostgreSQL 15** - Base de datos moderna con optimizaciones
* **Helm charts** - Despliegues Kubernetes listos para producción
* **Docker Compose** - Configuración fácil para desarrollo local


### Infraestructura Lista para Producción
* **Construcciones Docker multi-etapa** - Tamaños de imagen optimizados
* **Principios de aplicación 12-factor** - Configuración basada en entorno
* **Volúmenes persistentes** - Almacenamiento seguro de documentos y configuración
* **Afinidad de sesión** - Sesiones persistentes para despliegues multi-réplica
* **Verificaciones de salud** - Pruebas de preparación y actividad de Kubernetes
* **Endurecimiento de seguridad** - Contenedores sin root, permisos mínimos

### Integración con IA mediante Model Context Protocol (MCP)
* **Servidor MCP incluido** - Soporte nativo para integración con asistentes de IA
* **Listo para Claude Desktop & Claude Code** - Integración perfecta con las herramientas de IA de Anthropic
* **Cobertura completa de API** - Operaciones CRUD completas para carpetas, documentos y tesauros
* **Interfaz de lenguaje natural** - Gestione documentos usando comandos conversacionales
* **Formatos de respuesta duales** - Markdown para humanos, JSON para máquinas
* **Autenticación automática** - Gestión de credenciales basada en entorno
* **Ver [MCP/README.md](MCP/README.md)** para la guía completa de integración

### Sistema RAG Integrado (Generación Aumentada por Recuperación)
* **Búsqueda de documentos con IA** - Búsqueda semántica con consultas en lenguaje natural
* **Capacidades de preguntas y respuestas** - Haga preguntas y obtenga respuestas de sus documentos
* **Ingesta automática de documentos** - Los nuevos documentos se indexan automáticamente para RAG
* **Base de conocimientos por carpeta** - Cada carpeta de OpenProdoc se convierte en una base de conocimientos separada
* **Acceso basado en permisos** - Los usuarios solo acceden a bases de conocimientos de documentos con permisos
* **Autenticación transparente** - Los usuarios de OpenProdoc inician sesión automáticamente en la interfaz OpenWebUI
* **Integración nativa basada en eventos** - El contenedor watcher externo ha sido reemplazado por un CustomTask JAR que se ejecuta dentro de la JVM de OpenProdoc, reaccionando a eventos de documentos y carpetas en tiempo real sin contenedores adicionales
* **Sincronización automática de usuarios y grupos** - Una tarea cron integrada replica los usuarios y grupos de OpenProdoc en Open WebUI, preservando las membresías de grupo y los permisos
* **Stack de nivel producción** - Incluye PGVector, Ollama (optimizado para CPU) y Open WebUI
* **Ver [docs/RAG_SETUP.md](docs/RAG_SETUP.md)** para la guía de despliegue

----

## 📋 Características OpenProdoc

### Características Técnicas
* **Soporte multiplataforma** (Linux, Windows, Mac)
* **Soporte para múltiples bases de datos** con optimización para PostgreSQL
  * PostgreSQL (recomendado), MySQL, Oracle, DB2, SQLServer, SQLLite, HSQLDB
* **Múltiples métodos de autenticación** (LDAP, Base de datos, OS, Integrado)
* **Almacenamiento flexible de documentos**
  * Sistema de archivos (predeterminado), BLOB de base de datos, FTP, Referencia URL, Amazon S3
* **Metadatos orientados a objetos** con soporte de herencia
* **Permisos detallados** y capacidades de delegación
* **Soporte multiidioma** (Inglés, Español, Portugués, Catalán)
* **Interfaz web** (ProdocWeb2)
* **API REST** para acceso programático
* **Código abierto** bajo GNU AGPL v3

### Características de Gestión de Documentos
* **Gestión de tesauros** con soporte para estándar SKOS-RDF
* **Validación de metadatos** contra términos de tesauro
* **Control de versiones** con flujo de trabajo checkout/checkin
* **Gestión del ciclo de vida** de documentos con purgado
* **Búsqueda de texto completo** con Apache Lucene
* **Jerarquía de carpetas** con herencia de permisos
* **Capacidades de importación/exportación** de documentos



----

## 🏗️ Arquitectura

### Componentes de Despliegue OpenProdoc Red
```
┌─────────────────────────────────────┐
│      OpenProdoc Core Engine         │
│      (Tomcat 9 + ProdocWeb2)        │
│         Puerto: 8080                │
│   ┌──────────────────────────┐      │
│   │  UI Web: /ProdocWeb2/    │      │
│   │  API REST: /APIRest/     │      │
│   └──────────────────────────┘      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼────────┐
│ PostgreSQL │    │ Almacenamiento│
│ Base Datos │    │   de Archivos │
└────────────┘    └───────────────┘
```

### Arquitectura de Almacenamiento
* **Base de datos (PostgreSQL)** - Metadatos, usuarios, permisos, configuración
* **Volumen del sistema de archivos** - Binarios de documentos, encriptación configurable
* **Volúmenes persistentes** - Almacenamiento gestionado por Kubernetes para persistencia de datos

Aunque los elementos principales de la Arquitectura de OpenProdoc Red viene dados (como la base de datos), otros elementos de la [Arquitectura Estandar de OpenProdoc](https://jhierrot.github.io/openprodoc/help/ES/Architect.html) siguen estando disponibles, como las alternativas de autenticación o el almacenamiento de algunos tipos de documentos en otros repositorios.

----

## 🚢 Inicio Rápido

### Docker Compose (Recomendado para Desarrollo)

```bash
# Clonar repositorio
Clone el repositorio https://github.com/egenillo/openprodoc_red en su entorno local

# Iniciar servicios
docker-compose up -d

# Esperar inicio (2-3 minutos para instalación inicial)
docker-compose logs -f core-engine

# Acceder a la aplicación
# UI Web: http://localhost:8080/ProdocWeb2/
# API REST: http://localhost:8080/ProdocWeb2/APIRest/

# Credenciales predeterminadas
# Usuario: root
# Contraseña: admin
```

### Despliegue en Kubernetes

```bash

# Desplegar PostgreSQL
helm install openprodoc-postgresql ./helm/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# Desplegar OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# Acceso local vía port-forward
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# Acceder a la aplicación
# UI Web: http://localhost:8080/ProdocWeb2/
# API REST: http://localhost:8080/ProdocWeb2/APIRest/
```

Consulte la [Guía de Despliegue Helm](docs/HELM_DEPLOYMENT_GUIDE.md) para instrucciones detalladas.

----

## 📡 Desarrollo y API REST OpenProdoc

OpenProdoc incluye una API REST completa que se publica igualmente en los contenedores de este proyecto para facilitar el desarrollo y la integración.

### Ejemplo Rápido

```bash
# Iniciar sesión
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d "{\"Name\":\"root\",\"Password\":\"admin\"}"

# Retorna token JWT
{"Res":"OK","Token":"eyJhbGci..."}

# Usar token para solicitudes autenticadas
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

### Endpoints Disponibles

* **Gestión de sesiones** - Login, logout
* **API de carpetas** - Crear, leer, actualizar, eliminar carpetas
* **API de documentos** - Subir, descargar, buscar documentos
* **API de tesauros** - Gestionar vocabularios controlados

**Documentación**:
* [Guía de Uso de API REST](docs/api/API_USAGE_GUIDE.md) - Referencia completa con ejemplos
* [Referencia Rápida de API REST](docs/api/API_QUICK_REFERENCE.md) - Hoja de trucos de comandos
* [Colección Postman](docs/api/OpenProdoc-API-Collection.json) - Importar en herramientas de prueba de API

**Scripts de Prueba**:
* Linux/Mac: `./docs/api/test-api.sh`
* Windows: `docs/api/test-api.bat`

**Otras formas de desarrollo**:

Además del API REST, **OpenProdoc dispone de un API Java y de la posibilidad de realizar desarrollos e integraciones que incluyen TODAS las funciones, incluidas las de administración**.

La documentación completa de desarrollo OpenProdoc (Java, REST, configuración avanzada, etc) está disponible en: [Development SDK](https://jhierrot.github.io/openprodoc/Docs/OPD_Development3.0.2.html)


----

## 🛠️ Configuración

### Variables de Entorno

OpenProdoc Red utiliza variables de entorno para configuración:

```bash
# Configuración de Base de Datos
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=prodoc
DB_USER=prodoc
DB_PASSWORD=tu-contraseña-segura
DB_JDBC_CLASS=org.postgresql.Driver
DB_JDBC_URL_TEMPLATE=jdbc:postgresql://{HOST}:{PORT}/{DATABASE}

# Configuración de Instalación
INSTALL_ON_STARTUP=true
ROOT_PASSWORD=admin
DEFAULT_LANG=EN
TIMESTAMP_FORMAT="dd/MM/yyyy HH:mm:ss"
DATE_FORMAT="dd/MM/yyyy"
MAIN_KEY=uthfytnbh84kflh06fhru  # Clave de encriptación de documentos

# Configuración de Repositorio
REPO_NAME=Reposit
REPO_ENCRYPT=False
REPO_URL=/storage/OPD/
REPO_TYPE=FS  # Almacenamiento en sistema de archivos
REPO_USER=
REPO_PASSWORD=
REPO_PARAM=

# Driver JDBC
JDBC_DRIVER_PATH=./lib/postgresql-42.3.8.jar
```

### Configuración de Kubernetes

El archivo Helm values.yaml proporciona opciones de configuración completas:

```yaml
coreEngine:
  replicaCount: 2  # Alta disponibilidad

  service:
    type: ClusterIP
    port: 8080
    sessionAffinity:
      enabled: true  # Sesiones persistentes
      timeoutSeconds: 10800  # 3 horas

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

Consulte [values.yaml](helm/openprodoc/values.yaml) para todas las opciones.

----

## 📊 Monitoreo y Operaciones

### Verificaciones de Salud

```bash
# Verificar salud de la aplicación (UI web)
curl http://localhost:8080/ProdocWeb2/

# Verificar API REST
curl http://localhost:8080/ProdocWeb2/APIRest/session

# Estado del pod de Kubernetes
kubectl get pods
kubectl logs -f <nombre-pod>
```

----

## 🔒 Seguridad

### Configuración de Seguridad Predeterminada

* **Contenedores sin root** - Se ejecuta como usuario 1000
* **Capacidades mínimas** - Elimina todas las capacidades innecesarias de Linux
* **Sistema de archivos raíz de solo lectura** - Deshabilitado (requerido para directorios de trabajo de Tomcat)
* **Sin escalamiento de privilegios** - Aplicado vía contexto de seguridad

### Lista de Verificación de Seguridad en Producción

- [ ] Cambiar contraseña de administrador predeterminada (`ROOT_PASSWORD`)
- [ ] Cambiar contraseña de base de datos (`DB_PASSWORD`)
- [ ] Cambiar clave de encriptación de documentos (`MAIN_KEY`)
- [ ] Usar etiquetas de imagen específicas (no `latest`)
- [ ] Habilitar TLS/HTTPS vía Ingress
- [ ] Configurar políticas de red
- [ ] Establecer límites de recursos
- [ ] Habilitar registro de auditoría
- [ ] Actualizaciones de seguridad regulares
- [ ] Estrategia de respaldo implementada

----

## 🔄 Migración desde instalaciones OpenProdoc existentes

OpenProdoc Red mantiene el modelo de datos de OpenProdoc. Si la base de datos utilizada es PostgreSQL, **la compatibilidad es total** y la migración involucra:

1. **Exportar base de datos existente** desde OpenProdoc 
2. **Importar en PostgreSQL** en el nuevo entorno
3. **Copiar almacenamiento de documentos** al volumen persistente
4. **Configurar variables de entorno** coincidiendo con la configuración antigua
5. **Desplegar usando Docker Compose o Helm**

La aplicación detectará la base de datos existente y omitirá la instalación inicial.


**Si la instalación existente utiliza otra base de datos, tambien es posible la migración, aunque un poco más compleja.**

La recomendación sería exportar las definiciones (Usuarios, Grupos, Tipos documentales, Tareas, etc) desde las opciones de administración y luego, utilizando el cliente pesado Swing de OpenProdoc (vease las opciones de arquitectura) exportar las ramas enteras de carpetas a un sistema de archivos e importarlas al nuevo entorno, igualmente con el cliente pesado.

----

## 📖 Documentación

* **[Guía de Despliegue Helm](docs/HELM_DEPLOYMENT_GUIDE.md)** - Guía completa de despliegue en Kubernetes
* **[Guía de Uso de API REST](docs/api/API_USAGE_GUIDE.md)** - Referencia completa de API
* **[Referencia Rápida de API REST](docs/api/API_QUICK_REFERENCE.md)** - Búsqueda rápida de comandos
* **[Índice de Documentación](docs/README.md)** - Toda la documentación disponible
* **[Ayuda Online OpenProdoc](https://jhierrot.github.io/openprodoc/help/ES/HelpIndex.html)** - Ayuda de OpenProdoc tambien disponible en el menu Help tras la instalación.
* **[Manual detallado de OpenProdoc](https://jhierrot.github.io/openprodoc/Docs/Introducci%C3%B3nG.D.OpenProdoc.html)** - Un documento PDF explicando gradualmente todas las funciones de OpenProdoc, incluyendo la administración y configuración.

----

## 🧪 Pruebas

### Pruebas Automatizadas de API

```bash
# Linux/Mac
./docs/api/test-api.sh

# Windows
docs\api\test-api.bat
```

### Pruebas Manuales

1. Acceder a UI web: http://localhost:8080/ProdocWeb2/
2. Iniciar sesión con `root` / `admin`
3. Crear carpetas y subir documentos
4. Probar API REST con scripts proporcionados

----

## 📄 Licencia

OpenProdoc Red es software libre y de código abierto licenciado bajo:
* **GNU Affero General Public License v3** (AGPL-3.0)

Esta licencia asegura que cualquier modificación o servicio de red que use este software permanezca como código abierto.

----

## 🤝 Contribuciones

Se aceptan contribuciones para:
* Mejoras en despliegue de Kubernetes
* Documentación y ejemplos
* Optimizaciones de rendimiento
* Correcciones de errores y pruebas
* Backends de almacenamiento adicionales
* Integraciones con proveedores de nube

----

## 📞 Soporte

* **Documentación**: Ver carpeta `docs/`
* **Problemas**: Reportar errores y solicitudes de características
* **OpenProdoc**: https://jhierrot.github.io/openprodoc/
* **Licencia**: Licencia AGPL-3.0

----

## 🙏 Agradecimientos

**OpenProdoc** - Creado por Joaquín Hierro

**OpenProdoc Red** - Containerización nativa en la nube, capacidades de inteligencia artificial y despliegue en Kubernetes

Este proyecto mantiene compatibilidad total con el OpenProdoc original mientras proporciona capacidades modernas de despliegue en la nube.

----

## 📈 Información de Versión

* **Versión del Chart**: 1.0.0
* **Versión de la Aplicación**: 3.0.3
* **Tomcat**: 9.0.x
* **PostgreSQL**: 15.x (recomendado)
* **Java**: OpenJDK 11


