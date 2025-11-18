import React, { useState, useEffect } from 'react';
import { MessageCircle, Brain, TrendingDown, Shield, Send, X, Minimize2 } from 'lucide-react';

const AIAssistant = ({ userRole = 'user', userId = 'user001', location = 'toronto' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [financialAdvice, setFinancialAdvice] = useState(null);
  const [securityData, setSecurityData] = useState(null);

  // API base URL - adjust as needed
  const API_BASE = 'http://localhost:5001/api';

  useEffect(() => {
    // Initialize with welcome message based on user role
    const welcomeMessage = userRole === 'admin' 
      ? "Hello Admin! I can help you with security analysis, threat detection, and system monitoring. How can I assist you today?"
      : "Hi there! I'm your financial advisor. I can help you save money, analyze spending patterns, and find great deals. What would you like to know?";
    
    setMessages([{
      id: 1,
      text: welcomeMessage,
      sender: 'ai',
      timestamp: new Date()
    }]);
  }, [userRole]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          user_id: userId,
          user_role: userRole,
          location: location
        })
      });

      const data = await response.json();

      if (data.success) {
        const aiMessage = {
          id: messages.length + 2,
          text: data.response,
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(data.error || 'Failed to get response');
      }
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        sender: 'ai',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  };

  const getFinancialAdvice = async () => {
    setIsLoading(true);
    try {
      // Mock spending data - in real app, this would come from transaction history
      const spendingData = {
        week1: 120.50,
        week2: 145.30,
        week3: 135.80,
        week4: 160.20
      };

      const response = await fetch(`${API_BASE}/user/financial-advice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          location: location,
          spending_data: spendingData,
          category: 'grocery',
          target_reduction: 30.00
        })
      });

      const data = await response.json();

      if (data.success) {
        setFinancialAdvice(data.advice);
      } else {
        throw new Error(data.error || 'Failed to get financial advice');
      }
    } catch (error) {
      console.error('Error getting financial advice:', error);
      setFinancialAdvice({
        analysis_summary: 'Unable to generate advice at this time.',
        weekly_spending: 0,
        recommended_reduction: 0,
        savings_suggestions: ['Please try again later.'],
        grocery_deals: [],
        action_plan: 'Contact support if the issue persists.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getSecurityData = async () => {
    if (userRole !== 'admin') return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/dashboard`);
      const data = await response.json();

      if (data.success) {
        setSecurityData(data.dashboard);
      } else {
        throw new Error(data.error || 'Failed to get security data');
      }
    } catch (error) {
      console.error('Error getting security data:', error);
      setSecurityData({
        recent_threats: [],
        blocked_ips_count: 0,
        suspicious_users_count: 0,
        total_events_24h: 0,
        top_attack_types: []
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Quick action buttons based on user role
  const QuickActions = () => {
    if (userRole === 'admin') {
      return (
        <div className="flex flex-wrap gap-2 mb-4">
          <button 
            onClick={() => setInputMessage('Show me the latest security threats')}
            className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm hover:bg-red-200"
          >
            🚨 Security Status
          </button>
          <button 
            onClick={() => setInputMessage('Analyze recent log files')}
            className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm hover:bg-orange-200"
          >
            📊 Log Analysis
          </button>
          <button 
            onClick={() => setInputMessage('Run threat detection scan')}
            className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm hover:bg-yellow-200"
          >
            🔍 Threat Scan
          </button>
        </div>
      );
    } else {
      return (
        <div className="flex flex-wrap gap-2 mb-4">
          <button 
            onClick={() => setInputMessage('How can I save money on groceries?')}
            className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm hover:bg-green-200"
          >
            🛒 Grocery Savings
          </button>
          <button 
            onClick={() => setInputMessage('Analyze my spending this week')}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200"
          >
            📈 Spending Analysis
          </button>
          <button 
            onClick={() => setInputMessage('Find deals near me')}
            className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm hover:bg-purple-200"
          >
            🎯 Local Deals
          </button>
        </div>
      );
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-full shadow-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2"
        >
          <Brain className="w-6 h-6" />
          <span className="hidden md:inline">AI Assistant</span>
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed bottom-6 right-6 bg-white rounded-lg shadow-2xl z-50 transition-all duration-300 ${
      isMinimized ? 'w-80 h-16' : 'w-96 h-[600px]'
    }`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain className="w-5 h-5" />
          <span className="font-semibold">
            {userRole === 'admin' ? '🔒 Security Agent' : '💰 Financial Advisor'}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="hover:bg-white/20 p-1 rounded"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="hover:bg-white/20 p-1 rounded"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Tabs */}
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 py-2 px-4 text-sm font-medium ${
                activeTab === 'chat' 
                  ? 'border-b-2 border-blue-500 text-blue-600 bg-blue-50' 
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageCircle className="w-4 h-4 inline mr-1" />
              Chat
            </button>
            
            {userRole === 'admin' ? (
              <button
                onClick={() => {
                  setActiveTab('security');
                  if (!securityData) getSecurityData();
                }}
                className={`flex-1 py-2 px-4 text-sm font-medium ${
                  activeTab === 'security' 
                    ? 'border-b-2 border-red-500 text-red-600 bg-red-50' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <Shield className="w-4 h-4 inline mr-1" />
                Security
              </button>
            ) : (
              <button
                onClick={() => {
                  setActiveTab('advice');
                  if (!financialAdvice) getFinancialAdvice();
                }}
                className={`flex-1 py-2 px-4 text-sm font-medium ${
                  activeTab === 'advice' 
                    ? 'border-b-2 border-green-500 text-green-600 bg-green-50' 
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <TrendingDown className="w-4 h-4 inline mr-1" />
                Advice
              </button>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 flex flex-col h-[500px]">
            {activeTab === 'chat' && (
              <div className="flex flex-col h-full">
                {/* Quick Actions */}
                <div className="p-3 border-b bg-gray-50">
                  <QuickActions />
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs px-3 py-2 rounded-lg ${
                          message.sender === 'user'
                            ? 'bg-blue-500 text-white'
                            : message.isError
                            ? 'bg-red-100 text-red-700'
                            : 'bg-gray-200 text-gray-800'
                        }`}
                      >
                        <p className="text-sm">{message.text}</p>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-200 px-3 py-2 rounded-lg">
                        <p className="text-sm">AI is thinking...</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Input */}
                <div className="p-3 border-t flex gap-2">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything..."
                    className="flex-1 border rounded-lg px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="2"
                  />
                  <button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'security' && userRole === 'admin' && (
              <div className="p-4 overflow-y-auto">
                <h3 className="font-semibold mb-3">Security Dashboard</h3>
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                    <p className="mt-2 text-sm text-gray-600">Loading security data...</p>
                  </div>
                ) : securityData ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-red-50 p-3 rounded-lg">
                        <p className="text-xs text-gray-600">Blocked IPs</p>
                        <p className="text-lg font-semibold text-red-600">{securityData.blocked_ips_count}</p>
                      </div>
                      <div className="bg-yellow-50 p-3 rounded-lg">
                        <p className="text-xs text-gray-600">Suspicious Users</p>
                        <p className="text-lg font-semibold text-yellow-600">{securityData.suspicious_users_count}</p>
                      </div>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">Events (24h)</p>
                      <p className="text-lg font-semibold text-blue-600">{securityData.total_events_24h}</p>
                    </div>
                    <button 
                      onClick={() => setInputMessage('Generate detailed security report')}
                      className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600"
                    >
                      Generate Full Report
                    </button>
                  </div>
                ) : (
                  <p className="text-gray-600">Failed to load security data.</p>
                )}
              </div>
            )}

            {activeTab === 'advice' && userRole !== 'admin' && (
              <div className="p-4 overflow-y-auto">
                <h3 className="font-semibold mb-3">Financial Advice</h3>
                {isLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                    <p className="mt-2 text-sm text-gray-600">Analyzing your spending...</p>
                  </div>
                ) : financialAdvice ? (
                  <div className="space-y-3">
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">Weekly Spending</p>
                      <p className="text-lg font-semibold text-green-600">${financialAdvice.weekly_spending.toFixed(2)}</p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-xs text-gray-600">Potential Savings</p>
                      <p className="text-lg font-semibold text-blue-600">${financialAdvice.recommended_reduction.toFixed(2)}</p>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium">💡 Suggestions:</p>
                      {financialAdvice.savings_suggestions.slice(0, 3).map((suggestion, index) => (
                        <p key={index} className="text-xs text-gray-600">• {suggestion}</p>
                      ))}
                    </div>
                    <button 
                      onClick={() => setInputMessage('Show me more detailed savings plan')}
                      className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
                    >
                      Get Detailed Plan
                    </button>
                  </div>
                ) : (
                  <p className="text-gray-600">Failed to load financial advice.</p>
                )}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AIAssistant;