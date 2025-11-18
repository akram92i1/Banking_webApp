# AI Banking Agent with LangChain - Complete Guide

## 🎯 Overview

This AI Banking Agent combines **threat detection for admins** and **financial advisory for users** using LangChain and local LLMs. It integrates with your existing banking system to provide intelligent security analysis and personalized financial advice.

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │    │   Flask API      │    │  AI Agent Core  │
│                 │◄──►│                  │◄──►│                 │
│ • Chat Interface│    │ • REST Endpoints │    │ • LangChain     │
│ • Admin Dashboard│   │ • CORS Support   │    │ • Ollama LLM    │
│ • User Advisory │    │ • JSON APIs      │    │ • Memory/Tools  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Existing Systems │
                       │                  │
                       │ • Log Analysis   │
                       │ • Q-Learning RL  │
                       │ • Security Agent │
                       │ • Database       │
                       └──────────────────┘
```

## 🚀 Features

### 🔒 Admin Security Features
- **Real-time threat detection** using ML and RL
- **Comprehensive log analysis** with AI insights
- **Security dashboard** with key metrics
- **Intelligent threat prioritization**
- **Automated response recommendations**

### 💰 User Financial Features
- **Spending pattern analysis** 
- **Personalized savings recommendations**
- **Local grocery deal finder**
- **Budget optimization suggestions**
- **Interactive financial coaching**

## 🛠️ Installation & Setup

### 1. Prerequisites

```bash
# Install Ollama (for local LLM)
# Visit: https://ollama.ai/download
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required model
ollama pull llama3.2
# OR
ollama pull mistral
```

### 2. Python Environment

```bash
cd logging/

# Create virtual environment
python -m venv ai_agent_env
source ai_agent_env/bin/activate  # Linux/Mac
# OR
ai_agent_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirement.txt
```

### 3. Frontend Dependencies

```bash
cd ../finance_front_end/

# Install React dependencies (lucide-react for icons)
npm install lucide-react
```

## 🔧 Key LangChain Concepts Explained

### 1. **ChatOllama** - Local LLM Integration
```python
from langchain_ollama import ChatOllama

# Benefits: Privacy, no API costs, offline capability
llm = ChatOllama(
    model="llama3.2",
    temperature=0.1,  # Low for consistent responses
    top_p=0.9
)
```

### 2. **PromptTemplate** - Structured AI Interactions
```python
from langchain_core.prompts import ChatPromptTemplate

# Creates reusable prompt structures
security_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a cybersecurity expert..."),
    ("human", "Analyze this data: {log_data}")
])
```

### 3. **Memory** - Conversation Context
```python
from langchain.memory import ConversationBufferWindowMemory

# Keeps last 10 exchanges for context-aware responses
memory = ConversationBufferWindowMemory(
    k=10,
    return_messages=True
)
```

### 4. **Tools** - Function Calling
```python
from langchain.tools import BaseTool

class LogAnalysisTool(BaseTool):
    name = "analyze_security_logs"
    description = "Analyze security logs for threats"
    
    def _run(self, log_file_path: str) -> str:
        # AI can call this function
        return analyze_logs(log_file_path)
```

### 5. **Agents** - Intelligent Decision Making
```python
from langchain.agents import initialize_agent

# AI that can use tools and make decisions
agent = initialize_agent(
    tools=[log_tool, rl_tool],
    llm=llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION
)
```

### 6. **Output Parsers** - Structured Data
```python
from langchain_core.output_parsers import JsonOutputParser

# Ensures AI returns structured JSON
parser = JsonOutputParser()
chain = prompt | llm | parser
```

## 🚀 Running the System

### 1. Start Ollama Service
```bash
# Make sure Ollama is running
ollama serve
```

### 2. Start AI Agent API
```bash
cd logging/
python api_server.py
# Server starts on http://localhost:5001
```

### 3. Start React Frontend
```bash
cd finance_front_end/
npm start
# Frontend starts on http://localhost:3000
```

### 4. Start Banking API (Optional)
```bash
cd banking-api/demo/
mvn spring-boot:run
# API starts on http://localhost:8082
```

## 📋 API Endpoints

### Admin Endpoints
```bash
# Security Dashboard
GET /api/admin/dashboard

# Comprehensive Threat Analysis
POST /api/admin/security-analysis
{
  "user_id": "admin001",
  "transaction_data": {...},
  "location": "toronto"
}
```

### User Endpoints
```bash
# Financial Advice
POST /api/user/financial-advice
{
  "user_id": "user001",
  "location": "toronto", 
  "spending_data": {
    "week1": 120.50,
    "week2": 145.30
  },
  "category": "grocery"
}

# Chat Interface
POST /api/chat
{
  "message": "How can I save money?",
  "user_id": "user001",
  "user_role": "user",
  "location": "toronto"
}
```

## 🎮 Usage Examples

### Admin Security Analysis
```python
# Run comprehensive security analysis
agent = AIBankingAgent()

admin_context = UserContext(
    user_id="admin001",
    role=UserRole.ADMIN,
    location="toronto"
)

# Analyze transaction for threats
threat_analysis = await agent.analyze_security_threats(
    transaction_data={
        "amount": 15000,
        "location": "foreign",
        "user_id": "suspicious_user"
    },
    user_context=admin_context
)

print(f"Threat: {threat_analysis.threat_detected}")
print(f"Severity: {threat_analysis.severity}")
print(f"Recommendation: {threat_analysis.recommendation}")
```

### User Financial Advisory
```python
# Get personalized financial advice
user_context = UserContext(
    user_id="user001", 
    role=UserRole.USER,
    location="toronto"
)

advice = await agent.provide_financial_advice(
    user_context=user_context,
    spending_data={
        "week1": 120.50,
        "week2": 145.30,
        "week3": 135.80,
        "week4": 160.20
    },
    category="grocery"
)

print(f"Weekly Spending: ${advice.weekly_spending}")
print(f"Recommended Reduction: ${advice.recommended_reduction}")
print("Suggestions:", advice.savings_suggestions)
```

## 🎨 Frontend Integration

The AI Assistant appears as a floating chat bubble in the bottom-right corner:

### User View Features:
- 💬 **Natural language chat** 
- 📊 **Spending analysis tab**
- 🛒 **Quick action buttons** (Grocery Savings, Spending Analysis, Local Deals)
- 🎯 **Local deal finder**

### Admin View Features:
- 🔒 **Security chat** for threat queries
- 📈 **Security dashboard tab** 
- 🚨 **Quick actions** (Security Status, Log Analysis, Threat Scan)
- 📊 **Real-time metrics**

## 🔧 Customization

### Adding New Tools
```python
class CustomTool(BaseTool):
    name = "custom_analysis"
    description = "Performs custom analysis"
    
    def _run(self, data: str) -> str:
        # Your custom logic here
        return process_data(data)

# Add to agent
agent.tools.append(CustomTool())
```

### Modifying Prompts
```python
# Customize system prompts
custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a specialized banking AI with focus on..."),
    ("human", "{user_input}")
])
```

### Adding New LLM Models
```python
# Switch to different Ollama models
llm = ChatOllama(model="mistral")  # or "codellama", "vicuna", etc.
```

## 🧪 Testing

### Run Demo Scripts
```bash
# Test core AI agent
python ai_banking_agent.py

# Test API endpoints
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_role": "user"}'
```

### Frontend Testing
1. Open React app at `http://localhost:3000`
2. Click the AI Assistant button (bottom-right)
3. Test both user and admin functionalities

## 🔍 Monitoring & Debugging

### Logs
- AI Agent logs: `/app/logs/security_agent.log`
- Flask API logs: Console output
- Frontend: Browser developer tools

### Database
- Security events: `/app/data/security_events.db`
- SQLite browser for inspection

## 🚀 Production Deployment

### Security Considerations
1. **API Authentication**: Add JWT tokens
2. **HTTPS**: Use SSL certificates
3. **Rate Limiting**: Prevent API abuse
4. **Input Validation**: Sanitize all inputs

### Performance Optimization
1. **Connection Pooling**: Database connections
2. **Caching**: LLM responses for common queries
3. **Load Balancing**: Multiple AI agent instances
4. **Model Optimization**: Fine-tune Ollama models

## 📚 Learning Resources

### LangChain Documentation
- [LangChain Official Docs](https://python.langchain.com/docs/get_started/introduction)
- [Ollama Integration](https://python.langchain.com/docs/integrations/llms/ollama)

### Banking AI Best Practices
- [Financial AI Ethics](https://www.federalreserve.gov/publications/files/machine-learning-in-banking.pdf)
- [Security in AI Systems](https://owasp.org/www-project-machine-learning-security-top-10/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-capability`)
3. Commit changes (`git commit -am 'Add new capability'`)
4. Push to branch (`git push origin feature/new-capability`)
5. Create Pull Request

## 📄 License

This project is part of the banking application system. Refer to the main project license.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section below
2. Review logs for error details
3. Test individual components separately
4. Contact the development team

## 🔧 Troubleshooting

### Common Issues

**Ollama not responding:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

**Frontend can't connect to API:**
- Verify API is running on port 5001
- Check CORS configuration
- Ensure correct API_BASE URL in AIAssistant.js

**LangChain import errors:**
```bash
# Reinstall with correct versions
pip install langchain==0.1.0 langchain-ollama==0.1.0
```

**Memory/Performance issues:**
- Reduce conversation memory window
- Use smaller LLM models
- Implement request queuing

This comprehensive AI Banking Agent demonstrates the power of LangChain for creating intelligent, context-aware financial applications! 🚀