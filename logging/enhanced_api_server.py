#!/usr/bin/env python3
"""
Enhanced Flask API Server for AI Banking Agent with Database Integration
Provides REST endpoints for frontend integration and connects to PostgreSQL
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
import uuid

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
        
        # Check if user_id is a valid UUID
        is_uuid = False
        try:
            uuid.UUID(str(user_id))
            is_uuid = True
        except ValueError:
            is_uuid = False
            
        if is_uuid:
            query = """
            SELECT t.transaction_id, t.amount, t.description, t.transaction_type,
                   t.transaction_status, t.created_at, t.from_account_id, t.to_account_id
            FROM transactions t
            JOIN accounts a ON (t.from_account_id = a.account_id OR t.to_account_id = a.account_id)
            WHERE a.user_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s
            """
        else:
            # Assume it's a username
            query = """
            SELECT t.transaction_id, t.amount, t.description, t.transaction_type,
                   t.transaction_status, t.created_at, t.from_account_id, t.to_account_id
            FROM transactions t
            JOIN accounts a ON (t.from_account_id = a.account_id OR t.to_account_id = a.account_id)
            JOIN users u ON a.user_id = u.user_id
            WHERE u.username = %s
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
        JOIN accounts a ON t.from_account_id = a.account_id
        JOIN users u ON a.user_id = u.user_id
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint with database status"""
    db_status = "connected" if get_db_connection() else "disconnected"
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Enhanced AI Banking Agent API",
        "database_status": db_status,
        "ai_agent_status": "active"
    })

@app.route('/api/admin/security-analysis', methods=['POST'])
def admin_security_analysis():
    """Enhanced admin endpoint for comprehensive security analysis"""
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
        
        # Get real suspicious transactions from database
        suspicious_transactions = fetch_suspicious_transactions()
        
        # Prepare transaction data for AI analysis
        transaction_data = None
        if suspicious_transactions:
            latest = suspicious_transactions[0]
            transaction_data = {
                "amount": latest['amount'],
                "timestamp": latest['created_at'],
                "merchant_type": latest['description'],
                "user_email": latest['user_email'],
                "transaction_type": latest['transaction_type']
            }
        
        # Run analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_agent()
        result = loop.run_until_complete(
            agent.analyze_security_threats(
                transaction_data=transaction_data,
                user_context=admin_context
            )
        )
        
        loop.close()
        
        return jsonify({
            "success": True,
            "analysis": {
                "threat_detected": result.threat_detected,
                "threat_type": result.threat_type,
                "confidence_score": result.confidence_score,
                "severity": result.severity,
                "recommendation": result.recommendation,
                "explanation": result.explanation
            },
            "system_data": {
                "suspicious_transactions_count": len(suspicious_transactions),
                "suspicious_transactions": suspicious_transactions[:5],  # Top 5
                "analysis_timestamp": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Get enhanced admin security dashboard data with real database info"""
    try:
        agent = get_agent()
        
        # Get real data from database
        suspicious_transactions = fetch_suspicious_transactions()
        
        # Get dashboard data from security agent
        dashboard_data = agent.security_agent.get_security_dashboard()
        
        # Enhance with real database statistics
        conn = get_db_connection()
        db_stats = {}
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get transaction statistics
                cursor.execute("SELECT COUNT(*) FROM transactions WHERE created_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'")
                db_stats['transactions_24h'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users")
                db_stats['total_users'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM accounts")
                db_stats['total_accounts'] = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error getting DB stats: {e}")
                if conn:
                    conn.close()
        
        # Combine dashboard data
        enhanced_dashboard = {
            **dashboard_data,
            "database_stats": db_stats,
            "suspicious_transactions": suspicious_transactions[:10],
            "real_time_data": True
        }
        
        return jsonify({
            "success": True,
            "dashboard": enhanced_dashboard,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/user/financial-advice', methods=['POST'])
def user_financial_advice():
    """Enhanced user endpoint for financial advice with real transaction data"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user')
        
        # Get real transaction data from database
        real_transactions = fetch_user_transactions(user_id, 100)
        
        # Calculate real spending data
        spending_data = {}
        if real_transactions:
            # Group transactions by week
            now = datetime.now()
            for i in range(4):
                week_start = now - timedelta(days=(i+1)*7)
                week_end = now - timedelta(days=i*7)
                
                week_spending = sum(
                    abs(t['amount']) for t in real_transactions
                    if t['created_at'] and week_start.isoformat() <= t['created_at'] < week_end.isoformat()
                    and t['amount'] < 0  # Only outgoing transactions
                )
                spending_data[f'week{4-i}'] = week_spending
        else:
            # Fallback to provided data
            spending_data = data.get('spending_data', {
                'week1': 120.50, 'week2': 145.30, 'week3': 135.80, 'week4': 160.20
            })
        
        # Create user context
        user_context = UserContext(
            user_id=user_id,
            role=UserRole.USER,
            location=data.get('location', 'toronto'),
            preferences=data.get('preferences', {}),
            transaction_history=real_transactions
        )
        
        # Run analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_agent()
        advice = loop.run_until_complete(
            agent.provide_financial_advice(
                user_context=user_context,
                spending_data=spending_data,
                category=data.get('category', 'grocery'),
                target_reduction=data.get('target_reduction')
            )
        )
        
        loop.close()
        
        return jsonify({
            "success": True,
            "advice": {
                "analysis_summary": advice.analysis_summary,
                "weekly_spending": advice.weekly_spending,
                "recommended_reduction": advice.recommended_reduction,
                "savings_suggestions": advice.savings_suggestions,
                "grocery_deals": advice.grocery_deals,
                "action_plan": advice.action_plan
            },
            "real_data": {
                "transaction_count": len(real_transactions),
                "data_source": "database" if real_transactions else "mock",
                "spending_breakdown": spending_data
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_agent():
    """Enhanced chat endpoint with database context"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user')
        
        # Get user transaction context for better responses
        recent_transactions = fetch_user_transactions(user_id, 20)
        
        # Create user context
        user_role = UserRole.ADMIN if data.get('user_role') == 'admin' else UserRole.USER
        user_context = UserContext(
            user_id=user_id,
            role=user_role,
            location=data.get('location', 'toronto'),
            preferences=data.get('preferences', {}),
            transaction_history=recent_transactions
        )
        
        # Get chat response asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_agent()
        response = loop.run_until_complete(
            agent.chat_with_agent(
                message=data.get('message', ''),
                user_context=user_context
            )
        )
        
        loop.close()
        
        return jsonify({
            "success": True,
            "response": response,
            "context": {
                "transaction_count": len(recent_transactions),
                "user_role": user_role.value,
                "has_real_data": len(recent_transactions) > 0
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/user/spending-analysis', methods=['POST'])
def analyze_user_spending():
    """Enhanced spending analysis using real transaction data"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'user')
        
        # Get real transaction data
        transactions = fetch_user_transactions(user_id, 200)
        
        if not transactions:
            return jsonify({
                "success": False,
                "error": "No transaction data available",
                "timestamp": datetime.now().isoformat()
            }), 404
        
        # Analyze spending patterns
        total_spending = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
        transaction_count = len([t for t in transactions if t['amount'] < 0])
        
        # Category analysis
        categories = {}
        for transaction in transactions:
            if transaction['amount'] < 0:  # Outgoing only
                desc = transaction.get('description', 'Other')
                amount = abs(transaction['amount'])
                categories[desc] = categories.get(desc, 0) + amount
        
        # Top spending categories
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        
        spending_analysis = {
            "total_spending": total_spending,
            "transaction_count": transaction_count,
            "average_transaction": total_spending / max(transaction_count, 1),
            "categories": dict(top_categories),
            "spending_trend": "stable",  # Would calculate based on time analysis
            "recommendations": [
                f"Your largest spending category is {top_categories[0][0]} (${top_categories[0][1]:.2f})" if top_categories else "No spending data available",
                "Consider setting budget limits for your top spending categories",
                "Review recurring transactions for potential savings"
            ]
        }
        
        return jsonify({
            "success": True,
            "analysis": spending_analysis,
            "data_source": "real_database",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/grocery-deals/<location>', methods=['GET'])
def get_grocery_deals(location):
    """Get grocery deals for a specific location"""
    try:
        agent = get_agent()
        deals = agent._get_grocery_deals(location)
        
        return jsonify({
            "success": True,
            "location": location,
            "deals": deals,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced AI Banking Agent API Server...")
    print("📖 Available endpoints:")
    print("   GET  /api/health")
    print("   POST /api/admin/security-analysis")
    print("   GET  /api/admin/dashboard")
    print("   POST /api/user/financial-advice")
    print("   POST /api/chat")
    print("   POST /api/user/spending-analysis")
    print("   GET  /api/grocery-deals/<location>")
    print("🔗 Database integration: PostgreSQL")
    print("🧠 AI Agent: LangChain + Ollama")
    
    # Test database connection
    if get_db_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,  # Different port from main banking API
        debug=True
    )