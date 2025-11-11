#!/usr/bin/env python3
"""
OpenProdoc MCP Server.

This server provides tools to interact with OpenProdoc REST API for document management,
including folder operations, document upload/download, and thesaurus management.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
import json
import base64
import os
import logging
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP, Context
import httpx

# Configure logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log.txt', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('openprodoc_mcp')

logger.info("=" * 80)
logger.info("Starting OpenProdoc MCP Server initialization")
logger.info("=" * 80)

# Initialize the MCP server
mcp = FastMCP("openprodoc_mcp")
logger.info("FastMCP server instance created")

# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters
DEFAULT_TIMEOUT = 30.0
DEFAULT_PAGINATION_LIMIT = 200

# Global variable to store the authentication token and base URL
# These can be configured via environment variables:
# - OPENPRODOC_BASE_URL: Base URL for the OpenProdoc API
# - OPENPRODOC_USERNAME: Default username for auto-login (optional)
# - OPENPRODOC_PASSWORD: Default password for auto-login (optional)
_auth_token: Optional[str] = None
_base_url: str = os.getenv("OPENPRODOC_BASE_URL", "http://localhost:8080/ProdocWeb2/APIRest")
_default_username: Optional[str] = os.getenv("OPENPRODOC_USERNAME")
_default_password: Optional[str] = os.getenv("OPENPRODOC_PASSWORD")

logger.info(f"Configuration loaded - Base URL: {_base_url}")
logger.info(f"Default username configured: {bool(_default_username)}")
logger.info(f"Default password configured: {bool(_default_password)}")


# ============================================================================
# ENUMS AND PYDANTIC MODELS
# ============================================================================

class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class AttributeType(str, Enum):
    """Supported attribute types in OpenProdoc."""
    STRING = "String"
    DATE = "Date"
    BOOLEAN = "Boolean"
    INTEGER = "Integer"


class Attribute(BaseModel):
    """Represents a custom attribute in OpenProdoc."""
    Name: str = Field(..., description="Attribute name")
    Type: AttributeType = Field(..., description="Attribute type")
    Values: List[str] = Field(..., description="List of values for this attribute")


# ============================================================================
# AUTHENTICATION MODELS
# ============================================================================

class LoginInput(BaseModel):
    """Input model for login operation."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    username: Optional[str] = Field(
        default=None,
        description="OpenProdoc username (falls back to OPENPRODOC_USERNAME env var if not provided)",
        min_length=1,
        max_length=100
    )
    password: Optional[str] = Field(
        default=None,
        description="OpenProdoc password (falls back to OPENPRODOC_PASSWORD env var if not provided)",
        min_length=1,
        max_length=100
    )
    base_url: Optional[str] = Field(
        default=None,
        description="Base URL for OpenProdoc API (falls back to OPENPRODOC_BASE_URL env var or default)"
    )


# ============================================================================
# FOLDER MODELS
# ============================================================================

class CreateFolderInput(BaseModel):
    """Input model for creating a folder."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    name: str = Field(..., description="Folder name", min_length=1, max_length=200)
    folder_type: str = Field(..., description="Folder type (e.g., 'PD_FOLDERS', 'Course')")
    parent_id: Optional[str] = Field(default=None, description="Parent folder ID")
    parent_path: Optional[str] = Field(default=None, description="Parent folder path (alternative to parent_id)")
    acl: str = Field(default="Public", description="Access control list")
    attributes: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="List of custom attributes with Name, Type, and Values fields"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class GetFolderInput(BaseModel):
    """Input model for getting folder metadata."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    folder_id: Optional[str] = Field(default=None, description="Folder ID (use either folder_id or folder_path)")
    folder_path: Optional[str] = Field(default=None, description="Folder path (use either folder_id or folder_path)")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('folder_path')
    @classmethod
    def validate_identifiers(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one identifier is provided."""
        folder_id = info.data.get('folder_id')
        if not folder_id and not v:
            raise ValueError("Either folder_id or folder_path must be provided")
        return v


class UpdateFolderInput(BaseModel):
    """Input model for updating a folder."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    folder_id: Optional[str] = Field(default=None, description="Folder ID (use either folder_id or folder_path)")
    folder_path: Optional[str] = Field(default=None, description="Folder path (use either folder_id or folder_path)")
    name: Optional[str] = Field(default=None, description="New folder name")
    acl: Optional[str] = Field(default=None, description="New access control list")
    attributes: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Updated custom attributes with Name, Type, and Values fields"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('folder_path')
    @classmethod
    def validate_identifiers(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one identifier is provided."""
        folder_id = info.data.get('folder_id')
        if not folder_id and not v:
            raise ValueError("Either folder_id or folder_path must be provided")
        return v


class DeleteFolderInput(BaseModel):
    """Input model for deleting a folder."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    folder_id: Optional[str] = Field(default=None, description="Folder ID (use either folder_id or folder_path)")
    folder_path: Optional[str] = Field(default=None, description="Folder path (use either folder_id or folder_path)")

    @field_validator('folder_path')
    @classmethod
    def validate_identifiers(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one identifier is provided."""
        folder_id = info.data.get('folder_id')
        if not folder_id and not v:
            raise ValueError("Either folder_id or folder_path must be provided")
        return v


class ListSubfoldersInput(BaseModel):
    """Input model for listing subfolders."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    folder_id: Optional[str] = Field(default=None, description="Parent folder ID (use either folder_id or folder_path)")
    folder_path: Optional[str] = Field(default=None, description="Parent folder path (use either folder_id or folder_path)")
    initial: int = Field(default=0, description="Starting index for pagination", ge=0)
    final: int = Field(default=DEFAULT_PAGINATION_LIMIT, description="Ending index for pagination", ge=1)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('folder_path')
    @classmethod
    def validate_identifiers(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one identifier is provided."""
        folder_id = info.data.get('folder_id')
        if not folder_id and not v:
            raise ValueError("Either folder_id or folder_path must be provided")
        return v


class ListDocumentsInput(BaseModel):
    """Input model for listing documents in a folder."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    folder_id: Optional[str] = Field(default=None, description="Folder ID (use either folder_id or folder_path)")
    folder_path: Optional[str] = Field(default=None, description="Folder path (use either folder_id or folder_path)")
    initial: int = Field(default=0, description="Starting index for pagination", ge=0)
    final: int = Field(default=DEFAULT_PAGINATION_LIMIT, description="Ending index for pagination", ge=1)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )

    @field_validator('folder_path')
    @classmethod
    def validate_identifiers(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure at least one identifier is provided."""
        folder_id = info.data.get('folder_id')
        if not folder_id and not v:
            raise ValueError("Either folder_id or folder_path must be provided")
        return v


class SearchInput(BaseModel):
    """Input model for search operations."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    query: str = Field(..., description="SQL-like query string (e.g., 'Select PDId,Title from PD_DOCS where PDId<>\"xxx\"')", min_length=1)
    initial: int = Field(default=0, description="Starting index for results", ge=0)
    final: int = Field(default=100, description="Ending index for results", ge=1, le=1000)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


# ============================================================================
# DOCUMENT MODELS
# ============================================================================

class GetDocumentInput(BaseModel):
    """Input model for getting document metadata."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    document_id: str = Field(..., description="Document ID", min_length=1)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class DownloadDocumentInput(BaseModel):
    """Input model for downloading document content."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    document_id: str = Field(..., description="Document ID", min_length=1)
    output_path: str = Field(..., description="Local file path to save the document", min_length=1)


class DeleteDocumentInput(BaseModel):
    """Input model for deleting a document."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    document_id: str = Field(..., description="Document ID", min_length=1)


class UploadDocumentInput(BaseModel):
    """Input model for uploading a document."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    file_path: str = Field(..., description="Local file path to upload", min_length=1)
    title: str = Field(..., description="Document title", min_length=1, max_length=200)
    document_type: str = Field(..., description="Document type (e.g., 'PD_DOCS', 'ECM_Standards')")
    parent_folder_id: str = Field(..., description="Parent folder ID where document will be stored")
    acl: str = Field(default="Public", description="Access control list")
    version_label: str = Field(default="1.0", description="Version label")
    doc_date: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d"),
        description="Document date in YYYY-MM-DD format (defaults to today)"
    )
    attributes: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="List of custom attributes with Name, Type, and Values fields"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class UpdateDocumentInput(BaseModel):
    """Input model for updating a document."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    document_id: str = Field(..., description="Document ID to update", min_length=1)
    file_path: Optional[str] = Field(default=None, description="New file to upload (optional)")
    title: Optional[str] = Field(default=None, description="New document title")
    document_type: Optional[str] = Field(default=None, description="Document type (e.g., 'PD_DOCS', 'ECM_Standards'). Required when uploading a new file version.")
    parent_folder_id: Optional[str] = Field(default=None, description="Parent folder ID where document is stored")
    acl: Optional[str] = Field(default=None, description="New access control list")
    version_label: Optional[str] = Field(default=None, description="New version label (e.g., '1.0', '2.0')")
    doc_date: Optional[str] = Field(default=None, description="Document date in YYYY-MM-DD format")
    author: Optional[str] = Field(default=None, description="Document author")
    pd_date: Optional[str] = Field(default=None, description="PDDate timestamp in 'YYYY-MM-DD HH:MM:SS' format")
    attributes: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Updated custom attributes with Name, Type, and Values fields"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


# ============================================================================
# THESAURUS MODELS
# ============================================================================

class CreateTermInput(BaseModel):
    """Input model for creating a thesaurus term."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    name: str = Field(..., description="Term name", min_length=1, max_length=200)
    description: str = Field(..., description="Term description", min_length=1)
    language: str = Field(default="EN", description="Language code (e.g., 'EN', 'ES')")
    scope_note: Optional[str] = Field(default=None, description="Scope note for the term")
    parent_id: Optional[str] = Field(default=None, description="Parent term ID for hierarchical structure")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class GetTermInput(BaseModel):
    """Input model for getting thesaurus term metadata."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    term_id: str = Field(..., description="Term ID", min_length=1)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class UpdateTermInput(BaseModel):
    """Input model for updating a thesaurus term."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    term_id: str = Field(..., description="Term ID to update", min_length=1)
    name: Optional[str] = Field(default=None, description="New term name")
    description: Optional[str] = Field(default=None, description="New term description")
    language: Optional[str] = Field(default=None, description="New language code")
    scope_note: Optional[str] = Field(default=None, description="New scope note")
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


class DeleteTermInput(BaseModel):
    """Input model for deleting a thesaurus term."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    term_id: str = Field(..., description="Term ID to delete", min_length=1)


class ListSubtermsInput(BaseModel):
    """Input model for listing subterms."""
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    parent_term_id: str = Field(..., description="Parent term ID", min_length=1)
    initial: int = Field(default=0, description="Starting index for pagination", ge=0)
    final: int = Field(default=DEFAULT_PAGINATION_LIMIT, description="Ending index for pagination", ge=1)
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' or 'json'"
    )


# ============================================================================
# SHARED UTILITY FUNCTIONS
# ============================================================================

def _get_auth_headers() -> Dict[str, str]:
    """Get authentication headers with current token."""
    if not _auth_token:
        logger.error("Authentication required but no token available")
        raise ValueError("Not authenticated. Please login first using openprodoc_login.")
    logger.debug(f"Using auth token (length: {len(_auth_token)})")
    return {
        "Authorization": f"Bearer {_auth_token}",
        "Accept": "application/json"
    }


async def _make_api_request(
    endpoint: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Reusable function for all API calls to OpenProdoc.

    Args:
        endpoint: API endpoint path (e.g., 'folders', 'documents/ById/123')
        method: HTTP method (GET, POST, PUT, DELETE)
        headers: Optional additional headers
        json_data: JSON data for request body
        params: Query parameters
        files: Files for multipart upload
        data: Form data for multipart upload

    Returns:
        Parsed JSON response from the API

    Raises:
        httpx.HTTPStatusError: If the API returns an error status
        httpx.TimeoutException: If the request times out
    """
    url = f"{_base_url}/{endpoint}"
    request_headers = headers or {}

    logger.debug(f"API Request - Method: {method}, URL: {url}")
    logger.debug(f"API Request - Params: {params}")
    if json_data:
        logger.debug(f"API Request - JSON Data: {json.dumps(json_data, indent=2)}")
    if files:
        logger.debug(f"API Request - Files: {list(files.keys())}")

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=request_headers,
                json=json_data,
                params=params,
                files=files,
                data=data
            )

            logger.debug(f"API Response - Status: {response.status_code}")
            logger.debug(f"API Response - Headers: {dict(response.headers)}")

            response.raise_for_status()

            # Handle binary responses
            if "application/json" not in response.headers.get("content-type", ""):
                logger.debug(f"API Response - Binary content, size: {len(response.content)} bytes")
                return {"binary_content": response.content}

            response_data = response.json()
            logger.debug(f"API Response - JSON: {json.dumps(response_data, indent=2)}")
            return response_data
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP Error - Status: {e.response.status_code}, URL: {url}")
        logger.error(f"HTTP Error - Response: {e.response.text}")
        raise
    except httpx.TimeoutException as e:
        logger.error(f"Timeout Error - URL: {url}, Timeout: {DEFAULT_TIMEOUT}s")
        raise
    except Exception as e:
        logger.error(f"Unexpected Error in API request - {type(e).__name__}: {str(e)}")
        raise


def _handle_api_error(e: Exception) -> str:
    """Consistent error formatting across all tools."""
    if isinstance(e, httpx.HTTPStatusError):
        if e.response.status_code == 401:
            return "Error: Unauthorized. Your session may have expired. Please login again using openprodoc_login."
        elif e.response.status_code == 404:
            return "Error: Resource not found. Please check the ID or path is correct."
        elif e.response.status_code == 403:
            return "Error: Permission denied. You don't have access to this resource."
        elif e.response.status_code == 406:
            # Try to extract error message from response
            try:
                error_data = e.response.json()
                if error_data.get("Res") == "KO":
                    return f"Error: {error_data.get('Msg', 'Not Acceptable')}"
            except:
                pass
            return "Error: Request not acceptable. Check your input data for validation errors or duplicate entries."
        elif e.response.status_code == 429:
            return "Error: Rate limit exceeded. Please wait before making more requests."
        elif e.response.status_code == 500:
            # Try to extract error message from response (e.g., "Empty_conditions", query errors)
            try:
                error_data = e.response.json()
                if error_data.get("Res") == "KO":
                    error_msg = error_data.get('Msg', 'Internal server error')
                    return f"Error: Internal server error - {error_msg}"
                elif isinstance(error_data, dict) and "Msg" in error_data:
                    return f"Error: Internal server error - {error_data.get('Msg')}"
            except:
                pass
            return "Error: Internal server error. This may be due to invalid query syntax or missing WHERE clause in search queries."
        return f"Error: API request failed with status {e.response.status_code}"
    elif isinstance(e, httpx.TimeoutException):
        return "Error: Request timed out. The server may be slow or unreachable. Please try again."
    elif isinstance(e, ValueError):
        return f"Error: {str(e)}"
    return f"Error: Unexpected error occurred: {type(e).__name__}: {str(e)}"


def _extract_attr_value(item: Dict[str, Any], attr_name: str, default: str = 'N/A') -> str:
    """
    Extract a value from the Attrs array structure returned by OpenProdoc search.

    OpenProdoc search results return data in this format:
    {
        "Attrs": [
            {"Name": "PDId", "Type": "String", "Values": ["some-id"]},
            {"Name": "Title", "Type": "String", "Values": ["Some Title"]},
            ...
        ]
    }
    """
    # First try direct access (for get/create/update operations)
    if attr_name in item:
        return str(item.get(attr_name, default))

    # Then try Attrs array (for search operations)
    attrs = item.get('Attrs', [])
    for attr in attrs:
        if attr.get('Name') == attr_name:
            values = attr.get('Values', [])
            return values[0] if values else default

    return default


def _format_folder_markdown(folder: Dict[str, Any]) -> str:
    """Format folder data as markdown."""
    name = _extract_attr_value(folder, 'Title', 'Unknown')
    folder_id = _extract_attr_value(folder, 'PDId', 'N/A')
    folder_type = _extract_attr_value(folder, 'FolderType', 'N/A')
    acl = _extract_attr_value(folder, 'ACL', 'N/A')
    parent_id = _extract_attr_value(folder, 'ParentId', 'N/A')
    created = _extract_attr_value(folder, 'PDDate', 'N/A')
    author = _extract_attr_value(folder, 'PDAutor', 'N/A')

    lines = [f"# Folder: {name}"]
    lines.append("")
    lines.append(f"- **ID**: {folder_id}")
    lines.append(f"- **Type**: {folder_type}")
    lines.append(f"- **ACL**: {acl}")
    lines.append(f"- **Parent ID**: {parent_id}")
    lines.append(f"- **Created**: {created}")
    lines.append(f"- **Author**: {author}")

    # Add custom attributes if present
    list_attr = folder.get('ListAttr', [])
    if list_attr:
        lines.append("")
        lines.append("## Custom Attributes")
        for attr in list_attr:
            attr_name = attr.get('Name', 'Unknown')
            attr_type = attr.get('Type', 'Unknown')
            attr_values = ', '.join(attr.get('Values', []))
            lines.append(f"- **{attr_name}** ({attr_type}): {attr_values}")

    return "\n".join(lines)


def _format_folders_list_markdown(folders: List[Dict[str, Any]], total: Optional[int] = None) -> str:
    """Format list of folders as markdown."""
    if not folders:
        return "No folders found."

    lines = ["# Folders"]
    if total is not None:
        lines.append(f"\nTotal: {total} folders (showing {len(folders)})")
    else:
        lines.append(f"\nShowing {len(folders)} folders")
    lines.append("")

    for folder in folders:
        name = _extract_attr_value(folder, 'Title', 'Unknown')
        folder_id = _extract_attr_value(folder, 'PDId', 'N/A')
        folder_type = _extract_attr_value(folder, 'FolderType', 'N/A')
        created = _extract_attr_value(folder, 'PDDate', 'N/A')
        author = _extract_attr_value(folder, 'PDAutor', 'N/A')

        lines.append(f"## {name} ({folder_id})")
        lines.append(f"- **Type**: {folder_type}")
        lines.append(f"- **Created**: {created}")
        lines.append(f"- **Author**: {author}")

        # Show a few key attributes if present
        list_attr = folder.get('ListAttr', [])
        if list_attr:
            lines.append(f"- **Attributes**: {len(list_attr)} custom attributes")
        lines.append("")

    return "\n".join(lines)


def _format_document_markdown(doc: Dict[str, Any]) -> str:
    """Format document metadata as markdown."""
    title = _extract_attr_value(doc, 'Title', 'Unknown')
    doc_id = _extract_attr_value(doc, 'PDId', 'N/A')
    doc_type = _extract_attr_value(doc, 'DocType', 'N/A')
    acl = _extract_attr_value(doc, 'ACL', 'N/A')
    parent_id = _extract_attr_value(doc, 'ParentId', 'N/A')
    version = _extract_attr_value(doc, 'Version', 'N/A')
    doc_date = _extract_attr_value(doc, 'DocDate', 'N/A')
    created = _extract_attr_value(doc, 'PDDate', 'N/A')
    author = _extract_attr_value(doc, 'PDAutor', 'N/A')

    lines = [f"# Document: {title}"]
    lines.append("")
    lines.append(f"- **ID**: {doc_id}")
    lines.append(f"- **Type**: {doc_type}")
    lines.append(f"- **ACL**: {acl}")
    lines.append(f"- **Parent Folder ID**: {parent_id}")
    lines.append(f"- **Version**: {version}")
    lines.append(f"- **Document Date**: {doc_date}")
    lines.append(f"- **Created**: {created}")
    lines.append(f"- **Author**: {author}")

    # Add custom attributes if present
    list_attr = doc.get('ListAttr', [])
    if list_attr:
        lines.append("")
        lines.append("## Custom Attributes")
        for attr in list_attr:
            attr_name = attr.get('Name', 'Unknown')
            attr_type = attr.get('Type', 'Unknown')
            attr_values = ', '.join(attr.get('Values', []))
            lines.append(f"- **{attr_name}** ({attr_type}): {attr_values}")

    return "\n".join(lines)


def _format_documents_list_markdown(documents: List[Dict[str, Any]], total: Optional[int] = None) -> str:
    """Format list of documents as markdown."""
    if not documents:
        return "No documents found."

    lines = ["# Documents"]
    if total is not None:
        lines.append(f"\nTotal: {total} documents (showing {len(documents)})")
    else:
        lines.append(f"\nShowing {len(documents)} documents")
    lines.append("")

    for doc in documents:
        title = _extract_attr_value(doc, 'Title', 'Unknown')
        doc_id = _extract_attr_value(doc, 'PDId', 'N/A')
        doc_type = _extract_attr_value(doc, 'DocType', 'N/A')
        version = _extract_attr_value(doc, 'Version', 'N/A')
        created = _extract_attr_value(doc, 'PDDate', 'N/A')
        author = _extract_attr_value(doc, 'PDAutor', 'N/A')

        lines.append(f"## {title} ({doc_id})")
        lines.append(f"- **Type**: {doc_type}")
        lines.append(f"- **Version**: {version}")
        lines.append(f"- **Created**: {created}")
        lines.append(f"- **Author**: {author}")

        # Show a few key attributes if present
        list_attr = doc.get('ListAttr', [])
        if list_attr:
            lines.append(f"- **Attributes**: {len(list_attr)} custom attributes")
        lines.append("")

    return "\n".join(lines)


def _format_term_markdown(term: Dict[str, Any]) -> str:
    """Format thesaurus term as markdown."""
    name = _extract_attr_value(term, 'Name', 'Unknown')
    term_id = _extract_attr_value(term, 'Id', 'N/A')
    description = _extract_attr_value(term, 'Desc', 'N/A')
    language = _extract_attr_value(term, 'Lang', 'N/A')
    scope_note = _extract_attr_value(term, 'ScopeNote', 'N/A')
    parent_id = _extract_attr_value(term, 'ParentId', 'N/A')

    lines = [f"# Term: {name}"]
    lines.append("")
    lines.append(f"- **ID**: {term_id}")
    lines.append(f"- **Description**: {description}")
    lines.append(f"- **Language**: {language}")
    lines.append(f"- **Scope Note**: {scope_note}")
    lines.append(f"- **Parent ID**: {parent_id}")

    return "\n".join(lines)


def _format_terms_list_markdown(terms: List[Dict[str, Any]], total: Optional[int] = None) -> str:
    """Format list of terms as markdown."""
    if not terms:
        return "No terms found."

    lines = ["# Thesaurus Terms"]
    if total is not None:
        lines.append(f"\nTotal: {total} terms (showing {len(terms)})")
    else:
        lines.append(f"\nShowing {len(terms)} terms")
    lines.append("")

    for term in terms:
        name = _extract_attr_value(term, 'Name', 'Unknown')
        term_id = _extract_attr_value(term, 'Id', 'N/A')
        description = _extract_attr_value(term, 'Desc', 'N/A')
        language = _extract_attr_value(term, 'Lang', 'N/A')

        lines.append(f"## {name} ({term_id})")
        lines.append(f"- **Description**: {description}")
        lines.append(f"- **Language**: {language}")
        lines.append("")

    return "\n".join(lines)


def _check_truncation(result: str, data: List[Any], item_type: str = "items") -> str:
    """Check if response exceeds character limit and truncate if needed."""
    if len(result) > CHARACTER_LIMIT:
        # Truncate to half the items
        truncated_count = max(1, len(data) // 2)
        result_lines = result.split('\n')
        # Keep header and first half
        estimated_lines = len(result_lines) // 2
        truncated_result = '\n'.join(result_lines[:estimated_lines])

        truncation_msg = (
            f"\n\n---\n**TRUNCATED**: Response too large. "
            f"Showing approximately {truncated_count} of {len(data)} {item_type}. "
            f"Use pagination parameters (initial/final) or add filters to see more results."
        )
        return truncated_result + truncation_msg
    return result


# ============================================================================
# AUTHENTICATION TOOLS
# ============================================================================

@mcp.tool(
    name="openprodoc_login",
    annotations={
        "title": "Login to OpenProdoc",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_login(params: LoginInput) -> str:
    """
    Authenticate with OpenProdoc and obtain a JWT token for subsequent API calls.

    This tool must be called before any other OpenProdoc tools. It creates a session
    and returns a JWT token that is automatically stored for use in subsequent requests.
    The token is valid for approximately 24 hours.

    Args:
        params (LoginInput): Login credentials containing:
            - username (str): OpenProdoc username (e.g., "root", "admin")
            - password (str): OpenProdoc password
            - base_url (Optional[str]): Base URL for OpenProdoc API
              (default: "http://localhost:8080/ProdocWeb2/APIRest")

    Returns:
        str: Success message with token information or error message

        Success response:
        "Successfully logged in to OpenProdoc as <username>. Token is valid for 24 hours."

        Error response:
        "Error: Unauthorized. Invalid username or password."
        "Error: Request timed out. The server may be unreachable."

    Examples:
        - Use when: Starting a session before performing any document operations
        - Use when: Token has expired and you need to re-authenticate
        - Don't use when: Already logged in with a valid token

    Error Handling:
        - Returns "Error: Unauthorized" for invalid credentials (401 status)
        - Returns "Error: Request timed out" if server is unreachable
        - Automatically stores the token for use in subsequent API calls
    """
    global _auth_token, _base_url, _default_username, _default_password

    logger.info("=" * 60)
    logger.info("TOOL CALLED: openprodoc_login")
    logger.info("=" * 60)

    try:
        # Use environment variable fallbacks
        username = params.username or _default_username
        password = params.password or _default_password
        base_url = params.base_url or _base_url

        logger.info(f"Login attempt - Username: {username}, Base URL: {base_url}")

        # Validate that we have credentials
        if not username or not password:
            logger.error("Login failed - Missing credentials")
            return "Error: Username and password are required. Provide them as parameters or set OPENPRODOC_USERNAME and OPENPRODOC_PASSWORD environment variables."

        # Update base URL if provided or from env
        _base_url = base_url

        # Make login request
        logger.debug(f"Sending login request to {_base_url}/session")
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.put(
                f"{_base_url}/session",
                json={
                    "Name": username,
                    "Password": password
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            logger.debug(f"Login response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()

        # Check response
        if data.get("Res") == "OK" and "Token" in data:
            _auth_token = data["Token"]
            logger.info(f"Login successful - Username: {username}, Token length: {len(_auth_token)}")
            return f"Successfully logged in to OpenProdoc as {username}. Token is valid for 24 hours."
        else:
            logger.error(f"Login failed - Response: {data}")
            return f"Error: Login failed. {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        logger.error(f"Login exception - {type(e).__name__}: {str(e)}")
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_logout",
    annotations={
        "title": "Logout from OpenProdoc",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_logout() -> str:
    """
    Close the current OpenProdoc session and invalidate the authentication token.

    This tool should be called when you're done working with OpenProdoc to properly
    close the session and clean up server-side resources.

    Returns:
        str: Success message confirming logout or error message

        Success response:
        "Successfully logged out from OpenProdoc."

        Error response:
        "Error: Not authenticated. Please login first."

    Examples:
        - Use when: Finished working with OpenProdoc
        - Use when: Need to switch to a different user account
        - Don't use when: Not currently logged in

    Error Handling:
        - Returns error if not currently authenticated
        - Clears the stored token even if the server request fails
    """
    global _auth_token

    logger.info("=" * 60)
    logger.info("TOOL CALLED: openprodoc_logout")
    logger.info("=" * 60)

    try:
        if not _auth_token:
            logger.warning("Logout attempt with no active session")
            return "Error: Not authenticated. No active session to close."

        logger.info("Logging out - Clearing authentication token")

        # Make logout request
        headers = _get_auth_headers()
        # Don't set Content-Type for DELETE requests without body

        data = await _make_api_request(
            "session",
            method="DELETE",
            headers=headers
        )

        # Clear the token
        _auth_token = None
        logger.info("Logout successful - Token cleared")

        if data.get("Res") == "OK":
            return "Successfully logged out from OpenProdoc."
        else:
            return f"Session closed (with message: {data.get('Msg', 'Unknown')})"

    except Exception as e:
        # Clear token even on error
        _auth_token = None
        logger.error(f"Logout exception - {type(e).__name__}: {str(e)}")
        return _handle_api_error(e)


# ============================================================================
# FOLDER TOOLS
# ============================================================================

@mcp.tool(
    name="openprodoc_create_folder",
    annotations={
        "title": "Create OpenProdoc Folder",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def openprodoc_create_folder(params: CreateFolderInput) -> str:
    """
    Create a new folder in OpenProdoc with custom attributes.

    Folders in OpenProdoc are containers that organize documents hierarchically.
    Each folder can have a specific type and custom attributes defined by the schema.

    IMPORTANT: If no parent_id or parent_path is specified, the folder will be created
    under "RootFolder" (the top-level folder) by default.

    ATTRIBUTE TYPES AND FORMATS:
        Allowed attribute types:
        - String: Text values
        - Integer: Whole numbers
        - Decimal: Decimal numbers
        - Boolean: True/False values
        - Date: Date values in format "yyyy-MM-dd" (e.g., "2025-01-15")
        - TimeStamp: Date and time in format "yyyy-MM-dd HH:mm:ss" (e.g., "2025-01-15 14:30:00")
        - Thesaur: Thesaurus term reference (use Term ID as value)

        ListAttr requirements:
        - Must include ALL metadata/attributes defined for the folder type
        - For PD_FOLDERS: No additional attributes required (can be empty list)
        - For custom folder types: Provide all required attributes per schema
        - Each attribute format: {"Name": "field_name", "Type": "field_type", "Values": ["value1", "value2"]}
        - For Thesaur fields: Values must contain the Term ID from thesaurus

    Args:
        params (CreateFolderInput): Folder creation parameters containing:
            - name (str): Folder name (e.g., "Project Documents", "2024 Reports")
            - folder_type (str): Folder type matching your schema (e.g., "PD_FOLDERS", "Course")
            - parent_id (Optional[str]): Parent folder ID for nested structure (defaults to "RootFolder" if not specified)
            - parent_path (Optional[str]): Alternative to parent_id, use folder path
            - acl (str): Access control list (default: "Public")
            - attributes (Optional[List[Dict]]): Custom attributes with Name, Type, Values
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted response with created folder ID

        Success response (markdown):
        "# Folder Created Successfully

        - **Folder ID**: 16cdeb939d9-3fc5285f4ed8aef0
        - **Name**: Project Documents
        - **Type**: PD_FOLDERS
        - **Parent ID**: 16ac20d9415-3fedb58bdb94afd4"

        Error response:
        "Error: Not Acceptable. Duplicate folder name in parent."

    Examples:
        - Create simple PD_FOLDERS folder:
          name="Projects 2024", folder_type="PD_FOLDERS"
          (No parent specified = RootFolder, no attributes needed)

        - Create nested folder:
          name="Q1 Reports", folder_type="PD_FOLDERS", parent_id="Projects2024FolderId"

        - Create folder with attributes:
          name="Course Material", folder_type="Course",
          attributes=[
            {"Name": "Teacher", "Type": "String", "Values": ["John Doe"]},
            {"Name": "StartDate", "Type": "Date", "Values": ["2025-01-15"]},
            {"Name": "Category", "Type": "Thesaur", "Values": ["term_id_12345"]}
          ]

        - Find parent IDs: Use openprodoc_search_folders with query:
          "Select * from PD_FOLDERS where PDId<>''"

        - Don't use when: You want to upload a document (use openprodoc_upload_document instead)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Not Acceptable" for duplicate names or validation errors (406)
        - Returns "Error: Permission denied" if user lacks folder creation rights (403)
        - Returns "Error: Internal server error" for incorrect attributes (500)
    """
    logger.info("TOOL CALLED: openprodoc_create_folder")
    logger.debug(f"Create folder - Name: {params.name}, Type: {params.folder_type}")

    try:
        # Build request body
        body: Dict[str, Any] = {
            "Id": "",
            "Name": params.name,
            "ACL": params.acl,
            "Type": params.folder_type,
            "ListAttr": params.attributes or []
        }

        if params.parent_id:
            body["Idparent"] = params.parent_id
            body["PathParent"] = ""
        elif params.parent_path:
            body["PathParent"] = params.parent_path
            body["Idparent"] = ""
        else:
            # Default to RootFolder if no parent specified
            body["Idparent"] = "RootFolder"
            body["PathParent"] = ""

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            "folders",
            method="POST",
            headers=headers,
            json_data=body
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            # Extract ID from message like "Creado=16cdeb939d9-3fc5285f4ed8aef0"
            folder_id = msg.split("=")[1] if "=" in msg else "Unknown"

            if params.response_format == ResponseFormat.MARKDOWN:
                lines = ["# Folder Created Successfully", ""]
                lines.append(f"- **Folder ID**: {folder_id}")
                lines.append(f"- **Name**: {params.name}")
                lines.append(f"- **Type**: {params.folder_type}")
                if params.parent_id:
                    lines.append(f"- **Parent ID**: {params.parent_id}")
                elif params.parent_path:
                    lines.append(f"- **Parent Path**: {params.parent_path}")
                return "\n".join(lines)
            else:
                return json.dumps({
                    "status": "success",
                    "folder_id": folder_id,
                    "name": params.name,
                    "type": params.folder_type
                }, indent=2)
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_get_folder",
    annotations={
        "title": "Get OpenProdoc Folder Metadata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_get_folder(params: GetFolderInput) -> str:
    """
    Retrieve metadata for a specific folder by ID or path.

    Returns complete folder information including custom attributes, creation date,
    author, and access control settings.

    Args:
        params (GetFolderInput): Folder retrieval parameters containing:
            - folder_id (Optional[str]): Folder ID (use either folder_id or folder_path)
            - folder_path (Optional[str]): Folder path like "/Project/Subproject/"
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted folder metadata

        Success response includes:
        - Folder ID, name, type
        - Access control list (ACL)
        - Parent folder ID
        - Creation date and author
        - All custom attributes with their values

        Error response:
        "Error: Resource not found. Please check the ID or path is correct."

    Examples:
        - Use when: Need to check folder properties before creating subfolders
        - Use when: Retrieving custom attribute values for a folder
        - Don't use when: You want to list contents (use openprodoc_list_subfolders instead)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if folder doesn't exist (404)
        - Requires either folder_id or folder_path to be provided
    """
    try:
        # Determine endpoint based on identifier
        if params.folder_id:
            endpoint = f"folders/ById/{params.folder_id}"
        elif params.folder_path:
            # Ensure path ends with /
            path = params.folder_path if params.folder_path.endswith('/') else f"{params.folder_path}/"
            endpoint = f"folders/ByPath{path}"
        else:
            return "Error: Either folder_id or folder_path must be provided"

        # Make API request
        headers = _get_auth_headers()
        data = await _make_api_request(endpoint, headers=headers)

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_folder_markdown(data)
        else:
            return json.dumps(data, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_update_folder",
    annotations={
        "title": "Update OpenProdoc Folder",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_update_folder(params: UpdateFolderInput) -> str:
    """
    Update an existing folder's metadata and custom attributes.

    Allows modification of folder name, access control, and custom attributes.
    Only provided fields will be updated; omitted fields remain unchanged.

    Args:
        params (UpdateFolderInput): Update parameters containing:
            - folder_id (Optional[str]): Folder ID (use either folder_id or folder_path)
            - folder_path (Optional[str]): Folder path
            - name (Optional[str]): New folder name
            - acl (Optional[str]): New access control list
            - attributes (Optional[List[Dict]]): Updated custom attributes
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Success message with updated folder ID or error message

        Success response (markdown):
        "# Folder Updated Successfully

        - **Folder ID**: 16cdecd4f0f-3fe5e0dbbe1ff838
        - **Updated Fields**: name, attributes"

        Error response:
        "Error: Permission denied. You don't have access to this resource."

    Examples:
        - Use when: Renaming a folder
        - Use when: Updating custom attribute values
        - Use when: Changing folder access permissions
        - Don't use when: Moving a folder to a different parent (recreate instead)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if folder doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks update rights (403)
        - At least one update field (name, acl, or attributes) must be provided
    """
    try:
        # Build request body with only provided fields
        body: Dict[str, Any] = {}
        updated_fields = []

        if params.name is not None:
            body["Name"] = params.name
            updated_fields.append("name")

        if params.acl is not None:
            body["ACL"] = params.acl
            updated_fields.append("acl")

        if params.attributes is not None:
            body["ListAttr"] = params.attributes
            updated_fields.append("attributes")

        if not body:
            return "Error: No fields to update. Provide at least one of: name, acl, or attributes."

        # Determine endpoint based on identifier
        if params.folder_id:
            endpoint = f"folders/ById/{params.folder_id}"
        elif params.folder_path:
            path = params.folder_path if params.folder_path.endswith('/') else f"{params.folder_path}/"
            endpoint = f"folders/ByPath{path}"
        else:
            return "Error: Either folder_id or folder_path must be provided"

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            endpoint,
            method="PUT",
            headers=headers,
            json_data=body
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            folder_id = msg.split("=")[1] if "=" in msg else "Unknown"

            if params.response_format == ResponseFormat.MARKDOWN:
                lines = ["# Folder Updated Successfully", ""]
                lines.append(f"- **Folder ID**: {folder_id}")
                lines.append(f"- **Updated Fields**: {', '.join(updated_fields)}")
                return "\n".join(lines)
            else:
                return json.dumps({
                    "status": "success",
                    "folder_id": folder_id,
                    "updated_fields": updated_fields
                }, indent=2)
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_delete_folder",
    annotations={
        "title": "Delete OpenProdoc Folder",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_delete_folder(params: DeleteFolderInput) -> str:
    """
    Delete a folder from OpenProdoc.

    WARNING: This operation is destructive. Deleting a folder may also delete
    its contents depending on server configuration. Ensure you have appropriate
    permissions and backups before deletion.

    Args:
        params (DeleteFolderInput): Deletion parameters containing:
            - folder_id (Optional[str]): Folder ID (use either folder_id or folder_path)
            - folder_path (Optional[str]): Folder path

    Returns:
        str: Success message with deleted folder ID or error message

        Success response:
        "Successfully deleted folder: 16cdeb939d9-3fc5285f4ed8aef0"

        Error response:
        "Error: Permission denied. User_without_permissions_over_folder"

    Examples:
        - Use when: Removing obsolete project folders
        - Use when: Cleaning up temporary folder structures
        - Don't use when: Folder contains important documents (backup first)
        - Don't use when: Unsure about folder contents (check first with openprodoc_get_folder)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if folder doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks delete rights (403/406)
        - May fail if folder contains documents or subfolders (check server policy)
    """
    try:
        # Determine endpoint based on identifier
        if params.folder_id:
            endpoint = f"folders/ById/{params.folder_id}"
            identifier = params.folder_id
        elif params.folder_path:
            path = params.folder_path if params.folder_path.endswith('/') else f"{params.folder_path}/"
            endpoint = f"folders/ByPath{path}"
            identifier = params.folder_path
        else:
            return "Error: Either folder_id or folder_path must be provided"

        # Make API request
        headers = _get_auth_headers()
        # Don't set Content-Type for DELETE requests without body

        data = await _make_api_request(
            endpoint,
            method="DELETE",
            headers=headers
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            folder_id = msg.split("=")[1] if "=" in msg else identifier
            return f"Successfully deleted folder: {folder_id}"
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_list_subfolders",
    annotations={
        "title": "List Subfolders in OpenProdoc Folder",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_list_subfolders(params: ListSubfoldersInput) -> str:
    """
    List all subfolders within a parent folder with pagination support.

    Returns a list of immediate child folders (not recursive) with their metadata
    and custom attributes. Useful for exploring folder hierarchy.

    Args:
        params (ListSubfoldersInput): Listing parameters containing:
            - folder_id (Optional[str]): Parent folder ID
            - folder_path (Optional[str]): Parent folder path
            - initial (int): Starting index for pagination (default: 0)
            - final (int): Ending index for pagination (default: 200)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted list of subfolders

        Success response includes for each subfolder:
        - Folder ID, name, type
        - Creation date and author
        - Number of custom attributes
        - Access control settings

        Empty response:
        "No folders found."

    Examples:
        - Use when: Exploring folder structure in a project
        - Use when: Finding all subfolders to process recursively
        - Use when: Building a folder tree visualization
        - Don't use when: You want documents (use openprodoc_list_documents_in_folder)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if parent folder doesn't exist (404)
        - Automatically truncates if result exceeds 25,000 characters
        - Use pagination (initial/final) for large result sets
    """
    try:
        # Determine endpoint based on identifier
        if params.folder_id:
            endpoint = f"folders/SubFoldersById/{params.folder_id}"
        elif params.folder_path:
            # For path-based, construct the path carefully
            path = params.folder_path
            endpoint = f"folders/SubFoldersByPath{path}"
        else:
            return "Error: Either folder_id or folder_path must be provided"

        # Make API request with pagination
        headers = _get_auth_headers()
        query_params = {
            "Initial": str(params.initial),
            "Final": str(params.final)
        }

        data = await _make_api_request(
            endpoint,
            headers=headers,
            params=query_params
        )

        # Data should be an array
        folders = data if isinstance(data, list) else []

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_folders_list_markdown(folders)
            return _check_truncation(result, folders, "folders")
        else:
            response = {
                "count": len(folders),
                "initial": params.initial,
                "final": params.final,
                "folders": folders
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_list_documents_in_folder",
    annotations={
        "title": "List Documents in OpenProdoc Folder",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_list_documents_in_folder(params: ListDocumentsInput) -> str:
    """
    List all documents contained in a specific folder with pagination support.

    Returns document metadata for all files directly contained in the folder
    (not recursive into subfolders).

    Args:
        params (ListDocumentsInput): Listing parameters containing:
            - folder_id (Optional[str]): Folder ID
            - folder_path (Optional[str]): Folder path
            - initial (int): Starting index for pagination (default: 0)
            - final (int): Ending index for pagination (default: 200)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted list of documents

        Success response includes for each document:
        - Document ID and title
        - Document type and version
        - Creation date and author
        - Number of custom attributes

        Empty response:
        "No documents found."

    Examples:
        - Use when: Listing all PDFs in a folder
        - Use when: Finding documents created in a specific project
        - Use when: Checking folder contents before deletion
        - Don't use when: You want subfolders (use openprodoc_list_subfolders)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if folder doesn't exist (404)
        - Automatically truncates if result exceeds 25,000 characters
        - Use pagination (initial/final) for large document sets
    """
    try:
        # Determine endpoint based on identifier
        if params.folder_id:
            endpoint = f"folders/ContDocsById/{params.folder_id}"
        elif params.folder_path:
            path = params.folder_path
            endpoint = f"folders/ContDocsByPath{path}"
        else:
            return "Error: Either folder_id or folder_path must be provided"

        # Make API request with pagination
        headers = _get_auth_headers()
        query_params = {
            "Initial": str(params.initial),
            "Final": str(params.final)
        }

        data = await _make_api_request(
            endpoint,
            headers=headers,
            params=query_params
        )

        # Data should be an array
        documents = data if isinstance(data, list) else []

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_documents_list_markdown(documents)
            return _check_truncation(result, documents, "documents")
        else:
            response = {
                "count": len(documents),
                "initial": params.initial,
                "final": params.final,
                "documents": documents
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_search_folders",
    annotations={
        "title": "Search OpenProdoc Folders",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_search_folders(params: SearchInput) -> str:
    """
    Search for folders using SQL-like query with custom criteria.

    Allows powerful searching across folder metadata and custom attributes using
    SQL SELECT syntax. Returns matching folders with full metadata.

    IMPORTANT: OpenProdoc REQUIRES a WHERE clause in all search queries. Queries without
    a WHERE clause will fail with "Empty_conditions" error. Always include at least a
    minimal WHERE clause like "where PDId<>''" to list all folders.

    BEST PRACTICES:
        1. Always use "Select *" to get complete folder data with all attributes
        2. Use "where PDId<>''" to retrieve all folders (most reliable pattern)
        3. LIKE operator is NOT supported - will cause casting errors
        4. For text searching, retrieve all folders and filter client-side
        5. Use JSON response format for easier programmatic parsing
        6. Use comparison operators (=, <>, >, <) for exact field matching

    Args:
        params (SearchInput): Search parameters containing:
            - query (str): SQL-like query with REQUIRED WHERE clause
              Examples: "Select * from PD_FOLDERS where PDId<>''"
                       "Select * from Course where Teacher='Ana María'"
            - initial (int): Starting index for results (default: 0)
            - final (int): Ending index for results (default: 100, max: 1000)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted search results

        Success response includes matching folders with:
        - All selected fields from query
        - Custom attributes if requested
        - Pagination information

        Empty response:
        "No folders found matching your query."

    Examples:
        - List all PD_FOLDERS (RECOMMENDED):
          query="Select * from PD_FOLDERS where PDId<>''"

        - Find specific folder type:
          query="Select * from Course where PDId<>''"

        - Search by attribute:
          query="Select * from Course where Teacher='Ana María'"

        - Find by date:
          query="Select * from PD_FOLDERS where PDDate>'2024-01-01'"

        - For text search (e.g., titles containing "2025"):
          Use "Select * from PD_FOLDERS where PDId<>''" then filter results client-side

        - Don't use when: You know the exact folder ID (use openprodoc_get_folder instead)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Not Acceptable" for invalid SQL syntax (406)
        - Returns "Empty_conditions" error if WHERE clause is missing (500)
        - LIKE operator causes "cannot be cast" error - use client-side filtering instead
        - Automatically truncates if result exceeds 25,000 characters
        - Query syntax must match OpenProdoc SQL dialect
    """
    try:
        # Build request body
        body = {
            "Query": params.query,
            "Initial": str(params.initial),
            "Final": str(params.final)
        }

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            "folders/Search",
            method="POST",
            headers=headers,
            json_data=body
        )

        # Data should be an array
        folders = data if isinstance(data, list) else []

        if not folders:
            return "No folders found matching your query."

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_folders_list_markdown(folders)
            return _check_truncation(result, folders, "folders")
        else:
            response = {
                "count": len(folders),
                "query": params.query,
                "initial": params.initial,
                "final": params.final,
                "folders": folders
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)


# ============================================================================
# DOCUMENT TOOLS
# ============================================================================

@mcp.tool(
    name="openprodoc_get_document_metadata",
    annotations={
        "title": "Get OpenProdoc Document Metadata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_get_document_metadata(params: GetDocumentInput) -> str:
    """
    Retrieve metadata for a specific document without downloading the file content.

    Returns complete document information including title, version, custom attributes,
    creation date, author, and parent folder location.

    Args:
        params (GetDocumentInput): Document retrieval parameters containing:
            - document_id (str): Document ID
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted document metadata

        Success response includes:
        - Document ID, title, type
        - Version label and document date
        - Parent folder ID
        - Access control list (ACL)
        - Creation date and author
        - All custom attributes with values

        Error response:
        "Error: Resource not found. Please check the ID is correct."

    Examples:
        - Use when: Checking document properties before download
        - Use when: Retrieving custom attribute values
        - Use when: Verifying document version information
        - Don't use when: You need the file content (use openprodoc_download_document)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if document doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks read access (403)
    """
    try:
        # Make API request
        headers = _get_auth_headers()
        data = await _make_api_request(
            f"documents/ById/{params.document_id}",
            headers=headers
        )

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_document_markdown(data)
        else:
            return json.dumps(data, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_download_document",
    annotations={
        "title": "Download OpenProdoc Document Content",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_download_document(params: DownloadDocumentInput) -> str:
    """
    Download the binary content of a document and save it to a local file.

    Retrieves the actual file content (PDF, DOCX, image, etc.) and saves it
    to the specified local path.

    Args:
        params (DownloadDocumentInput): Download parameters containing:
            - document_id (str): Document ID to download
            - output_path (str): Local file path where document will be saved
              (e.g., "C:\\Downloads\\report.pdf", "/tmp/document.docx")

    Returns:
        str: Success message with file path and size or error message

        Success response:
        "Successfully downloaded document to C:\\Downloads\\report.pdf (Size: 1.2 MB)"

        Error response:
        "Error: Resource not found. Document may have been deleted."
        "Error: Permission denied. You don't have access to this document."

    Examples:
        - Use when: Downloading a PDF report for review
        - Use when: Retrieving document files for batch processing
        - Use when: Backing up important documents locally
        - Don't use when: You only need metadata (use openprodoc_get_document_metadata)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if document doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks read access (403)
        - May fail if output path is invalid or not writable
    """
    try:
        # Make API request
        headers = _get_auth_headers()
        headers["Accept"] = "application/octet-stream"  # Override for binary download
        data = await _make_api_request(
            f"documents/ContentById/{params.document_id}",
            headers=headers
        )

        # Get binary content
        if "binary_content" in data:
            content = data["binary_content"]

            # Write to file
            with open(params.output_path, "wb") as f:
                f.write(content)

            # Get file size
            file_size = len(content)
            size_mb = file_size / (1024 * 1024)

            return f"Successfully downloaded document to {params.output_path} (Size: {size_mb:.2f} MB)"
        else:
            return "Error: No binary content received from server."

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_delete_document",
    annotations={
        "title": "Delete OpenProdoc Document",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_delete_document(params: DeleteDocumentInput) -> str:
    """
    Delete a document from OpenProdoc permanently.

    WARNING: This operation is destructive and irreversible. The document and its
    metadata will be permanently removed. Ensure you have backups before deletion.

    Args:
        params (DeleteDocumentInput): Deletion parameters containing:
            - document_id (str): Document ID to delete

    Returns:
        str: Success message with deleted document ID or error message

        Success response:
        "Successfully deleted document: 16c7fa8b123-3fe9663c99e730f2"

        Error response:
        "Error: Permission denied. You don't have delete rights for this document."

    Examples:
        - Use when: Removing obsolete or duplicate documents
        - Use when: Cleaning up test documents
        - Don't use when: Document might be needed (download backup first)
        - Don't use when: Unsure about document content (check metadata first)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if document doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks delete rights (403)
    """
    try:
        # Make API request
        headers = _get_auth_headers()

        data = await _make_api_request(
            f"documents/ById/{params.document_id}",
            method="DELETE",
            headers=headers
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            doc_id = msg.split("=")[1] if "=" in msg else params.document_id
            return f"Successfully deleted document: {doc_id}"
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_upload_document",
    annotations={
        "title": "Upload Document to OpenProdoc",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def openprodoc_upload_document(params: UploadDocumentInput) -> str:
    """
    Upload a new document to OpenProdoc with metadata and custom attributes.

    Uploads a file from the local filesystem to OpenProdoc, creating a new document
    with specified metadata, type, and custom attributes.

    Args:
        params (UploadDocumentInput): Upload parameters containing:
            - file_path (str): Local file path to upload (e.g., "C:\\Documents\\report.pdf")
            - title (str): Document title
            - document_type (str): Document type matching schema (e.g., "PD_DOCS", "ECM_Standards")
            - parent_folder_id (str): Parent folder ID where document will be stored
            - acl (str): Access control list (default: "Public")
            - version_label (str): Version label (default: "1.0")
            - doc_date (Optional[str]): Document date in YYYY-MM-DD format
            - attributes (Optional[List[Dict]]): Custom attributes with Name, Type, Values
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted response with created document ID

        Success response (markdown):
        "# Document Uploaded Successfully

        - **Document ID**: 16c7fa8b456-3fe9663c99e730f2
        - **Title**: Quarterly Report
        - **Type**: PD_DOCS
        - **Version**: 1.0
        - **Parent Folder**: 16ac20d9415-3fedb58bdb94afd4"

        Error response:
        "Error: Not Acceptable. Invalid file format or missing required attributes."

    Examples:
        - Use when: Adding new documents to a project folder
        - Use when: Importing scanned documents with metadata
        - Use when: Creating document records with custom attributes
        - Don't use when: Updating existing document (use openprodoc_update_document)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if parent folder doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks upload rights (403)
        - Returns "Error: Not Acceptable" for validation errors or missing attributes (406)
        - File must exist and be readable at specified path
    """
    try:
        # Read file content
        with open(params.file_path, "rb") as f:
            file_content = f.read()

        # Extract filename from path
        import os
        filename = os.path.basename(params.file_path)

        # Build metadata JSON
        metadata = {
            "Title": params.title,
            "ACL": params.acl,
            "Idparent": params.parent_folder_id,
            "Type": params.document_type,
            "VerLabel": params.version_label,
            "DocDate": params.doc_date,  # Always include DocDate (now has a default value)
            "ListAttr": params.attributes or []
        }

        # Prepare multipart form data
        files = {
            "Binary": (filename, file_content)
        }

        form_data = {
            "Metadata": json.dumps(metadata)
        }

        # Make API request
        headers = _get_auth_headers()
        # Don't set Content-Type - httpx will set it with boundary for multipart

        data = await _make_api_request(
            "documents",
            method="POST",
            headers=headers,
            files=files,
            data=form_data
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            doc_id = msg.split("=")[1] if "=" in msg else "Unknown"

            if params.response_format == ResponseFormat.MARKDOWN:
                lines = ["# Document Uploaded Successfully", ""]
                lines.append(f"- **Document ID**: {doc_id}")
                lines.append(f"- **Title**: {params.title}")
                lines.append(f"- **Type**: {params.document_type}")
                lines.append(f"- **Version**: {params.version_label}")
                lines.append(f"- **Parent Folder**: {params.parent_folder_id}")
                return "\n".join(lines)
            else:
                return json.dumps({
                    "status": "success",
                    "document_id": doc_id,
                    "title": params.title,
                    "type": params.document_type,
                    "version": params.version_label
                }, indent=2)
        else:
            error_msg = data.get('Msg', 'Unknown error')
            if not error_msg or error_msg.strip() == "":
                error_msg = "API returned an error without details. This may indicate missing required fields (e.g., DocDate) or invalid data."
            return f"Error: {error_msg}"

    except FileNotFoundError:
        return f"Error: File not found at path: {params.file_path}"
    except Exception as e:
        return _handle_api_error(e)


async def _get_document_metadata_raw(document_id: str) -> Optional[Dict[str, Any]]:
    """
    Internal helper to fetch raw document metadata.

    Args:
        document_id: Document ID to fetch

    Returns:
        Dictionary with document metadata or None if not found
    """
    try:
        headers = _get_auth_headers()
        data = await _make_api_request(
            f"documents/ById/{document_id}",
            headers=headers
        )
        return data
    except Exception:
        return None


@mcp.tool(
    name="openprodoc_update_document",
    annotations={
        "title": "Update OpenProdoc Document",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_update_document(params: UpdateDocumentInput) -> str:
    """
    Update an existing document's metadata and optionally replace its file content.

    Allows modification of document metadata, custom attributes, and binary content.
    Only provided fields will be updated; omitted fields remain unchanged.

    IMPORTANT: When uploading a new file version, you MUST include the document_type
    parameter, otherwise OpenProdoc will fail with a NullPointerException.

    Args:
        params (UpdateDocumentInput): Update parameters containing:
            - document_id (str): Document ID to update (REQUIRED)
            - file_path (Optional[str]): New file to upload for versioning
            - title (Optional[str]): New document title
            - document_type (Optional[str]): Document type (e.g., 'PD_DOCS', 'ECM_Standards')
              **REQUIRED when uploading a new file version**
            - parent_folder_id (Optional[str]): Parent folder ID
            - acl (Optional[str]): Access control list (e.g., 'Public')
            - version_label (Optional[str]): Version label (e.g., '1.0', '2.0')
            - doc_date (Optional[str]): Document date in YYYY-MM-DD format
            - author (Optional[str]): Document author username
            - pd_date (Optional[str]): PDDate timestamp in 'YYYY-MM-DD HH:MM:SS' format
            - attributes (Optional[List[Dict]]): Custom attributes with Name, Type, Values
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Success message with updated document ID or error message

        Success response (markdown):
        "# Document Updated Successfully

        - **Document ID**: 16c7fa8b456-3fe9663c99e730f2
        - **Updated Fields**: title, document_type, version_label, binary"

        Error response:
        "Error: Permission denied. You don't have update rights for this document."

    Examples:
        - Metadata only update:
          document_id="123", title="Updated Title", version_label="1.1"

        - Upload new file version (versioning):
          document_id="123", file_path="/path/to/file.pdf",
          document_type="PD_DOCS", version_label="2.0"

        - Update multiple fields:
          document_id="123", title="New Title", acl="Private",
          doc_date="2025-01-15", author="john_doe"

        - Don't use when: Creating a new document (use openprodoc_upload_document)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if document doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks update rights (403)
        - Returns API error 500 if document_type is missing when updating with file
        - At least one update field must be provided
        - If file_path provided, file must exist and be readable
    """
    try:
        updated_fields = []

        # STEP 1: Fetch existing document metadata
        existing_doc = await _get_document_metadata_raw(params.document_id)
        if not existing_doc:
            return "Error: Could not retrieve existing document metadata. Document may not exist."

        # STEP 2: Build complete metadata starting with existing values
        metadata: Dict[str, Any] = {
            "Title": existing_doc.get("Title", ""),
            "ACL": existing_doc.get("ACL", "Public"),
            "Idparent": existing_doc.get("ParentId", ""),
            "Type": existing_doc.get("Type", ""),
            "VerLabel": existing_doc.get("VerLabel", "1.0"),
            "DocDate": existing_doc.get("DocDate", ""),
            "PDDate": existing_doc.get("PDDate", ""),
            "PDAuthor": existing_doc.get("PDAuthor", ""),
            "ListAttr": existing_doc.get("ListAttr", [])
        }

        # STEP 3: Override with new values if provided
        if params.title is not None:
            metadata["Title"] = params.title
            updated_fields.append("title")

        if params.document_type is not None:
            metadata["Type"] = params.document_type
            updated_fields.append("document_type")

        if params.parent_folder_id is not None:
            metadata["Idparent"] = params.parent_folder_id
            updated_fields.append("parent_folder_id")

        if params.acl is not None:
            metadata["ACL"] = params.acl
            updated_fields.append("acl")

        if params.version_label is not None:
            metadata["VerLabel"] = params.version_label
            updated_fields.append("version_label")

        if params.doc_date is not None:
            metadata["DocDate"] = params.doc_date
            updated_fields.append("doc_date")

        if params.author is not None:
            metadata["PDAuthor"] = params.author
            updated_fields.append("author")

        if params.pd_date is not None:
            metadata["PDDate"] = params.pd_date
            updated_fields.append("pd_date")

        if params.attributes is not None:
            metadata["ListAttr"] = params.attributes
            updated_fields.append("attributes")

        if not updated_fields and not params.file_path:
            return "Error: No fields to update. Provide at least one of: file_path, title, document_type, parent_folder_id, acl, version_label, doc_date, author, pd_date, or attributes."

        # Prepare request
        headers = _get_auth_headers()

        if params.file_path:
            # Multipart upload with file
            updated_fields.append("binary")

            with open(params.file_path, "rb") as f:
                file_content = f.read()

            import os
            filename = os.path.basename(params.file_path)

            files = {
                "Binary": (filename, file_content)
            }

            form_data = {
                "Metadata": json.dumps(metadata)
            }

            data = await _make_api_request(
                f"documents/ById/{params.document_id}",
                method="PUT",
                headers=headers,
                files=files,
                data=form_data
            )
        else:
            # Metadata only update
            headers["Content-Type"] = "application/json"

            form_data_dict = {
                "Metadata": json.dumps(metadata)
            }

            data = await _make_api_request(
                f"documents/ById/{params.document_id}",
                method="PUT",
                headers=headers,
                data=form_data_dict
            )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            doc_id = msg.split("=")[1] if "=" in msg else params.document_id

            if params.response_format == ResponseFormat.MARKDOWN:
                lines = ["# Document Updated Successfully", ""]
                lines.append(f"- **Document ID**: {doc_id}")
                lines.append(f"- **Updated Fields**: {', '.join(updated_fields)}")
                return "\n".join(lines)
            else:
                return json.dumps({
                    "status": "success",
                    "document_id": doc_id,
                    "updated_fields": updated_fields
                }, indent=2)
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except FileNotFoundError:
        return f"Error: File not found at path: {params.file_path}"
    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_search_documents",
    annotations={
        "title": "Search OpenProdoc Documents",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_search_documents(params: SearchInput) -> str:
    """
    Search for documents using SQL-like query with custom criteria.

    Allows powerful searching across document metadata and custom attributes using
    SQL SELECT syntax. Returns matching documents with full metadata.

    IMPORTANT: OpenProdoc REQUIRES a WHERE clause in all search queries. Queries without
    a WHERE clause will fail with "Empty_conditions" error. Always include at least a
    minimal WHERE clause like "where PDId<>''" to list all documents.

    BEST PRACTICES:
        1. Always use "Select *" to get complete document data with all attributes
        2. Use "where PDId<>''" to retrieve all documents (most reliable pattern)
        3. LIKE operator is NOT supported - will cause casting errors
        4. For text searching, retrieve all documents and filter client-side
        5. Use JSON response format for easier programmatic parsing
        6. Use comparison operators (=, <>, >, <) for exact field matching

    Args:
        params (SearchInput): Search parameters containing:
            - query (str): SQL-like query with REQUIRED WHERE clause
              Examples: "Select * from PD_DOCS where PDId<>''"
                       "Select * from PD_DOCS where PDAuthor='root'"
            - initial (int): Starting index for results (default: 0)
            - final (int): Ending index for results (default: 100, max: 1000)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted search results

        Success response includes matching documents with:
        - All selected fields from query
        - Custom attributes if requested
        - Pagination information

        Empty response:
        "No documents found matching your query."

    Examples:
        - List all documents (RECOMMENDED):
          query="Select * from PD_DOCS where PDId<>''"

        - Find by author:
          query="Select * from PD_DOCS where PDAuthor='root'"

        - Find by date range:
          query="Select * from PD_DOCS where DocDate>'2024-01-01'"

        - Find by exact title:
          query="Select * from PD_DOCS where Title='Remote Work Policy 2025'"

        - For text search (e.g., titles containing "2025"):
          Use "Select * from PD_DOCS where PDId<>''" then filter results client-side

        - Don't use when: You know the exact document ID (use openprodoc_get_document_metadata)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Not Acceptable" for invalid SQL syntax (406)
        - Returns "Empty_conditions" error if WHERE clause is missing (500)
        - LIKE operator causes "cannot be cast" error - use client-side filtering instead
        - Automatically truncates if result exceeds 25,000 characters
        - Query syntax must match OpenProdoc SQL dialect
    """
    try:
        # Build request body
        body = {
            "Query": params.query,
            "Initial": str(params.initial),
            "Final": str(params.final)
        }

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            "documents/Search",
            method="POST",
            headers=headers,
            json_data=body
        )

        # Data should be an array
        documents = data if isinstance(data, list) else []

        if not documents:
            return "No documents found matching your query."

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_documents_list_markdown(documents)
            return _check_truncation(result, documents, "documents")
        else:
            response = {
                "count": len(documents),
                "query": params.query,
                "initial": params.initial,
                "final": params.final,
                "documents": documents
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)


# ============================================================================
# THESAURUS TOOLS
# ============================================================================

@mcp.tool(
    name="openprodoc_create_term",
    annotations={
        "title": "Create OpenProdoc Thesaurus Term",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def openprodoc_create_term(params: CreateTermInput) -> str:
    """
    Create a new thesaurus term in OpenProdoc.

    Thesaurus terms are used for controlled vocabulary and hierarchical taxonomy
    management in OpenProdoc. Terms can be organized in parent-child relationships.

    Args:
        params (CreateTermInput): Term creation parameters containing:
            - name (str): Term name (e.g., "Business Units", "Marketing")
            - description (str): Term description
            - language (str): Language code (default: "EN", e.g., "ES", "FR")
            - scope_note (Optional[str]): Scope note explaining term usage
            - parent_id (Optional[str]): Parent term ID for hierarchical structure
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted response with created term ID

        Success response (markdown):
        "# Thesaurus Term Created Successfully

        - **Term ID**: 88888
        - **Name**: Business Units
        - **Language**: EN
        - **Parent ID**: 77777"

        Error response:
        "Error: Not Acceptable. Duplicate term name or validation error."

    Examples:
        - Use when: Building controlled vocabulary for document classification
        - Use when: Creating hierarchical taxonomies for organization
        - Use when: Adding new terms to existing thesaurus structure
        - Don't use when: You want to create a folder (use openprodoc_create_folder)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Not Acceptable" for duplicate names or validation errors (406)
        - Returns "Error: Permission denied" if user lacks term creation rights (403)
    """
    try:
        # Build request body
        body = {
            "Name": params.name,
            "Descrip": params.description,
            "Lang": params.language
        }

        if params.scope_note:
            body["SCN"] = params.scope_note

        if params.parent_id:
            body["ParentId"] = params.parent_id

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            "thesauri",
            method="POST",
            headers=headers,
            json_data=body
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            term_id = msg.split("=")[1] if "=" in msg else "Unknown"

            if params.response_format == ResponseFormat.MARKDOWN:
                lines = ["# Thesaurus Term Created Successfully", ""]
                lines.append(f"- **Term ID**: {term_id}")
                lines.append(f"- **Name**: {params.name}")
                lines.append(f"- **Language**: {params.language}")
                if params.parent_id:
                    lines.append(f"- **Parent ID**: {params.parent_id}")
                return "\n".join(lines)
            else:
                return json.dumps({
                    "status": "success",
                    "term_id": term_id,
                    "name": params.name,
                    "language": params.language
                }, indent=2)
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_get_term",
    annotations={
        "title": "Get OpenProdoc Thesaurus Term Metadata",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_get_term(params: GetTermInput) -> str:
    """
    Retrieve metadata for a specific thesaurus term.

    Returns complete term information including name, description, language,
    scope note, and parent term relationship.

    Args:
        params (GetTermInput): Term retrieval parameters containing:
            - term_id (str): Term ID
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted term metadata

        Success response includes:
        - Term ID, name, description
        - Language code
        - Scope note
        - Parent term ID

        Error response:
        "Error: Resource not found. Please check the term ID is correct."

    Examples:
        - Use when: Checking term properties before creating subterms
        - Use when: Retrieving term hierarchy information
        - Don't use when: You want to list all subterms (use openprodoc_list_subterms)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if term doesn't exist (404)
    """
    try:
        # Make API request
        headers = _get_auth_headers()
        data = await _make_api_request(
            f"thesauri/ById/{params.term_id}",
            headers=headers
        )

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            return _format_term_markdown(data)
        else:
            return json.dumps(data, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_update_term",
    annotations={
        "title": "Update OpenProdoc Thesaurus Term",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_update_term(params: UpdateTermInput) -> str:
    """
    Update an existing thesaurus term's metadata.

    Allows modification of term name, description, language, and scope note.
    Only provided fields will be updated; omitted fields remain unchanged.

    Args:
        params (UpdateTermInput): Update parameters containing:
            - term_id (str): Term ID to update
            - name (Optional[str]): New term name
            - description (Optional[str]): New term description
            - language (Optional[str]): New language code
            - scope_note (Optional[str]): New scope note
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Success message with updated term ID or error message

        Success response (markdown):
        "# Thesaurus Term Updated Successfully

        - **Term ID**: 88888
        - **Updated Fields**: name, description"

        Error response:
        "Error: Permission denied. You don't have update rights for this term."

    Examples:
        - Use when: Correcting term names or descriptions
        - Use when: Updating scope notes for clarity
        - Use when: Changing term language designation
        - Don't use when: Moving term to different parent (recreation may be needed)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if term doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks update rights (403)
        - At least one update field must be provided
    """
    try:
        # Build request body with only provided fields
        body: Dict[str, Any] = {}
        updated_fields = []

        if params.name is not None:
            body["Name"] = params.name
            updated_fields.append("name")

        if params.description is not None:
            body["Descrip"] = params.description
            updated_fields.append("description")

        if params.language is not None:
            body["Lang"] = params.language
            updated_fields.append("language")

        if params.scope_note is not None:
            body["SCN"] = params.scope_note
            updated_fields.append("scope_note")

        if not body:
            return "Error: No fields to update. Provide at least one of: name, description, language, or scope_note."

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            f"thesauri/ById/{params.term_id}",
            method="PUT",
            headers=headers,
            json_data=body
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            term_id = msg.split("=")[1] if "=" in msg else params.term_id

            if params.response_format == ResponseFormat.MARKDOWN:
                lines = ["# Thesaurus Term Updated Successfully", ""]
                lines.append(f"- **Term ID**: {term_id}")
                lines.append(f"- **Updated Fields**: {', '.join(updated_fields)}")
                return "\n".join(lines)
            else:
                return json.dumps({
                    "status": "success",
                    "term_id": term_id,
                    "updated_fields": updated_fields
                }, indent=2)
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_delete_term",
    annotations={
        "title": "Delete OpenProdoc Thesaurus Term",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_delete_term(params: DeleteTermInput) -> str:
    """
    Delete a thesaurus term from OpenProdoc.

    WARNING: This operation is destructive. Deleting a term may affect documents
    or folders that reference it. Ensure you understand the impact before deletion.

    Args:
        params (DeleteTermInput): Deletion parameters containing:
            - term_id (str): Term ID to delete

    Returns:
        str: Success message with deleted term ID or error message

        Success response:
        "Successfully deleted thesaurus term: 88888"

        Error response:
        "Error: Permission denied. You don't have delete rights for this term."

    Examples:
        - Use when: Removing obsolete thesaurus terms
        - Use when: Cleaning up test taxonomy structures
        - Don't use when: Term has subterms (delete children first or check server policy)
        - Don't use when: Term is actively used in document classification

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if term doesn't exist (404)
        - Returns "Error: Permission denied" if user lacks delete rights (403)
        - May fail if term has subterms or is referenced by documents
    """
    try:
        # Make API request
        headers = _get_auth_headers()
        # Don't set Content-Type for DELETE requests without body

        data = await _make_api_request(
            f"thesauri/ById/{params.term_id}",
            method="DELETE",
            headers=headers
        )

        # Parse response
        if data.get("Res") == "OK":
            msg = data.get("Msg", "")
            term_id = msg.split("=")[1] if "=" in msg else params.term_id
            return f"Successfully deleted thesaurus term: {term_id}"
        else:
            return f"Error: {data.get('Msg', 'Unknown error')}"

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_list_subterms",
    annotations={
        "title": "List Subterms in OpenProdoc Thesaurus",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_list_subterms(params: ListSubtermsInput) -> str:
    """
    List all subterms under a parent thesaurus term with pagination support.

    Returns a list of immediate child terms (not recursive) under the specified
    parent term. Useful for exploring thesaurus hierarchy.

    Args:
        params (ListSubtermsInput): Listing parameters containing:
            - parent_term_id (str): Parent term ID
            - initial (int): Starting index for pagination (default: 0)
            - final (int): Ending index for pagination (default: 200)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted list of subterms

        Success response includes for each subterm:
        - Term ID, name, description
        - Language code
        - Scope note (if present)

        Empty response:
        "No terms found."

    Examples:
        - Use when: Exploring thesaurus hierarchy
        - Use when: Building taxonomy tree visualizations
        - Use when: Finding all child terms for bulk operations
        - Don't use when: You need term metadata (use openprodoc_get_term)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Resource not found" if parent term doesn't exist (404)
        - Automatically truncates if result exceeds 25,000 characters
        - Use pagination (initial/final) for large result sets
    """
    try:
        # Make API request with pagination
        headers = _get_auth_headers()
        query_params = {
            "Initial": str(params.initial),
            "Final": str(params.final)
        }

        data = await _make_api_request(
            f"thesauri/SubThesById/{params.parent_term_id}",
            headers=headers,
            params=query_params
        )

        # Data should be an array
        terms = data if isinstance(data, list) else []

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_terms_list_markdown(terms)
            return _check_truncation(result, terms, "terms")
        else:
            response = {
                "count": len(terms),
                "parent_term_id": params.parent_term_id,
                "initial": params.initial,
                "final": params.final,
                "terms": terms
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)


@mcp.tool(
    name="openprodoc_search_terms",
    annotations={
        "title": "Search OpenProdoc Thesaurus Terms",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def openprodoc_search_terms(params: SearchInput) -> str:
    """
    Search for thesaurus terms using SQL-like query.

    Allows powerful searching across term metadata using SQL SELECT syntax.
    Returns matching terms with full metadata.

    IMPORTANT: OpenProdoc REQUIRES a WHERE clause in all search queries. Queries without
    a WHERE clause will fail with "Empty_conditions" error. Always include at least a
    minimal WHERE clause to list all terms.

    NOTE: The table name for thesaurus queries is "this" (not a standard table name).

    BEST PRACTICES:
        1. Always use "Select *" to get complete term data with all attributes
        2. Use "where Name<>''" to retrieve all terms (most reliable pattern)
        3. LIKE operator is NOT supported - will cause casting errors
        4. For text searching, retrieve all terms and filter client-side
        5. Use JSON response format for easier programmatic parsing
        6. Use comparison operators (=, <>, >, <) for exact field matching

    Args:
        params (SearchInput): Search parameters containing:
            - query (str): SQL-like query with REQUIRED WHERE clause
              Examples: "Select * from this where ParentId='77777'"
                       "Select * from this where Lang='ES'"
            - initial (int): Starting index for results (default: 0)
            - final (int): Ending index for results (default: 100, max: 1000)
            - response_format (ResponseFormat): Output format ('markdown' or 'json')

    Returns:
        str: Markdown or JSON formatted search results

        Success response includes matching terms with:
        - All selected fields from query
        - Pagination information

        Empty response:
        "No terms found matching your query."

    Examples:
        - List all terms (RECOMMENDED):
          query="Select * from this where Name<>''"

        - Find terms by parent:
          query="Select * from this where ParentId='123'"

        - Find by language:
          query="Select * from this where Lang='ES'"

        - Find by exact name:
          query="Select * from this where Name='Business Units'"

        - For text search (e.g., names containing "Business"):
          Use "Select * from this where Name<>''" then filter results client-side

        - Don't use when: You know the exact term ID (use openprodoc_get_term)

    Error Handling:
        - Returns "Error: Not authenticated" if not logged in (401)
        - Returns "Error: Not Acceptable" for invalid SQL syntax (406)
        - Returns "Empty_conditions" error if WHERE clause is missing (500)
        - LIKE operator causes "cannot be cast" error - use client-side filtering instead
        - Automatically truncates if result exceeds 25,000 characters
        - Query syntax must match OpenProdoc SQL dialect
        - Remember: Table name for thesaurus is "this" in queries
    """
    try:
        # Build request body
        body = {
            "Query": params.query,
            "Initial": str(params.initial),
            "Final": str(params.final)
        }

        # Make API request
        headers = _get_auth_headers()
        headers["Content-Type"] = "application/json"

        data = await _make_api_request(
            "thesauri/Search",
            method="POST",
            headers=headers,
            json_data=body
        )

        # Data should be an array
        terms = data if isinstance(data, list) else []

        if not terms:
            return "No terms found matching your query."

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            result = _format_terms_list_markdown(terms)
            return _check_truncation(result, terms, "terms")
        else:
            response = {
                "count": len(terms),
                "query": params.query,
                "initial": params.initial,
                "final": params.final,
                "terms": terms
            }
            return json.dumps(response, indent=2)

    except Exception as e:
        return _handle_api_error(e)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("Starting MCP server - Entering mcp.run()")
    logger.info("Server ready to accept client connections")
    logger.info("=" * 80)
    try:
        mcp.run()
    except Exception as e:
        logger.critical(f"FATAL ERROR - Server crashed: {type(e).__name__}: {str(e)}")
        logger.exception("Full traceback:")
        raise
