#!/usr/bin/env python3
"""
Startup script for the complete AI Banking Agent integrated system
Coordinates all services: Database, Spring Boot API, AI Agent, Frontend
"""

import os
import sys
import subprocess
import time
import requests
import psycopg2
import threading
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_status(message, status="INFO"):
    color = {
        "INFO": Colors.OKBLUE,
        "SUCCESS": Colors.OKGREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "HEADER": Colors.HEADER
    }.get(status, Colors.OKBLUE)
    
    print(f"{color}{status}: {message}{Colors.ENDC}")

def check_database_connection():
    """Check if PostgreSQL database is accessible"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5433,
            database='my_finance_db',
            user='bank_database_admin',
            password='admin123'
        )
        conn.close()
        return True
    except Exception as e:
        print_status(f"Database connection failed: {e}", "ERROR")
        return False

def check_service(url, service_name, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print_status(f"{service_name} is running ✓", "SUCCESS")
            return True
        else:
            print_status(f"{service_name} responded with status {response.status_code}", "WARNING")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"{service_name} is not accessible: {e}", "ERROR")
        return False

def start_service_in_background(command, cwd, service_name):
    """Start a service in background"""
    try:
        print_status(f"Starting {service_name}...", "INFO")
        process = subprocess.Popen(
            command,
            cwd=cwd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process
    except Exception as e:
        print_status(f"Failed to start {service_name}: {e}", "ERROR")
        return None

def wait_for_service(url, service_name, max_wait=60):
    """Wait for a service to become available"""
    print_status(f"Waiting for {service_name} to start...", "INFO")
    
    for i in range(max_wait):
        if check_service(url, service_name, timeout=2):
            return True
        time.sleep(1)
        if i % 10 == 0 and i > 0:
            print_status(f"Still waiting for {service_name}... ({i}s)", "WARNING")
    
    print_status(f"{service_name} failed to start within {max_wait} seconds", "ERROR")
    return False

def main():
    print_status("🏦 AI Banking Agent - Integrated System Startup", "HEADER")
    print_status("=" * 60, "INFO")
    
    # Check prerequisites
    print_status("Checking prerequisites...", "INFO")
    
    # Check if database is running
    if not check_database_connection():
        print_status("Please ensure PostgreSQL database is running on localhost:5433", "ERROR")
        print_status("You can start it with: cd databaseService && docker-compose up -d", "INFO")
        return False
    
    print_status("Database connection ✓", "SUCCESS")
    
    # Check if required directories exist
    required_dirs = [
        "banking-api/demo",
        "logging",
        "finance_front_end"
    ]
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print_status(f"Required directory {dir_path} not found", "ERROR")
            return False
    
    print_status("Required directories found ✓", "SUCCESS")
    
    # Start services in sequence
    services = []
    
    # 1. Start Spring Boot Banking API
    print_status("Starting Spring Boot Banking API...", "INFO")
    spring_process = start_service_in_background(
        "./mvnw spring-boot:run",
        "banking-api/demo",
        "Spring Boot API"
    )
    if spring_process:
        services.append(("Spring Boot API", spring_process))
        
        # Wait for Spring Boot to start
        if not wait_for_service("http://localhost:8082/api/health", "Spring Boot API", 90):
            print_status("Spring Boot API failed to start. Check the logs.", "ERROR")
            return False
    
    # 2. Start AI Agent API Server
    print_status("Starting AI Agent API Server...", "INFO")
    ai_process = start_service_in_background(
        "python enhanced_api_server.py",
        "logging",
        "AI Agent API"
    )
    if ai_process:
        services.append(("AI Agent API", ai_process))
        
        # Wait for AI Agent to start
        if not wait_for_service("http://localhost:5001/api/health", "AI Agent API", 30):
            print_status("AI Agent API failed to start. Check if Ollama is running.", "WARNING")
    
    # 3. Start React Frontend
    print_status("Starting React Frontend...", "INFO")
    react_process = start_service_in_background(
        "npm start",
        "finance_front_end",
        "React Frontend"
    )
    if react_process:
        services.append(("React Frontend", react_process))
        
        # Wait for React to start
        if not wait_for_service("http://localhost:3000", "React Frontend", 60):
            print_status("React Frontend failed to start", "WARNING")
    
    # Final system check
    print_status("\n" + "=" * 60, "INFO")
    print_status("System Status Check", "HEADER")
    print_status("=" * 60, "INFO")
    
    services_status = [
        ("Database (PostgreSQL)", "http://localhost:5433", check_database_connection()),
        ("Banking API", "http://localhost:8082/api/health", check_service("http://localhost:8082/api/health", "Banking API")),
        ("AI Agent API", "http://localhost:5001/api/health", check_service("http://localhost:5001/api/health", "AI Agent API")),
        ("React Frontend", "http://localhost:3000", check_service("http://localhost:3000", "React Frontend"))
    ]
    
    all_running = True
    for service_name, url, status in services_status:
        status_text = "✓ Running" if status else "✗ Not Running"
        color = "SUCCESS" if status else "ERROR"
        print_status(f"{service_name:<20} {status_text}", color)
        if not status:
            all_running = False
    
    print_status("\n" + "=" * 60, "INFO")
    
    if all_running:
        print_status("🎉 All services are running successfully!", "SUCCESS")
        print_status("\nAccess URLs:", "HEADER")
        print_status("• Frontend: http://localhost:3000", "INFO")
        print_status("• Banking API: http://localhost:8082", "INFO")
        print_status("• AI Agent API: http://localhost:5001", "INFO")
        print_status("• AI Integration: http://localhost:8082/api/ai/*", "INFO")
        
        print_status("\n🤖 AI Agent Features:", "HEADER")
        print_status("• Real-time transaction analysis", "INFO")
        print_status("• Financial advice with actual spending data", "INFO")
        print_status("• Security threat detection for admins", "INFO")
        print_status("• Natural language chat interface", "INFO")
        print_status("• Database-integrated recommendations", "INFO")
        
        print_status("\nPress Ctrl+C to stop all services", "WARNING")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print_status("\nShutting down services...", "WARNING")
            for service_name, process in services:
                try:
                    process.terminate()
                    print_status(f"Stopped {service_name}", "INFO")
                except:
                    pass
    else:
        print_status("Some services failed to start. Please check the logs above.", "ERROR")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\nStartup interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        print_status(f"Startup failed: {e}", "ERROR")
        sys.exit(1)