package org.openprodoc.api.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.event.EventListener;
import org.springframework.core.env.Environment;
import org.springframework.jdbc.core.JdbcTemplate;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

@Configuration
public class InitializationConfiguration {

    private static final Logger logger = LoggerFactory.getLogger(InitializationConfiguration.class);
    
    @Autowired
    private Environment environment;
    
    @Autowired
    private DataSource dataSource;
    
    @Autowired
    private JdbcTemplate jdbcTemplate;

    @EventListener(ApplicationReadyEvent.class)
    public void initializeSystem() {
        logger.info("Starting OpenProdoc Red post-startup initialization...");
        
        try {
            // Verify system is properly initialized by Flyway migrations
            verifySystemInitialization();
            
            // Create required runtime directories
            createRuntimeDirectories();
            
            // Validate storage configuration
            validateStorageConfiguration();
            
            logger.info("OpenProdoc Red initialization completed successfully");
            
        } catch (Exception e) {
            logger.error("Failed to complete system initialization", e);
            throw new RuntimeException("System initialization failed", e);
        }
    }

    private void verifySystemInitialization() {
        try {
            String sql = "SELECT config_value FROM pd_config WHERE config_name = 'SYSTEM_INITIALIZED'";
            String initialized = jdbcTemplate.queryForObject(sql, String.class);
            
            if (!"true".equals(initialized)) {
                throw new RuntimeException("System not properly initialized by database migrations");
            }
            
            logger.info("System initialization verified successfully");
            
        } catch (Exception e) {
            logger.error("System initialization verification failed", e);
            throw new RuntimeException("System not properly initialized", e);
        }
    }

    private void createRuntimeDirectories() {
        String[] directories = {
            System.getProperty("openprodoc.storage.path", "/app/storage"),
            System.getProperty("openprodoc.lucene.path", "/app/storage/lucene"),
            "/app/temp"
        };
        
        for (String dirPath : directories) {
            java.io.File dir = new java.io.File(dirPath);
            if (!dir.exists()) {
                if (dir.mkdirs()) {
                    logger.info("Created directory: {}", dirPath);
                } else {
                    logger.warn("Failed to create directory: {}", dirPath);
                }
            }
        }
    }

    private void validateStorageConfiguration() {
        try {
            // Validate storage path is accessible
            String storagePath = System.getProperty("openprodoc.storage.path", "/app/storage");
            java.io.File storageDir = new java.io.File(storagePath);
            
            if (!storageDir.exists() || !storageDir.canWrite()) {
                logger.error("Storage directory not accessible: {}", storagePath);
                throw new RuntimeException("Storage directory not accessible: " + storagePath);
            }
            
            // Test write access
            java.io.File testFile = new java.io.File(storageDir, ".write-test");
            try {
                testFile.createNewFile();
                testFile.delete();
                logger.info("Storage directory write access validated: {}", storagePath);
            } catch (Exception e) {
                throw new RuntimeException("Storage directory not writable: " + storagePath, e);
            }
            
        } catch (Exception e) {
            logger.error("Storage configuration validation failed", e);
            throw e;
        }
    }
}