#!/usr/bin/env python3
"""
Flask API Server for AI Banking Agent
Provides REST endpoints for frontend integration
"""

import os
import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any

import gc
from agent_types import UserContext, UserRole
from finance_agent import FinanceAgent
from grocery_agent import GroceryAgent

import jwt

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global agent instances
_finance_agent = None
_grocery_agent = None

def get_finance_agent():
    """Get Finance agent, put Grocery agent to sleep"""
    global _finance_agent, _grocery_agent
    if _grocery_agent is not None:
        print("💤 Sleeping Grocery Agent to free graphics memory...")
        del _grocery_agent
        _grocery_agent = None
        gc.collect()
        
    if _finance_agent is None:
        print("🚀 Waking Finance Agent...")
        _finance_agent = FinanceAgent()
    return _finance_agent

def get_grocery_agent():
    """Get Grocery agent, put Finance agent to sleep"""
    global _finance_agent, _grocery_agent
    if _finance_agent is not None:
        print("💤 Sleeping Finance Agent to free graphics memory...")
        del _finance_agent
        _finance_agent = None
        gc.collect()
        
    if _grocery_agent is None:
        print("🚀 Waking Grocery Agent...")
        _grocery_agent = GroceryAgent()
    return _grocery_agent

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "AI Banking Agent API"
    })

@app.route('/api/agent/activate', methods=['POST'])
def activate_agent():
    """Endpoint explicitly hit by the frontend UI loading spinner to pre-warm the agent"""
    try:
        data = request.get_json()
        target = data.get('agent', 'finance')
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if target == 'grocery':
            get_grocery_agent()
        else:
            get_finance_agent()
            
        loop.close()
        
        return jsonify({"success": True, "agent_loaded": target})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/security-analysis', methods=['POST'])
def admin_security_analysis():
    """
    Admin endpoint for comprehensive security analysis
    
    Expected JSON payload:
    {
        "user_id": "admin001",
        "log_file_path": "/path/to/logs.json",
        "transaction_data": {...},
        "location": "toronto"
    }
    """
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
        
        # Run analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_finance_agent()
        result = loop.run_until_complete(
            agent.analyze_security_threats(
                log_file_path=data.get('log_file_path'),
                transaction_data=data.get('transaction_data'),
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
    """Get admin security dashboard data"""
    try:
        agent = get_agent()
        dashboard_data = agent.security_agent.get_security_dashboard()
        
        return jsonify({
            "success": True,
            "dashboard": dashboard_data,
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
    """
    User endpoint for financial advice
    
    Expected JSON payload:
    {
        "user_id": "user001",
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
    """
    try:
        data = request.get_json()
        
        # Create user context
        user_context = UserContext(
            user_id=data.get('user_id', 'user'),
            role=UserRole.USER,
            location=data.get('location', 'toronto'),
            preferences=data.get('preferences', {}),
            transaction_history=data.get('transaction_history', [])
        )
        
        # Run analysis asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_finance_agent()
        advice = loop.run_until_complete(
            agent.provide_financial_advice(
                user_context=user_context,
                spending_data=data.get('spending_data', {}),
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
    """
    Chat endpoint for natural language interaction
    
    Expected JSON payload:
    {
        "message": "How can I save money on groceries?",
        "user_id": "user001",
        "user_role": "user",
        "location": "toronto"
    }
    """
    try:
        data = request.get_json()
        
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        user_id = data.get('user_id', 'user')
        if token:
            try:
                # In a real application, use a securely stored secret key
                decoded_token = jwt.decode(token, options={"verify_signature": False})
                user_id = decoded_token.get('sub')
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "error": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"success": False, "error": "Invalid token"}), 401

        # Create user context
        user_role = UserRole.ADMIN if data.get('user_role') == 'admin' else UserRole.USER
        user_context = UserContext(
            user_id=user_id,
            role=user_role,
            location=data.get('location', 'toronto'),
            preferences=data.get('preferences', {}),
            transaction_history=[],
            token=token
        )
        
        # Get chat response asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_finance_agent()
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
    """
    Analyze user spending patterns from transaction history
    
    Expected JSON payload:
    {
        "user_id": "user001",
        "transactions": [...],
        "time_period": "weekly"
    }
    """
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        # Analyze spending patterns
        spending_analysis = {
            "total_spending": sum(float(t.get('amount', '0').replace('$', '').replace('-', '').replace('+', '')) 
                                for t in transactions),
            "transaction_count": len(transactions),
            "categories": {},
            "trends": "spending_increasing",  # Would be calculated from actual data
            "recommendations": [
                "Consider setting a weekly budget limit",
                "Look for recurring subscriptions you can cancel",
                "Compare prices before making purchases"
            ]
        }
        
        # Group by categories
        for transaction in transactions:
            category = transaction.get('description', 'Other')
            amount = float(transaction.get('amount', '0').replace('$', '').replace('-', '').replace('+', ''))
            spending_analysis['categories'][category] = spending_analysis['categories'].get(category, 0) + amount
        
        return jsonify({
            "success": True,
            "analysis": spending_analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/advice-chat', methods=['POST'])
def advice_chat_endpoint():
    """
    Advice Chat endpoint mapped to the Grocery Agent
    """
    try:
        data = request.get_json()
        
        auth_header = request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        user_id = data.get('user_id', 'user')
        if token:
            try:
                decoded_token = jwt.decode(token, options={"verify_signature": False})
                user_id = decoded_token.get('sub')
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                pass

        user_role = UserRole.ADMIN if data.get('user_role') == 'admin' else UserRole.USER
        user_context = UserContext(
            user_id=user_id,
            role=user_role,
            location=data.get('location', 'toronto'),
            preferences=data.get('preferences', {}),
            transaction_history=[],
            token=token
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        agent = get_grocery_agent()
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
        agent = get_grocery_agent()
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
    print("🚀 Starting AI Banking Agent API Server...")
    print("📖 Available endpoints:")
    print("   GET  /api/health")
    print("   POST /api/admin/security-analysis")
    print("   GET  /api/admin/dashboard")
    print("   POST /api/user/financial-advice")
    print("   POST /api/chat")
    print("   POST /api/user/spending-analysis")
    print("   GET  /api/grocery-deals/<location>")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5001,  # Different port from main banking API
        debug=True
    )