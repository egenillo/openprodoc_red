package org.openprodoc.api.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.env.Environment;
import prodoc.ProdocFW;
import prodoc.DriverGeneric;

import javax.sql.DataSource;
import java.util.Properties;

@Configuration
@ConfigurationProperties(prefix = "openprodoc")
public class ProdocConfiguration {
    
    private DatabaseConfig database = new DatabaseConfig();
    private StorageConfig storage = new StorageConfig();
    private SecurityConfig security = new SecurityConfig();
    private FullTextConfig fulltext = new FullTextConfig();
    
    @Bean
    public DataSource dataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(database.getUrl());
        config.setUsername(database.getUsername());
        config.setPassword(database.getPassword());
        config.setDriverClassName(database.getDriverClassName());
        
        // Connection pool settings
        config.setMaximumPoolSize(database.getMaxPoolSize());
        config.setMinimumIdle(database.getMinIdle());
        config.setConnectionTimeout(database.getConnectionTimeout());
        config.setIdleTimeout(database.getIdleTimeout());
        config.setMaxLifetime(database.getMaxLifetime());
        
        // PostgreSQL optimizations
        if (database.getUrl().contains("postgresql")) {
            config.addDataSourceProperty("cachePrepStmts", "true");
            config.addDataSourceProperty("prepStmtCacheSize", "250");
            config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
            config.addDataSourceProperty("useServerPrepStmts", "true");
        }
        
        return new HikariDataSource(config);
    }
    
    @Bean
    public Properties prodocProperties(Environment env) {
        Properties props = new Properties();
        
        // Database configuration
        props.setProperty("DRIVER", database.getDriverClassName());
        props.setProperty("URL", database.getUrl());
        props.setProperty("USER", database.getUsername());
        props.setProperty("PASSWORD", database.getPassword());
        
        // Storage configuration
        props.setProperty("STORAGE_TYPE", storage.getType());
        props.setProperty("STORAGE_PATH", storage.getPath());
        
        if ("S3".equals(storage.getType())) {
            props.setProperty("S3_BUCKET", storage.getS3Bucket());
            props.setProperty("S3_REGION", storage.getS3Region());
        }
        
        // Security configuration
        props.setProperty("AUTH_TYPE", security.getAuthType());
        props.setProperty("SESSION_TIMEOUT", String.valueOf(security.getSessionTimeout()));
        props.setProperty("JWT_SECRET", security.getJwtSecret());
        
        // Full-text search configuration
        props.setProperty("FULLTEXT_ENGINE", fulltext.getEngine());
        props.setProperty("FULLTEXT_INDEX_PATH", fulltext.getIndexPath());
        
        return props;
    }
    
    // Getter and setter classes for configuration
    public static class DatabaseConfig {
        private String driverClassName = "org.postgresql.Driver";
        private String url = "jdbc:postgresql://localhost:5432/openprodoc";
        private String username = "openprodoc";
        private String password = "openprodoc";
        private int maxPoolSize = 10;
        private int minIdle = 2;
        private long connectionTimeout = 30000;
        private long idleTimeout = 600000;
        private long maxLifetime = 1800000;
        
        // Getters and setters
        public String getDriverClassName() { return driverClassName; }
        public void setDriverClassName(String driverClassName) { this.driverClassName = driverClassName; }
        public String getUrl() { return url; }
        public void setUrl(String url) { this.url = url; }
        public String getUsername() { return username; }
        public void setUsername(String username) { this.username = username; }
        public String getPassword() { return password; }
        public void setPassword(String password) { this.password = password; }
        public int getMaxPoolSize() { return maxPoolSize; }
        public void setMaxPoolSize(int maxPoolSize) { this.maxPoolSize = maxPoolSize; }
        public int getMinIdle() { return minIdle; }
        public void setMinIdle(int minIdle) { this.minIdle = minIdle; }
        public long getConnectionTimeout() { return connectionTimeout; }
        public void setConnectionTimeout(long connectionTimeout) { this.connectionTimeout = connectionTimeout; }
        public long getIdleTimeout() { return idleTimeout; }
        public void setIdleTimeout(long idleTimeout) { this.idleTimeout = idleTimeout; }
        public long getMaxLifetime() { return maxLifetime; }
        public void setMaxLifetime(long maxLifetime) { this.maxLifetime = maxLifetime; }
    }
    
    public static class StorageConfig {
        private String type = "FILESYSTEM";
        private String path = "/var/openprodoc/documents";
        private String s3Bucket;
        private String s3Region = "us-east-1";
        
        // Getters and setters
        public String getType() { return type; }
        public void setType(String type) { this.type = type; }
        public String getPath() { return path; }
        public void setPath(String path) { this.path = path; }
        public String getS3Bucket() { return s3Bucket; }
        public void setS3Bucket(String s3Bucket) { this.s3Bucket = s3Bucket; }
        public String getS3Region() { return s3Region; }
        public void setS3Region(String s3Region) { this.s3Region = s3Region; }
    }
    
    public static class SecurityConfig {
        private String authType = "OPD";
        private int sessionTimeout = 3600;
        private String jwtSecret = "${random.value}";
        
        // Getters and setters
        public String getAuthType() { return authType; }
        public void setAuthType(String authType) { this.authType = authType; }
        public int getSessionTimeout() { return sessionTimeout; }
        public void setSessionTimeout(int sessionTimeout) { this.sessionTimeout = sessionTimeout; }
        public String getJwtSecret() { return jwtSecret; }
        public void setJwtSecret(String jwtSecret) { this.jwtSecret = jwtSecret; }
    }
    
    public static class FullTextConfig {
        private String engine = "LUCENE";
        private String indexPath = "/var/openprodoc/lucene";
        
        // Getters and setters
        public String getEngine() { return engine; }
        public void setEngine(String engine) { this.engine = engine; }
        public String getIndexPath() { return indexPath; }
        public void setIndexPath(String indexPath) { this.indexPath = indexPath; }
    }
    
    // Main getters and setters
    public DatabaseConfig getDatabase() { return database; }
    public void setDatabase(DatabaseConfig database) { this.database = database; }
    public StorageConfig getStorage() { return storage; }
    public void setStorage(StorageConfig storage) { this.storage = storage; }
    public SecurityConfig getSecurity() { return security; }
    public void setSecurity(SecurityConfig security) { this.security = security; }
    public FullTextConfig getFulltext() { return fulltext; }
    public void setFulltext(FullTextConfig fulltext) { this.fulltext = fulltext; }
}