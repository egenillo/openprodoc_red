package org.openprodoc.api.service;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.decorators.Decorators;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.timelimiter.TimeLimiter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.dao.DataAccessException;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.function.Supplier;

@Service
public class ResilientDatabaseService {
    
    private static final Logger logger = LoggerFactory.getLogger(ResilientDatabaseService.class);
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Autowired
    @Qualifier("databaseCircuitBreaker")
    private CircuitBreaker circuitBreaker;
    
    @Autowired
    @Qualifier("databaseRetry")
    private Retry retry;
    
    @Autowired
    @Qualifier("databaseTimeLimiter")
    private TimeLimiter timeLimiter;
    
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    
    /**
     * Execute a database query with full resilience patterns applied
     */
    public <T> T executeResilientQuery(Supplier<T> querySupplier, T fallbackValue) {
        try {
            Supplier<CompletableFuture<T>> futureSupplier = () -> 
                CompletableFuture.supplyAsync(querySupplier, scheduler);
            
            Supplier<CompletableFuture<T>> decoratedSupplier = Decorators
                .ofSupplier(futureSupplier)
                .withTimeLimiter(timeLimiter, scheduler)
                .withCircuitBreaker(circuitBreaker)
                .withRetry(retry)
                .decorate();
            
            return decoratedSupplier.get().join();
            
        } catch (Exception e) {
            logger.error("Resilient database query failed, returning fallback value", e);
            return fallbackValue;
        }
    }
    
    /**
     * Execute a database update with resilience patterns
     */
    public boolean executeResilientUpdate(Supplier<Integer> updateSupplier) {
        try {
            Supplier<CompletableFuture<Integer>> futureSupplier = () -> 
                CompletableFuture.supplyAsync(updateSupplier, scheduler);
            
            Supplier<CompletableFuture<Integer>> decoratedSupplier = Decorators
                .ofSupplier(futureSupplier)
                .withTimeLimiter(timeLimiter, scheduler)
                .withCircuitBreaker(circuitBreaker)
                .withRetry(retry)
                .decorate();
            
            Integer result = decoratedSupplier.get().join();
            return result != null && result > 0;
            
        } catch (Exception e) {
            logger.error("Resilient database update failed", e);
            return false;
        }
    }
    
    /**
     * Test database connectivity with resilience
     */
    public boolean testConnection() {
        return executeResilientQuery(() -> {
            try {
                Integer result = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
                return result != null && result.equals(1);
            } catch (DataAccessException e) {
                logger.warn("Database connectivity test failed", e);
                throw new RuntimeException("Database connectivity test failed", e);
            }
        }, false);
    }
    
    /**
     * Get database connection count with resilience
     */
    public int getActiveConnectionCount() {
        return executeResilientQuery(() -> {
            try {
                return jdbcTemplate.queryForObject(
                    "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'", 
                    Integer.class);
            } catch (DataAccessException e) {
                logger.warn("Failed to get active connection count", e);
                throw new RuntimeException("Failed to get connection count", e);
            }
        }, -1);
    }
    
    /**
     * Get system configuration with resilience
     */
    public String getSystemConfig(String configKey) {
        return executeResilientQuery(() -> {
            try {
                return jdbcTemplate.queryForObject(
                    "SELECT config_value FROM opd_core.pd_config WHERE config_key = ?", 
                    String.class, configKey);
            } catch (DataAccessException e) {
                logger.warn("Failed to get system config for key: {}", configKey, e);
                throw new RuntimeException("Failed to get system config", e);
            }
        }, null);
    }
    
    /**
     * Update system configuration with resilience
     */
    public boolean updateSystemConfig(String configKey, String configValue) {
        return executeResilientUpdate(() -> {
            try {
                return jdbcTemplate.update(
                    "UPDATE opd_core.pd_config SET config_value = ?, updated_at = CURRENT_TIMESTAMP WHERE config_key = ?",
                    configValue, configKey);
            } catch (DataAccessException e) {
                logger.error("Failed to update system config for key: {}", configKey, e);
                throw new RuntimeException("Failed to update system config", e);
            }
        });
    }
    
    /**
     * Get document count with resilience
     */
    public long getDocumentCount() {
        return executeResilientQuery(() -> {
            try {
                Long count = jdbcTemplate.queryForObject(
                    "SELECT count(*) FROM opd_docs.pd_documents WHERE active = true", 
                    Long.class);
                return count != null ? count : 0L;
            } catch (DataAccessException e) {
                logger.warn("Failed to get document count", e);
                throw new RuntimeException("Failed to get document count", e);
            }
        }, 0L);
    }
    
    /**
     * Check if user exists with resilience
     */
    public boolean userExists(String username) {
        return executeResilientQuery(() -> {
            try {
                Integer count = jdbcTemplate.queryForObject(
                    "SELECT count(*) FROM opd_core.pd_users WHERE user_name = ? AND active = true", 
                    Integer.class, username);
                return count != null && count > 0;
            } catch (DataAccessException e) {
                logger.warn("Failed to check if user exists: {}", username, e);
                throw new RuntimeException("Failed to check user existence", e);
            }
        }, false);
    }
    
    /**
     * Record audit log entry with resilience
     */
    public boolean recordAuditLog(String actionType, String resourceType, String resourceId, 
                                  String username, String details) {
        return executeResilientUpdate(() -> {
            try {
                return jdbcTemplate.update(
                    "INSERT INTO opd_admin.pd_audit_log (action_type, resource_type, resource_id, user_name, details) VALUES (?, ?, ?, ?, ?::jsonb)",
                    actionType, resourceType, resourceId, username, details);
            } catch (DataAccessException e) {
                logger.error("Failed to record audit log entry", e);
                throw new RuntimeException("Failed to record audit log", e);
            }
        });
    }
    
    /**
     * Clean up expired sessions with resilience
     */
    public int cleanupExpiredSessions() {
        return executeResilientQuery(() -> {
            try {
                return jdbcTemplate.update(
                    "DELETE FROM opd_core.pd_sessions WHERE expires_at < CURRENT_TIMESTAMP OR (last_access < CURRENT_TIMESTAMP - INTERVAL '24 hours' AND active = false)");
            } catch (DataAccessException e) {
                logger.error("Failed to cleanup expired sessions", e);
                throw new RuntimeException("Failed to cleanup sessions", e);
            }
        }, 0);
    }
    
    /**
     * Get circuit breaker state for monitoring
     */
    public String getCircuitBreakerState() {
        return circuitBreaker.getState().toString();
    }
    
    /**
     * Get circuit breaker metrics
     */
    public CircuitBreaker.Metrics getCircuitBreakerMetrics() {
        return circuitBreaker.getMetrics();
    }
    
    /**
     * Get retry metrics
     */
    public Retry.Metrics getRetryMetrics() {
        return retry.getMetrics();
    }
    
    /**
     * Force circuit breaker to open state (for testing)
     */
    public void forceCircuitBreakerOpen() {
        circuitBreaker.transitionToOpenState();
        logger.warn("Circuit breaker forced to OPEN state");
    }
    
    /**
     * Force circuit breaker to closed state
     */
    public void forceCircuitBreakerClosed() {
        circuitBreaker.transitionToClosedState();
        logger.info("Circuit breaker forced to CLOSED state");
    }
    
    /**
     * Shutdown the scheduler
     */
    public void shutdown() {
        scheduler.shutdown();
    }
}