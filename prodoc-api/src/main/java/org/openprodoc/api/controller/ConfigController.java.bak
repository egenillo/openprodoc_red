package org.openprodoc.api.controller;

import io.micrometer.core.annotation.Timed;
import org.openprodoc.api.config.ProdocConfiguration;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.actuate.info.Info;
import org.springframework.boot.actuate.info.InfoContributor;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/v1/config")
public class ConfigController implements InfoContributor {
    
    private static final Logger logger = LoggerFactory.getLogger(ConfigController.class);
    
    private final ProdocConfiguration prodocConfig;
    
    public ConfigController(ProdocConfiguration prodocConfig) {
        this.prodocConfig = prodocConfig;
    }
    
    @GetMapping("/info")
    @Timed(value = "config.info", description = "Time taken to get configuration info")
    public Map<String, Object> getConfigInfo() {
        logger.debug("Retrieving configuration information");
        
        Map<String, Object> info = new HashMap<>();
        info.put("timestamp", LocalDateTime.now());
        info.put("database", getDatabaseInfo());
        info.put("storage", getStorageInfo());
        info.put("security", getSecurityInfo());
        info.put("fulltext", getFullTextInfo());
        
        return info;
    }
    
    @GetMapping("/database")
    @PreAuthorize("hasRole('ADMIN')")
    @Timed(value = "config.database", description = "Time taken to get database configuration")
    public Map<String, Object> getDatabaseInfo() {
        Map<String, Object> dbInfo = new HashMap<>();
        ProdocConfiguration.DatabaseConfig db = prodocConfig.getDatabase();
        
        dbInfo.put("driver", db.getDriverClassName());
        dbInfo.put("url", maskSensitiveUrl(db.getUrl()));
        dbInfo.put("username", db.getUsername());
        dbInfo.put("maxPoolSize", db.getMaxPoolSize());
        dbInfo.put("minIdle", db.getMinIdle());
        
        return dbInfo;
    }
    
    @GetMapping("/storage")
    @PreAuthorize("hasRole('ADMIN')")
    public Map<String, Object> getStorageInfo() {
        Map<String, Object> storageInfo = new HashMap<>();
        ProdocConfiguration.StorageConfig storage = prodocConfig.getStorage();
        
        storageInfo.put("type", storage.getType());
        
        if ("FILESYSTEM".equals(storage.getType())) {
            storageInfo.put("path", storage.getPath());
        } else if ("S3".equals(storage.getType())) {
            storageInfo.put("bucket", storage.getS3Bucket());
            storageInfo.put("region", storage.getS3Region());
        }
        
        return storageInfo;
    }
    
    @GetMapping("/security")
    @PreAuthorize("hasRole('ADMIN')")
    public Map<String, Object> getSecurityInfo() {
        Map<String, Object> securityInfo = new HashMap<>();
        ProdocConfiguration.SecurityConfig security = prodocConfig.getSecurity();
        
        securityInfo.put("authType", security.getAuthType());
        securityInfo.put("sessionTimeout", security.getSessionTimeout());
        securityInfo.put("jwtSecretConfigured", security.getJwtSecret() != null && !security.getJwtSecret().isEmpty());
        
        return securityInfo;
    }
    
    public Map<String, Object> getFullTextInfo() {
        Map<String, Object> ftInfo = new HashMap<>();
        ProdocConfiguration.FullTextConfig ft = prodocConfig.getFulltext();
        
        ftInfo.put("engine", ft.getEngine());
        ftInfo.put("indexPath", ft.getIndexPath());
        
        return ftInfo;
    }
    
    @Override
    public void contribute(Info.Builder builder) {
        builder.withDetail("openprodoc", getConfigInfo());
    }
    
    private String maskSensitiveUrl(String url) {
        if (url == null) return null;
        // Mask password in JDBC URL if present
        return url.replaceAll("password=[^&;]*", "password=***");
    }
}