# دليل نشر OpenProdoc في بيئة الإنتاج

يقدم هذا الدليل تعليمات خطوة بخطوة لنشر OpenProdoc في بيئات الإنتاج.

## خيارات النشر

| الطريقة | الأنسب لـ |
|---|---|
| **Docker Compose** | النشر على خادم واحد، الفرق الصغيرة |
| **Kubernetes (Helm)** | المجموعات متعددة العقد، التوافر العالي، المؤسسات |

## المتطلبات الأساسية

### لـ Kubernetes (Helm)

- مجموعة Kubernetes إصدار 1.19+ (تم اختبارها على الإصدار 1.24+)
- Helm إصدار 3.2.0+
- kubectl مُهيأ مع صلاحيات الوصول إلى المجموعة
- Storage class مُهيأ (لـ PersistentVolumes)
- Ingress controller مُثبت (Traefik أو nginx)
- cert-manager (اختياري، لشهادات TLS التلقائية)
- سجل حاويات (Container registry) (في حال استخدام صور خاصة)

### لـ Docker Compose

- Docker Engine إصدار 20.10+ مع Docker Compose v2
- ذاكرة وصول عشوائي (RAM) لا تقل عن 16 جيجابايت (Ollama + نماذج LLM تستهلك ذاكرة كبيرة)
- مساحة تخزين 100 جيجابايت أو أكثر (النماذج، المستندات، قواعد البيانات)


## الخطوة 1: تجهيز بيانات الاعتماد السرية

أنشئ كلمة مرور آمنة ومفتاح تشفير:

```bash
# Generate strong passwords
export OPENPRODOC_ROOT_USER_PASSWORD=$(openssl rand -base64 16)
export ENCRYPTION_KEY=$(openssl rand -base64 32 | cut -c1-32)

echo "Save these credentials securely:"
echo "Openprodocc root user Password: $OPENPRODOC_ADMIN_USER_PASSWORD"
echo "Encryption Key: $ENCRYPTION_KEY"
```

## الخطوة 2: إنشاء ملف قيم الإنتاج

عدّل الملف `production-values.yaml` أو `values.yaml`:

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

## الخطوة 3: تثبيت OpenProdoc

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

## الخطوة 4: انتظار التثبيت الأولي

سيقوم core engine بتثبيت OpenProdoc تلقائياً عند التشغيل لأول مرة:

```bash
# Watch core engine logs
kubectl logs -f -n openprodoc -l app.kubernetes.io/component=core-engine

# Wait for message: "OpenProdoc installation completed successfully"
```

## الخطوة 5: التحقق من النشر

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

## الخطوة 6: اختبار الوصول

### Kubernetes

```bash
# Port forward to access locally
kubectl port-forward svc/openprodoc-core-engine 8081:8080
kubectl port-forward svc/openprodoc-openwebui 8080:8080

# Or if ingress is enabled:
kubectl get ingress -n openprodoc openprodoc -o jsonpath='{.spec.rules[0].host}'
```

### Docker Compose

يمكن الوصول إلى الخدمات مباشرة:
- **OpenProdoc**: `http://localhost:8081/ProdocWeb2/`
- **Open WebUI**: `http://localhost:8080`

### بيانات الاعتماد الافتراضية

- **OpenProdoc**: اسم المستخدم: `root` / كلمة المرور: `admin` (يجب تغييرها في بيئة الإنتاج)
- **Open WebUI**: أول مستخدم يسجّل يصبح مسؤولاً (استخدم `watcher@openprodoc.local` / `12345678`)

## قائمة التحقق للإنتاج

- [ ] جميع كلمات المرور قوية ومخزنة بشكل آمن (مدير كلمات المرور، sealed secrets، إلخ.)
- [ ] Storage classes مُهيأة بخصائص أداء مناسبة (Kubernetes)
- [ ] حدود الموارد (Resource limits) محددة بناءً على الحمل المتوقع
- [ ] شهادات TLS صالحة وتُجدد تلقائياً (Kubernetes مع ingress)
- [ ] حساب المسؤول `watcher@openprodoc.local` تم إنشاؤه في Open WebUI
- [ ] المستخدم `watcher` تم إنشاؤه في OpenProdoc مع صلاحيات READ ACL المناسبة
- [ ] تم تغيير SCIM token و WebUI secret key من القيم الافتراضية
- [ ] استراتيجية النسخ الاحتياطي موضوعة لـ PostgreSQL و pgvector و ollama volumes


## التوسع

### التوسع اليدوي (Kubernetes)

```bash
# Scale Core Engine
kubectl scale deployment openprodoc-core-engine -n openprodoc --replicas=3

# Or via Helm
helm upgrade openprodoc openprodoc/openprodoc \
  -f production-values.yaml \
  --set coreEngine.replicaCount=3 \
  --namespace openprodoc
```

ملاحظة: عمليات نشر Docker Compose تعمل بنسخة واحدة فقط. للتوسع بنسخ متعددة، استخدم Kubernetes.


## استكشاف الأخطاء وإصلاحها

### Pod لا يبدأ (Kubernetes)

```bash
kubectl describe pod <pod-name> -n openprodoc
kubectl logs <pod-name> -n openprodoc
```

### الحاوية لا تبدأ (Docker Compose)

```bash
docker compose logs <service-name>
docker inspect openprodoc-<service-name>
```

### مشاكل الاتصال بقاعدة البيانات

```bash
# Kubernetes
kubectl exec -it -n openprodoc openprodoc-core-engine-xxx -- \
  nc -zv openprodoc-postgresql 5432

# Docker Compose
docker compose exec core-engine bash -c "nc -zv postgres 5432"
```

### فشل مصادقة watcher

إذا أظهرت سجلات watcher رسالة `authentication failed`، تأكد من وجود المستخدم المسؤول `watcher@openprodoc.local` في Open WebUI. راجع [RAG_SETUP.md](RAG_SETUP.md#step-4-setup-rag-users) لتعليمات الإعداد.
