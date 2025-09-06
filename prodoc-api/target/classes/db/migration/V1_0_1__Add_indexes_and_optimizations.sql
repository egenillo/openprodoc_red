-- OpenProdoc Red - Database Optimizations
-- Version: 1.0.1
-- Description: Add additional indexes and PostgreSQL-specific optimizations

-- =========================================================================
-- PERFORMANCE INDEXES
-- =========================================================================

-- Composite indexes for common queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_folder_created 
ON opd_docs.pd_documents(folder_id, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_type_created 
ON opd_docs.pd_documents(doc_type, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_user_created 
ON opd_docs.pd_documents(created_by, created_at DESC);

-- Index for version queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_version_current
ON opd_docs.pd_documents(doc_id, version_number DESC) 
WHERE is_current_version = true;

-- Partial indexes for active records only
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_users_active_name
ON opd_core.pd_users(user_name) WHERE active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_active_name
ON opd_docs.pd_documents(doc_name) WHERE active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_folders_active_name
ON opd_docs.pd_folders(folder_name) WHERE active = true;

-- =========================================================================
-- FULL-TEXT SEARCH OPTIMIZATIONS
-- =========================================================================

-- GIN index for document full-text search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_fts_gin
ON opd_docs.pd_documents USING GIN(to_tsvector('english', 
    COALESCE(doc_name, '') || ' ' || 
    COALESCE(doc_title, '') || ' ' || 
    COALESCE(full_text, '')
));

-- GIN index for folder search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_folders_fts_gin
ON opd_docs.pd_folders USING GIN(to_tsvector('english', 
    COALESCE(folder_name, '') || ' ' || 
    COALESCE(description, '')
));

-- Trigram indexes for similarity search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_docs_name_trgm
ON opd_docs.pd_documents USING GIN(doc_name gin_trgm_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_pd_folders_name_trgm
ON opd_docs.pd_folders USING GIN(folder_name gin_trgm_ops);

-- =========================================================================
-- STATISTICS AND MAINTENANCE
-- =========================================================================

-- Update table statistics for better query planning
ANALYZE opd_core.pd_users;
ANALYZE opd_core.pd_groups;
ANALYZE opd_docs.pd_documents;
ANALYZE opd_docs.pd_folders;
ANALYZE opd_docs.pd_document_attributes;
ANALYZE opd_admin.pd_acl;
ANALYZE opd_admin.pd_audit_log;

-- Set statistics targets for better performance on large tables
ALTER TABLE opd_docs.pd_documents ALTER COLUMN doc_name SET STATISTICS 1000;
ALTER TABLE opd_docs.pd_documents ALTER COLUMN created_at SET STATISTICS 1000;
ALTER TABLE opd_docs.pd_documents ALTER COLUMN folder_id SET STATISTICS 1000;
ALTER TABLE opd_docs.pd_folders ALTER COLUMN folder_path SET STATISTICS 1000;
ALTER TABLE opd_admin.pd_audit_log ALTER COLUMN created_at SET STATISTICS 1000;

-- =========================================================================
-- PARTITIONING PREPARATION (for large deployments)
-- =========================================================================

-- Create partitioned audit log table for better performance with large datasets
-- This is commented out by default but can be enabled for high-volume deployments

/*
-- Drop existing audit log table and recreate as partitioned
-- DROP TABLE IF EXISTS opd_admin.pd_audit_log;

CREATE TABLE opd_admin.pd_audit_log (
    log_id UUID DEFAULT uuid_generate_v4(),
    action_type VARCHAR(20) NOT NULL,
    resource_type VARCHAR(20) NOT NULL,
    resource_id UUID,
    user_name VARCHAR(50),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- Create monthly partitions for the current year
CREATE TABLE opd_admin.pd_audit_log_2024_01 PARTITION OF opd_admin.pd_audit_log
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE opd_admin.pd_audit_log_2024_02 PARTITION OF opd_admin.pd_audit_log
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Add more partitions as needed...
*/

-- =========================================================================
-- CONSTRAINT OPTIMIZATIONS
-- =========================================================================

-- Add check constraints for data validation
ALTER TABLE opd_docs.pd_documents 
ADD CONSTRAINT chk_file_size_positive 
CHECK (file_size IS NULL OR file_size > 0);

ALTER TABLE opd_docs.pd_documents 
ADD CONSTRAINT chk_version_positive 
CHECK (version_number > 0);

ALTER TABLE opd_core.pd_users 
ADD CONSTRAINT chk_email_format 
CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- =========================================================================
-- MATERIALIZED VIEWS FOR REPORTING
-- =========================================================================

-- Document count by folder materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS opd_docs.mv_folder_doc_counts AS
SELECT 
    f.folder_id,
    f.folder_name,
    f.folder_path,
    COUNT(d.doc_id) AS document_count,
    COUNT(CASE WHEN d.created_at > CURRENT_DATE - INTERVAL '30 days' THEN 1 END) AS recent_documents,
    MAX(d.created_at) AS last_document_created
FROM opd_docs.pd_folders f
LEFT JOIN opd_docs.pd_documents d ON f.folder_id = d.folder_id AND d.active = true
WHERE f.active = true
GROUP BY f.folder_id, f.folder_name, f.folder_path;

-- Create unique index on materialized view
CREATE UNIQUE INDEX idx_mv_folder_counts_id ON opd_docs.mv_folder_doc_counts(folder_id);
CREATE INDEX idx_mv_folder_counts_path ON opd_docs.mv_folder_doc_counts(folder_path);

-- Document statistics by type
CREATE MATERIALIZED VIEW IF NOT EXISTS opd_docs.mv_doc_type_stats AS
SELECT 
    dt.type_id,
    dt.type_name,
    COUNT(d.doc_id) AS document_count,
    AVG(d.file_size) AS avg_file_size,
    SUM(d.file_size) AS total_size,
    COUNT(CASE WHEN d.created_at > CURRENT_DATE - INTERVAL '7 days' THEN 1 END) AS documents_last_week
FROM opd_docs.pd_doc_types dt
LEFT JOIN opd_docs.pd_documents d ON dt.type_id = d.doc_type AND d.active = true
WHERE dt.active = true
GROUP BY dt.type_id, dt.type_name;

-- Create unique index on doc type stats
CREATE UNIQUE INDEX idx_mv_doc_type_stats_id ON opd_docs.mv_doc_type_stats(type_id);

-- =========================================================================
-- FUNCTIONS FOR MAINTENANCE
-- =========================================================================

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_reporting_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY opd_docs.mv_folder_doc_counts;
    REFRESH MATERIALIZED VIEW CONCURRENTLY opd_docs.mv_doc_type_stats;
    
    -- Update table statistics
    ANALYZE opd_docs.pd_documents;
    ANALYZE opd_docs.pd_folders;
    
    RAISE NOTICE 'Materialized views refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old audit logs (older than 1 year)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM opd_admin.pd_audit_log 
    WHERE created_at < CURRENT_DATE - INTERVAL '1 year';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RAISE NOTICE 'Deleted % old audit log entries', deleted_count;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM opd_core.pd_sessions 
    WHERE expires_at < CURRENT_TIMESTAMP OR 
          (last_access < CURRENT_TIMESTAMP - INTERVAL '24 hours' AND active = false);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RAISE NOTICE 'Deleted % expired sessions', deleted_count;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =========================================================================
-- MONITORING VIEWS
-- =========================================================================

-- View for database size monitoring
CREATE OR REPLACE VIEW opd_admin.v_database_size AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables 
WHERE schemaname IN ('opd_core', 'opd_docs', 'opd_admin')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- View for index usage statistics
CREATE OR REPLACE VIEW opd_admin.v_index_usage AS
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE schemaname IN ('opd_core', 'opd_docs', 'opd_admin')
ORDER BY idx_scan DESC;

-- =========================================================================
-- UPDATE CONFIGURATION
-- =========================================================================

-- Update database version
UPDATE opd_core.pd_config 
SET config_value = '1.0.1', updated_at = CURRENT_TIMESTAMP
WHERE config_key = 'database.version';

COMMIT;