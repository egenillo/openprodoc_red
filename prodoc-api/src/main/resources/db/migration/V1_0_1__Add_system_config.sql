-- Add system configuration and initialization tracking
CREATE TABLE IF NOT EXISTS pd_config (
    config_id SERIAL PRIMARY KEY,
    config_name VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on config_name for fast lookups
CREATE INDEX IF NOT EXISTS idx_pd_config_name ON pd_config(config_name);

-- Insert default system configuration
INSERT INTO pd_config (config_name, config_value, description) VALUES
('MAX_UPLOAD_SIZE', '52428800', 'Maximum file upload size in bytes'),
('DEFAULT_STORAGE_TYPE', 'FILESYSTEM', 'Default document storage type'),
('LUCENE_INDEX_PATH', '/app/storage/lucene', 'Lucene index storage path'),
('SESSION_TIMEOUT', '3600', 'Session timeout in seconds')
ON CONFLICT (config_name) DO NOTHING;

-- Create admin user if it doesn't exist
INSERT INTO pd_users (user_id, user_name, user_password, email, user_type, active, created_date)
VALUES ('admin', 'Administrator', 
        '$2a$10$rByFbGz8.VhBz8KZdBhGZ.GlGJ2Q1YOJ7VgDRg2J8AjX8M8JvP7Gi', 
        'admin@openprodoc.org', 'ADMIN', true, CURRENT_TIMESTAMP)
ON CONFLICT (user_id) DO NOTHING;

-- Create root folder if it doesn't exist
INSERT INTO pd_folders (folder_id, folder_name, parent_folder_id, folder_type, 
                       created_by, created_date, acl)
VALUES ('ROOT', 'Root Folder', NULL, 'SYSTEM', 'admin', CURRENT_TIMESTAMP, '{}')
ON CONFLICT (folder_id) DO NOTHING;

-- Mark system as initialized
INSERT INTO pd_config (config_name, config_value, description, created_date)
VALUES ('SYSTEM_INITIALIZED', 'true', 'System initialization completed by Flyway migration', CURRENT_TIMESTAMP)
ON CONFLICT (config_name) DO NOTHING;