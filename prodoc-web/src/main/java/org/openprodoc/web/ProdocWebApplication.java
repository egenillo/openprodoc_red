package org.openprodoc.web;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@SpringBootApplication
@RestController
public class ProdocWebApplication extends SpringBootServletInitializer {
    
    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(ProdocWebApplication.class);
    }
    
    public static void main(String[] args) {
        SpringApplication.run(ProdocWebApplication.class, args);
    }

    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "UP");
        health.put("service", "prodoc-web");
        health.put("version", "1.0");
        health.put("timestamp", System.currentTimeMillis());
        return health;
    }

    @GetMapping("/")
    public Map<String, Object> home() {
        Map<String, Object> info = new HashMap<>();
        info.put("application", "OpenProdoc Red Web Interface");
        info.put("version", "1.0");
        info.put("status", "Running");
        info.put("apiUrl", System.getenv("API_BASE_URL"));
        return info;
    }
}