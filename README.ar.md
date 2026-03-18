# OpenProdoc Red
----

[🇬🇧 English](README.md) | [🇪🇸 Español](README.es.md) | [🇫🇷 Français](README.fr.md) | [🇩🇪 Deutsch](README.de.md) | [🇸🇦 العربية](README.ar.md)

## نظام إدارة المستندات السحابي الأصلي

**OpenProdoc Red** هو نسخة جاهزة لـ Kubernetes من نظام OpenProdoc DMS (نظام إدارة المستندات). تم تغليف هذه النسخة وتحسينها للنشر السحابي مع مخططات Helm ودعم Docker وبنية تحتية جاهزة للإنتاج.

----

## 🚀 الجديد في OpenProdoc Red

### بنية سحابية أصلية
* **جاهز للنشر على Kubernetes** مع مخططات Helm
* **تصميم يركز على الحاويات** مع دعم Docker و Docker Compose
* **توفر عالي** مع إمكانيات التوسع الأفقي وارتباط الجلسة
* **محسّن لـ PostgreSQL** لنشر قواعد البيانات السحابية
* **تكوين قائم على البيئة** مع إعدادات خارجية

### حزمة نشر حديثة
* **Tomcat 9 مع OpenJDK 11** - خادم تطبيقات مستقر
* **PostgreSQL 15** - قاعدة بيانات حديثة مع تحسينات
* **مخططات Helm** - نشر Kubernetes جاهز للإنتاج
* **Docker Compose** - إعداد سهل للتطوير المحلي
* **واجهة برمجة تطبيقات REST مفعّلة** - وصول برمجي كامل

### بنية تحتية جاهزة للإنتاج
* **بناء Docker متعدد المراحل** - أحجام صور محسّنة
* **مبادئ التطبيق ذي الـ 12 عامل** - تكوين قائم على البيئة
* **وحدات تخزين دائمة** - تخزين آمن للمستندات والتكوين
* **ارتباط الجلسة** - جلسات ثابتة للنشر متعدد النسخ
* **فحوصات الصحة** - مجسات الجاهزية والنشاط لـ Kubernetes
* **تقوية الأمان** - حاويات بدون صلاحيات root، أذونات دنيا

### التكامل مع الذكاء الاصطناعي عبر Model Context Protocol (MCP)
* **خادم MCP مضمّن** - دعم أصلي لتكامل المساعدين الذكيين
* **جاهز لـ Claude Desktop و Claude Code** - تكامل سلس مع أدوات الذكاء الاصطناعي من Anthropic
* **تغطية شاملة لواجهة برمجة التطبيقات** - عمليات CRUD كاملة للمجلدات والمستندات والمكنز
* **واجهة لغة طبيعية** - إدارة المستندات باستخدام أوامر محادثة
* **تنسيقات استجابة مزدوجة** - Markdown للبشر، JSON للآلات
* **مصادقة تلقائية** - إدارة بيانات الاعتماد القائمة على البيئة
* **راجع [MCP/README.md](MCP/README.md)** للحصول على دليل التكامل الكامل

### نظام RAG المدمج (التوليد المعزز بالاسترجاع)
* **بحث مستندات بالذكاء الاصطناعي** - بحث دلالي باستخدام استعلامات اللغة الطبيعية
* **إمكانات الأسئلة والأجوبة** - اطرح أسئلة واحصل على إجابات من مستنداتك
* **استيعاب تلقائي للمستندات** - يتم فهرسة المستندات الجديدة تلقائيًا لنظام RAG
* **قاعدة معرفية لكل مجلد** - يصبح كل مجلد OpenProdoc قاعدة معرفية منفصلة
* **وصول قائم على الأذونات** - يصل المستخدمون فقط إلى قواعد المعرفة للمستندات المصرح بها
* **مصادقة سلسة** - يسجل مستخدمو OpenProdoc الدخول تلقائيًا إلى واجهة OpenWebUI
* **تكامل أصلي قائم على الأحداث** - تم استبدال حاوية المراقب الخارجية بملف CustomTask JAR يعمل داخل JVM الخاص بـ OpenProdoc، يستجيب لأحداث المستندات والمجلدات في الوقت الفعلي دون حاويات إضافية
* **مزامنة تلقائية للمستخدمين والمجموعات** - مهمة cron مدمجة تنسخ مستخدمي ومجموعات OpenProdoc إلى Open WebUI مع الحفاظ على عضويات المجموعات والأذونات
* **حزمة جاهزة للإنتاج** - تتضمن PGVector و Ollama (محسّن لوحدة المعالجة المركزية) و Open WebUI
* **راجع [docs/RAG_SETUP.md](docs/RAG_SETUP.md)** للحصول على دليل النشر

----

## 📋 ميزات ECM الأساسية

* **دعم متعدد المنصات** (Linux، Windows، Mac عبر الحاويات)
* **دعم قواعد بيانات متعددة** مع تحسين PostgreSQL
  * PostgreSQL (موصى به)، MySQL، Oracle، DB2، SQLServer، SQLLite، HSQLDB
* **طرق مصادقة متعددة** (LDAP، قاعدة البيانات، نظام التشغيل، مدمج)
* **تخزين مرن للمستندات**
  * نظام الملفات (افتراضي)، BLOB قاعدة البيانات، FTP، مرجع URL، Amazon S3
* **بيانات تعريف موجهة للكائنات** مع دعم الوراثة
* **أذونات دقيقة** وقدرات التفويض
* **دعم متعدد اللغات** (الإنجليزية، الإسبانية، البرتغالية، الكتالونية)
* **واجهة ويب** (ProdocWeb2)
* **واجهة برمجة تطبيقات REST** للوصول البرمجي
* **مفتوح المصدر** تحت GNU AGPL v3

### ميزات إدارة المستندات
* **إدارة المكنز** مع دعم معيار SKOS-RDF
* **التحقق من البيانات الوصفية** مقابل مصطلحات المكنز
* **التحكم في الإصدارات** مع سير عمل checkout/checkin
* **إدارة دورة حياة المستند** مع التطهير
* **البحث في النص الكامل** باستخدام Apache Lucene
* **تسلسل هرمي للمجلدات** مع وراثة الأذونات
* **قدرات استيراد/تصدير المستندات**

----

## 🏗️ البنية المعمارية

### مكونات النشر
```
┌─────────────────────────────────────┐
│      OpenProdoc Core Engine         │
│      (Tomcat 9 + ProdocWeb2)        │
│         المنفذ: 8080                │
│   ┌──────────────────────────┐      │
│   │  واجهة الويب: /ProdocWeb2/│      │
│   │  واجهة REST: /APIRest/   │      │
│   └──────────────────────────┘      │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────────┐    ┌──────▼────────┐
│ PostgreSQL │    │   تخزين      │
│قاعدة بيانات│    │   الملفات    │
└────────────┘    └───────────────┘
```

### بنية التخزين
* **قاعدة البيانات (PostgreSQL)** - البيانات الوصفية، المستخدمون، الأذونات، التكوين
* **وحدة تخزين نظام الملفات** - ملفات المستندات الثنائية، تشفير قابل للتكوين
* **وحدات التخزين الدائمة** - تخزين مُدار بواسطة Kubernetes لاستمرارية البيانات

----

## 🚢 البدء السريع

### Docker Compose (موصى به للتطوير)

```bash
# استنساخ المستودع
استنسخ المستودع https://github.com/egenillo/openprodoc_red في بيئتك المحلية

# بدء الخدمات
docker-compose up -d

# انتظر بدء التشغيل (2-3 دقائق للتثبيت الأولي)
docker-compose logs -f core-engine

# الوصول إلى التطبيق
# واجهة الويب: http://localhost:8080/ProdocWeb2/
# واجهة REST: http://localhost:8080/ProdocWeb2/APIRest/

# بيانات الاعتماد الافتراضية
# اسم المستخدم: root
# كلمة المرور: admin
```

### نشر Kubernetes

```bash

# نشر PostgreSQL
helm install openprodoc-postgresql ./helm/postgresql \
  --set auth.username=user1 \
  --set auth.password=pass1 \
  --set auth.database=prodoc

# نشر OpenProdoc
helm install openprodoc ./helm/openprodoc \
  --set coreEngine.config.database.user=user1 \
  --set coreEngine.config.database.password=pass1 \
  --set coreEngine.install.rootPassword=admin

# الوصول المحلي عبر إعادة توجيه المنفذ
kubectl port-forward svc/openprodoc-core-engine 8080:8080

# الوصول إلى التطبيق
# واجهة الويب: http://localhost:8080/ProdocWeb2/
# واجهة REST: http://localhost:8080/ProdocWeb2/APIRest/
```

راجع [دليل نشر Helm](docs/HELM_DEPLOYMENT_GUIDE.md) للحصول على تعليمات مفصلة.

----

## 📡 واجهة برمجة التطبيقات REST

يتضمن OpenProdoc Red واجهة برمجة تطبيقات REST كاملة للوصول البرمجي.

### مثال سريع

```bash
# تسجيل الدخول
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d "{\"Name\":\"root\",\"Password\":\"admin\"}"

# يُرجع رمز JWT
{"Res":"OK","Token":"eyJhbGci..."}

# استخدم الرمز للطلبات المصادق عليها
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

### نقاط النهاية المتاحة

* **إدارة الجلسة** - تسجيل الدخول، تسجيل الخروج
* **واجهة برمجة المجلدات** - إنشاء، قراءة، تحديث، حذف المجلدات
* **واجهة برمجة المستندات** - رفع، تنزيل، البحث في المستندات
* **واجهة برمجة المكنز** - إدارة المفردات المحكومة

**التوثيق**:
* [دليل استخدام واجهة برمجة التطبيقات REST](docs/api/API_USAGE_GUIDE.md) - مرجع كامل مع أمثلة
* [مرجع سريع لواجهة برمجة التطبيقات REST](docs/api/API_QUICK_REFERENCE.md) - ورقة غش للأوامر
* [مجموعة Postman](docs/api/OpenProdoc-API-Collection.json) - للاستيراد في أدوات اختبار API

**نصوص الاختبار**:
* Linux/Mac: `./docs/api/test-api.sh`
* Windows: `docs/api/test-api.bat`

----

## 🛠️ التكوين

### متغيرات البيئة

يستخدم OpenProdoc Red متغيرات البيئة للتكوين:

```bash
# تكوين قاعدة البيانات
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=prodoc
DB_USER=prodoc
DB_PASSWORD=your-secure-password
DB_JDBC_CLASS=org.postgresql.Driver
DB_JDBC_URL_TEMPLATE=jdbc:postgresql://{HOST}:{PORT}/{DATABASE}

# إعدادات التثبيت
INSTALL_ON_STARTUP=true
ROOT_PASSWORD=admin
DEFAULT_LANG=EN
TIMESTAMP_FORMAT="dd/MM/yyyy HH:mm:ss"
DATE_FORMAT="dd/MM/yyyy"
MAIN_KEY=uthfytnbh84kflh06fhru  # مفتاح تشفير المستندات

# تكوين المستودع
REPO_NAME=Reposit
REPO_ENCRYPT=False
REPO_URL=/storage/OPD/
REPO_TYPE=FS  # تخزين نظام الملفات
REPO_USER=
REPO_PASSWORD=
REPO_PARAM=

# برنامج تشغيل JDBC
JDBC_DRIVER_PATH=./lib/postgresql-42.3.8.jar
```

### تكوين Kubernetes

يوفر ملف Helm values.yaml خيارات تكوين شاملة:

```yaml
coreEngine:
  replicaCount: 2  # توفر عالي

  service:
    type: ClusterIP
    port: 8080
    sessionAffinity:
      enabled: true  # جلسات ثابتة
      timeoutSeconds: 10800  # 3 ساعات

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

راجع [values.yaml](helm/openprodoc/values.yaml) لجميع الخيارات.

----

## 📊 المراقبة والعمليات

### فحوصات الصحة

```bash
# فحص صحة التطبيق (واجهة الويب)
curl http://localhost:8080/ProdocWeb2/

# فحص واجهة برمجة التطبيقات REST
curl http://localhost:8080/ProdocWeb2/APIRest/session

# حالة حاوية Kubernetes
kubectl get pods
kubectl logs -f <pod-name>
```

----

## 🔒 الأمان

### إعدادات الأمان الافتراضية

* **حاويات بدون صلاحيات root** - يعمل كمستخدم 1000
* **قدرات دنيا** - يزيل جميع قدرات Linux غير الضرورية
* **نظام ملفات جذر للقراءة فقط** - معطل (مطلوب لأدلة عمل Tomcat)
* **لا توسع للامتيازات** - مفروض عبر سياق الأمان

### قائمة تحقق أمان الإنتاج

- [ ] تغيير كلمة مرور المسؤول الافتراضية (`ROOT_PASSWORD`)
- [ ] تغيير كلمة مرور قاعدة البيانات (`DB_PASSWORD`)
- [ ] تغيير مفتاح تشفير المستندات (`MAIN_KEY`)
- [ ] استخدام علامات صور محددة (وليس `latest`)
- [ ] تمكين TLS/HTTPS عبر Ingress
- [ ] تكوين سياسات الشبكة
- [ ] تعيين حدود الموارد
- [ ] تمكين سجل التدقيق
- [ ] تحديثات أمان منتظمة
- [ ] وجود استراتيجية نسخ احتياطي

----

## 🔄 الترحيل من OpenProdoc الكلاسيكي

يحافظ OpenProdoc Red على **توافق كامل** مع قواعد بيانات OpenProdoc الموجودة. يتضمن الترحيل:

1. **تصدير قاعدة البيانات الموجودة** من OpenProdoc الكلاسيكي
2. **الاستيراد إلى PostgreSQL** في البيئة الجديدة
3. **نسخ مخزن المستندات** إلى وحدة التخزين الدائمة
4. **تكوين متغيرات البيئة** لمطابقة التكوين القديم
5. **النشر باستخدام Docker Compose أو Helm**

سيكتشف التطبيق قاعدة البيانات الموجودة ويتخطى التثبيت الأولي.

----

## 📖 التوثيق

* **[دليل نشر Helm](docs/HELM_DEPLOYMENT_GUIDE.md)** - دليل نشر Kubernetes كامل
* **[دليل استخدام واجهة برمجة التطبيقات REST](docs/api/API_USAGE_GUIDE.md)** - مرجع API شامل
* **[مرجع سريع لواجهة برمجة التطبيقات REST](docs/api/API_QUICK_REFERENCE.md)** - بحث سريع عن الأوامر
* **[فهرس التوثيق](docs/README.md)** - جميع التوثيقات المتاحة

----

## 🧪 الاختبار

### اختبارات واجهة برمجة التطبيقات الآلية

```bash
# Linux/Mac
./docs/api/test-api.sh

# Windows
docs\api\test-api.bat
```

### الاختبار اليدوي

1. الوصول إلى واجهة الويب: http://localhost:8080/ProdocWeb2/
2. تسجيل الدخول باستخدام `root` / `admin`
3. إنشاء مجلدات ورفع المستندات
4. اختبار واجهة برمجة التطبيقات REST باستخدام النصوص المقدمة

----

## 📄 الترخيص

OpenProdoc Red هو برنامج مجاني ومفتوح المصدر مرخص بموجب:
* **GNU Affero General Public License v3** (AGPL-3.0)

يضمن هذا الترخيص بقاء أي تعديلات أو خدمات شبكة تستخدم هذا البرنامج مفتوحة المصدر.

----

## 🤝 المساهمات

المساهمات مرحب بها في:
* تحسينات نشر Kubernetes
* التوثيق والأمثلة
* تحسينات الأداء
* إصلاح الأخطاء والاختبار
* خلفيات تخزين إضافية
* تكاملات مزودي السحابة

----

## 📞 الدعم

* **التوثيق**: راجع مجلد `docs/`
* **المشكلات**: الإبلاغ عن الأخطاء وطلبات الميزات
* **OpenProdoc الأصلي**: https://jhierrot.github.io/openprodoc/
* **الترخيص**: ترخيص AGPL-3.0

----

## 🙏 الشكر والتقدير

**OpenProdoc الأصلي** - من إنشاء Joaquín Hierro
**OpenProdoc Red** - الحوية السحابية الأصلية ونشر Kubernetes

يحافظ هذا المشروع على توافق كامل مع OpenProdoc الأصلي مع توفير قدرات نشر سحابية حديثة.

----

## 📈 معلومات الإصدار

* **إصدار المخطط**: 1.0.0
* **إصدار التطبيق**: 3.0.3
* **Tomcat**: 9.0.x
* **PostgreSQL**: 15.x (موصى به)
* **Java**: OpenJDK 11


