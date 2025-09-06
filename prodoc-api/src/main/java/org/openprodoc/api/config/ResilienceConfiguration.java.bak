package org.openprodoc.api.config;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import io.github.resilience4j.timelimiter.TimeLimiter;
import io.github.resilience4j.timelimiter.TimeLimiterConfig;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.sql.SQLException;
import java.sql.SQLTransientException;
import java.time.Duration;
import java.util.concurrent.TimeoutException;

@Configuration
@ConfigurationProperties(prefix = "openprodoc.resilience")
public class ResilienceConfiguration {
    
    private static final Logger logger = LoggerFactory.getLogger(ResilienceConfiguration.class);
    
    // Circuit Breaker configuration
    private int circuitBreakerFailureThreshold = 5;
    private int circuitBreakerSlowCallThreshold = 10;
    private Duration circuitBreakerSlowCallDuration = Duration.ofSeconds(5);
    private Duration circuitBreakerWaitDurationInOpenState = Duration.ofSeconds(30);
    private int circuitBreakerPermittedCallsInHalfOpenState = 3;
    private int circuitBreakerSlidingWindowSize = 10;
    
    // Retry configuration
    private int retryMaxAttempts = 3;
    private Duration retryWaitDuration = Duration.ofSeconds(2);
    private double retryExponentialBackoffMultiplier = 2.0;
    
    // Time limiter configuration
    private Duration timeLimiterTimeout = Duration.ofSeconds(10);
    
    @Bean
    public CircuitBreaker databaseCircuitBreaker() {
        logger.info("Configuring database circuit breaker with failure threshold: {}", circuitBreakerFailureThreshold);
        
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(50) // 50% failure rate threshold
            .slowCallRateThreshold(50) // 50% slow call rate threshold
            .waitDurationInOpenState(circuitBreakerWaitDurationInOpenState)
            .slowCallDurationThreshold(circuitBreakerSlowCallDuration)
            .permittedNumberOfCallsInHalfOpenState(circuitBreakerPermittedCallsInHalfOpenState)
            .minimumNumberOfCalls(circuitBreakerFailureThreshold)
            .slidingWindowSize(circuitBreakerSlidingWindowSize)
            .recordExceptions(
                SQLException.class,
                SQLTransientException.class,
                TimeoutException.class,
                RuntimeException.class
            )
            .ignoreExceptions(
                IllegalArgumentException.class,
                IllegalStateException.class
            )
            .build();
        
        CircuitBreaker circuitBreaker = CircuitBreaker.of("database", config);
        
        // Add event listeners for monitoring
        circuitBreaker.getEventPublisher()
            .onStateTransition(event -> 
                logger.warn("Database circuit breaker state transition: {} -> {}", 
                    event.getStateTransition().getFromState(), 
                    event.getStateTransition().getToState()));
        
        circuitBreaker.getEventPublisher()
            .onCallNotPermitted(event -> 
                logger.error("Database circuit breaker call not permitted - circuit is OPEN"));
        
        circuitBreaker.getEventPublisher()
            .onFailureRateExceeded(event ->
                logger.error("Database circuit breaker failure rate exceeded: {}%", 
                    event.getFailureRate()));
        
        return circuitBreaker;
    }
    
    @Bean
    public Retry databaseRetry() {
        logger.info("Configuring database retry with max attempts: {} and wait duration: {}", 
                   retryMaxAttempts, retryWaitDuration);
        
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(retryMaxAttempts)
            .waitDuration(retryWaitDuration)
            .exponentialBackoffMultiplier(retryExponentialBackoffMultiplier)
            .retryOnException(throwable -> {
                // Retry on specific database-related exceptions
                if (throwable instanceof SQLException) {
                    SQLException sqlEx = (SQLException) throwable;
                    String sqlState = sqlEx.getSQLState();
                    
                    // PostgreSQL connection errors that should trigger retry
                    return sqlState != null && (
                        sqlState.startsWith("08") ||  // Connection exception
                        sqlState.startsWith("53") ||  // Insufficient resources
                        sqlState.equals("57P03") ||   // Cannot connect now
                        sqlState.equals("40001")      // Serialization failure
                    );
                }
                
                // Retry on transient exceptions
                return throwable instanceof SQLTransientException ||
                       throwable instanceof TimeoutException;
            })
            .build();
        
        Retry retry = Retry.of("database", config);
        
        // Add event listeners
        retry.getEventPublisher()
            .onRetry(event -> 
                logger.warn("Database operation retry attempt {}/{}: {}", 
                    event.getNumberOfRetryAttempts(),
                    retryMaxAttempts,
                    event.getLastThrowable().getMessage()));
        
        retry.getEventPublisher()
            .onError(event ->
                logger.error("Database operation failed after {} retry attempts: {}", 
                    event.getNumberOfRetryAttempts(),
                    event.getLastThrowable().getMessage()));
        
        return retry;
    }
    
    @Bean
    public TimeLimiter databaseTimeLimiter() {
        logger.info("Configuring database time limiter with timeout: {}", timeLimiterTimeout);
        
        TimeLimiterConfig config = TimeLimiterConfig.custom()
            .timeoutDuration(timeLimiterTimeout)
            .cancelRunningFuture(true)
            .build();
        
        return TimeLimiter.of("database", config);
    }
    
    // Circuit breaker for external API calls
    @Bean
    public CircuitBreaker externalApiCircuitBreaker() {
        CircuitBreakerConfig config = CircuitBreakerConfig.custom()
            .failureRateThreshold(60) // Higher threshold for external APIs
            .slowCallRateThreshold(80)
            .waitDurationInOpenState(Duration.ofMinutes(1)) // Longer wait for external APIs
            .slowCallDurationThreshold(Duration.ofSeconds(10))
            .permittedNumberOfCallsInHalfOpenState(2)
            .minimumNumberOfCalls(3)
            .slidingWindowSize(8)
            .build();
        
        CircuitBreaker circuitBreaker = CircuitBreaker.of("external-api", config);
        
        circuitBreaker.getEventPublisher()
            .onStateTransition(event -> 
                logger.info("External API circuit breaker state transition: {} -> {}", 
                    event.getStateTransition().getFromState(), 
                    event.getStateTransition().getToState()));
        
        return circuitBreaker;
    }
    
    // Retry for external API calls
    @Bean
    public Retry externalApiRetry() {
        RetryConfig config = RetryConfig.custom()
            .maxAttempts(2) // Fewer retries for external APIs
            .waitDuration(Duration.ofSeconds(5))
            .exponentialBackoffMultiplier(1.5)
            .retryOnException(throwable -> {
                // Retry on network-related exceptions
                return throwable instanceof java.net.SocketTimeoutException ||
                       throwable instanceof java.net.ConnectException ||
                       throwable instanceof java.io.IOException;
            })
            .build();
        
        Retry retry = Retry.of("external-api", config);
        
        retry.getEventPublisher()
            .onRetry(event -> 
                logger.warn("External API retry attempt {}: {}", 
                    event.getNumberOfRetryAttempts(),
                    event.getLastThrowable().getMessage()));
        
        return retry;
    }
    
    // Getters and setters for configuration properties
    public int getCircuitBreakerFailureThreshold() { return circuitBreakerFailureThreshold; }
    public void setCircuitBreakerFailureThreshold(int circuitBreakerFailureThreshold) { 
        this.circuitBreakerFailureThreshold = circuitBreakerFailureThreshold; 
    }
    
    public int getCircuitBreakerSlowCallThreshold() { return circuitBreakerSlowCallThreshold; }
    public void setCircuitBreakerSlowCallThreshold(int circuitBreakerSlowCallThreshold) { 
        this.circuitBreakerSlowCallThreshold = circuitBreakerSlowCallThreshold; 
    }
    
    public Duration getCircuitBreakerSlowCallDuration() { return circuitBreakerSlowCallDuration; }
    public void setCircuitBreakerSlowCallDuration(Duration circuitBreakerSlowCallDuration) { 
        this.circuitBreakerSlowCallDuration = circuitBreakerSlowCallDuration; 
    }
    
    public Duration getCircuitBreakerWaitDurationInOpenState() { return circuitBreakerWaitDurationInOpenState; }
    public void setCircuitBreakerWaitDurationInOpenState(Duration circuitBreakerWaitDurationInOpenState) { 
        this.circuitBreakerWaitDurationInOpenState = circuitBreakerWaitDurationInOpenState; 
    }
    
    public int getCircuitBreakerPermittedCallsInHalfOpenState() { return circuitBreakerPermittedCallsInHalfOpenState; }
    public void setCircuitBreakerPermittedCallsInHalfOpenState(int circuitBreakerPermittedCallsInHalfOpenState) { 
        this.circuitBreakerPermittedCallsInHalfOpenState = circuitBreakerPermittedCallsInHalfOpenState; 
    }
    
    public int getCircuitBreakerSlidingWindowSize() { return circuitBreakerSlidingWindowSize; }
    public void setCircuitBreakerSlidingWindowSize(int circuitBreakerSlidingWindowSize) { 
        this.circuitBreakerSlidingWindowSize = circuitBreakerSlidingWindowSize; 
    }
    
    public int getRetryMaxAttempts() { return retryMaxAttempts; }
    public void setRetryMaxAttempts(int retryMaxAttempts) { 
        this.retryMaxAttempts = retryMaxAttempts; 
    }
    
    public Duration getRetryWaitDuration() { return retryWaitDuration; }
    public void setRetryWaitDuration(Duration retryWaitDuration) { 
        this.retryWaitDuration = retryWaitDuration; 
    }
    
    public double getRetryExponentialBackoffMultiplier() { return retryExponentialBackoffMultiplier; }
    public void setRetryExponentialBackoffMultiplier(double retryExponentialBackoffMultiplier) { 
        this.retryExponentialBackoffMultiplier = retryExponentialBackoffMultiplier; 
    }
    
    public Duration getTimeLimiterTimeout() { return timeLimiterTimeout; }
    public void setTimeLimiterTimeout(Duration timeLimiterTimeout) { 
        this.timeLimiterTimeout = timeLimiterTimeout; 
    }
}