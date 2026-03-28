# دليل إعداد حل RAG في OpenProdoc

يشرح هذا الدليل كيفية نشر واستخدام حل RAG (Retrieval-Augmented Generation) المتكامل مع OpenProdoc.

## نظرة عامة

يوسّع حل RAG إمكانيات OpenProdoc بقدرات البحث في المستندات والإجابة على الأسئلة المدعومة بالذكاء الاصطناعي. يتكون من المكونات الرئيسية التالية:

1. **PGVector** - PostgreSQL مع إضافة المتجهات لتخزين تضمينات المستندات
2. **Ollama** - محرك LLM والتضمينات يعمل على المعالج المركزي
3. **Open WebUI** - واجهة المستخدم ومنسق RAG
4. **RAG CustomTask** - معالجات أحداث أصلية في OpenProdoc تقوم تلقائياً بمزامنة المستندات والمجلدات والمستخدمين والمجموعات مع Open WebUI

## البنية المعمارية

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

يعمل CustomTask داخل JVM الخاص بـ OpenProdoc — لا حاجة لحاوية جانبية خارجية أو حاوية استقصاء. تُطلق أحداث المستندات والمجلدات استدعاءات HTTP API إلى Open WebUI في الوقت الفعلي، وتقوم مهمة cron بمزامنة المستخدمين والمجموعات كل 5 دقائق عبر SCIM.

## المكونات

### 1. PGVector (قاعدة بيانات المتجهات)

- **الصورة**: `pgvector/pgvector:pg16`
- **الغرض**: تخزين تضمينات المستندات للبحث الدلالي
- **التخزين**: 20Gi افتراضياً (قابل للتعديل)
- **الموارد**: 250m CPU، 512Mi RAM (الحد الأدنى المطلوب)

### 2. Ollama (محرك LLM)

- **الصورة**: `ollama/ollama:0.18.2`
- **النماذج**:
  - LLM: `llama3.1:latest` (أو `phi3` لاستخدام موارد أقل)
  - التضمينات: `nomic-embed-text:latest` (خفيف، محسّن للمعالج المركزي)
- **التخزين**: 50Gi للنماذج
- **الموارد**: 2-4 أنوية معالج، 4-8Gi ذاكرة

### 3. Open WebUI (واجهة RAG)

- **الصورة**: `ghcr.io/open-webui/open-webui:main`
- **الميزات**:
  - واجهة محادثة للاستعلام عن المستندات
  - استيعاب تلقائي للمستندات من مخزن OpenProdoc
  - معالجة RAG بحجم قطع قابل للتعديل
- **التخزين**: 5Gi للبيانات الوصفية
- **الموارد**: 500m-2000m CPU، 1-4Gi RAM

### 4. RAG CustomTask

- **الحزمة**: `openprodoc-ragtask.jar` (يتم رفعها إلى OpenProdoc كمستند)
- **الغرض**: تكامل مبني على الأحداث يقوم تلقائياً بمزامنة المستندات والمجلدات والمستخدمين والمجموعات من OpenProdoc إلى Open WebUI
- **النشر**: يعمل داخل JVM الخاص بـ OpenProdoc — لا حاجة لحاوية منفصلة
- **المهام**:
  - `RAGEventDoc` — يستجيب لأحداث INSERT/UPDATE/DELETE على المستندات
  - `RAGEventFold` — يستجيب لأحداث INSERT/UPDATE/DELETE على المجلدات
  - `RAGSyncCron` — يزامن المستخدمين والمجموعات مع Open WebUI كل 5 دقائق عبر SCIM
- **التنسيقات المدعومة**: pdf, doc, docx, txt, md, rtf, html, json, csv, xml, odt
- **الموارد**: لا موارد إضافية (يعمل ضمن JVM للمحرك الأساسي)

## النشر

### الخيار أ: Docker Compose (موصى به للتطوير)

أبسط طريقة لنشر حل RAG الكامل:

```bash
cd docker/

# بدء جميع الخدمات
docker compose up -d

# مراقبة بدء التشغيل (سحب نموذج Ollama قد يستغرق عدة دقائق)
docker compose logs -f

# الوصول:
# OpenProdoc:  http://localhost:8081/ProdocWeb2/
# Open WebUI:  http://localhost:8080
```

ينشر ملف docker-compose.yml جميع الخدمات بترتيب بدء صحيح وفحوصات صحية. تقوم حاوية `rag-init` ذات التشغيل الواحد تلقائياً برفع ملف CustomTask JAR وإنشاء تعريفات مهام الأحداث/cron وتوفير حساب مسؤول المراقب في Open WebUI.

**ملاحظة:** عند التشغيل لأول مرة، تقوم حاوية `ollama-pull-models` بتنزيل نموذج LLM (حوالي 4-5 جيجابايت) ونموذج التضمين. قد يستغرق هذا عدة دقائق حسب سرعة اتصالك بالإنترنت. يمكنك مراقبة التقدم باستخدام `docker logs -f openprodoc-model-puller`. بمجرد اكتمال التنزيل، ستظهر النماذج في Open WebUI وتكون متاحة للاختيار.

#### تهيئة النماذج

يمكن تهيئة نماذج LLM والتضمين عبر متغيرات البيئة:

| المتغير | القيمة الافتراضية | الوصف |
|---|---|---|
| `LLM_MODEL` | `llama3.1:latest` | نموذج LLM للمحادثة |
| `EMBEDDING_MODEL` | `nomic-embed-text:latest` | نموذج التضمين لـ RAG |

يمكنك تجاوزها بعدة طرق:

**مباشرة:**
```bash
LLM_MODEL=phi3 EMBEDDING_MODEL=nomic-embed-text:latest docker compose up -d
```

**باستخدام ملف `.env`** في مجلد `docker/`:
```
LLM_MODEL=phi3
EMBEDDING_MODEL=nomic-embed-text:latest
```

**التصدير:**
```bash
export LLM_MODEL=phi3
docker compose up -d
```

إذا لم يتم تعيينها، يتم استخدام القيم الافتراضية (`llama3.1:latest` و `nomic-embed-text:latest`).

#### دعم GPU واختيار صورة Ollama

يمكن لـ Ollama استخدام GPU لتسريع استدلال LLM بشكل كبير. يتم توفير سكربتات بدء للكشف التلقائي عن توفر GPU وتطبيق تهيئة Docker Compose المناسبة.

**خيارات صورة Ollama:**

| الصورة | الحجم | حالة الاستخدام |
|---|---|---|
| `ollama/ollama:0.18.2` | **~3.86 جيجابايت** | صورة كاملة مع تعريفات GPU لـ NVIDIA و AMD. تُستخدم عند توفر GPU. |
| `alpine/ollama:0.18.2` | **~70 ميجابايت** | صورة مُصغّرة للمعالج المركزي فقط بدون تعريفات GPU. تُستخدم عند عدم توفر GPU. |

عندما لا يتم الكشف عن GPU، تستخدم سكربتات البدء تلقائياً صورة `alpine/ollama` الخفيفة عبر ملف التجاوز `docker-compose.cpu-light.yml`، مما يتجنب تنزيل 3.86 جيجابايت لا يفيد بدون GPU.

**خيارات سكربتات البدء:**

| المنصة | السكربت | دعم GPU |
|---|---|---|
| Linux | `./start-linux.sh` | NVIDIA و AMD (كشف تلقائي) |
| Windows | `start-windows.bat` | NVIDIA فقط |
| macOS | غير مطلوب — استخدم `docker compose up -d` مباشرة | لا يوجد (Docker Desktop يعمل في VM، لا يوجد تمرير GPU) |

تقبل السكربتات معاملاً اختيارياً لفرض وضع محدد:

```bash
./start-linux.sh              # كشف تلقائي: GPU → صورة كاملة، بدون GPU → alpine
./start-linux.sh --light      # فرض alpine/ollama (~70 ميجابايت، معالج مركزي فقط)
./start-linux.sh --cpu        # فرض ollama/ollama (~3.86 جيجابايت، وضع المعالج المركزي، بدون تجاوز GPU)
./start-linux.sh --nvidia     # فرض وضع NVIDIA GPU
./start-linux.sh --amd        # فرض وضع AMD GPU (Linux فقط)
```

```cmd
start-windows.bat             # كشف تلقائي: NVIDIA → صورة كاملة، بدون GPU → alpine
start-windows.bat --light     # فرض alpine/ollama (~70 ميجابايت، معالج مركزي فقط)
start-windows.bat --cpu       # فرض ollama/ollama (~3.86 جيجابايت، وضع المعالج المركزي)
start-windows.bat --nvidia    # فرض وضع NVIDIA GPU
```

**Linux:**

```bash
cd docker/
chmod +x start-linux.sh
./start-linux.sh
```

يكشف السكربت عن وحدات NVIDIA GPU عبر `nvidia-smi` ووحدات AMD GPU عبر `/dev/kfd`، ثم يطلق Docker Compose مع ملف التجاوز المناسب (`docker-compose.nvidia.yml` أو `docker-compose.amd.yml`). إذا لم يتم العثور على GPU، يستخدم `docker-compose.cpu-light.yml` للتبديل إلى صورة `alpine/ollama` الخفيفة.

**المتطلبات الأساسية لاستخدام GPU:**
- **NVIDIA**: يجب تثبيت تعريفات NVIDIA و [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) على الجهاز المضيف. مدعوم على Linux و Windows.
- **AMD**: يجب تثبيت GPU متوافق مع ROCm والتعريفات. **Linux فقط** — صورة Docker `ollama/ollama:0.18.2-rocm` مصممة خصيصاً لأنظمة Linux مع وحدات AMD GPU وغير مدعومة على Windows أو macOS.

**Windows:**

```cmd
cd docker
start-windows.bat
```

يتحقق السكربت من وجود NVIDIA GPU عبر `nvidia-smi`. إذا لم يتم العثور على GPU، يستخدم `alpine/ollama` (~70 ميجابايت) بدلاً من الصورة الكاملة (~3.86 جيجابايت). على Windows، تمرير GPU في Docker Desktop مدعوم رسمياً فقط لوحدات NVIDIA GPU باستخدام واجهة WSL2 الخلفية. لا توجد صورة Docker متخصصة لتسريع ROCm على Windows.

**Windows مع AMD GPU:** إذا كان لديك AMD Radeon GPU على Windows، فالنهج الموصى به هو تثبيت Ollama محلياً بدلاً من استخدام Docker:

1. قم بتنزيل `OllamaSetup.exe` من [موقع Ollama الرسمي](https://ollama.com/download)
2. تأكد من تثبيت أحدث تعريفات AMD
3. سيكتشف Ollama تلقائياً بطاقة Radeon المتوافقة
4. قم بتهيئة `OLLAMA_BASE_URL` في خدمة `openwebui` في Docker Compose للإشارة إلى نسخة Ollama المحلية (مثل `http://host.docker.internal:11434`) بدلاً من النسخة المحتواة

**macOS:**

لا حاجة لسكربت بدء. يعمل Docker Desktop لنظام Mac بتشغيل الحاويات داخل VM يعمل بنظام Linux، لذا لا يمكن الوصول إلى وحدات NVIDIA أو AMD أو Apple Silicon GPU من الحاويات. ببساطة قم بتشغيل:

```bash
cd docker/
docker compose up -d
```

#### الإيقاف واستمرارية البيانات

**مهم:** كن حذراً مع علامة `-v` عند إيقاف الخدمات:

| الأمر | التأثير |
|---|---|
| `docker compose stop` | يوقف الحاويات. لا فقدان للبيانات. |
| `docker compose down` | يوقف ويزيل الحاويات والشبكات. **يتم الاحتفاظ بالأقراص (البيانات).** |
| `docker compose down -v` | يوقف ويزيل الحاويات والشبكات **وجميع الأقراص. تُفقد جميع البيانات.** |

استخدام `docker compose down -v` يدمر الأقراص المسماة التالية وجميع بياناتها:

- **`postgres-data`** — قاعدة بيانات OpenProdoc (بيانات المستندات الوصفية، المستخدمون، التهيئة)
- **`openprodoc-storage`** — ملفات المستندات المخزنة في نظام الملفات
- **`pgvector-data`** — تضمينات RAG المتجهية
- **`ollama-data`** — نماذج LLM المُنزّلة (حوالي 4-5 جيجابايت)
- **`openwebui-data`** — إعدادات Open WebUI وحسابات المستخدمين

استخدم `docker compose down` (بدون `-v`) لإيقاف كل شيء بأمان مع الحفاظ على بياناتك سليمة.

### الخيار ب: Kubernetes (Helm)

#### الخطوة 1: تهيئة القيم

قم بتحرير `values.yaml` لتفعيل وتهيئة مكونات RAG:

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

#### الخطوة 2: ضبط حدود الموارد

لبيئات الإنتاج، اضبط الموارد بناءً على سعة المجموعة:

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

#### الخطوة 3: النشر

```bash
# Install or upgrade the Helm chart
helm upgrade --install openprodoc ./helm/openprodoc \
  --namespace openprodoc \
  --create-namespace

# Monitor the deployment
kubectl get pods -n openprodoc -w
```

### الخطوة 4: تهيئة RAG

تعمل حاوية `rag-init` ذات التشغيل الواحد (Docker Compose) أو Kubernetes Job (Helm) تلقائياً بعد النشر وتتولى:

1. **حساب مسؤول المراقب** — إنشاء `watcher@openprodoc.local` في Open WebUI بصلاحيات المسؤول. يُستخدم هذا الحساب بواسطة CustomTask لإدارة قواعد المعرفة والملفات والمستخدمين والمجموعات.
2. **رفع JAR** — رفع `openprodoc-ragtask.jar` إلى OpenProdoc عبر REST API.
3. **تعريفات المهام** — إدراج مهام الأحداث (INSERT/UPDATE/DELETE للمستندات والمجلدات) ومهمة cron (مزامنة المستخدمين/المجموعات كل 5 دقائق) في قاعدة بيانات OpenProdoc.

التهيئة **متكررة الأمان** — إذا كانت المهام موجودة بالفعل، يتوقف التنفيذ فوراً دون إجراء تغييرات. هذا يسمح بإعادة التشغيل الآمنة عند `helm upgrade` أو `docker compose up`.

بعد النشر، يمكنك تسجيل الدخول إلى Open WebUI باستخدام بيانات اعتماد مسؤول المراقب الافتراضية:

- **البريد الإلكتروني**: `watcher@openprodoc.local`
- **كلمة المرور**: `12345678`

هذه البيانات قابلة للتهيئة عبر `OPENWEBUI_ADMIN_EMAIL` / `OPENWEBUI_ADMIN_PASSWORD` في Docker Compose، أو `ragInit.config.watcherEmail` / `ragInit.config.watcherPassword` في قيم Helm. قم بتغييرها لبيئات الإنتاج.

#### المزامنة التلقائية للمستخدمين والمجموعات

بمجرد التهيئة، تقوم مهمة `RAGSyncCron` تلقائياً بـ:
- **نسخ مستخدمي OpenProdoc** إلى Open WebUI (كل 5 دقائق)
- **نسخ مجموعات OpenProdoc** إلى Open WebUI عبر SCIM API
- **تعيين المستخدمين للمجموعات** المطابقة لعضوياتهم في مجموعات OpenProdoc

هذا يعني أن مستخدمي OpenProdoc يمكنهم تسجيل الدخول إلى Open WebUI دون تسجيل منفصل.

### الخطوة 5: التحقق من النشر

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

### الخطوة 6: مصادقة المستخدمين وتنظيم قواعد المعرفة

**النسخ التلقائي للمستخدمين**: يتم نسخ جميع مستخدمي ومجموعات OpenProdoc تلقائياً في بيئة OpenWebUI. هذا يعني:

- **تسجيل دخول سلس**: يمكن لمستخدمي OpenProdoc تسجيل الدخول تلقائياً إلى OpenWebUI دون أي إعداد أو تسجيل إضافي
- **تسجيل دخول موحد**: يتم مزامنة بيانات اعتماد المستخدمين بين OpenProdoc و OpenWebUI
- **عضوية المجموعات**: يتم الحفاظ على ارتباطات المستخدمين بالمجموعات في كلا النظامين

**التحكم بالوصول المبني على الصلاحيات**:

كل مستخدم في OpenWebUI سيكون لديه وصول إلى قواعد المعرفة بناءً على صلاحياته في OpenProdoc:

- يمكن للمستخدمين فقط الوصول إلى قواعد المعرفة للمستندات التي لديهم صلاحيات عليها في OpenProdoc
- يتم فرض التحكم بالوصول على مستوى Knowledge Base
- يتم توريث الصلاحيات من نظام ACL في OpenProdoc

**تنظيم قواعد المعرفة**:

ينشئ نظام RAG تعييناً واحداً لواحد بين مجلدات OpenProdoc وقواعد المعرفة في OpenWebUI:

- **كل مجلد في OpenProdoc ينشئ Knowledge Base منفصلة في OpenWebUI**
- تحتوي كل Knowledge Base على المعرفة المفهرسة من جميع المستندات الموجودة في مجلد OpenProdoc المقابل
- يرى المستخدمون فقط قواعد المعرفة للمجلدات التي لديهم حق الوصول إليها
- هذا التنظيم القائم على المجلدات يجعل من السهل إدارة مجموعات المستندات المتخصصة والاستعلام عنها

**مثال**:

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

تضمن هذه البنية المعمارية تطبيق سياسات أمان المستندات والتحكم بالوصول المحددة في OpenProdoc بسلاسة في نظام RAG.

## الاستخدام

### الوصول إلى الخدمات

#### Docker Compose

| الخدمة | الرابط | منفذ المضيف | منفذ الحاوية |
|---|---|---|---|
| OpenProdoc | `http://localhost:8081/ProdocWeb2/` | 8081 | 8080 |
| OpenProdoc REST API | `http://localhost:8081/ProdocWeb2/APIRest/` | 8081 | 8080 |
| Open WebUI (RAG) | `http://localhost:8082` | 8082 | 8080 |
| PostgreSQL | `localhost:5433` | 5433 | 5432 |

#### Kubernetes

إذا كان ingress مفعلاً، يمكنك الوصول إلى Open WebUI على `http://localhost/rag` و OpenProdoc على `http://localhost/`.

إذا كان ingress معطلاً، استخدم إعادة توجيه المنافذ:

```bash
kubectl port-forward svc/openprodoc-openwebui 8080:8080
kubectl port-forward svc/openprodoc-core-engine 8081:8080
```

### الاستعلام من قواعد المعرفة

لاستخدام Knowledge Base في محادثة دردشة في Open WebUI:

1. افتح محادثة جديدة في Open WebUI
2. في حقل إدخال الرسالة، اكتب **`#`** — ستظهر قائمة منسدلة تعرض قواعد المعرفة المتاحة
3. اختر Knowledge Base المطلوبة (مثل `folder1`)
4. اكتب سؤالك وأرسله — سيستخدم LLM تقنية RAG للبحث في Knowledge Base المختارة عند إنشاء إجابته

يمكنك إرفاق عدة قواعد معرفة بمحادثة واحدة عن طريق كتابة `#` مرة أخرى واختيار قواعد إضافية.

### كيف يعمل

1. **رفع المستند**: عند إدراج أو تحديث مستند في OpenProdoc، يتم تشغيل `RAGEventDoc` CustomTask
2. **الاستيعاب**: يقوم CustomTask برفع المستند إلى API الخاص بـ Open WebUI وإضافته إلى Knowledge Base المقابلة
3. **المعالجة**: يقوم Open WebUI بـ:
   - تقسيم المستندات إلى قطع (افتراضياً: 1500 حرف مع تداخل 100 حرف)
   - إنشاء التضمينات باستخدام نموذج `nomic-embed-text` من Ollama
   - تخزين التضمينات في قاعدة بيانات PGVector
4. **الاستعلام**: يطرح المستخدمون أسئلة عبر واجهة المحادثة
5. **الاسترجاع**: يقوم Open WebUI بـ:
   - إنشاء تضمين الاستعلام
   - البحث في PGVector عن القطع ذات الصلة
   - تقديم السياق لـ LLM
6. **الاستجابة**: يولّد Ollama إجابة بناءً على السياق المسترجع

### أنواع المستندات المدعومة

يعالج CustomTask تلقائياً أنواع الملفات التالية:
- نصوص: `.txt`، `.md`، `.rst`، `.rtf`
- مستندات: `.pdf`، `.doc`، `.docx`
- ويب: `.html`، `.htm`
- بيانات: `.json`، `.csv`، `.xml`

## خيارات التهيئة

### تغيير نماذج LLM

للحصول على أداء أفضل في المجموعات محدودة الموارد، استخدم Phi-3:

```yaml
ollama:
  config:
    models:
      llm: "phi3"  # Smaller, faster than llama3:8b
```

### ضبط معلمات RAG

```yaml
openwebui:
  config:
    rag:
      enabled: true
      chunkSize: 1500      # Size of document chunks
      chunkOverlap: 100    # Overlap between chunks
```

### تهيئة التخزين

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

## استكشاف الأخطاء وإصلاحها

### نماذج Ollama لا تُنزّل

تحقق من سجلات حاوية التهيئة:

```bash
kubectl logs -n openprodoc <ollama-pod> -c pull-models
```

النماذج كبيرة الحجم (4-8 جيجابايت لكل نموذج) وقد تستغرق وقتاً للتنزيل.

### المستندات لا تظهر في Open WebUI

تحقق من اكتمال rag-init بنجاح:

```bash
# Docker Compose
docker compose logs rag-init

# Kubernetes
kubectl logs -n openprodoc -l app.kubernetes.io/name=rag-init
```

تأكد من:
1. اكتمال حاوية/مهمة `rag-init` بدون أخطاء
2. وجود حساب `watcher@openprodoc.local` المسؤول في Open WebUI
3. رفع ملف CustomTask JAR (تحقق من مجلد النظام في OpenProdoc)
4. المهام الحدثية نشطة (تحقق من إدارة المهام في لوحة إدارة OpenProdoc)
5. إمكانية وصول core-engine إلى Open WebUI على الرابط المُهيّأ
6. نوع MIME للمستند موجود في القائمة المدعومة

### مشاكل اتصال PGVector

تحقق من pod الخاص بـ PGVector:

```bash
kubectl logs -n openprodoc <pgvector-pod>
kubectl exec -it -n openprodoc <pgvector-pod> -- psql -U rag_user -d rag_vectors
```

تحقق من إضافة المتجهات:

```sql
\dx  -- Should show 'vector' extension
```

### استخدام مرتفع للموارد

لبيئات محدودة المعالج المركزي:

1. التبديل إلى نماذج أصغر:
   ```yaml
   ollama:
     config:
       models:
         llm: "phi3"  # Instead of llama3:8b
   ```

2. تقليل حدود الموارد:
   ```yaml
   ollama:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. تعطيل تهيئة CustomTask واستخدام رفع المستندات اليدوي:
   ```yaml
   ragInit:
     enabled: false
   ```

## تعطيل مكونات RAG

لتعطيل حل RAG بالكامل:

```yaml
pgvector:
  enabled: false

ollama:
  enabled: false

openwebui:
  enabled: false
```

## اعتبارات الأمان

1. **الأسرار**: يتم تخزين كلمة مرور PGVector في Kubernetes secret. قم بتغيير كلمة المرور الافتراضية:
   ```yaml
   pgvector:
     config:
       password: "your-secure-password"
   ```

2. **سياسات الشبكة**: فكر في تطبيق network policies لتقييد الاتصال بين pods

3. **مصادقة API**: قم بتهيئة مصادقة Open WebUI في بيئة الإنتاج. بعد اكتمال rag-init، فكر في تعيين `ENABLE_SIGNUP=false` و `DEFAULT_USER_ROLE=user` لمنع إنشاء حسابات مسؤول غير مصرح بها.

## ضبط الأداء

### للنشر عالي الحجم

1. **زيادة التوازي في Ollama**:
   ```yaml
   # Set via environment in ollama deployment
   OLLAMA_NUM_PARALLEL: "8"
   ```

2. **توسيع PGVector**:
   ```yaml
   pgvector:
     resources:
       limits:
         cpu: 2000m
         memory: 4Gi
   ```

3. **تفعيل التخزين المؤقت**: يحتفظ Ollama بالنماذج في الذاكرة بناءً على `OLLAMA_KEEP_ALIVE`

### للنشر محدود الموارد

1. استخدم نموذج Phi-3 (أصغر وأسرع)
2. قلّل حجم القطع لمعالجة تضمينات أقل
3. عطّل `ragInit` واستخدم رفع المستندات اليدوي عبر Open WebUI

## المراقبة

مراقبة مكونات RAG:

```bash
# Resource usage
kubectl top pods -n openprodoc

# Service status
kubectl get svc -n openprodoc

# Logs
kubectl logs -n openprodoc -l app.kubernetes.io/part-of=openprodoc --tail=100
```

## قراءات إضافية

- [وثائق Open WebUI](https://docs.openwebui.com/)
- [مكتبة نماذج Ollama](https://ollama.com/library)
- [وثائق PGVector](https://github.com/pgvector/pgvector)
