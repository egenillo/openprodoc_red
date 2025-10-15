package com.openprodoc.dbcheck;

import java.sql.Connection;
import java.sql.DriverManager;

/**
 * Database Connection Test Utility for OpenProdoc
 *
 * This utility performs a simple JDBC connection test to verify database availability.
 * It is database-agnostic and works with any JDBC-compliant database.
 *
 * Exit codes:
 * 0 = Database is available and connection successful
 * 1 = Database is NOT available or connection failed
 * 2 = Invalid arguments
 */
public class DBConnectionTest {

    public static void main(String[] args) {
        if (args.length < 4) {
            System.err.println("Usage: DBConnectionTest <jdbcClass> <jdbcUrl> <user> <password>");
            System.exit(2);
        }

        String jdbcClass = args[0];
        String jdbcUrl = args[1];
        String user = args[2];
        String password = args[3];

        try {
            // Load JDBC driver
            Class.forName(jdbcClass);

            // Attempt to connect to database
            Connection conn = DriverManager.getConnection(jdbcUrl, user, password);

            // Execute a simple query to verify the connection works
            conn.createStatement().execute("SELECT 1");

            // Close connection
            conn.close();

            // Success - database is available
            System.exit(0);

        } catch (ClassNotFoundException e) {
            System.err.println("JDBC Driver not found: " + jdbcClass);
            System.exit(1);
        } catch (Exception e) {
            // Connection failed - database not available or credentials invalid
            System.exit(1);
        }
    }
}
