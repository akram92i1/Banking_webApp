#!/usr/bin/env python3
"""
Comprehensive test script for AI Banking Agent integration
Tests all endpoints and integration points
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BANKING_API = "http://localhost:8082"
AI_API = "http://localhost:5001"
FRONTEND = "http://localhost:3000"

# Test user credentials (you'll need to adjust these)
TEST_USER = {
    "email": "test@example.com",
    "password": "password123"
}

TEST_ADMIN = {
    "email": "admin@example.com", 
    "password": "admin123"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name, status="INFO"):
    colors = {"PASS": Colors.GREEN, "FAIL": Colors.RED, "INFO": Colors.BLUE, "WARN": Colors.YELLOW}
    color = colors.get(status, Colors.WHITE)
    print(f"{color}[{status}] {test_name}{Colors.ENDC}")

def test_service_health():
    """Test basic service health"""
    print_test("=== HEALTH CHECK TESTS ===", "INFO")
    
    services = [
        ("Frontend", FRONTEND),
        ("Banking API Health", f"{BANKING_API}/actuator/health"),
        ("Banking API AI Health", f"{BANKING_API}/api/ai/health"), 
        ("AI Agent Health", f"{AI_API}/api/health")
    ]
    
    results = []
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print_test(f"{name}: ✓ Running", "PASS")
                results.append(True)
            else:
                print_test(f"{name}: ✗ Status {response.status_code}", "FAIL")
                results.append(False)
        except Exception as e:
            print_test(f"{name}: ✗ Connection failed ({str(e)[:50]}...)", "FAIL")
            results.append(False)
    
    return all(results)

def get_auth_token(user_creds):
    """Get authentication token"""
    try:
        response = requests.post(f"{BANKING_API}/auth/signin", json=user_creds)
        if response.status_code == 200:
            data = response.json()
            return data.get('token') or data.get('accessToken')
        return None
    except Exception as e:
        print_test(f"Auth failed: {e}", "FAIL")
        return None

def test_ai_chat_integration():
    """Test AI chat through both APIs"""
    print_test("\n=== AI CHAT INTEGRATION TESTS ===", "INFO")
    
    # Test 1: Direct AI Agent Chat
    try:
        chat_data = {
            "message": "Hello! Can you help me analyze my spending?",
            "user_id": "test_user",
            "user_role": "user", 
            "location": "toronto"
        }
        
        response = requests.post(f"{AI_API}/api/chat", json=chat_data, timeout=15)
        if response.status_code == 200 and response.json().get('success'):
            print_test("Direct AI Chat: ✓ Working", "PASS")
        else:
            print_test(f"Direct AI Chat: ✗ Failed ({response.status_code})", "FAIL")
            
    except Exception as e:
        print_test(f"Direct AI Chat: ✗ Error ({str(e)[:50]}...)", "FAIL")
    
    # Test 2: Banking API Integration (requires auth)
    token = get_auth_token(TEST_USER)
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            chat_data = {
                "message": "What can you tell me about my recent spending?",
                "location": "toronto"
            }
            
            response = requests.post(f"{BANKING_API}/api/ai/chat", json=chat_data, headers=headers, timeout=15)
            if response.status_code == 200:
                print_test("Banking API AI Chat: ✓ Working", "PASS")
            else:
                print_test(f"Banking API AI Chat: ✗ Failed ({response.status_code})", "FAIL")
                
        except Exception as e:
            print_test(f"Banking API AI Chat: ✗ Error ({str(e)[:50]}...)", "FAIL")
    else:
        print_test("Banking API AI Chat: ✗ No auth token", "WARN")

def test_financial_advice():
    """Test financial advice functionality"""
    print_test("\n=== FINANCIAL ADVICE TESTS ===", "INFO")
    
    # Test 1: Direct AI Agent
    try:
        advice_data = {
            "user_id": "test_user",
            "location": "toronto",
            "spending_data": {
                "week1": 120.50,
                "week2": 145.30,
                "week3": 135.80,
                "week4": 160.20
            },
            "category": "grocery",
            "target_reduction": 30.00
        }
        
        response = requests.post(f"{AI_API}/api/user/financial-advice", json=advice_data, timeout=20)
        if response.status_code == 200 and response.json().get('success'):
            advice = response.json().get('advice', {})
            print_test(f"Direct Financial Advice: ✓ Generated ({len(advice.get('savings_suggestions', []))} suggestions)", "PASS")
        else:
            print_test("Direct Financial Advice: ✗ Failed", "FAIL")
            
    except Exception as e:
        print_test(f"Direct Financial Advice: ✗ Error ({str(e)[:50]}...)", "FAIL")
    
    # Test 2: Banking API Integration
    token = get_auth_token(TEST_USER)
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}"}
            advice_data = {"location": "toronto", "category": "grocery"}
            
            response = requests.post(f"{BANKING_API}/api/ai/financial-advice", json=advice_data, headers=headers, timeout=20)
            if response.status_code == 200:
                print_test("Banking API Financial Advice: ✓ Working with real data", "PASS")
            else:
                print_test(f"Banking API Financial Advice: ✗ Failed ({response.status_code})", "FAIL")
                
        except Exception as e:
            print_test(f"Banking API Financial Advice: ✗ Error ({str(e)[:50]}...)", "FAIL")
    else:
        print_test("Banking API Financial Advice: ✗ No auth token", "WARN")

def test_admin_features():
    """Test admin security features"""
    print_test("\n=== ADMIN SECURITY TESTS ===", "INFO")
    
    # Test 1: Security Dashboard
    try:
        response = requests.get(f"{AI_API}/api/admin/dashboard", timeout=15)
        if response.status_code == 200 and response.json().get('success'):
            dashboard = response.json().get('dashboard', {})
            print_test(f"Security Dashboard: ✓ Working (events: {dashboard.get('total_events_24h', 'N/A')})", "PASS")
        else:
            print_test("Security Dashboard: ✗ Failed", "FAIL")
            
    except Exception as e:
        print_test(f"Security Dashboard: ✗ Error ({str(e)[:50]}...)", "FAIL")
    
    # Test 2: Security Analysis
    admin_token = get_auth_token(TEST_ADMIN)
    if admin_token:
        try:
            headers = {"Authorization": f"Bearer {admin_token}"}
            analysis_data = {"location": "toronto"}
            
            response = requests.post(f"{BANKING_API}/api/ai/security-analysis", json=analysis_data, headers=headers, timeout=20)
            if response.status_code == 200:
                print_test("Admin Security Analysis: ✓ Working", "PASS")
            elif response.status_code == 403:
                print_test("Admin Security Analysis: ✗ Access denied (check admin role)", "WARN")
            else:
                print_test(f"Admin Security Analysis: ✗ Failed ({response.status_code})", "FAIL")
                
        except Exception as e:
            print_test(f"Admin Security Analysis: ✗ Error ({str(e)[:50]}...)", "FAIL")
    else:
        print_test("Admin Security Analysis: ✗ No admin token", "WARN")

def test_database_integration():
    """Test database connectivity through AI services"""
    print_test("\n=== DATABASE INTEGRATION TESTS ===", "INFO")
    
    # Test through AI health endpoint
    try:
        response = requests.get(f"{AI_API}/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            db_status = health_data.get('database_status', 'unknown')
            if db_status == 'connected':
                print_test("AI Agent DB Connection: ✓ Connected", "PASS")
            else:
                print_test(f"AI Agent DB Connection: ✗ Status: {db_status}", "FAIL")
        else:
            print_test("AI Agent DB Connection: ✗ Health check failed", "FAIL")
            
    except Exception as e:
        print_test(f"AI Agent DB Connection: ✗ Error ({str(e)[:50]}...)", "FAIL")
    
    # Test spending analysis (requires real data)
    try:
        analysis_data = {"user_id": "test_user", "transactions": []}
        response = requests.post(f"{AI_API}/api/user/spending-analysis", json=analysis_data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            data_source = result.get('data_source', 'unknown')
            print_test(f"Spending Analysis: ✓ Working (source: {data_source})", "PASS")
        elif response.status_code == 404:
            print_test("Spending Analysis: ⚠ No transaction data found", "WARN")
        else:
            print_test(f"Spending Analysis: ✗ Failed ({response.status_code})", "FAIL")
            
    except Exception as e:
        print_test(f"Spending Analysis: ✗ Error ({str(e)[:50]}...)", "FAIL")

def test_grocery_deals():
    """Test grocery deals functionality"""
    print_test("\n=== GROCERY DEALS TESTS ===", "INFO")
    
    locations = ["toronto", "montreal", "vancouver"]
    
    for location in locations:
        try:
            response = requests.get(f"{AI_API}/api/grocery-deals/{location}", timeout=10)
            if response.status_code == 200:
                deals_data = response.json()
                deals_count = len(deals_data.get('deals', []))
                print_test(f"Grocery Deals ({location}): ✓ {deals_count} deals found", "PASS")
            else:
                print_test(f"Grocery Deals ({location}): ✗ Failed", "FAIL")
                
        except Exception as e:
            print_test(f"Grocery Deals ({location}): ✗ Error ({str(e)[:30]}...)", "FAIL")

def run_performance_test():
    """Test response times"""
    print_test("\n=== PERFORMANCE TESTS ===", "INFO")
    
    endpoints = [
        ("Health Check", f"{AI_API}/api/health", "GET"),
        ("Chat", f"{AI_API}/api/chat", "POST", {"message": "Hello", "user_id": "test", "user_role": "user"}),
        ("Grocery Deals", f"{AI_API}/api/grocery-deals/toronto", "GET")
    ]
    
    for name, url, method, *data in endpoints:
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=data[0] if data else {}, timeout=15)
            
            elapsed = (time.time() - start_time) * 1000  # Convert to ms
            
            if response.status_code == 200:
                if elapsed < 1000:
                    print_test(f"{name}: ✓ {elapsed:.0f}ms (Fast)", "PASS")
                elif elapsed < 5000:
                    print_test(f"{name}: ✓ {elapsed:.0f}ms (OK)", "PASS") 
                else:
                    print_test(f"{name}: ⚠ {elapsed:.0f}ms (Slow)", "WARN")
            else:
                print_test(f"{name}: ✗ Failed ({response.status_code})", "FAIL")
                
        except Exception as e:
            print_test(f"{name}: ✗ Error ({str(e)[:30]}...)", "FAIL")

def main():
    print_test(f"\n🤖 AI Banking Agent Integration Test Suite", "INFO")
    print_test(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    print_test("=" * 60, "INFO")
    
    # Run all test suites
    overall_health = test_service_health()
    
    if overall_health:
        print_test("✓ All services running - proceeding with integration tests\n", "PASS")
        
        test_ai_chat_integration()
        test_financial_advice() 
        test_admin_features()
        test_database_integration()
        test_grocery_deals()
        run_performance_test()
        
        print_test("\n" + "=" * 60, "INFO")
        print_test("🎉 Integration test suite completed!", "INFO") 
        print_test("Review the results above to identify any issues.", "INFO")
        print_test("✅ PASS = Working correctly", "PASS")
        print_test("⚠ WARN = Working with limitations", "WARN") 
        print_test("✗ FAIL = Needs attention", "FAIL")
        
    else:
        print_test("✗ Some services are not running - please start them first", "FAIL")
        print_test("Run: python start_integrated_system.py", "INFO")

if __name__ == "__main__":
    main()