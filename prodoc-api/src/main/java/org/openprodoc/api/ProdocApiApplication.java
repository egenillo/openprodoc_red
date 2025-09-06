package org.openprodoc.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.http.ResponseEntity;
import java.util.HashMap;
import java.util.Map;
import javax.annotation.PostConstruct;

@SpringBootApplication
@RestController
public class ProdocApiApplication {
    
    @Autowired(required = false)
    private JdbcTemplate jdbcTemplate;
    
    public static void main(String[] args) {
        SpringApplication.run(ProdocApiApplication.class, args);
    }
    
    @PostConstruct
    public void init() {
        System.out.println("OpenProdoc Red API Starting...");
        if (jdbcTemplate != null) {
            try {
                jdbcTemplate.execute("SELECT 1");
                System.out.println("Database connection successful!");
            } catch (Exception e) {
                System.out.println("Database connection failed: " + e.getMessage());
            }
        }
    }
    
    @GetMapping("/api")
    public ResponseEntity<Map<String, Object>> apiInfo() {
        Map<String, Object> info = new HashMap<>();
        info.put("application", "OpenProdoc Red Core Engine");
        info.put("version", "1.0");
        info.put("status", "Running");
        
        if (jdbcTemplate != null) {
            try {
                jdbcTemplate.queryForObject("SELECT 1", Integer.class);
                info.put("database", "Connected");
            } catch (Exception e) {
                info.put("database", "Error: " + e.getMessage());
            }
        } else {
            info.put("database", "Not configured");
        }
        
        return ResponseEntity.ok(info);
    }
    
    @GetMapping("/api/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "prodoc-api");
        return ResponseEntity.ok(health);
    }
}