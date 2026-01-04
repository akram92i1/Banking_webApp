import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Brain, TrendingDown, Shield, Send, X, Minimize2, Wifi, WifiOff, Sparkles, Lock, Database } from 'lucide-react';
import aiService from '../services/aiService';

const ThinkingIndicator = () => {
  const [step, setStep] = useState(0);
  const steps = [
    "Analyzing Request...",
    "Accessing Secure Database...",
    "Processing Financial Data...",
    "Formulating Response..."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % steps.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center space-x-3 p-4 bg-white rounded-xl border border-gray-100 shadow-sm animate-fade-in-up w-fit">
      <div className="flex space-x-1">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-thinking" style={{ animationDelay: '0s' }}></div>
        <div className="w-2 h-2 bg-purple-500 rounded-full animate-thinking" style={{ animationDelay: '0.2s' }}></div>
        <div className="w-2 h-2 bg-pink-500 rounded-full animate-thinking" style={{ animationDelay: '0.4s' }}></div>
      </div>
      <span className="text-xs font-medium text-gray-400 animate-pulse">{steps[step]}</span>
    </div>
  );
};

const AIAssistant = ({ userRole = 'user', userId = 'user001', location = 'toronto' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [financialAdvice, setFinancialAdvice] = useState(null);
  const [securityData, setSecurityData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [serviceInfo, setServiceInfo] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    // Initialize AI service and check connection
    const initializeAI = async () => {
      try {
        setConnectionStatus('checking');
        const health = await aiService.checkHealth();
        setServiceInfo(health);
        setConnectionStatus('connected');

        let welcomeMessage;
        if (userRole === 'admin') {
          welcomeMessage = health.bankingIntegration?.status === 'healthy'
            ? "🔒 System Initialized. Administrative Access Granted. I am ready for security analysis and threat monitoring."
            : "🔒 System Initialized. Limited Mode Active.";
        } else {
          welcomeMessage = health.bankingIntegration?.status === 'healthy'
            ? "💰 Hello! I'm your Banking AI. I have secure access to your account data. How can I help you optimize your finances today?"
            : "💰 Hello! I'm currently operating in offline mode. I can still provide general advice.";
        }

        setMessages([{
          id: 1,
          text: welcomeMessage,
          sender: 'ai',
          timestamp: new Date(),
          serviceStatus: health
        }]);

      } catch (error) {
        console.error('AI initialization failed:', error);
        setConnectionStatus('error');
        setMessages([{
          id: 1,
          text: "⚠️ Neural Link Unstable. Retrying connection...",
          sender: 'ai',
          timestamp: new Date(),
          isError: true
        }]);
      }
    };

    initializeAI();
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
      const userContext = {
        userId,
        userRole,
        location,
        preferences: { theme: 'banking' }
      };

      // Simulate a small delay for "Processing" feel if response is too fast
      const [result] = await Promise.all([
        aiService.chat(inputMessage, userContext),
        new Promise(resolve => setTimeout(resolve, 1500)) // Min 1.5s wait for animation
      ]);

      const aiMessage = {
        id: messages.length + 2,
        text: result.response,
        sender: 'ai',
        timestamp: new Date(),
        source: result.source,
        context: result.context
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: `Error: ${error.message}. Please retry.`,
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
      const userContext = {
        userId,
        location,
        targetReduction: 30.00
      };

      const result = await aiService.getFinancialAdvice(userContext);
      setFinancialAdvice({
        ...result.advice,
        dataSource: result.source,
        hasRealData: result.spending_analysis || result.real_data
      });

    } catch (error) {
      setFinancialAdvice({
        analysis_summary: 'Unable to generate advice.',
        weekly_spending: 0,
        recommended_reduction: 0,
        savings_suggestions: ['Service unavailable'],
        grocery_deals: [],
        action_plan: 'Retry later.',
        dataSource: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getSecurityData = async () => {
    if (userRole !== 'admin') return;
    setIsLoading(true);
    try {
      const result = await aiService.getSecurityDashboard();
      setSecurityData({
        ...result.dashboard,
        dataSource: 'integrated',
        hasRealData: true
      });
    } catch (error) {
      setSecurityData({
        recent_threats: [],
        blocked_ips_count: 0,
        suspicious_users_count: 0,
        total_events_24h: 0,
        top_attack_types: [],
        dataSource: 'error'
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

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 sm:bottom-6 sm:right-6 z-50">
        <button
          onClick={() => setIsOpen(true)}
          className="relative w-14 h-14 sm:w-16 sm:h-16 group animate-float active:scale-95 transition-transform"
        >
          {/* Enhanced Orb Button - Dark Mode Theme Compatible */}
          <div className="absolute inset-0 bg-blue-600 rounded-full blur-lg opacity-50 group-hover:opacity-75 transition-opacity duration-300"></div>
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800 via-blue-900 to-slate-900 rounded-full shadow-2xl border-2 border-white/20 flex items-center justify-center overflow-hidden">
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
            <Brain className="w-6 h-6 sm:w-8 sm:h-8 text-white z-10 filter drop-shadow-md group-hover:scale-110 transition-transform duration-300" />

            {/* Shimmer */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
          </div>

          {/* Notification Dot */}
          <div className="absolute -top-1 -right-1 w-3 h-3 sm:w-4 sm:h-4 bg-green-500 rounded-full border-2 border-white animate-pulse"></div>
        </button>
      </div>
    );
  }

  return (
    <div className={`fixed z-50 transition-all duration-300 flex flex-col overflow-hidden shadow-2xl
      bg-white border border-gray-200
      /* Mobile Styles (Bottom Sheet) */
      inset-x-0 bottom-0 rounded-t-2xl
      ${isMinimized ? 'h-16' : 'h-[60vh]'}
      
      /* Desktop Styles (Floating Widget) */
      sm:inset-auto sm:bottom-6 sm:right-6 sm:rounded-2xl
      sm:${isMinimized ? 'w-64 h-16' : 'w-80 h-[600px] max-h-[600px] max-w-[320px]'}
    `}>
      {/* Header - Dark Gradient for Contrast */}
      <div className="bg-slate-900 text-white p-4 flex items-center justify-between shadow-lg shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
            <Brain className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-sm tracking-wide text-white">
              {userRole === 'admin' ? 'CYBER SECURITY AI' : 'BANKING ASSISTANT'}
            </h3>
            <div className="flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-500'}`}></span>
              <span className="text-[10px] uppercase tracking-wider text-gray-300">
                {connectionStatus === 'connected' ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex gap-2 text-gray-400">
          <button onClick={() => setIsMinimized(!isMinimized)} className="hover:text-white transition-colors">
            <Minimize2 className="w-4 h-4" />
          </button>
          <button onClick={() => setIsOpen(false)} className="hover:text-white transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Content Area - Light Mode */}
          <div className="flex-1 flex flex-col bg-slate-50 relative overflow-hidden">
            {/* Light Background Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.03)_1px,transparent_1px)] bg-[size:20px_20px]"></div>

            {/* Chat View */}
            {activeTab === 'chat' && (
              <div className="flex flex-col h-full relative z-10">
                {/* Messages List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}
                    >
                      <div className={`flex flex-col max-w-[85%] ${message.sender === 'user' ? 'items-end' : 'items-start'}`}>
                        <div
                          className={`px-4 py-3 rounded-2xl shadow-sm text-sm leading-relaxed ${message.sender === 'user'
                            ? 'bg-blue-600 text-white rounded-br-none'
                            : message.isError
                              ? 'bg-red-50 text-red-800 border border-red-100'
                              : 'bg-white text-gray-800 border border-gray-100 rounded-bl-none'
                            }`}
                        >
                          {message.text}
                        </div>
                        <span className="text-[10px] text-gray-400 mt-1 px-1">
                          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {message.sender === 'ai' ? 'AI Agent' : 'You'}
                        </span>
                      </div>
                    </div>
                  ))}

                  {isLoading && <ThinkingIndicator />}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input Area - Light Mode */}
                <div className="p-4 bg-white border-t border-gray-100 safe-area-bottom">
                  <div className="flex gap-2 items-end bg-gray-50 border border-gray-200 rounded-xl p-2 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask about finances..."
                      className="flex-1 bg-transparent border-none text-sm text-gray-800 placeholder-gray-400 focus:ring-0 resize-none max-h-32 py-2 px-1"
                      rows="1"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                      className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Advice Tab */}
            {activeTab === 'advice' && (
              <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                <p>Financial Analysis Module</p>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="flex items-center justify-center h-full text-gray-400 text-sm">
                <p>Security Dashboard Module</p>
              </div>
            )}

          </div>

          {/* Tab Bar - Light Mode */}
          <div className="bg-white border-t border-gray-100 p-2 flex justify-around shrink-0 relative z-20 pb-safe">
            <button
              onClick={() => setActiveTab('chat')}
              className={`p-2 rounded-lg transition-colors flex flex-col items-center gap-1 ${activeTab === 'chat' ? 'text-blue-600 bg-blue-50' : 'text-gray-400 hover:text-gray-600'}`}
            >
              <MessageCircle className="w-5 h-5" />
              <span className="text-[10px] font-medium">Chat</span>
            </button>
            {userRole === 'admin' ? (
              <button
                onClick={() => setActiveTab('security')}
                className={`p-2 rounded-lg transition-colors flex flex-col items-center gap-1 ${activeTab === 'security' ? 'text-red-600 bg-red-50' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <Shield className="w-5 h-5" />
                <span className="text-[10px] font-medium">Security</span>
              </button>
            ) : (
              <button
                onClick={() => setActiveTab('advice')}
                className={`p-2 rounded-lg transition-colors flex flex-col items-center gap-1 ${activeTab === 'advice' ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-gray-600'}`}
              >
                <TrendingDown className="w-5 h-5" />
                <span className="text-[10px] font-medium">Advice</span>
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default AIAssistant;