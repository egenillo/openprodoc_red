package org.openprodoc.web.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import javax.annotation.PostConstruct;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

@Service
public class ProdocApiService {
    
    private static final Logger logger = LoggerFactory.getLogger(ProdocApiService.class);
    
    @Value("${openprodoc.api.base-url:http://localhost:8080/api}")
    private String apiBaseUrl;
    
    @Value("${openprodoc.api.timeout:30000}")
    private int timeout;
    
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    
    public ProdocApiService() {
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }
    
    @PostConstruct
    public void init() {
        logger.info("Initialized ProdocApiService with base URL: {}", apiBaseUrl);
    }
    
    /**
     * Authenticate user with prodoc-api
     */
    public AuthResult authenticate(String username, String password) {
        try {
            String url = apiBaseUrl + "/v1/auth/login";
            
            Map<String, String> loginRequest = new HashMap<>();
            loginRequest.put("username", username);
            loginRequest.put("password", password);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(loginRequest, headers);
            
            logger.debug("Authenticating user: {} at URL: {}", username, url);
            
            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            
            if (response.getStatusCode() == HttpStatus.OK) {
                JsonNode responseBody = objectMapper.readTree(response.getBody());
                
                if ("OK".equals(responseBody.path("Res").asText())) {
                    String token = responseBody.path("Token").asText();
                    logger.info("Authentication successful for user: {}", username);
                    return new AuthResult(true, token, null);
                } else {
                    String message = responseBody.path("Msg").asText("Authentication failed");
                    logger.warn("Authentication failed for user: {} - {}", username, message);
                    return new AuthResult(false, null, message);
                }
            } else {
                logger.warn("Authentication failed for user: {} - HTTP {}", username, response.getStatusCode());
                return new AuthResult(false, null, "Authentication service unavailable");
            }
            
        } catch (RestClientException e) {
            logger.error("REST client error during authentication for user: {} - {}", username, e.getMessage());
            return new AuthResult(false, null, "Unable to connect to authentication service");
        } catch (Exception e) {
            logger.error("Unexpected error during authentication for user: {} - {}", username, e.getMessage());
            return new AuthResult(false, null, "System error during authentication");
        }
    }
    
    /**
     * Get documents for authenticated user
     */
    public ApiResponse getDocuments(String token, int limit, int offset) {
        try {
            String url = apiBaseUrl + "/v1/documents?limit=" + limit + "&offset=" + offset;
            
            HttpHeaders headers = createAuthHeaders(token);
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);
            
            return new ApiResponse(response.getStatusCode() == HttpStatus.OK, response.getBody());
            
        } catch (Exception e) {
            logger.error("Error fetching documents: {}", e.getMessage());
            return new ApiResponse(false, "Error fetching documents: " + e.getMessage());
        }
    }
    
    /**
     * Get folders for authenticated user
     */
    public ApiResponse getFolders(String token, String parentId) {
        try {
            String url = apiBaseUrl + "/v1/folders";
            if (parentId != null && !parentId.isEmpty()) {
                url += "?parent=" + parentId;
            }
            
            HttpHeaders headers = createAuthHeaders(token);
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);
            
            return new ApiResponse(response.getStatusCode() == HttpStatus.OK, response.getBody());
            
        } catch (Exception e) {
            logger.error("Error fetching folders: {}", e.getMessage());
            return new ApiResponse(false, "Error fetching folders: " + e.getMessage());
        }
    }
    
    /**
     * Search documents and folders
     */
    public ApiResponse search(String token, String query, String type) {
        try {
            String url = apiBaseUrl + "/v1/search?q=" + query;
            if (type != null && !type.isEmpty()) {
                url += "&type=" + type;
            }
            
            HttpHeaders headers = createAuthHeaders(token);
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);
            
            return new ApiResponse(response.getStatusCode() == HttpStatus.OK, response.getBody());
            
        } catch (Exception e) {
            logger.error("Error searching: {}", e.getMessage());
            return new ApiResponse(false, "Error searching: " + e.getMessage());
        }
    }
    
    /**
     * Check API health
     */
    public boolean isApiHealthy() {
        try {
            String url = apiBaseUrl + "/actuator/health";
            ResponseEntity<String> response = restTemplate.getForEntity(url, String.class);
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            logger.warn("API health check failed: {}", e.getMessage());
            return false;
        }
    }
    
    private HttpHeaders createAuthHeaders(String token) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        if (token != null && !token.isEmpty()) {
            headers.set("Authorization", "Bearer " + token);
        }
        return headers;
    }
    
    // Result classes
    public static class AuthResult {
        private final boolean success;
        private final String token;
        private final String errorMessage;
        
        public AuthResult(boolean success, String token, String errorMessage) {
            this.success = success;
            this.token = token;
            this.errorMessage = errorMessage;
        }
        
        public boolean isSuccess() { return success; }
        public String getToken() { return token; }
        public String getErrorMessage() { return errorMessage; }
    }
    
    public static class ApiResponse {
        private final boolean success;
        private final String data;
        
        public ApiResponse(boolean success, String data) {
            this.success = success;
            this.data = data;
        }
        
        public boolean isSuccess() { return success; }
        public String getData() { return data; }
    }
}