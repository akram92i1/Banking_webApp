#!/usr/bin/env python3
"""
Enhanced Flask API Server for AI Banking Agent with Comprehensive Security Analysis
Provides REST endpoints for frontend integration and connects to PostgreSQL with authentication log analysis
"""

import os
import json
import asyncio
import psycopg2
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any, List
import requests

# Import our AI agent
from ai_banking_agent import AIBankingAgent, UserContext, UserRole

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'my_finance_db',
    'user': 'bank_database_admin',
    'password': 'admin123'
}

# Global agent instance
ai_agent = None

def get_agent():
    """Get or create AI agent instance"""
    global ai_agent
    if ai_agent is None:
        ai_agent = AIBankingAgent()
    return ai_agent

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def fetch_user_transactions(user_id: str, limit: int = 50) -> List[Dict]:
    """Fetch user transactions from database"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT t.transaction_id, t.amount, t.description, t.transaction_type,
               t.transaction_status, t.created_at, t.from_account_id, t.to_account_id
        FROM transactions t
        JOIN accounts a ON (t.from_account_id = a.id OR t.to_account_id = a.id)
        WHERE a.user_id = %s
        ORDER BY t.created_at DESC
        LIMIT %s
        """
        
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()
        
        transactions = []
        for row in results:
            transactions.append({
                'transaction_id': str(row[0]),
                'amount': float(row[1]),
                'description': row[2],
                'transaction_type': row[3],
                'transaction_status': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'from_account_id': str(row[6]) if row[6] else None,
                'to_account_id': str(row[7]) if row[7] else None
            })
        
        cursor.close()
        conn.close()
        return transactions
        
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        if conn:
            conn.close()
        return []

def fetch_suspicious_transactions() -> List[Dict]:
    """Fetch suspicious transactions for admin analysis"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        query = """
        SELECT t.transaction_id, t.amount, t.description, t.transaction_type,
               t.transaction_status, t.created_at, u.first_name, u.last_name, u.email
        FROM transactions t
        JOIN accounts a ON t.from_account_id = a.id
        JOIN users u ON a.user_id = u.id
        WHERE ABS(t.amount) > 5000 
           OR t.created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
        ORDER BY t.created_at DESC
        LIMIT 20
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        transactions = []
        for row in results:
            transactions.append({
                'transaction_id': str(row[0]),
                'amount': float(row[1]),
                'description': row[2],
                'transaction_type': row[3],
                'transaction_status': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'user_name': f"{row[6]} {row[7]}",
                'user_email': row[8]
            })
        
        cursor.close()
        conn.close()
        return transactions
        
    except Exception as e:
        print(f"Error fetching suspicious transactions: {e}")
        if conn:
            conn.close()
        return []

# === SECURITY ANALYSIS HELPER FUNCTIONS ===

def determine_overall_risk_level(system_overview: Dict, user_analysis: Dict) -> str:
    """Determine overall security risk level"""
    risk_score = 0
    
    # System-level risks
    if system_overview:
        failure_rate = float(system_overview.get('system_failure_rate', '0').replace('%', ''))
        if failure_rate > 20: risk_score += 3
        elif failure_rate > 10: risk_score += 2
        elif failure_rate > 5: risk_score += 1
        
        high_risk_ips = len(system_overview.get('high_risk_ips', []))
        if high_risk_ips > 5: risk_score += 3
        elif high_risk_ips > 2: risk_score += 2
        elif high_risk_ips > 0: risk_score += 1
        
        compromised = len(system_overview.get('compromised_accounts', []))
        if compromised > 2: risk_score += 4
        elif compromised > 0: risk_score += 2
    
    # User-level risks
    if user_analysis:
        threat_level = user_analysis.get('threat_level', 'LOW')
        if threat_level == 'CRITICAL': risk_score += 5
        elif threat_level == 'HIGH': risk_score += 3
        elif threat_level == 'MEDIUM': risk_score += 2
        elif threat_level == 'LOW': risk_score += 1
    
    # Determine final level
    if risk_score >= 10: return "CRITICAL"
    elif risk_score >= 7: return "HIGH"
    elif risk_score >= 4: return "MEDIUM"
    elif risk_score >= 1: return "LOW"
    else: return "MINIMAL"

def extract_immediate_threats(system_overview: Dict, user_analysis: Dict) -> List[str]:
    """Extract immediate threat indicators"""
    threats = []
    
    if system_overview:
        if system_overview.get('compromised_accounts'):
            threats.append("Potentially compromised accounts detected")
        
        if len(system_overview.get('high_risk_ips', [])) > 3:
            threats.append("Multiple high-risk IP addresses active")
            
        if len(system_overview.get('attack_patterns', [])) > 0:
            threats.append("Coordinated attack patterns identified")
    
    if user_analysis:
        if user_analysis.get('threat_level') in ['CRITICAL', 'HIGH']:
            threats.append(f"User {user_analysis.get('analyzed_user')} shows {user_analysis.get('threat_level')} threat level")
        
        user_threats = user_analysis.get('security_threats', [])
        if user_threats:
            threats.extend(user_threats[:2])  # Top 2 user threats
    
    return threats

def assess_system_stability(system_overview: Dict) -> str:
    """Assess overall system stability"""
    if not system_overview:
        return "UNKNOWN"
    
    failure_rate = float(system_overview.get('system_failure_rate', '0').replace('%', ''))
    total_events = system_overview.get('total_events', 0)
    
    if failure_rate > 30: return "UNSTABLE"
    elif failure_rate > 15: return "DEGRADED"
    elif failure_rate > 5: return "CONCERNING"
    elif total_events > 100: return "STABLE"
    else: return "LIMITED_DATA"

def extract_geographic_risks(system_overview: Dict) -> List[str]:
    """Extract geographic risk indicators"""
    risks = []
    
    if system_overview:
        suspicious_ips = system_overview.get('suspicious_ips', [])
        if suspicious_ips:
            risks.append(f"Suspicious geographic locations detected: {len(suspicious_ips)} IPs")
        
        high_risk_ips = system_overview.get('high_risk_ips', [])
        if high_risk_ips:
            risks.append(f"High-risk geographic regions: {len(high_risk_ips)} locations")
    
    return risks

def check_brute_force_patterns(system_overview: Dict, user_analysis: Dict) -> List[str]:
    """Check for brute force attack patterns"""
    patterns = []
    
    if system_overview:
        failed_attempts = system_overview.get('total_failed_attempts', 0)
        if failed_attempts > 100:
            patterns.append(f"High system-wide failed attempts: {failed_attempts}")
    
    if user_analysis:
        failure_rate = user_analysis.get('failure_rate', '0%')
        if float(failure_rate.replace('%', '')) > 50:
            patterns.append(f"User shows high failure rate: {failure_rate}")
        
        risk_factors = user_analysis.get('risk_factors', [])
        if 'BRUTE_FORCE_PATTERN' in risk_factors:
            patterns.append("Brute force pattern detected in user activity")
    
    return patterns

def analyze_auth_transaction_correlation(user_analysis: Dict, transaction_data: Dict) -> str:
    """Analyze correlation between authentication and transaction anomalies"""
    if not user_analysis or not transaction_data:
        return "Insufficient data for correlation analysis"
    
    correlations = []
    
    # Check if authentication threats correlate with transaction timing
    if user_analysis.get('threat_level') in ['HIGH', 'CRITICAL']:
        correlations.append("High authentication threat level coincides with suspicious transaction")
    
    # Check for timing correlations
    security_threats = user_analysis.get('security_threats', [])
    for threat in security_threats:
        if 'unusual' in threat.lower() or 'night' in threat.lower():
            correlations.append("Unusual timing patterns in both authentication and transactions")
            break
    
    # Check IP correlations
    if user_analysis.get('unique_ips', 0) > 5:
        correlations.append("Multiple IPs in authentication logs suggest account compromise risk")
    
    if correlations:
        return "CORRELATION DETECTED: " + "; ".join(correlations)
    else:
        return "No significant correlations detected between authentication and transaction patterns"

def calculate_takeover_probability(user_analysis: Dict, transaction_data: Dict) -> str:
    """Calculate probability of account takeover"""
    score = 0
    
    if user_analysis:
        if user_analysis.get('threat_level') == 'CRITICAL': score += 4
        elif user_analysis.get('threat_level') == 'HIGH': score += 3
        elif user_analysis.get('threat_level') == 'MEDIUM': score += 2
        
        risk_factors = user_analysis.get('risk_factors', [])
        if 'MULTIPLE_IPS' in risk_factors: score += 2
        if 'SUSPICIOUS_GEOGRAPHY' in risk_factors: score += 2
        if 'BRUTE_FORCE_PATTERN' in risk_factors: score += 3
        if 'UNUSUAL_HOURS' in risk_factors: score += 1
        
        if user_analysis.get('unique_ips', 0) > 10: score += 2
    
    if transaction_data:
        amount = float(transaction_data.get('amount', 0))
        if amount > 10000: score += 2
        elif amount > 5000: score += 1
    
    if score >= 8: return "HIGH (80-95%)"
    elif score >= 6: return "MODERATE (60-80%)"
    elif score >= 4: return "LOW (30-60%)"
    elif score >= 2: return "MINIMAL (10-30%)"
    else: return "VERY LOW (<10%)"

def generate_integrated_recommendations(system_overview: Dict, user_analysis: Dict, transaction_data: Dict) -> List[str]:
    """Generate integrated security recommendations"""
    recommendations = []
    
    # Critical recommendations
    if user_analysis and user_analysis.get('threat_level') in ['CRITICAL', 'HIGH']:
        recommendations.append("🚨 IMMEDIATE: Suspend account and require identity verification")
        recommendations.append("📞 Contact user through verified channels to confirm recent activity")
    
    # System recommendations
    if system_overview:
        if len(system_overview.get('compromised_accounts', [])) > 0:
            recommendations.append("🔐 Force password reset for flagged accounts")
            recommendations.append("📧 Send security alerts to all affected users")
        
        if len(system_overview.get('high_risk_ips', [])) > 3:
            recommendations.append("🚫 Implement IP blocking for high-risk addresses")
            recommendations.append("🌍 Enable geographic access controls")
    
    # Transaction-specific recommendations
    if transaction_data:
        amount = float(transaction_data.get('amount', 0))
        if amount > 10000:
            recommendations.append("💰 Require additional authorization for large transactions")
            recommendations.append("⏱️ Implement transaction delays for verification")
    
    # Authentication recommendations
    if user_analysis:
        if user_analysis.get('unique_ips', 0) > 5:
            recommendations.append("🔒 Enable device registration and approval")
            recommendations.append("📱 Require MFA for new device logins")
        
        if 'UNUSUAL_HOURS' in user_analysis.get('risk_factors', []):
            recommendations.append("🕒 Implement time-based access restrictions")
    
    # Default recommendations if no specific threats
    if not recommendations:
        recommendations.extend([
            "✅ Continue monitoring with current security protocols",
            "🔄 Regular security reviews and user education",
            "📊 Implement behavioral analytics for early detection"
        ])
    
    return recommendations

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database status"""
    db_status = "connected" if get_db_connection() else "disconnected"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Enhanced Security AI Banking Agent API",
        "database_status": db_status,
        "ai_agent_status": "active",
        "security_analysis": "comprehensive"
    })

@app.route('/api/admin/security-analysis', methods=['POST'])
def admin_security_analysis():
    """Enhanced admin endpoint for comprehensive security analysis with authentication logs"""
    try:
        data = request.get_json()
        
        # Create admin context
        admin_context = UserContext(
            user_id=data.get('user_id', 'admin'),
            role=UserRole.ADMIN,
            location=data.get('location', 'toronto'),
            preferences=data.get('preferences', {}),
            transaction_history=[]
        )
        
        # Get comprehensive security context from banking API integration
        security_context = data.get('security_context', {})
        system_overview = security_context.get('system_overview', {})
        user_analysis = security_context.get('user_analysis', {})
        
        # Get real suspicious transactions from database
        suspicious_transactions = fetch_suspicious_transactions()
        
        # Prepare enhanced transaction data for AI analysis
        transaction_data = data.get('transaction_data')
        if not transaction_data and suspicious_transactions:
            latest = suspicious_transactions[0]
            transaction_data = {
                "amount": latest['amount'],
                "timestamp": latest['created_at'],
                "merchant_type": latest['description'],
                "user_email": latest['user_email'],
                "transaction_type": latest['transaction_type']
            }
        
        # Enhanced prompt with security context
        user_section = "No specific user analysis"
        if user_analysis:
            threats_str = str(user_analysis.get('security_threats', []))
            user_section = f"""
        Analyzed User: {user_analysis.get('analyzed_user', 'N/A')}
        Threat Level: {user_analysis.get('threat_level', 'N/A')}
        Login Attempts: {user_analysis.get('login_attempts', 'N/A')}
        Failed Logins: {user_analysis.get('failed_logins', 'N/A')}
        Failure Rate: {user_analysis.get('failure_rate', 'N/A')}
        Unique IPs: {user_analysis.get('unique_ips', 'N/A')}
        Security Threats: {threats_str}"""
            
        enhanced_prompt = f"""
        COMPREHENSIVE SECURITY ANALYSIS REQUEST
        
        === SYSTEM OVERVIEW ===
        Total Events: {system_overview.get('total_events', 'N/A')}
        Active Users: {system_overview.get('active_users', 'N/A')}
        System Failure Rate: {system_overview.get('system_failure_rate', 'N/A')}
        High Risk IPs: {len(system_overview.get('high_risk_ips', []))}
        Suspicious IPs: {len(system_overview.get('suspicious_ips', []))}
        Potentially Compromised Accounts: {len(system_overview.get('compromised_accounts', []))}
        Attack Patterns: {len(system_overview.get('attack_patterns', []))}
        
        === USER SPECIFIC ANALYSIS ==={user_section}
        
        === TRANSACTION DATA ===
        {"Suspicious Transaction: " + str(transaction_data) if transaction_data else "No suspicious transaction data"}
        
        === ANALYSIS REQUEST ===
        Please provide a comprehensive security analysis considering:
        1. Authentication log patterns and anomalies
        2. Transaction behavior analysis  
        3. Potential account compromise indicators
        4. Geographic and timing anomalies
        5. System-wide threat assessment
        6. Specific user risk assessment
        7. Coordinated attack patterns
        
        Focus on correlating authentication failures with transaction anomalies and identify potential account takeover scenarios.
        Provide specific, actionable recommendations for immediate security improvements.
        """
        
        # Run enhanced analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_agent()
        
        # Use direct chat for comprehensive analysis
        comprehensive_analysis = loop.run_until_complete(
            agent.chat_with_agent(
                message=enhanced_prompt,
                user_context=admin_context
            )
        )
        
        # Also run traditional security analysis if transaction data exists
        traditional_result = None
        if transaction_data:
            traditional_result = loop.run_until_complete(
                agent.analyze_security_threats(
                    transaction_data=transaction_data,
                    user_context=admin_context
                )
            )
        
        loop.close()
        
        # Prepare comprehensive response
        analysis_response = {
            "comprehensive_analysis": comprehensive_analysis,
            "threat_assessment": {
                "overall_risk": determine_overall_risk_level(system_overview, user_analysis),
                "immediate_threats": extract_immediate_threats(system_overview, user_analysis),
                "user_compromise_risk": user_analysis.get('threat_level', 'UNKNOWN') if user_analysis else 'NO_DATA',
                "system_stability": assess_system_stability(system_overview)
            },
            "authentication_insights": {
                "login_anomalies": user_analysis.get('security_threats', []) if user_analysis else [],
                "geographic_risks": extract_geographic_risks(system_overview),
                "timing_patterns": "Analyzed in authentication logs",
                "brute_force_indicators": check_brute_force_patterns(system_overview, user_analysis)
            },
            "correlation_analysis": {
                "auth_transaction_correlation": analyze_auth_transaction_correlation(user_analysis, transaction_data),
                "compromise_indicators": user_analysis.get('risk_factors', []) if user_analysis else [],
                "account_takeover_probability": calculate_takeover_probability(user_analysis, transaction_data)
            }
        }
        
        if traditional_result:
            analysis_response["traditional_analysis"] = {
                "threat_detected": traditional_result.threat_detected,
                "threat_type": traditional_result.threat_type,
                "confidence_score": traditional_result.confidence_score,
                "severity": traditional_result.severity,
                "recommendation": traditional_result.recommendation,
                "explanation": traditional_result.explanation
            }
        
        return jsonify({
            "success": True,
            "analysis": analysis_response,
            "security_context_applied": True,
            "data_sources": security_context.get('data_sources', ['transaction_logs', 'authentication_logs']),
            "system_data": {
                "suspicious_transactions_count": len(suspicious_transactions),
                "auth_events_analyzed": system_overview.get('total_events', 0),
                "analysis_scope": security_context.get('analysis_scope', 'comprehensive'),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "recommendations": generate_integrated_recommendations(system_overview, user_analysis, transaction_data),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Enhanced security analysis error: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "fallback": "Consider using traditional security analysis if enhanced analysis fails"
        }), 500

# Include all other endpoints from the original enhanced_api_server.py
# (chat, financial-advice, dashboard, etc.)

if __name__ == '__main__':
    print("🚀 Starting Enhanced Security AI Banking Agent API Server...")
    print("🔒 Comprehensive security analysis with authentication log integration")
    print("📖 Available endpoints:")
    print("   GET  /api/health")
    print("   POST /api/admin/security-analysis (ENHANCED)")
    print("🔗 Database integration: PostgreSQL + Authentication Logs")
    print("🧠 AI Agent: LangChain + Ollama + Security Analytics")
    
    # Test database connection
    if get_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5002,  # Different port for enhanced security API
        debug=True
    )