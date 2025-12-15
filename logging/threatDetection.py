#!/usr/bin/env python3
"""
AI-Powered Security Agent for Banking Applications
Detects various types of attacks in real-time from log data
"""

import json
import time
import logging
import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import hashlib
import requests
from collections import defaultdict, deque
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import glob

# Configure paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Navigate relative to the script: ../banking-api/demo/logs
LOG_DIR = os.path.join(BASE_DIR, '..', 'banking-api', 'demo', 'logs')
# Navigate relative to the script: ../banking-api/demo/data
DATA_DIR = os.path.join(BASE_DIR, '..', 'banking-api', 'demo', 'data')

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'security_agent.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SecurityAgent")

class ThreatLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AttackType(Enum):
    SQL_INJECTION = "SQL_INJECTION"
    XSS = "XSS"
    BRUTE_FORCE = "BRUTE_FORCE"
    ACCOUNT_TAKEOVER = "ACCOUNT_TAKEOVER"
    FRAUD_TRANSACTION = "FRAUD_TRANSACTION"
    API_ABUSE = "API_ABUSE"
    SESSION_HIJACKING = "SESSION_HIJACKING"
    DDOS = "DDOS"
    SUSPICIOUS_LOGIN = "SUSPICIOUS_LOGIN"
    MONEY_LAUNDERING = "MONEY_LAUNDERING"

@dataclass
class SecurityEvent:
    timestamp: datetime
    attack_type: AttackType
    threat_level: ThreatLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    confidence_score: float
    raw_data: Dict[str, Any]
    action_taken: str = "LOGGED"

class BankingSecurityAgent:
    def __init__(self):
        self.threat_patterns = self._initialize_threat_patterns()
        self.ip_reputation = {}
        self.user_behavior_baseline = defaultdict(dict)
        self.recent_events = deque(maxlen=10000)
        self.blocked_ips = set()
        self.suspicious_users = set()
        self.transaction_patterns = {}
        self.db_connection = self._initialize_database()
        self.ml_models = self._initialize_ml_models()
        
        # Rate limiting trackers
        self.login_attempts = defaultdict(lambda: deque(maxlen=100))
        self.api_calls = defaultdict(lambda: deque(maxlen=1000))
        self.transaction_volumes = defaultdict(lambda: deque(maxlen=50))
        
    def _initialize_database(self):
        """Initialize SQLite database for storing security events"""
        db_path = os.path.join(DATA_DIR, 'security_events.db')
        conn = sqlite3.connect(db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                attack_type TEXT,
                threat_level TEXT,
                source_ip TEXT,
                user_id TEXT,
                description TEXT,
                confidence_score REAL,
                raw_data TEXT,
                action_taken TEXT
            )
        ''')
        conn.commit()
        return conn
        
    def _initialize_threat_patterns(self):
        """Initialize patterns for detecting various banking threats"""
        return {
            'sql_injection': [
                r"(\bunion\b.*\bselect\b)|(\bselect\b.*\bunion\b)",
                r"(\bor\b\s+\d+\s*=\s*\d+)|(\band\b\s+\d+\s*=\s*\d+)",
                r"(\bdrop\b\s+\btable\b)|(\bdelete\b\s+\bfrom\b)",
                r"(\binsert\b\s+\binto\b)|(\bupdate\b\s+\bset\b)",
                r"('|\"|`).*(union|select|insert|delete|update|drop)",
                r"\b(exec|execute)\s*\(",
                r"(;|\s)(shutdown|xp_cmdshell|sp_executesql)"
            ],
            'xss': [
                r"<script[^>]*>.*?</script>",
                r"javascript:\s*[^;]+",
                r"on(load|error|click|mouse|focus|blur)\s*=",
                r"<iframe[^>]*src\s*=",
                r"eval\s*\(",
                r"document\.(write|writeln|cookie)",
                r"window\.(location|open)"
            ],
            'account_takeover': [
                r"multiple_failed_attempts",
                r"password_reset_abuse",
                r"session_token_manipulation",
                r"credential_stuffing_pattern"
            ],
            'api_abuse': [
                r"excessive_api_calls",
                r"rate_limit_exceeded",
                r"unauthorized_endpoint_access",
                r"data_scraping_pattern"
            ]
        }
    
    def _initialize_ml_models(self):
        """Initialize simple ML models for fraud detection"""
        return {
            'transaction_fraud': self._create_transaction_fraud_model(),
            'login_anomaly': self._create_login_anomaly_model(),
            'behavioral_analysis': self._create_behavioral_model()
        }
    
    def _create_transaction_fraud_model(self):
        """Simple transaction fraud detection model"""
        class TransactionFraudModel:
            def __init__(self):
                self.thresholds = {
                    'amount_threshold': 10000,  # $10,000
                    'velocity_threshold': 5,    # 5 transactions per minute
                    'unusual_time_threshold': 0.1,  # Outside normal hours
                    'location_risk_threshold': 0.7   # Different location risk
                }
            
            def predict_fraud(self, transaction_data):
                score = 0.0
                factors = []
                
                # High amount check
                if transaction_data.get('amount', 0) > self.thresholds['amount_threshold']:
                    score += 0.3
                    factors.append("high_amount")
                
                # Velocity check
                user_id = transaction_data.get('user_id')
                if user_id:
                    recent_txns = len([t for t in self.recent_transactions.get(user_id, []) 
                                     if (datetime.now() - t['timestamp']).seconds < 60])
                    if recent_txns > self.thresholds['velocity_threshold']:
                        score += 0.4
                        factors.append("high_velocity")
                
                # Time-based analysis
                hour = datetime.now().hour
                if hour < 6 or hour > 22:  # Outside normal banking hours
                    score += 0.2
                    factors.append("unusual_time")
                
                # Location risk (simplified)
                if transaction_data.get('location_risk', 0) > self.thresholds['location_risk_threshold']:
                    score += 0.3
                    factors.append("location_risk")
                
                return min(score, 1.0), factors
            
            def __init__(self):
                super().__init__()
                self.recent_transactions = defaultdict(list)
        
        return TransactionFraudModel()
    
    def _create_login_anomaly_model(self):
        """Simple login anomaly detection model"""
        class LoginAnomalyModel:
            
            def detect_anomaly(self, login_data):
                score = 0.0
                factors = []
                
                # Multiple failed attempts
                failed_attempts = login_data.get('failed_attempts', 0)
                if failed_attempts > 3:
                    score += 0.4
                    factors.append("multiple_failures")
                
                # Unusual location
                if login_data.get('location_anomaly', False):
                    score += 0.3
                    factors.append("location_anomaly")
                
                # Unusual time
                hour = datetime.now().hour
                if hour < 5 or hour > 23:
                    score += 0.2
                    factors.append("unusual_time")
                
                # Device fingerprint mismatch
                if login_data.get('device_mismatch', False):
                    score += 0.3
                    factors.append("device_mismatch")
                
                return min(score, 1.0), factors
        
        return LoginAnomalyModel()
    
    def _create_behavioral_model(self):
        """Simple behavioral analysis model"""
        class BehaviorModel:
            def analyze_behavior(self, user_data):
                score = 0.0
                factors = []
                
                # Unusual transaction patterns
                if user_data.get('transaction_pattern_deviation', 0) > 0.7:
                    score += 0.4
                    factors.append("pattern_deviation")
                
                # Access pattern changes
                if user_data.get('access_pattern_change', 0) > 0.6:
                    score += 0.3
                    factors.append("access_change")
                
                return min(score, 1.0), factors
        
        return BehaviorModel()
    
    async def process_log_entry(self, log_entry: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Process a single log entry and detect potential threats"""
        try:
            # Extract key information
            timestamp = datetime.fromisoformat(log_entry.get('timestamp', datetime.now().isoformat()))
            source_ip = log_entry.get('source_ip', 'unknown')
            user_id = log_entry.get('user_id')
            endpoint = log_entry.get('endpoint', '')
            method = log_entry.get('method', '')
            payload = log_entry.get('payload', '')
            status_code = log_entry.get('status_code', 200)
            
            # Run multiple detection methods
            threats = []
            
            # Pattern-based detection
            pattern_threat = self._detect_pattern_based_threats(log_entry)
            if pattern_threat:
                threats.append(pattern_threat)
            
            # Behavioral analysis
            behavioral_threat = await self._detect_behavioral_anomalies(log_entry)
            if behavioral_threat:
                threats.append(behavioral_threat)
            
            # Rate limiting checks
            rate_threat = self._detect_rate_limiting_violations(log_entry)
            if rate_threat:
                threats.append(rate_threat)
            
            # Transaction fraud detection
            if 'transaction' in endpoint.lower():
                fraud_threat = self._detect_transaction_fraud(log_entry)
                if fraud_threat:
                    threats.append(fraud_threat)
            
            # Return the highest priority threat
            if threats:
                return max(threats, key=lambda x: x.confidence_score)
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing log entry: {e}")
            return None
    
    def _detect_pattern_based_threats(self, log_entry: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect threats using pattern matching"""
        payload = str(log_entry.get('payload', '')) + str(log_entry.get('url', ''))
        
        # SQL Injection Detection
        for pattern in self.threat_patterns['sql_injection']:
            if re.search(pattern, payload, re.IGNORECASE):
                return SecurityEvent(
                    timestamp=datetime.now(),
                    attack_type=AttackType.SQL_INJECTION,
                    threat_level=ThreatLevel.HIGH,
                    source_ip=log_entry.get('source_ip', 'unknown'),
                    user_id=log_entry.get('user_id'),
                    description=f"SQL injection attempt detected: {pattern}",
                    confidence_score=0.85,
                    raw_data=log_entry,
                    action_taken="BLOCKED"
                )
        
        # XSS Detection
        for pattern in self.threat_patterns['xss']:
            if re.search(pattern, payload, re.IGNORECASE):
                return SecurityEvent(
                    timestamp=datetime.now(),
                    attack_type=AttackType.XSS,
                    threat_level=ThreatLevel.HIGH,
                    source_ip=log_entry.get('source_ip', 'unknown'),
                    user_id=log_entry.get('user_id'),
                    description=f"XSS attempt detected: {pattern}",
                    confidence_score=0.80,
                    raw_data=log_entry
                )
        
        return None
    
    async def _detect_behavioral_anomalies(self, log_entry: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect behavioral anomalies using ML models"""
        user_id = log_entry.get('user_id')
        if not user_id:
            return None
        
        # Login anomaly detection
        if 'login' in log_entry.get('endpoint', '').lower():
            login_data = {
                'failed_attempts': self._count_recent_failed_logins(user_id),
                'location_anomaly': self._check_location_anomaly(log_entry),
                'device_mismatch': self._check_device_mismatch(log_entry)
            }
            
            score, factors = self.ml_models['login_anomaly'].detect_anomaly(login_data)
            
            if score > 0.6:
                return SecurityEvent(
                    timestamp=datetime.now(),
                    attack_type=AttackType.SUSPICIOUS_LOGIN,
                    threat_level=ThreatLevel.MEDIUM if score < 0.8 else ThreatLevel.HIGH,
                    source_ip=log_entry.get('source_ip', 'unknown'),
                    user_id=user_id,
                    description=f"Suspicious login behavior detected: {', '.join(factors)}",
                    confidence_score=score,
                    raw_data=log_entry
                )
        
        return None
    
    def _detect_rate_limiting_violations(self, log_entry: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect rate limiting violations and potential DDoS"""
        source_ip = log_entry.get('source_ip', '')
        endpoint = log_entry.get('endpoint', '')
        timestamp = datetime.now()
        
        # Track API calls per IP
        self.api_calls[source_ip].append(timestamp)
        
        # Remove old entries (older than 1 minute)
        cutoff_time = timestamp - timedelta(minutes=1)
        while self.api_calls[source_ip] and self.api_calls[source_ip][0] < cutoff_time:
            self.api_calls[source_ip].popleft()
        
        # Check if rate limit exceeded
        if len(self.api_calls[source_ip]) > 100:  # 100 requests per minute
            return SecurityEvent(
                timestamp=timestamp,
                attack_type=AttackType.DDOS,
                threat_level=ThreatLevel.HIGH,
                source_ip=source_ip,
                user_id=log_entry.get('user_id'),
                description=f"Rate limit exceeded: {len(self.api_calls[source_ip])} requests in 1 minute",
                confidence_score=0.90,
                raw_data=log_entry,
                action_taken="IP_BLOCKED"
            )
        
        return None
    
    def _detect_transaction_fraud(self, log_entry: Dict[str, Any]) -> Optional[SecurityEvent]:
        """Detect fraudulent transactions"""
        if 'transaction' not in log_entry.get('endpoint', '').lower():
            return None
        
        transaction_data = {
            'amount': log_entry.get('amount', 0),
            'user_id': log_entry.get('user_id'),
            'location_risk': self._calculate_location_risk(log_entry),
            'timestamp': datetime.now()
        }
        
        score, factors = self.ml_models['transaction_fraud'].predict_fraud(transaction_data)
        
        if score > 0.7:
            return SecurityEvent(
                timestamp=datetime.now(),
                attack_type=AttackType.FRAUD_TRANSACTION,
                threat_level=ThreatLevel.CRITICAL if score > 0.9 else ThreatLevel.HIGH,
                source_ip=log_entry.get('source_ip', 'unknown'),
                user_id=log_entry.get('user_id'),
                description=f"Fraudulent transaction detected: {', '.join(factors)}",
                confidence_score=score,
                raw_data=log_entry,
                action_taken="TRANSACTION_BLOCKED"
            )
        
        return None
    
    def _count_recent_failed_logins(self, user_id: str) -> int:
        """Count recent failed login attempts for a user"""
        # Implementation would check recent failed logins from logs
        return len([event for event in self.recent_events 
                   if event.user_id == user_id and 'failed_login' in str(event.raw_data)])
    
    def _check_location_anomaly(self, log_entry: Dict[str, Any]) -> bool:
        """Check if login location is anomalous"""
        # Simplified location check
        user_location = log_entry.get('location', '')
        user_id = log_entry.get('user_id', '')
        
        # Check against user's typical locations (simplified)
        typical_locations = self.user_behavior_baseline.get(user_id, {}).get('locations', [])
        return user_location not in typical_locations if typical_locations else False
    
    def _check_device_mismatch(self, log_entry: Dict[str, Any]) -> bool:
        """Check if device fingerprint doesn't match user's typical devices"""
        device_fingerprint = log_entry.get('device_fingerprint', '')
        user_id = log_entry.get('user_id', '')
        
        typical_devices = self.user_behavior_baseline.get(user_id, {}).get('devices', [])
        return device_fingerprint not in typical_devices if typical_devices else False
    
    def _calculate_location_risk(self, log_entry: Dict[str, Any]) -> float:
        """Calculate location-based risk score"""
        # Simplified location risk calculation
        location = log_entry.get('location', '')
        high_risk_countries = ['country1', 'country2']  # Configure as needed
        
        if any(country in location.lower() for country in high_risk_countries):
            return 0.8
        return 0.1
    
    def store_security_event(self, event: SecurityEvent):
        """Store security event in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO security_events 
                (timestamp, attack_type, threat_level, source_ip, user_id, 
                 description, confidence_score, raw_data, action_taken)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.timestamp.isoformat(),
                event.attack_type.value,
                event.threat_level.value,
                event.source_ip,
                event.user_id,
                event.description,
                event.confidence_score,
                json.dumps(event.raw_data),
                event.action_taken
            ))
            self.db_connection.commit()
            self.recent_events.append(event)
            
        except Exception as e:
            logger.error(f"Error storing security event: {e}")
    
    def take_action(self, event: SecurityEvent):
        """Take action based on security event"""
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            # Block IP
            self.blocked_ips.add(event.source_ip)
            logger.warning(f"BLOCKED IP: {event.source_ip} - {event.description}")
            
            # Add user to suspicious list if applicable
            if event.user_id:
                self.suspicious_users.add(event.user_id)
                logger.warning(f"FLAGGED USER: {event.user_id} - {event.description}")
            
            # Send alert (simplified)
            self.send_alert(event)
    
    def send_alert(self, event: SecurityEvent):
        """Send security alert"""
        alert_data = {
            'timestamp': event.timestamp.isoformat(),
            'attack_type': event.attack_type.value,
            'threat_level': event.threat_level.value,
            'source_ip': event.source_ip,
            'user_id': event.user_id,
            'description': event.description,
            'confidence_score': event.confidence_score
        }
        
        # In a real implementation, this would send to SIEM, Slack, email, etc.
        logger.critical(f"SECURITY ALERT: {json.dumps(alert_data, indent=2)}")
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Generate security dashboard data"""
        cursor = self.db_connection.cursor()
        
        # Get recent events
        cursor.execute('''
            SELECT attack_type, threat_level, COUNT(*) as count
            FROM security_events 
            WHERE datetime(timestamp) > datetime('now', '-24 hours')
            GROUP BY attack_type, threat_level
        ''')
        recent_threats = cursor.fetchall()
        
        # Get blocked IPs count
        blocked_ips_count = len(self.blocked_ips)
        
        # Get suspicious users count
        suspicious_users_count = len(self.suspicious_users)
        
        return {
            'recent_threats': recent_threats,
            'blocked_ips_count': blocked_ips_count,
            'suspicious_users_count': suspicious_users_count,
            'total_events_24h': sum([count for _, _, count in recent_threats]),
            'top_attack_types': [attack_type for attack_type, _, _ in 
                               sorted(recent_threats, key=lambda x: x[2], reverse=True)[:5]]
        }

class LogProcessor:
    def __init__(self, security_agent: BankingSecurityAgent):
        self.security_agent = security_agent
        self.executor = ThreadPoolExecutor(max_workers=10)
        
    async def process_logs_from_file(self, file_path: str):
        """Process logs from a file"""
        try:
            with open(file_path, 'r') as file:
                # Assuming one JSON object per file (array or object) or one per line
                # The auth_logs format usually is one JSON object with "logs": [...] array
                # Let's inspect content or try both strategies
                content = file.read().strip()
                if not content:
                    return

                try:
                    data = json.loads(content)
                    if isinstance(data, dict) and 'logs' in data:
                        # Format: {"logs": [...]}
                        for log_entry in data['logs']:
                            await self.process_single_log(log_entry)
                    elif isinstance(data, list):
                        # Format: [...]
                        for log_entry in data:
                            await self.process_single_log(log_entry)
                    else:
                        # Maybe single object?
                        await self.process_single_log(data)
                except json.JSONDecodeError:
                    # Maybe JSON per line?
                    file.seek(0)
                    for line in file:
                        if line.strip():
                            try:
                                log_entry = json.loads(line)
                                await self.process_single_log(log_entry)
                            except json.JSONDecodeError:
                                logger.warning(f"Invalid JSON in log line: {line.strip()[:50]}...")
                                
        except FileNotFoundError:
            logger.error(f"Log file not found: {file_path}")
    
    async def process_single_log(self, log_entry: Dict[str, Any]):
        """Process a single log entry"""
        event = await self.security_agent.process_log_entry(log_entry)
        if event:
            self.security_agent.store_security_event(event)
            self.security_agent.take_action(event)

# Example usage and testing
async def main():
    """Main function for testing the security agent"""
    agent = BankingSecurityAgent()
    processor = LogProcessor(agent)
    
    # Process actual log files from directory
    log_files = glob.glob(os.path.join(LOG_DIR, 'auth_logs_*.json'))
    logger.info(f"Found {len(log_files)} log files in {LOG_DIR}")
    
    if not log_files:
        logger.warning(f"No log files found in {LOG_DIR}. Check path configuration.")

    for log_file in log_files:
        logger.info(f"Processing log file: {os.path.basename(log_file)}")
        await processor.process_logs_from_file(log_file)

    # Sample log entries for testing (fallback)
    test_logs = [
        {
            "timestamp": "2024-12-28T10:30:00",
            "source_ip": "192.168.1.100",
            "user_id": "user123",
            "endpoint": "/api/login",
            "method": "POST",
            "payload": "username=admin&password=password",
            "status_code": 200
        },
        # ... more test logs ...
    ]
    
    # Process test logs
    # for log in test_logs:
    #     await processor.process_single_log(log)
    
    # Display dashboard
    dashboard = agent.get_security_dashboard()
    print("\n=== SECURITY DASHBOARD ===")
    print(json.dumps(dashboard, indent=2))
    
    # Close database connection
    agent.db_connection.close()

if __name__ == "__main__":
    asyncio.run(main())