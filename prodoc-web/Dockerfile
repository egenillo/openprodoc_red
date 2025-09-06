FROM tomcat:9.0-jdk17-openjdk-slim

LABEL maintainer="OpenProdoc Red Team"
LABEL description="OpenProdoc Red Web Interface"
LABEL version="3.0.0"

# Create application user
RUN groupadd -g 1001 prodoc && \
    useradd -u 1001 -g prodoc -s /bin/bash -m prodoc

# Install required packages
RUN apt-get update && \
    apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Remove default Tomcat applications
RUN rm -rf /usr/local/tomcat/webapps/*

# Create necessary directories
RUN mkdir -p /usr/local/tomcat/webapps/web && \
    mkdir -p /app/logs && \
    chown -R prodoc:prodoc /usr/local/tomcat && \
    chown -R prodoc:prodoc /app

# Copy WAR file and extract it
COPY target/prodoc-web-*.war /tmp/prodoc-web.war
RUN cd /usr/local/tomcat/webapps/web && \
    jar -xf /tmp/prodoc-web.war && \
    rm /tmp/prodoc-web.war && \
    chown -R prodoc:prodoc /usr/local/tomcat/webapps/web

# Optimize static assets - compress CSS and JS
RUN find /usr/local/tomcat/webapps/web -name "*.css" -exec gzip -9 -k {} \; && \
    find /usr/local/tomcat/webapps/web -name "*.js" -exec gzip -9 -k {} \; && \
    find /usr/local/tomcat/webapps/web -name "*.html" -exec gzip -9 -k {} \;

# Configure Tomcat for production
COPY docker/server.xml /usr/local/tomcat/conf/server.xml
COPY docker/web.xml /usr/local/tomcat/webapps/web/WEB-INF/web.xml

# Switch to non-root user
USER prodoc

# Environment variables with defaults
ENV CATALINA_OPTS="-Xmx512m -Xms256m -Djava.awt.headless=true" \
    SPRING_PROFILES_ACTIVE="docker" \
    API_BASE_URL="http://prodoc-api:8080/api" \
    API_TIMEOUT="30000" \
    SERVER_PORT="8090" \
    LOG_LEVEL_ROOT="INFO"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8090/web/actuator/health || exit 1

# Expose port
EXPOSE 8090

# Start Tomcat
CMD ["catalina.sh", "run"]