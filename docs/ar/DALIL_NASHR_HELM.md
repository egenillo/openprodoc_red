# دليل نشر OpenProdoc باستخدام Helm Chart

## نظرة عامة

يغطي هذا الدليل نشر نظام إدارة المحتوى المؤسسي OpenProdoc باستخدام Helm على Kubernetes (K3s أو K3d أو أي مجموعة Kubernetes).


**إصدار Chart**: 1.0.0
**إصدار التطبيق**: 3.0.4

---

## المتطلبات الأساسية

### الأدوات المطلوبة

- **مجموعة Kubernetes** (K3s أو K3d أو minikube أو مزود سحابي)
- **kubectl** - واجهة سطر أوامر Kubernetes
- **Helm 3.x** - مدير الحزم لـ Kubernetes
- **Docker** (اختياري) - مطلوب فقط لاستيراد الصور في K3d

### قاعدة البيانات المطلوبة

- **قاعدة بيانات Postgres** مطلوب وجود نسخة Postgres لنشر قاعدة بيانات openprodoc
- **نسخة قاعدة البيانات** يجب أن تحتوي قاعدة بيانات Postgres على قاعدة بيانات لنشر openprodoc
- **مستخدم مسؤول قاعدة البيانات** يجب أن تحتوي قاعدة بيانات Postgres على مستخدم لديه صلاحيات المسؤول لقاعدة بيانات openprodoc المحددة

### التحقق من المتطلبات الأساسية

```bash
# التحقق من مجموعة Kubernetes
kubectl cluster-info
kubectl get nodes

# التحقق من إصدار Helm
helm version

```


---

## طرق التثبيت

يمكن نشر OpenProdoc باستخدام ثلاث طرق:

1. **مستودع Helm** (موصى به) - التثبيت من مستودع Helm العام
2. **Chart محلي** - استخدام Charts من هذا المستودع
3. **حزمة TGZ** - تنزيل وتثبيت Chart المحزم

---

## البدء السريع (التطوير)

### الطريقة 1: التثبيت من مستودع Helm (موصى به)

```bash
# إضافة مستودع OpenProdoc Helm
helm repo add openprodoc https://egenillo.github.io/helm-charts/

# تحديث فهرس المستودع
helm repo update

# تثبيت PostgreSQL من مستودع OpenProdoc
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# تثبيت OpenProdoc من المستودع
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin


```

### الطريقة 2: التثبيت من Chart محلي

### 1. نشر قاعدة بيانات PostgreSQL

يتطلب OpenProdoc وجود PostgreSQL. قم بنشره أولاً:

```bash
# إضافة namespace لـ PostgreSQL (اختياري)
kubectl create namespace openprodoc

# تثبيت PostgreSQL باستخدام Chart المضمن
helm install openprodoc-postgresql ./helm/postgresql \
  --namespace default \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

```

### 2. نشر OpenProdoc

```bash
# الانتقال إلى مجلد helm chart

# تثبيت OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --namespace default \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

```

### الطريقة 3: التثبيت من حزمة TGZ

```bash
# الخيار أ: تنزيل TGZ من مستودع Helm
helm pull openprodoc/openprodoc --version 1.0.0

# الخيار ب: التنزيل مباشرة من إصدارات GitHub
# curl -LO https://egenillo.github.io/helm-charts/openprodoc-1.0.0.tgz

# تثبيت PostgreSQL من مستودع OpenProdoc
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# التثبيت من ملف TGZ
helm install openprodoc openprodoc-1.0.0.tgz \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# أو باستخدام ملف قيم مخصص
helm install openprodoc openprodoc-1.0.0.tgz \
  -f my-values.yaml

# مراقبة النشر
kubectl get pods -w
```

**مزايا طريقة TGZ**:
- لا حاجة لإضافة مستودع Helm
- يعمل في البيئات المعزولة عن الإنترنت
- سهل التحكم بالإصدارات والأرشفة
- يمكن تخزينه في مستودعات الحزم

### 4. الوصول إلى OpenProdoc

```bash
# إعادة توجيه المنفذ للوصول محلياً إلى التطبيق
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# الوصول عبر المتصفح محلياً:
# واجهة الويب: http://localhost:8080/ProdocWeb2/
# واجهة REST API: http://localhost:8080/ProdocWeb2/APIRest/

# بيانات الاعتماد الافتراضية:
# اسم المستخدم: root
# كلمة المرور: admin
```

للوصول عن بُعد، قم بتهيئة معلمات Ingress في values.yaml قبل النشر
---

## التهيئة

### بنية values.yaml

يستخدم Chart تهيئة هرمية:

```yaml
coreEngine:           # إعدادات التطبيق الأساسي
  replicaCount: 2     # عدد النسخ
  image:              # تهيئة صورة Docker
  service:            # خدمة Kubernetes
  config:             # تهيئة التطبيق
    database:         # اتصال PostgreSQL
    install:          # التثبيت الأولي
    repository:       # تخزين المستندات
  persistence:        # وحدات التخزين الدائمة
  resources:          # حدود المعالج/الذاكرة
```

### النشر باستخدام Docker Compose

يوفر Docker Compose بديلاً أبسط لـ Kubernetes للتطوير المحلي والنشر على خادم واحد. يقوم ملف `docker/docker-compose.yml` بنشر الحل الكامل بجميع المكونات.

#### الخدمات المنشورة

| الخدمة | الصورة | منفذ المضيف | الوصف |
|---|---|---|---|
| `postgres` | postgres:16-alpine | 5432 | قاعدة بيانات OpenProdoc |
| `core-engine` | openprodoc/core-engine:latest | **8081** | الخلفية + واجهة الويب لـ OpenProdoc |
| `pgvector` | pgvector/pgvector:pg16 | (داخلي) | قاعدة بيانات المتجهات لـ RAG |
| `ollama` | ollama/ollama:0.5.4 | (داخلي) | محرك LLM والتضمين |
| `ollama-pull-models` | curlimages/curl | - | أداة تنزيل النماذج لمرة واحدة |
| `openwebui` | ghcr.io/open-webui/open-webui:main | **8080** | واجهة RAG |
| `watcher` | openprodoc/openprodoc_rag:1.0.1 | (داخلي) | مزامنة المستندات/المستخدمين/المجموعات |

#### البدء السريع مع Docker Compose

```bash
# الانتقال إلى مجلد docker
cd docker/

# بدء جميع الخدمات
docker compose up -d

# مراقبة بدء التشغيل
docker compose logs -f

# الوصول إلى الخدمات:
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# OpenWebUI:   http://localhost:8080
```

#### الإيقاف والتنظيف

```bash
# إيقاف جميع الخدمات (مع الحفاظ على البيانات)
docker compose stop

# إيقاف وإزالة الحاويات (مع الحفاظ على وحدات التخزين)
docker compose down

# إيقاف وإزالة كل شيء بما في ذلك البيانات
docker compose down -v
```

#### صور Docker Hub

الصور متاحة على:
- `openprodoc/core-engine` - محرك OpenProdoc الأساسي
- `openprodoc/openprodoc_rag` - حاوية RAG Watcher المساعدة

**سحب الصور يدوياً**:
```bash
docker pull openprodoc/core-engine:latest
docker pull openprodoc/openprodoc_rag:1.0.1
```

#### الفروقات الرئيسية: Docker Compose مقابل Kubernetes

| الميزة | Docker Compose | Kubernetes (Helm) |
|---|---|---|
| نشر Watcher | حاوية منفصلة | Sidecar في pod الخاص بـ OpenWebUI |
| التوسع | نسخة واحدة | نسخ متعددة مع توفر عالي |
| الأسرار | متغيرات بيئة نصية عادية | Kubernetes Secrets |
| اكتشاف الخدمات | Docker DNS | Kubernetes Services |
| التخزين | وحدات تخزين Docker | PersistentVolumeClaims |
| فحوصات الصحة | Docker healthcheck | مسبارات Liveness/readiness |
| حاويات التهيئة | خدمة تنفيذ لمرة واحدة | حاويات init أصلية |
| Ingress | تعيين المنافذ | Traefik/nginx ingress |

---

## سيناريوهات النشر

### السيناريو 1: تطوير محلي باستخدام K3d (باستخدام مستودع Helm)


```bash
# إنشاء مجموعة K3d
k3d cluster create openprodoc-dev \
  --api-port 6443 \
  --servers 1 \
  --agents 2 \
  --port "8080:80@loadbalancer"

# إضافة مستودع Helm
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo update

# نشر PostgreSQL من مستودع OpenProdoc
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# نشر OpenProdoc من المستودع
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# الوصول عبر إعادة توجيه المنفذ
kubectl port-forward svc/openprodoc-core-engine 8080:8080
```


### السيناريو 2: نشر الإنتاج (باستخدام مستودع Helm)

راجع دليل نشر الإنتاج للحصول على التفاصيل.

```bash
# إنشاء namespace للإنتاج
kubectl create namespace production

# إضافة مستودع Helm
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo update

# إنشاء أسرار للبيانات الحساسة
kubectl create secret generic openprodoc-secrets \
  --namespace production \
  --from-literal=db-password='YourStrongDBPassword123!' \
  --from-literal=root-password='YourAdminPassword456!' \
  --from-literal=main-key='YourEncryptionKey32CharsLong!'

# نشر PostgreSQL من مستودع OpenProdoc
helm install openprodoc-postgresql openprodoc/openprodoc-postgresql \
  --namespace production \
  --set auth.username=prodoc \
  --set auth.password='YourStrongDBPassword123!' \
  --set auth.database=prodoc

# النشر بقيم الإنتاج من المستودع
helm install openprodoc openprodoc/openprodoc \
  --namespace production \
  --version 1.0.0 \
  --set coreEngine.image.tag=1.0.0 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=openprodoc.yourdomain.com

# مراقبة النشر
kubectl get pods -n production -w
```

**بديل: استخدام حزمة TGZ للبيئات المعزولة عن الإنترنت**
```bash
# تنزيل TGZ الخاص بـ chart
helm pull openprodoc/openprodoc --version 1.0.0

# النشر من TGZ
helm install openprodoc openprodoc-1.0.0.tgz \
  --namespace production \
  -f values-production.yaml
```

### السيناريو 3: فئة تخزين مخصصة

```bash
# إضافة المستودع
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm repo update

# النشر بفئة تخزين محددة من المستودع
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.persistence.storageClass=fast-ssd \
  --set coreEngine.persistence.size=500Gi \
  --set coreEngine.config.database.user='YourAdminDBUser' \
  --set coreEngine.config.database.password='YourPasswordDBUser' \
  --set coreEngine.install.rootPassword='YourPasswordRootUser'
```


### السيناريو 4: عقدة واحدة (موارد بحد أدنى)

```bash
# نشر بحد أدنى للاختبار من المستودع
helm repo add openprodoc https://egenillo.github.io/helm-charts/
helm install openprodoc openprodoc/openprodoc \
  --set coreEngine.replicaCount=1 \
  --set coreEngine.resources.limits.cpu=1000m \
  --set coreEngine.resources.limits.memory=2Gi \
  --set coreEngine.persistence.size=10Gi \
  --set coreEngine.config.database.user='YourAdminDBUser' \
  --set coreEngine.config.database.password='YourPasswordDBUser' \
  --set coreEngine.install.rootPassword='YourPasswordRootUser'

```

---

## مرجع أوامر Helm

### إدارة المستودع

```bash
# إضافة مستودع OpenProdoc Helm
helm repo add openprodoc https://egenillo.github.io/helm-charts/

# تحديث فهرس المستودع
helm repo update

# البحث عن Charts والإصدارات المتاحة
helm search repo openprodoc
helm search repo openprodoc --versions

# عرض معلومات Chart
helm show chart openprodoc/openprodoc
helm show values openprodoc/openprodoc
helm show readme openprodoc/openprodoc

# تنزيل Chart بدون تثبيت
helm pull openprodoc/openprodoc
helm pull openprodoc/openprodoc --version 1.0.0
helm pull openprodoc/openprodoc --untar

# إزالة المستودع
helm repo remove openprodoc
```

### التثبيت

```bash
# التثبيت من مستودع Helm (موصى به)
helm install openprodoc openprodoc/openprodoc

# التثبيت من مجلد chart محلي
helm install openprodoc ./helm/openprodoc

# التثبيت من ملف TGZ
helm install openprodoc openprodoc-1.0.0.tgz

# التثبيت بملف قيم مخصص
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# تثبيت إصدار محدد من المستودع
helm install openprodoc openprodoc/openprodoc --version 1.0.0

# التثبيت في namespace محدد
helm install openprodoc openprodoc/openprodoc \
  --namespace prod \
  --create-namespace

# تشغيل تجريبي لرؤية ما سيتم نشره
helm install openprodoc openprodoc/openprodoc --dry-run --debug
```

### إلغاء التثبيت

```bash
# إلغاء تثبيت الإصدار
helm uninstall openprodoc

# إلغاء التثبيت وحذف وحدات التخزين الدائمة
helm uninstall openprodoc
kubectl delete pvc openprodoc-storage
```



## أمثلة التخصيص

### المثال 1: ملف values.yaml مخصص

أنشئ ملف `my-values.yaml`:

```yaml
coreEngine:
  replicaCount: 3

  image:
    tag: "1.0.0"

  config:
    database:
      host: postgres.database.svc.cluster.local
      password: "securePassword123"

    install:
      rootPassword: "AdminPass456"
      defaultLang: "ES"

  persistence:
    size: 200Gi
    storageClass: "fast-storage"

  resources:
    limits:
      cpu: 4000m
      memory: 8Gi
    requests:
      cpu: 1000m
      memory: 4Gi

ingress:
  enabled: true
  hosts:
    - host: docs.mycompany.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: openprodoc-tls
      hosts:
        - docs.mycompany.com
```

النشر باستخدام:
```bash
# من مستودع Helm
helm install openprodoc openprodoc/openprodoc -f my-values.yaml

# أو من chart محلي
helm install openprodoc ./helm/openprodoc -f my-values.yaml
```


---

## استكشاف الأخطاء وإصلاحها

### التحقق من حالة Pod

```bash
# الحصول على pods
kubectl get pods -l app.kubernetes.io/name=openprodoc

# وصف pod
kubectl describe pod openprodoc-core-engine-xxx

# التحقق من السجلات
kubectl logs -f openprodoc-core-engine-xxx

# التحقق من سجلات الحاوية السابقة (في حالة التعطل)
kubectl logs openprodoc-core-engine-xxx --previous
```

### المشاكل الشائعة

#### المشكلة: Pod في حالة CrashLoopBackOff

```bash
# التحقق من السجلات
kubectl logs openprodoc-core-engine-xxx

# الأسباب الشائعة:
# 1. قاعدة البيانات غير جاهزة - تحقق من PostgreSQL
kubectl get pods -l app.kubernetes.io/name=postgresql

# 2. بيانات اعتماد قاعدة البيانات خاطئة
kubectl get secret openprodoc-secrets -o yaml

# 3. خطأ في سحب الصورة
kubectl describe pod openprodoc-core-engine-xxx | grep -A 5 Events
```

#### المشكلة: لا يمكن الاتصال بقاعدة البيانات

```bash
# اختبار الاتصال بقاعدة البيانات من pod
kubectl exec -it openprodoc-core-engine-xxx -- bash
pg_isready -h openprodoc-postgresql -p 5432 -U user1

# التحقق من الخدمة
kubectl get svc openprodoc-postgresql

# التحقق من سياسات الشبكة
kubectl get networkpolicies
```

#### المشكلة: PVC لا يرتبط

```bash
# التحقق من حالة PVC
kubectl get pvc

# التحقق من فئات التخزين
kubectl get storageclass

# وصف PVC للأحداث
kubectl describe pvc openprodoc-storage
```

### التوسع

```bash
# التوسع باستخدام kubectl
kubectl scale deployment openprodoc-core-engine --replicas=3

# التوسع باستخدام ترقية Helm
helm upgrade openprodoc ./helm/openprodoc \
  --set coreEngine.replicaCount=3
```



---

## أفضل ممارسات الأمان

### 1. تغيير كلمات المرور الافتراضية

```bash
# استخدام أسرار Kubernetes
kubectl create secret generic openprodoc-secrets \
  --from-literal=db-password='StrongPassword123!' \
  --from-literal=root-password='AdminPassword456!' \
  --from-literal=main-key='EncryptionKey32CharsHere12345'
```

### 2. استخدام علامات صور محددة

```yaml
coreEngine:
  image:
    tag: "1.0.0"  # ليس "latest"
```

### 3. تفعيل TLS لـ Ingress

```yaml
ingress:
  enabled: true
  tls:
    - secretName: openprodoc-tls
      hosts:
        - openprodoc.yourdomain.com
```

### 4. حدود الموارد

```yaml
coreEngine:
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### 5. مستخدم غير جذري

```yaml
coreEngine:
  podSecurityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
```
