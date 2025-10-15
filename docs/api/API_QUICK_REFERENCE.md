# OpenProdoc REST API Quick Reference

## Base URL
```
http://localhost:8080/ProdocWeb2/APIRest/
```

## Authentication

### Login
```bash
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d '{"Name":"root","Password":"admin"}'
```

### Logout
```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Authorization: Bearer $TOKEN"
```

## Common Headers

```
Authorization: Bearer <token>
Content-Type: application/json          # For JSON requests
Content-Type: multipart/form-data       # For file uploads
```

---

## Folders API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/folders/ById/{foldId}` | Get folder by ID |
| GET | `/folders/ByPath/{path}` | Get folder by path |
| GET | `/folders/SubFoldersById/{foldId}?Initial=0&Final=100` | List subfolders by ID |
| GET | `/folders/SubFoldersByPath/{path}?Initial=0&Final=100` | List subfolders by path |
| GET | `/folders/ContDocsById/{foldId}?Initial=0&Final=100` | List documents by folder ID |
| GET | `/folders/ContDocsByPath/{path}?Initial=0&Final=100` | List documents by folder path |
| POST | `/folders` | Create folder |
| PUT | `/folders/ById/{foldId}` | Update folder by ID |
| PUT | `/folders/ByPath/{path}` | Update folder by path |
| DELETE | `/folders/ById/{foldId}` | Delete folder by ID |
| DELETE | `/folders/ByPath/{path}` | Delete folder by path |
| POST | `/folders/Search` | Search folders |

---

## Documents API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/documents/ById/{docId}` | Get document metadata |
| GET | `/documents/ContentById/{docId}` | Download document content |
| POST | `/documents` | Upload new document |
| PUT | `/documents/ById/{docId}` | Update document (new version) |
| DELETE | `/documents/ById/{docId}` | Delete document |
| POST | `/documents/Search` | Search documents |

---

## Quick Examples

### Get Token
```bash
TOKEN=$(curl -s -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d '{"Name":"root","Password":"admin"}' | \
  grep -o '"Token":"[^"]*"' | cut -d'"' -f4)
```

### Get Folder
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

### List Subfolders
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/SubFoldersByPath/RootFolder?Initial=0&Final=10"
```

### List Documents in Folder
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/ContDocsByPath/RootFolder?Initial=0&Final=10"
```

### Create Folder
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/folders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "MyFolder",
    "Idparent": "RootFolder",
    "Type": "PD_FOLDERS",
    "ACL": "Public"
  }'
```

### Upload Document
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "Binary=@file.pdf" \
  -F 'Metadata={"Name":"file.pdf","Idparent":"RootFolder","Type":"PD_DOCS","Title":"My Doc"}'
```

### Download Document
```bash
curl -H "Authorization: Bearer $TOKEN" \
  -o output.pdf \
  http://localhost:8080/ProdocWeb2/APIRest/documents/ContentById/doc-123
```

### Search Documents
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/documents/Search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"Query":"MimeType=\"pdf\"","Initial":0,"Final":20}'
```

### Delete Document
```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/documents/ById/doc-123 \
  -H "Authorization: Bearer $TOKEN"
```

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Not Found |
| 415 | Unsupported Media Type |
| 500 | Internal Server Error |

---

## Response Format

### Success
```json
{
  "Res": "OK",
  "Msg": "Created=doc-123"
}
```

### Error
```json
{
  "Res": "KO",
  "Msg": "Error message"
}
```

---

## Kubernetes Access

### Port Forward
```bash
export KUBECONFIG="/path/to/kubeconfig.yaml"
kubectl port-forward -n default svc/openprodoc-core-engine 8080:8080
```

### Internal Cluster URL
```
http://openprodoc-core-engine.default.svc.cluster.local:8080/ProdocWeb2/APIRest/
```

---

## Query Syntax Examples

```
Name="MyFolder"
PDAuthor="root"
MimeType="pdf"
Name LIKE "%report%"
PDDate > "2025-01-01"
Name="Test" AND ACL="Public"
```

---

## Common Folder Structure

```
RootFolder/
├── System/
├── Users/
└── (your custom folders)
```

---

## Default Credentials

- **Username**: root
- **Password**: admin

**⚠️ Change in production!**
