package org.openprodoc.api.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api")
public class HealthController {

    private static final Logger logger = LoggerFactory.getLogger(HealthController.class);

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        boolean isHealthy = true;
        
        try {
            // Check database connectivity
            Map<String, Object> dbHealth = checkDatabaseHealth();
            health.put("database", dbHealth);
            if (!"UP".equals(dbHealth.get("status"))) {
                isHealthy = false;
            }
            
            // Check storage accessibility
            Map<String, Object> storageHealth = checkStorageHealth();
            health.put("storage", storageHealth);
            if (!"UP".equals(storageHealth.get("status"))) {
                isHealthy = false;
            }
            
            // Check system initialization
            Map<String, Object> initHealth = checkInitializationHealth();
            health.put("initialization", initHealth);
            if (!"UP".equals(initHealth.get("status"))) {
                isHealthy = false;
            }
            
            health.put("status", isHealthy ? "UP" : "DOWN");
            health.put("timestamp", System.currentTimeMillis());
            
            return ResponseEntity.ok(health);
            
        } catch (Exception e) {
            logger.error("Health check failed", e);
            health.put("status", "DOWN");
            health.put("error", e.getMessage());
            health.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(health);
        }
    }

    @GetMapping("/ready")
    public ResponseEntity<Map<String, Object>> readiness() {
        Map<String, Object> readiness = new HashMap<>();
        boolean isReady = true;
        
        try {
            // Check if system is fully initialized
            String sql = "SELECT config_value FROM pd_config WHERE config_name = 'SYSTEM_INITIALIZED'";
            String initialized = jdbcTemplate.queryForObject(sql, String.class);
            
            if (!"true".equals(initialized)) {
                isReady = false;
                readiness.put("initialization", Map.of("status", "DOWN", "message", "System not initialized"));
            } else {
                readiness.put("initialization", Map.of("status", "UP", "message", "System initialized"));
            }
            
            // Check storage directories exist and are writable
            String storagePath = System.getProperty("openprodoc.storage.path", "/app/storage");
            File storageDir = new File(storagePath);
            
            if (!storageDir.exists() || !storageDir.canWrite()) {
                isReady = false;
                readiness.put("storage", Map.of("status", "DOWN", "message", "Storage not accessible"));
            } else {
                readiness.put("storage", Map.of("status", "UP", "message", "Storage accessible"));
            }
            
            readiness.put("status", isReady ? "UP" : "DOWN");
            readiness.put("timestamp", System.currentTimeMillis());
            
            return ResponseEntity.ok(readiness);
            
        } catch (Exception e) {
            logger.error("Readiness check failed", e);
            readiness.put("status", "DOWN");
            readiness.put("error", e.getMessage());
            readiness.put("timestamp", System.currentTimeMillis());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(readiness);
        }
    }

    private Map<String, Object> checkDatabaseHealth() {
        Map<String, Object> dbHealth = new HashMap<>();
        
        try {
            // Simple connectivity test
            jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            
            // Check critical tables exist
            jdbcTemplate.queryForObject("SELECT COUNT(*) FROM pd_config", Integer.class);
            
            dbHealth.put("status", "UP");
            dbHealth.put("message", "Database connection successful");
            
        } catch (Exception e) {
            logger.error("Database health check failed", e);
            dbHealth.put("status", "DOWN");
            dbHealth.put("message", "Database connection failed: " + e.getMessage());
        }
        
        return dbHealth;
    }

    private Map<String, Object> checkStorageHealth() {
        Map<String, Object> storageHealth = new HashMap<>();
        
        try {
            String storagePath = System.getProperty("openprodoc.storage.path", "/app/storage");
            File storageDir = new File(storagePath);
            
            if (!storageDir.exists()) {
                storageHealth.put("status", "DOWN");
                storageHealth.put("message", "Storage directory does not exist: " + storagePath);
                return storageHealth;
            }
            
            if (!storageDir.canWrite()) {
                storageHealth.put("status", "DOWN");
                storageHealth.put("message", "Storage directory not writable: " + storagePath);
                return storageHealth;
            }
            
            // Test write access
            File testFile = new File(storageDir, ".health-check");
            testFile.createNewFile();
            testFile.delete();
            
            storageHealth.put("status", "UP");
            storageHealth.put("message", "Storage accessible");
            storageHealth.put("path", storagePath);
            
        } catch (Exception e) {
            logger.error("Storage health check failed", e);
            storageHealth.put("status", "DOWN");
            storageHealth.put("message", "Storage check failed: " + e.getMessage());
        }
        
        return storageHealth;
    }

    private Map<String, Object> checkInitializationHealth() {
        Map<String, Object> initHealth = new HashMap<>();
        
        try {
            String sql = "SELECT config_value FROM pd_config WHERE config_name = 'SYSTEM_INITIALIZED'";
            String initialized = jdbcTemplate.queryForObject(sql, String.class);
            
            if ("true".equals(initialized)) {
                initHealth.put("status", "UP");
                initHealth.put("message", "System properly initialized");
            } else {
                initHealth.put("status", "DOWN");
                initHealth.put("message", "System not initialized");
            }
            
        } catch (Exception e) {
            logger.error("Initialization health check failed", e);
            initHealth.put("status", "DOWN");
            initHealth.put("message", "Initialization check failed: " + e.getMessage());
        }
        
        return initHealth;
    }
}