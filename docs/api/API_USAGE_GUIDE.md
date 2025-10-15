# OpenProdoc REST API Usage Guide

## Overview

OpenProdoc provides a comprehensive REST API for programmatic access to the Enterprise Content Management system. The API supports document management, folder operations, thesauri management, and authentication via JWT tokens.

## Base URL

```
http://<host>:8080/ProdocWeb2/APIRest/
```

For Kubernetes deployments:
- **Internal (within cluster)**: `http://openprodoc-core-engine.default.svc.cluster.local:8080/ProdocWeb2/APIRest/`
- **Port-forward access**: `http://localhost:8080/ProdocWeb2/APIRest/`
- **Ingress (if enabled)**: `http://<ingress-host>/ProdocWeb2/APIRest/`

## Authentication

### Login (Create Session)

**Endpoint**: `PUT /session`

**Request**:
```bash
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d '{"Name":"root","Password":"admin"}'
```

**Response**:
```json
{
  "Res": "OK",
  "Token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJyb290IiwiTXVsdGlTZXNpb24iOjAuMDgxMzEwMTE2NjEzNTI2ODMsImlhdCI6MTc2MDUzODk0MSwiZXhwIjoxNzYwNjI1MzQxLCJpc3MiOiJPcGVuUHJvZG9jIn0..."
}
```

**Notes**:
- Save the `Token` value for subsequent API calls
- Default credentials: username=`root`, password=`admin`
- Token is a JWT (JSON Web Token) with expiration
- All subsequent API calls require this token in the `Authorization` header

### Logout (Close Session)

**Endpoint**: `DELETE /session`

**Request**:
```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Response**:
```json
{
  "Res": "OK",
  "Msg": "Closed"
}
```

## Using the API

### Authorization Header

All authenticated endpoints require the JWT token in the Authorization header:

```
Authorization: Bearer <your-token-here>
```

### Example with curl:
```bash
# Set token as environment variable
export TOKEN="eyJhbGciOiJIUzUxMiJ9..."

# Use in API calls
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder
```

---

## Folders API

Base path: `/folders`

### Get Folder by ID

**Endpoint**: `GET /folders/ById/{foldId}`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ById/RootFolder
```

**Response**:
```json
{
  "Id": "RootFolder",
  "Name": "RootFolder",
  "ACL": "Public",
  "Idparent": "RootFolder",
  "Type": "PD_FOLDERS",
  "PDDate": "2025-10-12 10:49:00",
  "PDAuthor": "Install",
  "ListAttr": []
}
```

### Get Folder by Path

**Endpoint**: `GET /folders/ByPath/{path}`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder/System
```

**Notes**:
- Path should not start with `/`
- Use URL encoding for special characters

### List Subfolders by ID

**Endpoint**: `GET /folders/SubFoldersById/{foldId}?Initial=0&Final=100`

**Parameters**:
- `Initial` (optional, default=0): Starting index
- `Final` (optional, default=100): Ending index

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/SubFoldersById/RootFolder?Initial=0&Final=10"
```

**Response**:
```json
[
  {
    "Id": "RootFolder",
    "Name": "RootFolder",
    "ACL": "Public",
    "Idparent": "RootFolder",
    "Type": "PD_FOLDERS",
    "PDDate": "2025-10-12 10:49:00",
    "PDAuthor": "Install",
    "ListAttr": []
  },
  {
    "Id": "System",
    "Name": "System",
    "ACL": "Public",
    "Idparent": "RootFolder",
    "Type": "PD_FOLDERS",
    "PDDate": "2025-10-12 10:49:00",
    "PDAuthor": "Install",
    "ListAttr": []
  }
]
```

### List Subfolders by Path

**Endpoint**: `GET /folders/SubFoldersByPath/{path}?Initial=0&Final=100`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/SubFoldersByPath/RootFolder?Initial=0&Final=5"
```

### List Documents in Folder by ID

**Endpoint**: `GET /folders/ContDocsById/{foldId}?Initial=0&Final=100`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/ContDocsById/RootFolder?Initial=0&Final=10"
```

**Response**:
```json
[
  {
    "Id": "doc-123",
    "Name": "document.pdf",
    "Type": "PD_DOCS",
    "Idparent": "RootFolder",
    "PDDate": "2025-10-12 15:30:00",
    "PDAuthor": "root",
    "MimeType": "pdf",
    "ListAttr": []
  }
]
```

### List Documents in Folder by Path

**Endpoint**: `GET /folders/ContDocsByPath/{path}?Initial=0&Final=100`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/ContDocsByPath/RootFolder?Initial=0&Final=5"
```

### Create Folder

**Endpoint**: `POST /folders`

**Request**:
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

**Response**:
```json
{
  "Res": "OK",
  "Msg": "Created=MyFolder"
}
```

### Update Folder by ID

**Endpoint**: `PUT /folders/ById/{foldId}`

**Request**:
```bash
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/folders/ById/MyFolder \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "RenamedFolder",
    "ACL": "Private"
  }'
```

### Update Folder by Path

**Endpoint**: `PUT /folders/ByPath/{path}`

**Request**:
```bash
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder/MyFolder \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "UpdatedFolder"
  }'
```

### Delete Folder by ID

**Endpoint**: `DELETE /folders/ById/{foldId}`

**Request**:
```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/folders/ById/MyFolder \
  -H "Authorization: Bearer $TOKEN"
```

**Response**:
```json
{
  "Res": "OK",
  "Msg": "Deleted=MyFolder"
}
```

### Delete Folder by Path

**Endpoint**: `DELETE /folders/ByPath/{path}`

**Request**:
```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/folders/ByPath/RootFolder/MyFolder \
  -H "Authorization: Bearer $TOKEN"
```

### Search Folders

**Endpoint**: `POST /folders/Search`

**Request**:
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/folders/Search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Query": "Name=\"System\"",
    "Initial": 0,
    "Final": 10
  }'
```

**Query Syntax**:
- Use OpenProdoc query syntax
- Example: `PDAuthor="Install"`
- Example: `Name="MyFolder" AND ACL="Public"`

---

## Documents API

Base path: `/documents`

### Get Document Metadata by ID

**Endpoint**: `GET /documents/ById/{docId}`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/documents/ById/doc-123
```

**Response**:
```json
{
  "Id": "doc-123",
  "Name": "document.pdf",
  "Type": "PD_DOCS",
  "Idparent": "RootFolder",
  "PDDate": "2025-10-12 15:30:00",
  "PDAuthor": "root",
  "MimeType": "pdf",
  "DocDate": "2025-10-12",
  "Title": "My Document",
  "ListAttr": []
}
```

### Download Document Content by ID

**Endpoint**: `GET /documents/ContentById/{docId}`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  -o downloaded-file.pdf \
  http://localhost:8080/ProdocWeb2/APIRest/documents/ContentById/doc-123
```

**Response**:
- Binary file content
- Content-Type header set to document's MIME type
- Content-Disposition header with filename

### Create Document (Upload)

**Endpoint**: `POST /documents`

**Content-Type**: `multipart/form-data`

**Request**:
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "Binary=@/path/to/file.pdf" \
  -F 'Metadata={
    "Name": "document.pdf",
    "Idparent": "RootFolder",
    "Type": "PD_DOCS",
    "Title": "My Document",
    "DocDate": "2025-10-12"
  }'
```

**Response**:
```json
{
  "Res": "OK",
  "Msg": "Created=doc-456"
}
```

**Notes**:
- `Binary`: File to upload
- `Metadata`: JSON string with document metadata
- File name is taken from the uploaded file

### Update Document (Upload New Version)

**Endpoint**: `PUT /documents/ById/{docId}`

**Content-Type**: `multipart/form-data`

**Request**:
```bash
curl -X PUT http://localhost:8080/ProdocWeb2/APIRest/documents/ById/doc-123 \
  -H "Authorization: Bearer $TOKEN" \
  -F "Binary=@/path/to/updated-file.pdf" \
  -F 'Metadata={
    "Title": "Updated Document",
    "VerLabel": "1.1"
  }'
```

**Response**:
```json
{
  "Res": "OK",
  "Msg": "Updated=doc-123"
}
```

**Notes**:
- Creates a new version of the document
- `VerLabel`: Version label for the new version
- Automatically performs checkout/checkin

### Delete Document by ID

**Endpoint**: `DELETE /documents/ById/{docId}`

**Request**:
```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/documents/ById/doc-123 \
  -H "Authorization: Bearer $TOKEN"
```

**Response**:
```json
{
  "Res": "OK",
  "Msg": "Deleted=doc-123"
}
```

### Search Documents

**Endpoint**: `POST /documents/Search`

**Request**:
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/documents/Search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Query": "MimeType=\"pdf\" AND PDAuthor=\"root\"",
    "Initial": 0,
    "Final": 20
  }'
```

**Response**:
```json
[
  {
    "Id": "doc-123",
    "Name": "document.pdf",
    "Type": "PD_DOCS",
    "MimeType": "pdf",
    "PDAuthor": "root"
  }
]
```

---

## Thesauri API

Base path: `/thesauri`

### Get Thesaurus by ID

**Endpoint**: `GET /thesauri/ById/{thesId}`

**Request**:
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/ProdocWeb2/APIRest/thesauri/ById/thes-001
```

### Create Thesaurus

**Endpoint**: `POST /thesauri`

**Request**:
```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/thesauri \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "MyThesaurus",
    "Type": "PD_THESAUR"
  }'
```

---

## Response Format

### Success Response

```json
{
  "Res": "OK",
  "Msg": "Operation successful message"
}
```

or for data retrieval:
```json
{
  "Id": "...",
  "Name": "...",
  ...
}
```

### Error Response

```json
{
  "Res": "KO",
  "Msg": "Error description"
}
```

### HTTP Status Codes

- `200 OK`: Success
- `400 Bad Request`: Invalid input/parameters
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Resource not found
- `415 Unsupported Media Type`: Wrong Content-Type header
- `500 Internal Server Error`: Server error

---

## Complete Example Workflow

### 1. Login and Get Token

```bash
# Login
TOKEN=$(curl -s -X PUT http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Content-Type: application/json" \
  -d '{"Name":"root","Password":"admin"}' | \
  grep -o '"Token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"
```

### 2. Create a Folder

```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/folders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "ProjectDocuments",
    "Idparent": "RootFolder",
    "Type": "PD_FOLDERS",
    "ACL": "Public"
  }'
```

### 3. Upload a Document

```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "Binary=@report.pdf" \
  -F 'Metadata={
    "Name": "report.pdf",
    "Idparent": "ProjectDocuments",
    "Type": "PD_DOCS",
    "Title": "Project Report",
    "DocDate": "2025-10-15"
  }'
```

### 4. List Documents in Folder

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8080/ProdocWeb2/APIRest/folders/ContDocsByPath/ProjectDocuments"
```

### 5. Download a Document

```bash
curl -H "Authorization: Bearer $TOKEN" \
  -o downloaded-report.pdf \
  http://localhost:8080/ProdocWeb2/APIRest/documents/ContentById/doc-123
```

### 6. Search for Documents

```bash
curl -X POST http://localhost:8080/ProdocWeb2/APIRest/documents/Search \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "Query": "Title LIKE \"%Report%\"",
    "Initial": 0,
    "Final": 50
  }'
```

### 7. Logout

```bash
curl -X DELETE http://localhost:8080/ProdocWeb2/APIRest/session \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## Programming Language Examples

### Python

```python
import requests
import json

# Base URL
base_url = "http://localhost:8080/ProdocWeb2/APIRest"

# Login
login_data = {"Name": "root", "Password": "admin"}
response = requests.put(f"{base_url}/session", json=login_data)
token = response.json()["Token"]

# Set headers for authenticated requests
headers = {"Authorization": f"Bearer {token}"}

# Get folder
folder = requests.get(f"{base_url}/folders/ByPath/RootFolder", headers=headers)
print(folder.json())

# List subfolders
subfolders = requests.get(
    f"{base_url}/folders/SubFoldersByPath/RootFolder",
    headers=headers,
    params={"Initial": 0, "Final": 10}
)
print(subfolders.json())

# Upload document
files = {"Binary": open("document.pdf", "rb")}
metadata = {
    "Name": "document.pdf",
    "Idparent": "RootFolder",
    "Type": "PD_DOCS",
    "Title": "My Document"
}
data = {"Metadata": json.dumps(metadata)}
response = requests.post(f"{base_url}/documents", headers=headers, files=files, data=data)
print(response.json())

# Logout
requests.delete(f"{base_url}/session", headers=headers, json={})
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const baseUrl = 'http://localhost:8080/ProdocWeb2/APIRest';

// Login
async function login() {
  const response = await axios.put(`${baseUrl}/session`, {
    Name: 'root',
    Password: 'admin'
  });
  return response.data.Token;
}

// Get folder
async function getFolder(token) {
  const response = await axios.get(`${baseUrl}/folders/ByPath/RootFolder`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
}

// Upload document
async function uploadDocument(token, filePath) {
  const form = new FormData();
  form.append('Binary', fs.createReadStream(filePath));
  form.append('Metadata', JSON.stringify({
    Name: 'document.pdf',
    Idparent: 'RootFolder',
    Type: 'PD_DOCS',
    Title: 'My Document'
  }));

  const response = await axios.post(`${baseUrl}/documents`, form, {
    headers: {
      ...form.getHeaders(),
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
}

// Main
(async () => {
  const token = await login();
  const folder = await getFolder(token);
  console.log(folder);
})();
```

### Java

```java
import java.net.http.*;
import java.net.URI;
import com.google.gson.*;

public class OpenProdocAPI {
    private static final String BASE_URL = "http://localhost:8080/ProdocWeb2/APIRest";
    private String token;

    public void login(String username, String password) throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        String json = String.format("{\"Name\":\"%s\",\"Password\":\"%s\"}",
                                    username, password);

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/session"))
            .header("Content-Type", "application/json")
            .PUT(HttpRequest.BodyPublishers.ofString(json))
            .build();

        HttpResponse<String> response = client.send(request,
                                          HttpResponse.BodyHandlers.ofString());

        JsonObject jsonResponse = JsonParser.parseString(response.body())
                                            .getAsJsonObject();
        this.token = jsonResponse.get("Token").getAsString();
    }

    public String getFolder(String path) throws Exception {
        HttpClient client = HttpClient.newHttpClient();

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/folders/ByPath/" + path))
            .header("Authorization", "Bearer " + token)
            .GET()
            .build();

        HttpResponse<String> response = client.send(request,
                                          HttpResponse.BodyHandlers.ofString());
        return response.body();
    }
}
```

---

## Troubleshooting

### Issue: 401 Unauthorized

**Cause**: Missing or invalid token, or API REST is disabled

**Solutions**:
- Ensure you've logged in and obtained a valid token
- Check that the token is included in the `Authorization` header
- Verify token hasn't expired
- Check that API REST is enabled in OpenProdoc configuration

### Issue: 415 Unsupported Media Type

**Cause**: Wrong or missing `Content-Type` header

**Solutions**:
- For JSON endpoints: Use `Content-Type: application/json`
- For file uploads: Use `Content-Type: multipart/form-data`
- Don't set Content-Type for GET requests (let curl/client set it)

### Issue: Token Expired

**Cause**: JWT tokens have an expiration time

**Solutions**:
- Login again to get a new token
- Implement token refresh logic in your application
- Store token expiration time and renew before it expires

### Issue: Connection Refused

**Cause**: Cannot reach the OpenProdoc service

**Solutions**:
- Check that OpenProdoc pods are running: `kubectl get pods`
- Verify port-forward is active: `kubectl port-forward svc/openprodoc-core-engine 8080:8080`
- Check service exists: `kubectl get svc openprodoc-core-engine`
- Test internal cluster access from another pod

---

## Security Best Practices

1. **Use HTTPS in production**: Configure ingress with TLS certificates
2. **Store tokens securely**: Never commit tokens to version control
3. **Implement token refresh**: Renew tokens before expiration
4. **Use environment variables**: Store credentials in env vars, not code
5. **Rotate passwords**: Change default credentials in production
6. **Limit token lifetime**: Configure appropriate expiration times
7. **Use service accounts**: Create dedicated users for API access
8. **Monitor API usage**: Log and audit API calls
9. **Implement rate limiting**: Protect against abuse
10. **Validate input**: Always validate data before sending to API

---

## Additional Resources

- OpenProdoc Documentation: Check `/ProdocWeb2/help/` on your installation
- Source Code: Review Java source in `ProdocWeb2/src/java/APIRest/`
- GitHub: [OpenProdoc Repository](https://github.com/jquast/openprodoc)
- Community Support: OpenProdoc user forums and mailing lists

---

## API Version

This guide covers OpenProdoc REST API version 3.0.x

Last Updated: October 2025
