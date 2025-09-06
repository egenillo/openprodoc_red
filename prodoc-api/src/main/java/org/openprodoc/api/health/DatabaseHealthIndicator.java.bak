package org.openprodoc.api.health;

import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

@Component("database")
public class DatabaseHealthIndicator implements HealthIndicator {
    
    private static final Logger logger = LoggerFactory.getLogger(DatabaseHealthIndicator.class);
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Autowired
    private DataSource dataSource;
    
    @Override
    public Health health() {
        try {
            return checkDatabaseHealth();
        } catch (Exception e) {
            logger.error("Database health check failed", e);
            return Health.down()
                .withDetail("error", e.getMessage())
                .withDetail("timestamp", System.currentTimeMillis())
                .build();
        }
    }
    
    private Health checkDatabaseHealth() {
        Health.Builder builder = Health.up();
        
        try {
            // Basic connectivity test
            long startTime = System.currentTimeMillis();
            Integer result = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            long queryTime = System.currentTimeMillis() - startTime;
            
            if (result == null || result != 1) {
                return Health.down()
                    .withDetail("error", "Database connectivity test failed")
                    .build();
            }
            
            builder.withDetail("status", "Database connection successful")
                   .withDetail("responseTime", queryTime + "ms");
            
            // Get database metadata
            addDatabaseMetadata(builder);
            
            // Check HikariCP pool status
            addConnectionPoolStatus(builder);
            
            // Check database-specific health
            addDatabaseSpecificChecks(builder);
            
            // Check schema version
            addSchemaVersion(builder);
            
            // Performance metrics
            addPerformanceMetrics(builder);
            
        } catch (DataAccessException e) {
            logger.error("Database health check failed with DataAccessException", e);
            return Health.down()
                .withDetail("error", "Database query failed: " + e.getMessage())
                .withDetail("type", "DataAccessException")
                .build();
        }
        
        return builder.build();
    }
    
    private void addDatabaseMetadata(Health.Builder builder) {
        try (Connection connection = dataSource.getConnection()) {
            DatabaseMetaData metaData = connection.getMetaData();
            
            Map<String, Object> dbInfo = new HashMap<>();
            dbInfo.put("productName", metaData.getDatabaseProductName());
            dbInfo.put("productVersion", metaData.getDatabaseProductVersion());
            dbInfo.put("driverName", metaData.getDriverName());
            dbInfo.put("driverVersion", metaData.getDriverVersion());
            dbInfo.put("url", maskPassword(metaData.getURL()));
            dbInfo.put("username", metaData.getUserName());
            dbInfo.put("readOnly", connection.isReadOnly());
            dbInfo.put("autoCommit", connection.getAutoCommit());
            dbInfo.put("catalog", connection.getCatalog());
            dbInfo.put("schema", connection.getSchema());
            
            builder.withDetail("database", dbInfo);
            
        } catch (SQLException e) {
            logger.warn("Could not retrieve database metadata", e);
            builder.withDetail("metadataError", e.getMessage());
        }
    }
    
    private void addConnectionPoolStatus(Health.Builder builder) {
        if (dataSource instanceof HikariDataSource) {
            HikariDataSource hikariDS = (HikariDataSource) dataSource;
            
            Map<String, Object> poolInfo = new HashMap<>();
            poolInfo.put("poolName", hikariDS.getPoolName());
            poolInfo.put("activeConnections", hikariDS.getHikariPoolMXBean().getActiveConnections());
            poolInfo.put("idleConnections", hikariDS.getHikariPoolMXBean().getIdleConnections());
            poolInfo.put("totalConnections", hikariDS.getHikariPoolMXBean().getTotalConnections());
            poolInfo.put("threadsAwaitingConnection", hikariDS.getHikariPoolMXBean().getThreadsAwaitingConnection());
            poolInfo.put("maximumPoolSize", hikariDS.getMaximumPoolSize());
            poolInfo.put("minimumIdle", hikariDS.getMinimumIdle());
            poolInfo.put("connectionTimeout", hikariDS.getConnectionTimeout());
            poolInfo.put("idleTimeout", hikariDS.getIdleTimeout());
            poolInfo.put("maxLifetime", hikariDS.getMaxLifetime());
            
            // Calculate pool utilization
            int active = hikariDS.getHikariPoolMXBean().getActiveConnections();
            int max = hikariDS.getMaximumPoolSize();
            double utilization = max > 0 ? (double) active / max * 100 : 0;
            poolInfo.put("utilizationPercent", Math.round(utilization * 100.0) / 100.0);
            
            // Determine pool health
            String poolHealth = "HEALTHY";
            if (utilization > 80) {
                poolHealth = "HIGH_UTILIZATION";
            } else if (hikariDS.getHikariPoolMXBean().getThreadsAwaitingConnection() > 0) {
                poolHealth = "THREADS_WAITING";
            }
            poolInfo.put("poolHealth", poolHealth);
            
            builder.withDetail("connectionPool", poolInfo);
        }
    }
    
    private void addDatabaseSpecificChecks(Health.Builder builder) {
        try {
            // Check if this is PostgreSQL and add specific checks
            String dbProduct = jdbcTemplate.queryForObject(
                "SELECT current_setting('server_version')", String.class);
            
            if (dbProduct != null) {
                Map<String, Object> pgInfo = new HashMap<>();
                pgInfo.put("version", dbProduct);
                
                // Check PostgreSQL-specific metrics
                try {
                    // Check database size
                    String dbSize = jdbcTemplate.queryForObject(
                        "SELECT pg_size_pretty(pg_database_size(current_database()))", String.class);
                    pgInfo.put("databaseSize", dbSize);
                    
                    // Check active connections
                    Integer activeConnections = jdbcTemplate.queryForObject(
                        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'", Integer.class);
                    pgInfo.put("activeQueries", activeConnections);
                    
                    // Check for long-running queries
                    Integer longRunning = jdbcTemplate.queryForObject(
                        "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '5 minutes'", 
                        Integer.class);
                    pgInfo.put("longRunningQueries", longRunning);
                    
                    // Check table statistics
                    Integer tableCount = jdbcTemplate.queryForObject(
                        "SELECT count(*) FROM information_schema.tables WHERE table_schema IN ('opd_core', 'opd_docs', 'opd_admin')", 
                        Integer.class);
                    pgInfo.put("openProdocTables", tableCount);
                    
                } catch (Exception e) {
                    pgInfo.put("metricsError", e.getMessage());
                }
                
                builder.withDetail("postgresql", pgInfo);
            }
            
        } catch (Exception e) {
            logger.debug("Could not retrieve database-specific information", e);
        }
    }
    
    private void addSchemaVersion(Health.Builder builder) {
        try {
            String schemaVersion = jdbcTemplate.queryForObject(
                "SELECT config_value FROM opd_core.pd_config WHERE config_key = 'database.version'", 
                String.class);
            
            if (schemaVersion != null) {
                builder.withDetail("schemaVersion", schemaVersion);
            } else {
                builder.withDetail("schemaVersionWarning", "Schema version not found in configuration");
            }
            
        } catch (DataAccessException e) {
            logger.debug("Could not retrieve schema version - database may not be initialized", e);
            builder.withDetail("schemaStatus", "NOT_INITIALIZED");
        }
    }
    
    private void addPerformanceMetrics(Health.Builder builder) {
        try {
            Map<String, Object> metrics = new HashMap<>();
            
            // Measure query performance with a more complex query
            long startTime = System.currentTimeMillis();
            Integer recordCount = jdbcTemplate.queryForObject(
                "SELECT COALESCE((SELECT count(*) FROM opd_docs.pd_documents WHERE active = true), 0)", 
                Integer.class);
            long complexQueryTime = System.currentTimeMillis() - startTime;
            
            metrics.put("documentCount", recordCount);
            metrics.put("complexQueryResponseTime", complexQueryTime + "ms");
            
            // Check for slow queries (if available)
            try {
                Integer slowQueries = jdbcTemplate.queryForObject(
                    "SELECT count(*) FROM pg_stat_statements WHERE mean_time > 1000", Integer.class);
                metrics.put("slowQueries", slowQueries);
            } catch (Exception e) {
                // pg_stat_statements may not be enabled
                metrics.put("slowQueriesNote", "pg_stat_statements extension not available");
            }
            
            builder.withDetail("performance", metrics);
            
        } catch (Exception e) {
            logger.debug("Could not retrieve performance metrics", e);
            builder.withDetail("performanceError", e.getMessage());
        }
    }
    
    private String maskPassword(String url) {
        if (url == null) return null;
        return url.replaceAll("password=[^&;]*", "password=***");
    }
}