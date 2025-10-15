package com.openprodoc.dbcheck;

import prodoc.DriverGeneric;
import prodoc.ProdocFW;

/**
 * Database Check Utility for OpenProdoc
 *
 * This utility checks if OpenProdoc has been installed in the database
 * by attempting to initialize the framework and obtain a session.
 *
 * Exit codes:
 * 0 = OpenProdoc is already installed (session obtained successfully)
 * 1 = OpenProdoc is NOT installed (needs installation)
 * 2 = Error occurred during check
 */
public class DBCheck {

    private static final String PRODOC_REF = "PD";
    private static final String DEFAULT_USER = "root";
    private static final String DEFAULT_PASSWORD = "admin";

    public static void main(String[] args) {
        String configPath = "/opt/openprodoc/Prodoc.properties";
        String user = DEFAULT_USER;
        String password = DEFAULT_PASSWORD;

        // Parse command line arguments
        if (args.length > 0) {
            configPath = args[0];
        }
        if (args.length > 1) {
            user = args[1];
        }
        if (args.length > 2) {
            password = args[2];
        }

        System.out.println("=== OpenProdoc Database Check ===");
        System.out.println("Config file: " + configPath);
        System.out.println("User: " + user);

        DriverGeneric session = null;
        try {
            // Initialize OpenProdoc framework
            System.out.println("Initializing OpenProdoc framework...");
            ProdocFW.InitProdoc(PRODOC_REF, configPath);
            System.out.println("Framework initialized successfully.");

            // Attempt to get a session
            System.out.println("Attempting to obtain session...");
            session = ProdocFW.getSession(PRODOC_REF, user, password);
            System.out.println("Session obtained successfully!");

            // If we got here, OpenProdoc is installed
            System.out.println("\n*** OpenProdoc is ALREADY INSTALLED ***");
            System.out.println("Database contains OpenProdoc objects.");
            System.out.println("Installation will be SKIPPED.");

            // Return session
            ProdocFW.freeSesion(PRODOC_REF, session);

            // Shutdown framework
            ProdocFW.ShutdownProdoc(PRODOC_REF);

            // Exit with code 0 (installed)
            System.exit(0);

        } catch (Exception e) {
            System.out.println("\n*** OpenProdoc is NOT INSTALLED ***");
            System.out.println("Reason: " + e.getMessage());
            System.out.println("Installation REQUIRED.");

            // Try to shutdown framework if it was initialized
            try {
                if (session != null) {
                    ProdocFW.freeSesion(PRODOC_REF, session);
                }
                ProdocFW.ShutdownProdoc(PRODOC_REF);
            } catch (Exception shutdownEx) {
                // Ignore shutdown errors
            }

            // Exit with code 1 (not installed - needs installation)
            System.exit(1);
        }
    }
}
