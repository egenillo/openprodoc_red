FROM openjdk:17-jdk-alpine

LABEL maintainer="OpenProdoc Red Team"
LABEL description="OpenProdoc Red Core Engine + REST API"
LABEL version="3.0.0"

# Create application user
RUN addgroup -g 1001 -S prodoc && \
    adduser -u 1001 -S prodoc -G prodoc

# Install required packages
RUN apk add --no-cache \
    curl \
    bash \
    tzdata

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/storage /app/lucene /app/temp && \
    chown -R prodoc:prodoc /app

# Copy application JAR
COPY target/prodoc-api-*.jar /app/prodoc-api.jar
RUN chown prodoc:prodoc /app/prodoc-api.jar

# Switch to non-root user
USER prodoc

# Environment variables with defaults
ENV JAVA_OPTS="-Xmx512m -Xms256m" \
    SPRING_PROFILES_ACTIVE="docker" \
    DB_URL="jdbc:postgresql://postgres:5432/openprodoc" \
    DB_USERNAME="openprodoc" \
    DB_PASSWORD="" \
    DB_MAX_POOL_SIZE="20" \
    STORAGE_TYPE="FILESYSTEM" \
    STORAGE_PATH="/app/storage" \
    LOG_LEVEL_ROOT="INFO" \
    SERVER_PORT="8080"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/api/actuator/health || exit 1

# Expose port
EXPOSE 8080

# Entry point script
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/prodoc-api.jar"]