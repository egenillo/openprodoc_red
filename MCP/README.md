# OpenProdoc MCP Server

A Model Context Protocol (MCP) server that provides comprehensive tools for interacting with the OpenProdoc document management system via its REST API.

## Overview

This MCP server enables AI assistants to manage documents, folders, and thesaurus terms in OpenProdoc through a standardized interface. It supports all major OpenProdoc operations including:

- **Session Management**: Login/logout with JWT authentication
- **Folder Operations**: Create, read, update, delete, and search folders with custom attributes
- **Document Operations**: Upload, download, update, delete, and search documents with metadata
- **Thesaurus Management**: Create and manage hierarchical controlled vocabularies

## Features

- 🔐 **JWT Authentication**: Secure session management with automatic token handling
- 📁 **Complete Folder Management**: Full CRUD operations with support for hierarchical structures
- 📄 **Document Handling**: Upload/download with custom metadata and attributes
- 🏷️ **Thesaurus Support**: Manage controlled vocabularies and taxonomies
- 🔍 **Powerful Search**: SQL-like queries across all resource types
- 📊 **Dual Response Formats**: Markdown (human-readable) and JSON (machine-readable)
- ⚡ **Pagination Support**: Handle large datasets efficiently
- 🛡️ **Error Handling**: Clear, actionable error messages

## Quick Start

### 1. Install Dependencies

```bash
cd /openprodoc_red/MCP
pip install -r requirements.txt
```

### 2. Configure Environment (Optional but Recommended)

Set environment variables directly:

```bash
# Linux/macOS
export OPENPRODOC_BASE_URL="http://your-server:8080/ProdocWeb2/APIRest"
export OPENPRODOC_USERNAME="root"
export OPENPRODOC_PASSWORD="your_password"

# Windows PowerShell
$env:OPENPRODOC_BASE_URL="http://your-server:8080/ProdocWeb2/APIRest"
$env:OPENPRODOC_USERNAME="root"
$env:OPENPRODOC_PASSWORD="your_password"
```

### 3. Configure Claude Desktop

Edit `claude_desktop_config.json` (see [Integration with Claude Desktop](#integration-with-claude-desktop) section below).

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Access to an OpenProdoc server (local or remote)
- OpenProdoc REST API enabled

### Install Dependencies

```bash
cd /openprodoc_red/MCP
pip install -r requirements.txt
```

Or install manually:

```bash
pip install mcp httpx pydantic
```

## Configuration

The server can be configured using **environment variables** for secure, persistent configuration.

### Environment Variables

Set these before starting the MCP server:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENPRODOC_BASE_URL` | OpenProdoc API base URL | No | `http://localhost:8080/ProdocWeb2/APIRest` |
| `OPENPRODOC_USERNAME` | Default username for login | No | None |
| `OPENPRODOC_PASSWORD` | Default password for login | No | None |

### Configuration Methods

#### Option 1: Environment Variables (Recommended for Claude Desktop)

**Windows (PowerShell):**
```powershell
$env:OPENPRODOC_BASE_URL="http://your-server:8080/ProdocWeb2/APIRest"
$env:OPENPRODOC_USERNAME="root"
$env:OPENPRODOC_PASSWORD="your_password"
```

**Windows (Command Prompt):**
```cmd
set OPENPRODOC_BASE_URL=http://your-server:8080/ProdocWeb2/APIRest
set OPENPRODOC_USERNAME=root
set OPENPRODOC_PASSWORD=your_password
```

**Linux/macOS:**
```bash
export OPENPRODOC_BASE_URL="http://your-server:8080/ProdocWeb2/APIRest"
export OPENPRODOC_USERNAME="root"
export OPENPRODOC_PASSWORD="your_password"
```

**For persistent configuration**, add these to your shell profile (`.bashrc`, `.zshrc`, etc.) or use a `.env` file.

#### Option 2: Claude Desktop Configuration

Add environment variables to your Claude Desktop config:

```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["C:\\openprodoc_red\\MCP\\openprodoc_mcp.py"],
      "env": {
        "OPENPRODOC_BASE_URL": "http://your-server:8080/ProdocWeb2/APIRest",
        "OPENPRODOC_USERNAME": "root",
        "OPENPRODOC_PASSWORD": "your_password"
      }
    }
  }
}
```

#### Option 3: Runtime Parameters

Override during login call (takes precedence over environment variables):

```python
# Login with custom parameters
openprodoc_login(
    username="your_username",
    password="your_password",
    base_url="http://your-server:port/context/APIRest"
)

# Or use environment variable defaults
openprodoc_login()  # Uses OPENPRODOC_USERNAME, OPENPRODOC_PASSWORD, OPENPRODOC_BASE_URL
```

## Usage

### Integration with Claude Desktop

Add to your Claude Desktop configuration file (`claude_desktop_config.json`):

**Basic Configuration (requires manual login each session):**
```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["C:\\openprodoc_red\\MCP\\openprodoc_mcp.py"]
    }
  }
}
```

**Recommended: With Environment Variables (automatic login):**
```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["C:\\openprodoc_red\\MCP\\openprodoc_mcp.py"],
      "env": {
        "OPENPRODOC_BASE_URL": "http://localhost:8080/ProdocWeb2/APIRest",
        "OPENPRODOC_USERNAME": "root",
        "OPENPRODOC_PASSWORD": "your_password"
      }
    }
  }
}
```

After configuration, restart Claude Desktop. You can then:
- **Without env vars**: "Login to OpenProdoc with username root and password root"
- **With env vars**: "Login to OpenProdoc" (uses configured credentials automatically)

### Integration with Claude Code

Claude Code is the official CLI tool for Claude that also supports MCP servers. Configuration is similar to Claude Desktop but uses a different config file.

#### Configuration Steps

1. **Locate the Claude Code config file**: `.claude.json`
   - **Windows**: `%USERPROFILE%\.claude\.claude.json`
   - **macOS**: `~/.claude/.claude.json`
   - **Linux**: `~/.claude/.claude.json`

2. **Add the OpenProdoc MCP server** to your configuration:

**Basic Configuration:**
```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["C:\\openprodoc_red\\MCP\\openprodoc_mcp.py"]
    }
  }
}
```

**Recommended: With Environment Variables (automatic login):**
```json
{
  "mcpServers": {
    "openprodoc": {
      "command": "python",
      "args": ["C:\\openprodoc_red\\MCP\\openprodoc_mcp.py"],
      "env": {
        "OPENPRODOC_BASE_URL": "http://localhost:8080/ProdocWeb2/APIRest",
        "OPENPRODOC_USERNAME": "root",
        "OPENPRODOC_PASSWORD": "your_password"
      }
    }
  }
}
```

**Note**: Adjust the path in `args` to match your actual installation directory:
- Windows: Use double backslashes `C:\\openprodoc_red\\MCP\\openprodoc_mcp.py`
- macOS/Linux: Use forward slashes `/path/to/openprodoc_red/MCP/openprodoc_mcp.py`

3. **Restart Claude Code** or reload the MCP configuration for changes to take effect.

4. **Verify the connection**: Once Claude Code starts, the OpenProdoc MCP tools should be automatically available. Test with:
   - "Login to OpenProdoc" (if you configured env vars)
   - "Login to OpenProdoc with username root and password root" (without env vars)

#### Usage Example in Claude Code

```bash
# Start Claude Code
claude-code

# In the Claude Code session, you can now use natural language:
> Login to OpenProdoc
> Create a folder named "2024 Projects" with type PD_FOLDERS
> Upload the document report.pdf to the folder
> Search for all documents created after 2024-01-01
```

#### Troubleshooting Claude Code Integration

**Problem**: "MCP server 'openprodoc' not found"
**Solutions**:
- Verify the config file path is correct for your OS
- Check that the Python path in the config is correct (try `python3` instead of `python` on some systems)
- Ensure the file path to `openprodoc_mcp.py` is absolute and correct
- Restart Claude Code after making config changes

**Problem**: "Python not found" error
**Solutions**:
- Ensure Python 3.10+ is installed and in your PATH
- Use the full Python path in the config:
  - Windows: `"command": "C:\\Python311\\python.exe"`
  - macOS/Linux: `"command": "/usr/bin/python3"`

**Problem**: Tools work but credentials fail
**Solutions**:
- Verify the `OPENPRODOC_BASE_URL` points to your running OpenProdoc server
- Check that the username and password are correct
- Ensure the OpenProdoc REST API is enabled and accessible

## Available Tools

### Authentication Tools

#### `openprodoc_login`
Authenticate with OpenProdoc and obtain a JWT token.

**Parameters:**
- `username` (str, optional): OpenProdoc username (uses `OPENPRODOC_USERNAME` env var if not provided)
- `password` (str, optional): OpenProdoc password (uses `OPENPRODOC_PASSWORD` env var if not provided)
- `base_url` (str, optional): API base URL (uses `OPENPRODOC_BASE_URL` env var or default if not provided)

**Examples:**
```python
# Explicit credentials
openprodoc_login(username="root", password="root")

# Use environment variable defaults
openprodoc_login()  # Reads from OPENPRODOC_USERNAME and OPENPRODOC_PASSWORD

# Override base URL
openprodoc_login(
    username="admin",
    password="secret",
    base_url="http://remote-server:8080/ProdocWeb2/APIRest"
)
```

#### `openprodoc_logout`
Close the current session and invalidate the token.

**Example:**
```python
openprodoc_logout()
```

---

### Folder Tools

#### `openprodoc_create_folder`
Create a new folder with custom attributes.

**Parameters:**
- `name` (str): Folder name
- `folder_type` (str): Folder type (e.g., "PD_FOLDERS", "Course")
- `parent_id` (str, optional): Parent folder ID
- `parent_path` (str, optional): Parent folder path
- `acl` (str): Access control list (default: "Public")
- `attributes` (list, optional): Custom attributes
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_create_folder(
    name="Project Documents",
    folder_type="PD_FOLDERS",
    parent_id="root-folder-id",
    attributes=[
        {"Name": "Department", "Type": "String", "Values": ["IT"]},
        {"Name": "StartDate", "Type": "Date", "Values": ["2024-01-01"]}
    ]
)
```

#### `openprodoc_get_folder`
Retrieve folder metadata by ID or path.

**Parameters:**
- `folder_id` (str, optional): Folder ID
- `folder_path` (str, optional): Folder path
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_get_folder(folder_id="16cdeb939d9-3fc5285f4ed8aef0")
```

#### `openprodoc_update_folder`
Update folder metadata and attributes.

**Parameters:**
- `folder_id` (str, optional): Folder ID
- `folder_path` (str, optional): Folder path
- `name` (str, optional): New name
- `acl` (str, optional): New ACL
- `attributes` (list, optional): Updated attributes
- `response_format` (str): "markdown" or "json"

#### `openprodoc_delete_folder`
Delete a folder.

**Parameters:**
- `folder_id` (str, optional): Folder ID
- `folder_path` (str, optional): Folder path

#### `openprodoc_list_subfolders`
List all subfolders in a parent folder.

**Parameters:**
- `folder_id` (str, optional): Parent folder ID
- `folder_path` (str, optional): Parent folder path
- `initial` (int): Starting index (default: 0)
- `final` (int): Ending index (default: 200)
- `response_format` (str): "markdown" or "json"

#### `openprodoc_list_documents_in_folder`
List all documents in a folder.

**Parameters:**
- `folder_id` (str, optional): Folder ID
- `folder_path` (str, optional): Folder path
- `initial` (int): Starting index (default: 0)
- `final` (int): Ending index (default: 200)
- `response_format` (str): "markdown" or "json"

#### `openprodoc_search_folders`
Search folders using SQL-like queries.

**Parameters:**
- `query` (str): SQL query (e.g., "Select * from Course where Teacher='John'")
- `initial` (int): Starting index (default: 0)
- `final` (int): Ending index (default: 100)
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_search_folders(
    query="Select PDId,Title from Course where StartDate>'2024-01-01'",
    final=50
)
```

---

### Document Tools

#### `openprodoc_upload_document`
Upload a document with metadata.

**Parameters:**
- `file_path` (str): Local file path to upload
- `title` (str): Document title
- `document_type` (str): Document type (e.g., "PD_DOCS")
- `parent_folder_id` (str): Parent folder ID
- `acl` (str): Access control list (default: "Public")
- `version_label` (str): Version label (default: "1.0")
- `doc_date` (str, optional): Document date (YYYY-MM-DD)
- `attributes` (list, optional): Custom attributes
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_upload_document(
    file_path="C:\\Documents\\report.pdf",
    title="Quarterly Report Q1 2024",
    document_type="PD_DOCS",
    parent_folder_id="folder-id-here",
    doc_date="2024-03-31",
    attributes=[
        {"Name": "Author", "Type": "String", "Values": ["John Doe"]},
        {"Name": "Department", "Type": "String", "Values": ["Finance"]}
    ]
)
```

#### `openprodoc_get_document_metadata`
Get document metadata without downloading content.

**Parameters:**
- `document_id` (str): Document ID
- `response_format` (str): "markdown" or "json"

#### `openprodoc_download_document`
Download document content to local file.

**Parameters:**
- `document_id` (str): Document ID
- `output_path` (str): Local file path to save

**Example:**
```python
openprodoc_download_document(
    document_id="doc-id-here",
    output_path="C:\\Downloads\\report.pdf"
)
```

#### `openprodoc_update_document`
Update document metadata and/or content.

**Parameters:**
- `document_id` (str): Document ID
- `file_path` (str, optional): New file to upload
- `title` (str, optional): New title
- `acl` (str, optional): New ACL
- `version_label` (str, optional): New version
- `doc_date` (str, optional): New document date
- `attributes` (list, optional): Updated attributes
- `response_format` (str): "markdown" or "json"

#### `openprodoc_delete_document`
Delete a document.

**Parameters:**
- `document_id` (str): Document ID to delete

#### `openprodoc_search_documents`
Search documents using SQL-like queries.

**Parameters:**
- `query` (str): SQL query
- `initial` (int): Starting index (default: 0)
- `final` (int): Ending index (default: 100)
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_search_documents(
    query="Select PDId,Title from PD_DOCS where PDAuthor='root' and DocDate>'2024-01-01'"
)
```

---

### Thesaurus Tools

#### `openprodoc_create_term`
Create a new thesaurus term.

**Parameters:**
- `name` (str): Term name
- `description` (str): Term description
- `language` (str): Language code (default: "EN")
- `scope_note` (str, optional): Scope note
- `parent_id` (str, optional): Parent term ID
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_create_term(
    name="Business Units",
    description="Organizational business units",
    language="EN",
    scope_note="Used for departmental classification",
    parent_id="root-term-id"
)
```

#### `openprodoc_get_term`
Get thesaurus term metadata.

**Parameters:**
- `term_id` (str): Term ID
- `response_format` (str): "markdown" or "json"

#### `openprodoc_update_term`
Update term metadata.

**Parameters:**
- `term_id` (str): Term ID
- `name` (str, optional): New name
- `description` (str, optional): New description
- `language` (str, optional): New language
- `scope_note` (str, optional): New scope note
- `response_format` (str): "markdown" or "json"

#### `openprodoc_delete_term`
Delete a thesaurus term.

**Parameters:**
- `term_id` (str): Term ID to delete

#### `openprodoc_list_subterms`
List subterms under a parent term.

**Parameters:**
- `parent_term_id` (str): Parent term ID
- `initial` (int): Starting index (default: 0)
- `final` (int): Ending index (default: 200)
- `response_format` (str): "markdown" or "json"

#### `openprodoc_search_terms`
Search thesaurus terms using SQL queries.

**Parameters:**
- `query` (str): SQL query (note: table name is "this" for thesaurus)
- `initial` (int): Starting index (default: 0)
- `final` (int): Ending index (default: 100)
- `response_format` (str): "markdown" or "json"

**Example:**
```python
openprodoc_search_terms(
    query="Select * from this where ParentId='root-id' and Lang='EN'"
)
```

---

## Common Workflows

### 1. Creating a Project Structure

```python
# Login
openprodoc_login(username="root", password="root")

# Create main project folder
result = openprodoc_create_folder(
    name="2024 Projects",
    folder_type="PD_FOLDERS"
)
# Extract folder ID from result

# Create subfolders
openprodoc_create_folder(
    name="Q1 Reports",
    folder_type="PD_FOLDERS",
    parent_id="main-folder-id"
)

# Upload document
openprodoc_upload_document(
    file_path="C:\\report.pdf",
    title="January Report",
    document_type="PD_DOCS",
    parent_folder_id="subfolder-id"
)
```

### 2. Searching and Downloading Documents

```python
# Search for documents
results = openprodoc_search_documents(
    query="Select PDId,Title from PD_DOCS where Title like '%Report%' and DocDate>'2024-01-01'"
)

# Download a specific document
openprodoc_download_document(
    document_id="found-doc-id",
    output_path="C:\\Downloads\\report.pdf"
)
```

### 3. Managing Thesaurus Taxonomy

```python
# Create root term
root_result = openprodoc_create_term(
    name="Departments",
    description="Company departments",
    language="EN"
)

# Create child term
openprodoc_create_term(
    name="IT",
    description="Information Technology",
    language="EN",
    parent_id="root-term-id"
)

# Search terms
openprodoc_search_terms(
    query="Select * from this where Lang='EN'"
)
```

## Error Handling

The server provides clear, actionable error messages:

- **401 Unauthorized**: Session expired or invalid credentials → Login again
- **404 Not Found**: Resource doesn't exist → Check ID/path
- **403 Permission Denied**: Insufficient permissions → Check ACL settings
- **406 Not Acceptable**: Validation error or duplicate entry → Review input data

## Response Formats

### Markdown (Default)
Human-readable formatted output with headers, lists, and structured information.

### JSON
Machine-readable structured data for programmatic processing.

Example:
```python
# Markdown response
openprodoc_get_folder(folder_id="abc", response_format="markdown")

# JSON response
openprodoc_get_folder(folder_id="abc", response_format="json")
```

## Pagination

For large result sets, use pagination parameters:

```python
# Get first 50 results
openprodoc_list_subfolders(
    folder_id="parent-id",
    initial=0,
    final=50
)

# Get next 50 results
openprodoc_list_subfolders(
    folder_id="parent-id",
    initial=50,
    final=100
)
```

## Character Limits

Responses are automatically truncated if they exceed 25,000 characters. The truncation message will guide you to use pagination or filters.


## License

This MCP server is part of the OpenProdoc ecosystem. Please refer to the main OpenProdoc license.

## Support

For OpenProdoc-specific questions, consult the OpenProdoc documentation.
For MCP-related questions, see the [MCP Documentation](https://modelcontextprotocol.io).

## Version

- **MCP Server Version**: 1.0.0
- **Compatible with**: OpenProdoc REST API
- **MCP SDK Version**: >=1.0.0
