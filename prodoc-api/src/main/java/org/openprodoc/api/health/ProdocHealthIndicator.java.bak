package org.openprodoc.api.health;

import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;
import javax.sql.DataSource;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;

@Component
public class ProdocHealthIndicator implements HealthIndicator {
    
    private final DataSource dataSource;
    
    public ProdocHealthIndicator(DataSource dataSource) {
        this.dataSource = dataSource;
    }
    
    @Override
    public Health health() {
        try {
            // Check database connectivity
            if (!isDatabaseHealthy()) {
                return Health.down()
                    .withDetail("database", "Unable to connect to database")
                    .build();
            }
            
            // Add more health checks as needed
            return Health.up()
                .withDetail("database", "Connected")
                .withDetail("status", "All systems operational")
                .build();
                
        } catch (Exception e) {
            return Health.down()
                .withDetail("error", e.getMessage())
                .build();
        }
    }
    
    private boolean isDatabaseHealthy() {
        try (Connection conn = dataSource.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT 1")) {
            return rs.next();
        } catch (Exception e) {
            return false;
        }
    }
}