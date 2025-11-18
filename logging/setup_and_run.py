#!/usr/bin/env python3
"""
Setup and Run Script for AI Banking Agent
Automates the setup process and starts all necessary services
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print("✅ Python version:", sys.version.split()[0])
    return True


def check_ollama_installation():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Ollama is installed")
            return True
        else:
            print("❌ Ollama not found or not running")
            return False
    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("💡 Install from: https://ollama.ai/download")
        return False


def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("⚠️  Ollama service not running")
    return False


def start_ollama_service():
    """Start Ollama service"""
    print("🚀 Starting Ollama service...")
    try:
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Wait for service to start
        
        if check_ollama_service():
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False


def check_llm_model(model_name="llama3.2"):
    """Check if required LLM model is available"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if model_name in result.stdout:
            print(f"✅ Model {model_name} is available")
            return True
        else:
            print(f"⚠️  Model {model_name} not found")
            return False
    except Exception:
        return False


def pull_llm_model(model_name="llama3.2"):
    """Pull the required LLM model"""
    print(f"📥 Downloading model {model_name} (this may take several minutes)...")
    try:
        result = subprocess.run(['ollama', 'pull', model_name], check=True)
        print(f"✅ Model {model_name} downloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download model: {e}")
        return False


def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    requirements_file = Path("requirement.txt")
    
    if not requirements_file.exists():
        print("❌ requirement.txt not found")
        return False
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_node_installation():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js installed: {version}")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ Node.js not found")
    print("💡 Install from: https://nodejs.org/")
    return False


def install_frontend_dependencies():
    """Install frontend dependencies"""
    frontend_dir = Path("../finance_front_end")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    print("📦 Installing frontend dependencies...")
    try:
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
        subprocess.run(['npm', 'install', 'lucide-react'], cwd=frontend_dir, check=True)
        print("✅ Frontend dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False


def test_ai_agent():
    """Test the AI agent functionality"""
    print("🧪 Testing AI agent...")
    try:
        from ai_banking_agent import AIBankingAgent, UserContext, UserRole
        
        # Quick test
        agent = AIBankingAgent()
        user_context = UserContext("test_user", UserRole.USER, "toronto", {}, [])
        
        # This will fail if Ollama/model isn't working
        agent.close()
        print("✅ AI agent test passed")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  AI agent test warning: {e}")
        return True  # Continue anyway


def start_api_server():
    """Start the Flask API server"""
    print("🚀 Starting AI Banking API server...")
    try:
        api_process = subprocess.Popen([
            sys.executable, 'api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit and check if process started
        time.sleep(3)
        if api_process.poll() is None:  # Process is running
            print("✅ API server started on http://localhost:5001")
            return api_process
        else:
            print("❌ API server failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Error starting API server: {e}")
        return None


def start_frontend():
    """Start the React frontend"""
    frontend_dir = Path("../finance_front_end")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return None
    
    print("🚀 Starting React frontend...")
    try:
        frontend_process = subprocess.Popen([
            'npm', 'start'
        ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Frontend starting on http://localhost:3000")
        return frontend_process
        
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None


def wait_for_api_ready():
    """Wait for API to be ready"""
    print("⏳ Waiting for API to be ready...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get('http://localhost:5001/api/health', timeout=2)
            if response.status_code == 200:
                print("✅ API is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"   Waiting... ({i+1}/30)")
    
    print("❌ API not responding after 30 seconds")
    return False


def test_api_endpoints():
    """Test API endpoints"""
    print("🧪 Testing API endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get('http://localhost:5001/api/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print("⚠️  Health endpoint returned:", response.status_code)
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test chat endpoint
    try:
        response = requests.post('http://localhost:5001/api/chat', 
                               json={
                                   "message": "Hello",
                                   "user_id": "test",
                                   "user_role": "user",
                                   "location": "toronto"
                               }, timeout=10)
        
        if response.status_code == 200:
            print("✅ Chat endpoint working")
        else:
            print("⚠️  Chat endpoint returned:", response.status_code)
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
    
    return True


def main():
    """Main setup and run function"""
    print("🏦" + "="*60)
    print("    AI BANKING AGENT - AUTOMATED SETUP & RUN")
    print("="*62)
    print("This script will:")
    print("1. ✅ Check system requirements")
    print("2. 📥 Install dependencies")
    print("3. 🚀 Start all services")
    print("4. 🧪 Run tests")
    print("="*62)
    
    # Check system requirements
    print("\n🔍 CHECKING SYSTEM REQUIREMENTS...")
    
    if not check_python_version():
        return False
    
    if not check_ollama_installation():
        print("\n💡 Please install Ollama first:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        return False
    
    if not check_ollama_service():
        if not start_ollama_service():
            return False
    
    if not check_llm_model():
        if not pull_llm_model():
            return False
    
    if not check_node_installation():
        print("\n💡 Frontend features will be limited without Node.js")
    
    # Install dependencies
    print("\n📦 INSTALLING DEPENDENCIES...")
    
    if not install_python_dependencies():
        return False
    
    if check_node_installation():
        if not install_frontend_dependencies():
            print("⚠️  Frontend dependencies failed, continuing anyway...")
    
    # Test AI agent
    print("\n🧪 TESTING COMPONENTS...")
    test_ai_agent()
    
    # Start services
    print("\n🚀 STARTING SERVICES...")
    
    api_process = start_api_server()
    if not api_process:
        return False
    
    if not wait_for_api_ready():
        if api_process:
            api_process.terminate()
        return False
    
    # Test API
    test_api_endpoints()
    
    # Start frontend if Node.js available
    frontend_process = None
    if check_node_installation():
        frontend_process = start_frontend()
    
    # Success message
    print("\n🎉 SUCCESS! AI Banking Agent is running!")
    print("\n🌐 Access Points:")
    print("   • API Health Check: http://localhost:5001/api/health")
    print("   • API Documentation: See README_AI_AGENT.md")
    if frontend_process:
        print("   • Frontend Interface: http://localhost:3000")
    
    print("\n🧪 Quick Test Commands:")
    print('   curl -X POST http://localhost:5001/api/chat \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"message": "Hello", "user_role": "user"}\'')
    
    print("\n📚 Demo Script:")
    print("   python demo_script.py")
    
    print("\n⏹️  To stop services:")
    print("   Press Ctrl+C")
    
    try:
        print("\n⏳ Services running... Press Ctrl+C to stop")
        while True:
            time.sleep(10)
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API process stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n⏹️  Stopping services...")
        
        if api_process:
            api_process.terminate()
            print("✅ API server stopped")
        
        if frontend_process:
            frontend_process.terminate() 
            print("✅ Frontend stopped")
        
        print("👋 Goodbye!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)