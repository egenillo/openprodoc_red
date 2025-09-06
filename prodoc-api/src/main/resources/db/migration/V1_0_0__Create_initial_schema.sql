-- OpenProdoc Red - Initial Database Schema
-- Version: 1.0.0
-- Description: Create core OpenProdoc tables optimized for PostgreSQL

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS opd_core;
CREATE SCHEMA IF NOT EXISTS opd_docs;
CREATE SCHEMA IF NOT EXISTS opd_admin;

-- Set search path
SET search_path = opd_core, opd_docs, opd_admin, public;

-- =========================================================================
-- CORE SYSTEM TABLES
-- =========================================================================

-- System configuration table
CREATE TABLE IF NOT EXISTS opd_core.pd_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT,
    description VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Users table with PostgreSQL optimizations
CREATE TABLE IF NOT EXISTS opd_core.pd_users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_name VARCHAR(50) UNIQUE NOT NULL,
    user_password VARCHAR(255), -- Encrypted
    full_name VARCHAR(200),
    email VARCHAR(150),
    active BOOLEAN DEFAULT true,
    language VARCHAR(10) DEFAULT 'EN',
    auth_type VARCHAR(20) DEFAULT 'OPD', -- OPD, LDAP, OS, etc.
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Create indexes for users
CREATE INDEX idx_pd_users_name ON opd_core.pd_users(user_name);
CREATE INDEX idx_pd_users_email ON opd_core.pd_users(email);
CREATE INDEX idx_pd_users_active ON opd_core.pd_users(active);

-- Groups/Roles table
CREATE TABLE IF NOT EXISTS opd_core.pd_groups (
    group_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(500),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- User-Group relationships
CREATE TABLE IF NOT EXISTS opd_core.pd_user_groups (
    user_id UUID REFERENCES opd_core.pd_users(user_id) ON DELETE CASCADE,
    group_id UUID REFERENCES opd_core.pd_groups(group_id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assigned_by VARCHAR(50),
    PRIMARY KEY (user_id, group_id)
);

-- =========================================================================
-- DOCUMENT MANAGEMENT TABLES
-- =========================================================================

-- Document types/definitions
CREATE TABLE IF NOT EXISTS opd_docs.pd_doc_types (
    type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(500),
    parent_type UUID REFERENCES opd_docs.pd_doc_types(type_id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- Folder types/definitions
CREATE TABLE IF NOT EXISTS opd_docs.pd_folder_types (
    type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(500),
    parent_type UUID REFERENCES opd_docs.pd_folder_types(type_id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- Folders table with hierarchical support
CREATE TABLE IF NOT EXISTS opd_docs.pd_folders (
    folder_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    folder_name VARCHAR(200) NOT NULL,
    folder_path TEXT NOT NULL, -- Materialized path for hierarchy
    parent_folder UUID REFERENCES opd_docs.pd_folders(folder_id),
    folder_type UUID REFERENCES opd_docs.pd_folder_types(type_id),
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Indexes for folder hierarchy and search
CREATE INDEX idx_pd_folders_path ON opd_docs.pd_folders USING GIN(folder_path gin_trgm_ops);
CREATE INDEX idx_pd_folders_parent ON opd_docs.pd_folders(parent_folder);
CREATE INDEX idx_pd_folders_name ON opd_docs.pd_folders(folder_name);
CREATE INDEX idx_pd_folders_type ON opd_docs.pd_folders(folder_type);

-- Documents table with PostgreSQL JSON support
CREATE TABLE IF NOT EXISTS opd_docs.pd_documents (
    doc_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    doc_name VARCHAR(200) NOT NULL,
    doc_title VARCHAR(500),
    doc_type UUID REFERENCES opd_docs.pd_doc_types(type_id),
    folder_id UUID REFERENCES opd_docs.pd_folders(folder_id),
    file_name VARCHAR(255),
    file_size BIGINT,
    mime_type VARCHAR(100),
    file_hash VARCHAR(64), -- SHA-256 hash
    storage_path TEXT,
    storage_type VARCHAR(20) DEFAULT 'FILESYSTEM', -- FILESYSTEM, S3, BLOB, etc.
    version_number INTEGER DEFAULT 1,
    is_current_version BOOLEAN DEFAULT true,
    checkout_user VARCHAR(50),
    checkout_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB, -- PostgreSQL JSON for flexible metadata
    full_text TEXT, -- Extracted text for search
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50),
    updated_by VARCHAR(50)
);

-- Indexes for documents with PostgreSQL optimizations
CREATE INDEX idx_pd_docs_name ON opd_docs.pd_documents(doc_name);
CREATE INDEX idx_pd_docs_folder ON opd_docs.pd_documents(folder_id);
CREATE INDEX idx_pd_docs_type ON opd_docs.pd_documents(doc_type);
CREATE INDEX idx_pd_docs_created ON opd_docs.pd_documents(created_at);
CREATE INDEX idx_pd_docs_metadata ON opd_docs.pd_documents USING GIN(metadata);
CREATE INDEX idx_pd_docs_fulltext ON opd_docs.pd_documents USING GIN(to_tsvector('english', full_text));
CREATE INDEX idx_pd_docs_hash ON opd_docs.pd_documents(file_hash);
CREATE INDEX idx_pd_docs_current ON opd_docs.pd_documents(is_current_version) WHERE is_current_version = true;

-- =========================================================================
-- ATTRIBUTE AND METADATA TABLES
-- =========================================================================

-- Attribute definitions
CREATE TABLE IF NOT EXISTS opd_core.pd_attributes (
    attr_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    attr_name VARCHAR(50) UNIQUE NOT NULL,
    attr_type VARCHAR(20) NOT NULL, -- STRING, INTEGER, DATE, BOOLEAN, etc.
    max_length INTEGER,
    required BOOLEAN DEFAULT false,
    multiple_values BOOLEAN DEFAULT false,
    default_value TEXT,
    validation_rule TEXT,
    description VARCHAR(500),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(50)
);

-- Document type attributes (which attributes apply to which document types)
CREATE TABLE IF NOT EXISTS opd_docs.pd_doc_type_attributes (
    type_id UUID REFERENCES opd_docs.pd_doc_types(type_id) ON DELETE CASCADE,
    attr_id UUID REFERENCES opd_core.pd_attributes(attr_id) ON DELETE CASCADE,
    required BOOLEAN DEFAULT false,
    display_order INTEGER,
    PRIMARY KEY (type_id, attr_id)
);

-- Document attribute values
CREATE TABLE IF NOT EXISTS opd_docs.pd_document_attributes (
    doc_id UUID REFERENCES opd_docs.pd_documents(doc_id) ON DELETE CASCADE,
    attr_id UUID REFERENCES opd_core.pd_attributes(attr_id) ON DELETE CASCADE,
    attr_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doc_id, attr_id)
);

-- Index for document attributes
CREATE INDEX idx_pd_doc_attrs_value ON opd_docs.pd_document_attributes(attr_value);

-- =========================================================================
-- ACCESS CONTROL AND PERMISSIONS
-- =========================================================================

-- ACL (Access Control List) table
CREATE TABLE IF NOT EXISTS opd_admin.pd_acl (
    acl_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(20) NOT NULL, -- DOCUMENT, FOLDER, etc.
    resource_id UUID NOT NULL,
    principal_type VARCHAR(10) NOT NULL, -- USER, GROUP
    principal_id UUID NOT NULL,
    permissions INTEGER NOT NULL, -- Bitmask for permissions
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by VARCHAR(50)
);

-- Indexes for ACL
CREATE INDEX idx_pd_acl_resource ON opd_admin.pd_acl(resource_type, resource_id);
CREATE INDEX idx_pd_acl_principal ON opd_admin.pd_acl(principal_type, principal_id);

-- =========================================================================
-- AUDIT AND LOGGING TABLES
-- =========================================================================

-- Audit log table
CREATE TABLE IF NOT EXISTS opd_admin.pd_audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type VARCHAR(20) NOT NULL, -- CREATE, UPDATE, DELETE, VIEW, etc.
    resource_type VARCHAR(20) NOT NULL,
    resource_id UUID,
    user_name VARCHAR(50),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for audit log
CREATE INDEX idx_pd_audit_date ON opd_admin.pd_audit_log(created_at);
CREATE INDEX idx_pd_audit_user ON opd_admin.pd_audit_log(user_name);
CREATE INDEX idx_pd_audit_resource ON opd_admin.pd_audit_log(resource_type, resource_id);

-- =========================================================================
-- SESSION MANAGEMENT
-- =========================================================================

-- Session table for web sessions
CREATE TABLE IF NOT EXISTS opd_core.pd_sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_access TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT,
    active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Index for session cleanup
CREATE INDEX idx_pd_sessions_expires ON opd_core.pd_sessions(expires_at);
CREATE INDEX idx_pd_sessions_user ON opd_core.pd_sessions(user_name);

-- =========================================================================
-- FULL-TEXT SEARCH CONFIGURATION
-- =========================================================================

-- Configure PostgreSQL full-text search
CREATE TEXT SEARCH CONFIGURATION opd_english (COPY = english);
CREATE TEXT SEARCH CONFIGURATION opd_spanish (COPY = spanish);

-- =========================================================================
-- TRIGGERS AND FUNCTIONS
-- =========================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_pd_users_updated_at BEFORE UPDATE ON opd_core.pd_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pd_groups_updated_at BEFORE UPDATE ON opd_core.pd_groups FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pd_documents_updated_at BEFORE UPDATE ON opd_docs.pd_documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_pd_folders_updated_at BEFORE UPDATE ON opd_docs.pd_folders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to maintain folder path
CREATE OR REPLACE FUNCTION update_folder_path()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.parent_folder IS NULL THEN
        NEW.folder_path = '/' || NEW.folder_name;
    ELSE
        SELECT folder_path || '/' || NEW.folder_name INTO NEW.folder_path
        FROM opd_docs.pd_folders
        WHERE folder_id = NEW.parent_folder;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply folder path trigger
CREATE TRIGGER update_pd_folder_path BEFORE INSERT OR UPDATE ON opd_docs.pd_folders FOR EACH ROW EXECUTE FUNCTION update_folder_path();

-- =========================================================================
-- INITIAL DATA
-- =========================================================================

-- Insert default configuration
INSERT INTO opd_core.pd_config (config_key, config_value, description) VALUES
('system.version', '3.0.0', 'OpenProdoc Red version'),
('system.name', 'OpenProdoc Red', 'System name'),
('database.version', '1.0.0', 'Database schema version'),
('session.timeout', '1800', 'Session timeout in seconds'),
('max.upload.size', '104857600', 'Maximum upload size in bytes (100MB)'),
('default.language', 'EN', 'Default system language')
ON CONFLICT (config_key) DO NOTHING;

-- Insert default admin user
INSERT INTO opd_core.pd_users (user_name, full_name, email, created_by) VALUES
('admin', 'System Administrator', 'admin@openprodoc.local', 'SYSTEM')
ON CONFLICT (user_name) DO NOTHING;

-- Insert default groups
INSERT INTO opd_core.pd_groups (group_name, description, created_by) VALUES
('Administrators', 'System administrators with full access', 'SYSTEM'),
('Users', 'Standard users with document access', 'SYSTEM'),
('Guests', 'Guest users with read-only access', 'SYSTEM')
ON CONFLICT (group_name) DO NOTHING;

-- Create root folder
INSERT INTO opd_docs.pd_folders (folder_name, folder_path, created_by) VALUES
('Root', '/', 'SYSTEM')
ON CONFLICT DO NOTHING;

COMMIT;