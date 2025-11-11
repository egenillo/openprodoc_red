# OpenProdoc Database Check Utility

## Overview

This utility checks if OpenProdoc has been installed in the database by attempting to initialize the framework and obtain a session using the ProdocFW API.

## Purpose

The dbcheck utility is used by the core-engine Docker container to determine whether the database already contains OpenProdoc objects, avoiding redundant installations.

## How It Works

1. Initializes OpenProdoc framework using `ProdocFW.InitProdoc()`
2. Attempts to obtain a session using `ProdocFW.getSession()`
3. Returns exit codes based on the result:
   - **Exit 0**: OpenProdoc is installed (session obtained successfully)
   - **Exit 1**: OpenProdoc is NOT installed (needs installation)
   - **Exit 2**: Error occurred during check

## Building

### Prerequisites
- Java JDK 11 or higher
- Maven 3.6+
- Prodoc.jar from core-engine (must be built first)


## Usage

### Command Line

```bash
java -Dfile.encoding=UTF-8 \
  -classpath .:./lib:./lib/Prodoc.jar:ProdocDBCheck.jar:./lib/tika-app-1.26.jar:$JDBC_DRIVER_PATH \
  com.openprodoc.dbcheck.DBCheck [configPath] [user] [password]
```

### Parameters

- `configPath` (optional): Path to Prodoc.properties file (default: `/opt/openprodoc/Prodoc.properties`)
- `user` (optional): Username for login attempt (default: `root`)
- `password` (optional): Password for login attempt (default: `admin`)

### Example

```bash
# Check with defaults
java -cp .:lib/*:ProdocDBCheck.jar com.openprodoc.dbcheck.DBCheck

# Check with custom config
java -cp .:lib/*:ProdocDBCheck.jar com.openprodoc.dbcheck.DBCheck /custom/path/Prodoc.properties root mypassword
```

## Integration with Docker

The utility is integrated into the core-engine Docker entrypoint script:

```bash
# Run database check
if java -cp ... com.openprodoc.dbcheck.DBCheck; then
  echo "OpenProdoc already installed, skipping installation"
else
  echo "OpenProdoc not installed, running installation..."
  # Run Install.sh and Setup.sh
fi
```

## Development Notes

Based on OpenProdoc Developer Documentation Section 4.2.1:

- Uses `ProdocFW.InitProdoc()` to start the framework
- Uses `ProdocFW.getSession()` to authenticate and obtain a session
- Properly calls `ProdocFW.freeSesion()` and `ProdocFW.ShutdownProdoc()` for cleanup

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Installed | Skip installation |
| 1 | Not Installed | Run installation |
| 2 | Error | Review logs |
