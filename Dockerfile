# Docker Compose Configuration
# docker-compose.yml

version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: banking-postgres
    environment:
      POSTGRES_DB: banking_db
      POSTGRES_USER: banking_user
      POSTGRES_PASSWORD: banking_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    networks:
      - banking-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U banking_user -d banking_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: banking-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - banking-network
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass redis_password
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Spring Boot Application
  banking-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: banking-api
    environment:
      # Database Configuration
      SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/banking_db
      SPRING_DATASOURCE_USERNAME: banking_user
      SPRING_DATASOURCE_PASSWORD: banking_password
      SPRING_JPA_HIBERNATE_DDL_AUTO: update
      SPRING_JPA_SHOW_SQL: false
      SPRING_JPA_PROPERTIES_HIBERNATE_DIALECT: org.hibernate.dialect.PostgreSQLDialect
      
      # Redis Configuration
      SPRING_REDIS_HOST: redis
      SPRING_REDIS_PORT: 6379
      SPRING_REDIS_PASSWORD: redis_password
      SPRING_CACHE_TYPE: redis
      
      # Application Configuration
      SERVER_PORT: 8080
      SPRING_PROFILES_ACTIVE: docker
      
      # Logging
      LOGGING_LEVEL_COM_BANKING_API: INFO
      LOGGING_LEVEL_ROOT: WARN
      
      # Security
      JWT_SECRET: mySecretKey123456789
      JWT_EXPIRATION: 86400000
      
    ports:
      - "8080:8080"
    networks:
      - banking-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  # Nginx Reverse Proxy (Optional)
  nginx:
    image: nginx:alpine
    container_name: banking-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - banking-network
    depends_on:
      - banking-api
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  banking-network:
    driver: bridge

---
# Dockerfile for Spring Boot Application

FROM openjdk:17-jdk-slim

# Set working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy Maven wrapper and pom.xml
COPY mvnw .
COPY .mvn .mvn
COPY pom.xml .

# Download dependencies
RUN chmod +x ./mvnw
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src ./src

# Build application
RUN ./mvnw clean package -DskipTests

# Create non-root user
RUN groupadd -r banking && useradd -r -g banking banking
RUN chown -R banking:banking /app
USER banking

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# Run application
ENTRYPOINT ["java", "-jar", "target/banking-api-1.0.0.jar"]

---
# application.yml for Spring Boot

spring:
  application:
    name: banking-api
  
  profiles:
    active: docker
  
  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://localhost:5432/banking_db}
    username: ${SPRING_DATASOURCE_USERNAME:banking_user}
    password: ${SPRING_DATASOURCE_PASSWORD:banking_password}
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 300000
      connection-timeout: 20000
      leak-detection-threshold: 60000
  
  jpa:
    hibernate:
      ddl-auto: ${SPRING_JPA_HIBERNATE_DDL_AUTO:update}
    show-sql: ${SPRING_JPA_SHOW_SQL:false}
    properties:
      hibernate:
        dialect: org.hibernate.dialect.PostgreSQLDialect
        format_sql: true
        jdbc:
          time_zone: UTC
        enable_lazy_load_no_trans: true
    open-in-view: false
  
  redis:
    host: ${SPRING_REDIS_HOST:localhost}
    port: ${SPRING_REDIS_PORT:6379}
    password: ${SPRING_REDIS_PASSWORD:redis_password}
    timeout: 2000ms
    lettuce:
      pool:
        max-active: 8
        max-idle
