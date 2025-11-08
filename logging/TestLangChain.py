from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import json

# --- 1. Define Log Data ---
log_data = [
    # MALICIOUS SCENARIOS (1-20)
    
    # 1. Credential Stuffing Attack
    {
        "timestamp": "2025-02-01T03:15:22",
        "source_ip": "45.142.212.61",
        "user_id": "john.smith@company.com",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=john.smith@company.com&password=Summer2023!",
        "status_code": 401,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T03:15:23",
        "source_ip": "45.142.212.61",
        "user_id": "sarah.jones@company.com",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=sarah.jones@company.com&password=Welcome123",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T03:15:24",
        "source_ip": "45.142.212.61",
        "user_id": "mike.wilson@company.com",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=mike.wilson@company.com&password=Password2023",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "label": "malicious"
    },
    
    # 2. Brute Force Attack
    {
        "timestamp": "2025-02-01T08:22:10",
        "source_ip": "203.0.113.45",
        "user_id": "admin",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=admin&password=admin123",
        "status_code": 401,
        "user_agent": "Python-requests/2.28.0",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T08:22:11",
        "source_ip": "203.0.113.45",
        "user_id": "admin",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=admin&password=password123",
        "status_code": 401,
        "user_agent": "Python-requests/2.28.0",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T08:22:12",
        "source_ip": "203.0.113.45",
        "user_id": "admin",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=admin&password=123456",
        "status_code": 401,
        "user_agent": "Python-requests/2.28.0",
        "label": "malicious"
    },
    
    # 3. SQL Injection Authentication Bypass
    {
        "timestamp": "2025-02-01T11:45:33",
        "source_ip": "185.220.101.23",
        "user_id": "admin'--",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=admin'--&password=anything",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T11:45:35",
        "source_ip": "185.220.101.23",
        "user_id": "' OR '1'='1",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=' OR '1'='1&password=' OR '1'='1",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64)",
        "label": "malicious"
    },
    
    # 4. Password Spraying
    {
        "timestamp": "2025-02-01T14:10:05",
        "source_ip": "91.198.174.192",
        "user_id": "alice.brown@company.com",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=alice.brown@company.com&password=Winter2024!",
        "status_code": 401,
        "user_agent": "curl/7.68.0",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T14:10:07",
        "source_ip": "91.198.174.192",
        "user_id": "bob.taylor@company.com",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=bob.taylor@company.com&password=Winter2024!",
        "status_code": 401,
        "user_agent": "curl/7.68.0",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T14:10:09",
        "source_ip": "91.198.174.192",
        "user_id": "carol.davis@company.com",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=carol.davis@company.com&password=Winter2024!",
        "status_code": 200,
        "user_agent": "curl/7.68.0",
        "label": "malicious"
    },
    
    # 5. Session Hijacking
    {
        "timestamp": "2025-02-01T09:30:15",
        "source_ip": "192.168.1.100",
        "user_id": "employee_456",
        "endpoint": "/dashboard",
        "method": "GET",
        "payload": "session_id=a3f7b2c9d4e5f6g7h8i9j0k1",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0",
        "label": "normal"
    },
    {
        "timestamp": "2025-02-01T09:32:45",
        "source_ip": "103.251.167.22",
        "user_id": "employee_456",
        "endpoint": "/api/transfer",
        "method": "POST",
        "payload": "session_id=a3f7b2c9d4e5f6g7h8i9j0k1&amount=50000",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (Linux; Android 10) Chrome/118.0",
        "label": "malicious"
    },
    
    # 6. Token Replay Attack
    {
        "timestamp": "2025-02-01T16:20:30",
        "source_ip": "198.51.100.88",
        "user_id": "user_789",
        "endpoint": "/api/profile",
        "method": "GET",
        "payload": "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired",
        "status_code": 200,
        "user_agent": "Postman/10.0",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T16:25:10",
        "source_ip": "198.51.100.88",
        "user_id": "user_789",
        "endpoint": "/api/profile",
        "method": "GET",
        "payload": "token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.expired",
        "status_code": 200,
        "user_agent": "Postman/10.0",
        "label": "malicious"
    },
    
    # 7. MFA Bypass Attempt
    {
        "timestamp": "2025-02-01T10:15:20",
        "source_ip": "167.172.58.144",
        "user_id": "manager_321",
        "endpoint": "/auth/login",
        "method": "POST",
        "payload": "username=manager_321&password=CorrectPassword123",
        "status_code": 302,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "label": "normal"
    },
    {
        "timestamp": "2025-02-01T10:15:21",
        "source_ip": "167.172.58.144",
        "user_id": "manager_321",
        "endpoint": "/api/dashboard",
        "method": "GET",
        "payload": "skip_mfa=true",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "label": "malicious"
    },
    
    # 8. Account Enumeration
    {
        "timestamp": "2025-02-01T13:05:01",
        "source_ip": "104.244.72.89",
        "user_id": "test001@company.com",
        "endpoint": "/auth/forgot-password",
        "method": "POST",
        "payload": "email=test001@company.com",
        "status_code": 404,
        "user_agent": "Python-urllib/3.9",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T13:05:02",
        "source_ip": "104.244.72.89",
        "user_id": "test002@company.com",
        "endpoint": "/auth/forgot-password",
        "method": "POST",
        "payload": "email=test002@company.com",
        "status_code": 404,
        "user_agent": "Python-urllib/3.9",
        "label": "malicious"
    },
    {
        "timestamp": "2025-02-01T13:05:03",
        "source_ip": "104.244.72.89",
        "user_id": "admin@company.com",
        "endpoint": "/auth/forgot-password",
        "method": "POST",
        "payload": "email=admin@company.com",
        "status_code": 200,
        "user_agent": "Python-urllib/3.9",
        "label": "malicious"
    },
    
    # 9. Privilege Escalation
    {
        "timestamp": "2025-02-01T15:40:12",
        "source_ip": "172.16.0.55",
        "user_id": "regular_user_99",
        "endpoint": "/admin/users/delete",
        "method": "DELETE",
        "payload": "user_id=123&role=admin",
        "status_code": 403,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "label": "normal"
    },
    {
        "timestamp": "2025-02-01T15:40:15",
        "source_ip": "172.16.0.55",
        "user_id": "regular_user_99",
        "endpoint": "/admin/users/delete",
        "method": "DELETE",
        "payload": "user_id=123&role=admin&bypass=true",
        "status_code": 200,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "label": "malicious"
    },
    
    # 10. API Key Abuse
    {
        "timestamp": "2025-02-01T18:25:33",
        "source_ip": "159.89.145.200",
        "user_id": "api_user_external",
        "endpoint": "/api/v1/data/export",
        "method": "GET",
        "payload": "api_key=sk_live_stolen_key_12345&limit=999999",
        "status_code": 200,
        "user_agent": "Go-http-client/2.0",
        "label": "malicious"
    }
]

# Convert the list of dictionaries into a formatted JSON string for better readability
log_text = json.dumps(log_data, indent=2)

# --- 2. Initialize Model with Optimizations ---
llm = ChatOllama(
    model="mistral:7b-instruct-v0.2-q4_K_M", 
    temperature=0.2,      # Slightly higher for more detailed responses
    keep_alive=-1,        # Keep model loaded
    num_ctx=4096,         # Increased context window for detailed analysis
    num_predict=2048      # Allow longer responses
)

# --- 3. Enhanced Prompt Template with Detailed Instructions ---
ENHANCED_ANALYSIS_PROMPT = PromptTemplate.from_template(
    """You are an elite cybersecurity analyst with expertise in threat detection, incident response, and forensic analysis. 
Your task is to perform a COMPREHENSIVE and DETAILED security analysis of the provided authentication log data.

ANALYSIS REQUIREMENTS:
Analyze the logs for ALL of the following threat categories and provide DETAILED findings:

1. **CREDENTIAL ATTACKS**
   - Brute force attempts (rapid sequential login failures)
   - Credential stuffing (multiple accounts from same IP)
   - Password spraying (same password across multiple accounts)
   - Provide: Attack pattern, timeline, affected accounts, success rate

2. **INJECTION ATTACKS**
   - SQL injection patterns in user_id or payload fields
   - Command injection attempts
   - Provide: Injection payloads detected, vulnerable endpoints, exploitation success

3. **SESSION & TOKEN ATTACKS**
   - Session hijacking (same session from different IPs/locations)
   - Token replay attacks (reused tokens)
   - Provide: Session IDs involved, geographic anomalies, time gaps

4. **PRIVILEGE ESCALATION**
   - Unauthorized access to admin endpoints
   - Role manipulation attempts
   - Bypass parameters in payloads
   - Provide: Users involved, escalation method, access gained

5. **RECONNAISSANCE ACTIVITIES**
   - Account enumeration patterns
   - Endpoint scanning
   - Provide: Enumeration technique, information disclosed

6. **AUTHENTICATION BYPASS**
   - MFA bypass attempts
   - Parameter manipulation
   - Provide: Bypass technique, success indicators

7. **ANOMALOUS BEHAVIOR PATTERNS**
   - Unusual user agents (automated tools)
   - Geographic anomalies
   - Time-based anomalies
   - Provide: Pattern details, risk indicators

LOG DATA:
{logs}

---
DETAILED SECURITY ANALYSIS REPORT:

For EACH threat detected, provide the following structure:

═══════════════════════════════════════════════════════════
THREAT #X: [THREAT NAME]
═══════════════════════════════════════════════════════════

**Threat Category:** [Category from above]
**Severity Level:** [CRITICAL/HIGH/MEDIUM/LOW]
**Attack Success:** [Successful/Failed/Partial]

**EVIDENCE:**
• Source IP(s): [List all IPs involved]
• Target User(s): [List all users/accounts]
• Affected Endpoint(s): [List endpoints]
• Timestamp Range: [Start time] → [End time]
• Attack Duration: [Calculate duration]

**ATTACK PATTERN:**
[Describe the attack sequence step-by-step with timestamps]

**TECHNICAL INDICATORS:**
• Status Codes: [List status codes and their significance]
• User Agent: [Agent used and what it reveals]
• Payload Analysis: [Detailed payload examination]
• Request Method: [Method and why it's suspicious]

**SECURITY IMPACT:**
• Accounts Compromised: [List if any]
• Data Accessed: [What data was potentially exposed]
• System Exposure: [What vulnerabilities were exploited]

**RECOMMENDED ACTIONS:**
1. [Immediate action required]
2. [Investigation steps]
3. [Mitigation measures]
4. [Prevention recommendations]

---

After analyzing ALL threats, provide:

**EXECUTIVE SUMMARY:**
• Total Threats Detected: [Number]
• Critical Incidents: [Number]
• Compromised Accounts: [List]
• Attack Vectors Used: [List all unique vectors]
• Overall Risk Assessment: [CRITICAL/HIGH/MEDIUM/LOW]

**CORRELATION ANALYSIS:**
[Identify if multiple attacks are related or part of a coordinated campaign]

**PRIORITY INCIDENT RESPONSE:**
[List top 3 threats requiring immediate attention]

Be thorough, specific, and actionable in your analysis. Reference exact log entries with timestamps when describing threats.
"""
)

# --- 4. Invoke the Enhanced Chain ---
chain = ENHANCED_ANALYSIS_PROMPT | llm

print("=" * 80)
print("INITIATING DEEP SECURITY ANALYSIS...")
print("=" * 80)
print()

# Invoke the chain
response = chain.invoke({"logs": log_text})

# Print the detailed response
print(response.content)

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)