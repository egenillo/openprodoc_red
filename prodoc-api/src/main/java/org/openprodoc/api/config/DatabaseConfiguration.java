package org.openprodoc.api.config;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

import javax.sql.DataSource;
import java.util.concurrent.TimeUnit;

@Configuration
@EnableTransactionManagement
@ConfigurationProperties(prefix = "openprodoc.database")
public class DatabaseConfiguration {
    
    private static final Logger logger = LoggerFactory.getLogger(DatabaseConfiguration.class);
    
    // Database connection properties
    private String driverClassName = "org.postgresql.Driver";
    private String url = "jdbc:postgresql://localhost:5432/openprodoc";
    private String username = "openprodoc";
    private String password = "openprodoc";
    
    // HikariCP connection pool properties
    private int maxPoolSize = 20;
    private int minIdle = 5;
    private long connectionTimeout = 30000; // 30 seconds
    private long idleTimeout = 600000; // 10 minutes
    private long maxLifetime = 1800000; // 30 minutes
    private long leakDetectionThreshold = 60000; // 1 minute
    private String connectionTestQuery = "SELECT 1";
    
    // PostgreSQL-specific properties
    private boolean cachePrepStmts = true;
    private int prepStmtCacheSize = 250;
    private int prepStmtCacheSqlLimit = 2048;
    private boolean useServerPrepStmts = true;
    private boolean rewriteBatchedStatements = true;
    private boolean maintainTimeStats = false;
    private boolean logUnclosedConnections = true;
    
    @Bean
    @Primary
    public DataSource dataSource() {
        logger.info("Configuring HikariCP DataSource for PostgreSQL");
        
        HikariConfig config = new HikariConfig();
        
        // Basic connection properties
        config.setDriverClassName(driverClassName);
        config.setJdbcUrl(url);
        config.setUsername(username);
        config.setPassword(password);
        
        // Connection pool settings
        config.setMaximumPoolSize(maxPoolSize);
        config.setMinimumIdle(minIdle);
        config.setConnectionTimeout(connectionTimeout);
        config.setIdleTimeout(idleTimeout);
        config.setMaxLifetime(maxLifetime);
        config.setLeakDetectionThreshold(leakDetectionThreshold);
        config.setConnectionTestQuery(connectionTestQuery);
        
        // Pool naming
        config.setPoolName("OpenProdocHikariPool");
        
        // PostgreSQL-specific optimizations
        if (isPostgreSQL()) {
            configurePostgreSQLOptimizations(config);
        }
        
        // Connection initialization SQL
        config.setConnectionInitSql("SET application_name = 'openprodoc-red'");
        
        // Health check and validation
        config.setValidationTimeout(5000);
        config.setInitializationFailTimeout(30000);
        
        // Monitoring and logging
        config.setRegisterMbeans(true);
        
        logger.info("HikariCP configured - Pool: {}, Min: {}, Max: {}, Timeout: {}ms", 
                   config.getPoolName(), config.getMinimumIdle(), 
                   config.getMaximumPoolSize(), config.getConnectionTimeout());
        
        return new HikariDataSource(config);
    }
    
    @Bean
    public JdbcTemplate jdbcTemplate(DataSource dataSource) {
        JdbcTemplate template = new JdbcTemplate(dataSource);
        template.setQueryTimeout(30); // 30 seconds
        template.setFetchSize(1000); // Optimize for bulk operations
        return template;
    }
    
    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        DataSourceTransactionManager manager = new DataSourceTransactionManager(dataSource);
        manager.setDefaultTimeout(30); // 30 seconds default transaction timeout
        return manager;
    }
    
    private boolean isPostgreSQL() {
        return url != null && url.contains("postgresql");
    }
    
    private void configurePostgreSQLOptimizations(HikariConfig config) {
        logger.info("Applying PostgreSQL-specific optimizations");
        
        // PostgreSQL driver optimizations
        config.addDataSourceProperty("cachePrepStmts", String.valueOf(cachePrepStmts));
        config.addDataSourceProperty("prepStmtCacheSize", String.valueOf(prepStmtCacheSize));
        config.addDataSourceProperty("prepStmtCacheSqlLimit", String.valueOf(prepStmtCacheSqlLimit));
        config.addDataSourceProperty("useServerPrepStmts", String.valueOf(useServerPrepStmts));
        config.addDataSourceProperty("rewriteBatchedStatements", String.valueOf(rewriteBatchedStatements));
        config.addDataSourceProperty("maintainTimeStats", String.valueOf(maintainTimeStats));
        config.addDataSourceProperty("logUnclosedConnections", String.valueOf(logUnclosedConnections));
        
        // PostgreSQL connection parameters
        config.addDataSourceProperty("tcpKeepAlive", "true");
        config.addDataSourceProperty("socketTimeout", "30");
        config.addDataSourceProperty("loginTimeout", "10");
        config.addDataSourceProperty("connectTimeout", "10");
        config.addDataSourceProperty("cancelSignalTimeout", "10");
        
        // SSL configuration for production
        if (url.contains("sslmode") || isProdEnvironment()) {
            config.addDataSourceProperty("ssl", "true");
            config.addDataSourceProperty("sslmode", "require");
        }
        
        // Character encoding
        config.addDataSourceProperty("characterEncoding", "UTF-8");
        config.addDataSourceProperty("useUnicode", "true");
        
        // Performance settings
        config.addDataSourceProperty("defaultRowFetchSize", "1000");
        config.addDataSourceProperty("readOnlyMode", "false");
        
        logger.info("PostgreSQL optimizations applied");
    }
    
    private boolean isProdEnvironment() {
        String profiles = System.getProperty("spring.profiles.active", "");
        return profiles.contains("prod") || profiles.contains("production");
    }
    
    // Development profile with smaller pool
    @Bean
    @Profile("dev")
    public DataSource devDataSource() {
        logger.info("Configuring development DataSource with smaller connection pool");
        
        this.maxPoolSize = 5;
        this.minIdle = 1;
        this.connectionTimeout = 10000; // 10 seconds for faster feedback
        this.leakDetectionThreshold = 30000; // 30 seconds for development
        
        return dataSource();
    }
    
    // Production profile with optimized settings
    @Bean  
    @Profile("prod")
    public DataSource prodDataSource() {
        logger.info("Configuring production DataSource with optimized settings");
        
        this.maxPoolSize = 50;
        this.minIdle = 10;
        this.connectionTimeout = 30000;
        this.idleTimeout = 300000; // 5 minutes
        this.maxLifetime = 900000; // 15 minutes
        this.leakDetectionThreshold = 120000; // 2 minutes
        
        return dataSource();
    }
    
    // Getters and setters for configuration properties
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
    
    public long getLeakDetectionThreshold() { return leakDetectionThreshold; }
    public void setLeakDetectionThreshold(long leakDetectionThreshold) { this.leakDetectionThreshold = leakDetectionThreshold; }
    
    public String getConnectionTestQuery() { return connectionTestQuery; }
    public void setConnectionTestQuery(String connectionTestQuery) { this.connectionTestQuery = connectionTestQuery; }
}