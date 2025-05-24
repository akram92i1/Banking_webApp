# 🏦 Banking Platform Microservices

A scalable, secure, and containerized banking application built with a microservices architecture. This project is aimed at simulating a modern banking system with robust modular services.

---

## 🧱 Architecture Overview

This platform is designed with Docker and includes the following microservices:

- 🔐 **Authentication Service** – Handles user registration, login, and token-based authentication.
- 🌐 **Frontend Web App** – User-facing interface built with modern web technologies (e.g., React).
- ⚙️ **Banking API** – Core business logic for managing accounts, transactions, and operations (Spring Boot).
- 🗃️ **PostgreSQL Database** – Stores all persistent application data.
- ⚡ **Memcached** – Used for caching frequently accessed data.
- 📡 **Nginx** – Acts as a reverse proxy and load balancer.
- 📊 **Monitoring Service** – Prometheus/Grafana for monitoring system health and performance.
- 📜 **Logging Service** – ELK stack (Elasticsearch, Logstash, Kibana) for centralized logging.

---

## 📁 Project Structure

