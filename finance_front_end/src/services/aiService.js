import axios from 'axios';

// AI Agent API configuration
const aiApi = axios.create({
  baseURL: 'http://localhost:5001/api', // AI Agent server
  timeout: 120000, // Increased to 2 mins for LLM processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Banking API configuration  
const bankingApi = axios.create({
  baseURL: 'http://localhost:8082/api', // Main Banking API
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptors for authentication
[aiApi, bankingApi].forEach(api => {
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      console.log(`🤖 AI Service Request: ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    (error) => {
      console.error('❌ AI Service Request Error:', error);
      return Promise.reject(error);
    }
  );

  api.interceptors.response.use(
    (response) => {
      console.log(`✅ AI Service Response: ${response.status} for ${response.config.method?.toUpperCase()} ${response.config.url}`);
      return response;
    },
    (error) => {
      console.error(`❌ AI Service Error: ${error.response?.status}`, error.response?.data);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
});

// AI Service Functions
const aiService = {

  // Health check for AI services
  async checkHealth() {
    try {
      const [aiHealth, bankingAiHealth] = await Promise.allSettled([
        aiApi.get('/health'),
        bankingApi.get('/ai/health')
      ]);

      return {
        aiAgent: aiHealth.status === 'fulfilled' ? aiHealth.value.data : { status: 'unavailable' },
        bankingIntegration: bankingAiHealth.status === 'fulfilled' ? bankingAiHealth.value.data : { status: 'unavailable' }
      };
    } catch (error) {
      console.error('Health check failed:', error);
      return { aiAgent: { status: 'error' }, bankingIntegration: { status: 'error' } };
    }
  },

  // Chat with AI Agent
  async chat(message, userContext = {}) {
    try {
      // Try banking API integration first (has user context and auth)
      try {
        const response = await bankingApi.post('/ai/chat', {
          message,
          location: userContext.location || 'toronto',
          preferences: userContext.preferences || {}
        });

        return {
          success: true,
          response: response.data.response,
          source: 'banking_integrated',
          context: response.data.user_context,
          timestamp: response.data.timestamp
        };
      } catch (bankingError) {
        console.warn('Banking API chat failed, falling back to direct AI agent:', bankingError.message);

        // Fallback to direct AI agent
        const response = await aiApi.post('/chat', {
          message,
          user_id: userContext.userId || 'user001',
          user_role: userContext.userRole || 'user',
          location: userContext.location || 'toronto',
          preferences: userContext.preferences || {}
        });

        return {
          success: true,
          response: response.data.response,
          source: 'ai_agent_direct',
          context: response.data.context,
          timestamp: response.data.timestamp
        };
      }
    } catch (error) {
      console.error('Chat failed:', error);
      throw new Error(`Chat service unavailable: ${error.response?.data?.error || error.message}`);
    }
  },

  // Get Financial Advice
  async getFinancialAdvice(userContext = {}) {
    try {
      // Try banking API integration first for real transaction data
      try {
        const response = await bankingApi.post('/ai/financial-advice', {
          location: userContext.location || 'toronto',
          category: 'grocery',
          target_reduction: userContext.targetReduction || null
        });

        return {
          success: true,
          advice: response.data.advice,
          spending_analysis: response.data.spending_analysis,
          source: 'banking_integrated',
          timestamp: response.data.timestamp
        };
      } catch (bankingError) {
        console.warn('Banking API advice failed, falling back to AI agent:', bankingError.message);

        // Fallback to direct AI agent with mock data
        const response = await aiApi.post('/user/financial-advice', {
          user_id: userContext.userId || 'user001',
          location: userContext.location || 'toronto',
          spending_data: userContext.spendingData || {
            week1: 120.50,
            week2: 145.30,
            week3: 135.80,
            week4: 160.20
          },
          category: 'grocery',
          target_reduction: userContext.targetReduction || 30.00
        });

        return {
          success: true,
          advice: response.data.advice,
          real_data: response.data.real_data,
          source: 'ai_agent_direct',
          timestamp: response.data.timestamp
        };
      }
    } catch (error) {
      console.error('Financial advice failed:', error);
      throw new Error(`Financial advice service unavailable: ${error.response?.data?.error || error.message}`);
    }
  },

  // Admin Security Analysis
  async getSecurityAnalysis(userContext = {}) {
    try {
      // Try banking API integration first
      try {
        const response = await bankingApi.post('/ai/security-analysis', {
          location: userContext.location || 'toronto'
        });

        return {
          success: true,
          analysis: response.data.analysis,
          system_data: response.data.system_data,
          source: 'banking_integrated',
          timestamp: response.data.timestamp
        };
      } catch (bankingError) {
        console.warn('Banking API security analysis failed, falling back to AI agent:', bankingError.message);

        // Fallback to direct AI agent
        const response = await aiApi.post('/admin/security-analysis', {
          user_id: userContext.userId || 'admin001',
          location: userContext.location || 'toronto'
        });

        return {
          success: true,
          analysis: response.data.analysis,
          system_data: response.data.system_data,
          source: 'ai_agent_direct',
          timestamp: response.data.timestamp
        };
      }
    } catch (error) {
      console.error('Security analysis failed:', error);
      throw new Error(`Security analysis service unavailable: ${error.response?.data?.error || error.message}`);
    }
  },

  // Get Security Dashboard
  async getSecurityDashboard() {
    try {
      const response = await aiApi.get('/admin/dashboard');

      return {
        success: true,
        dashboard: response.data.dashboard,
        timestamp: response.data.timestamp
      };
    } catch (error) {
      console.error('Security dashboard failed:', error);
      throw new Error(`Security dashboard unavailable: ${error.response?.data?.error || error.message}`);
    }
  },

  // Analyze User Spending
  async analyzeSpending(userContext = {}) {
    try {
      // Try to get real spending data from banking API
      try {
        const response = await bankingApi.get('/ai/user/spending-summary');

        return {
          success: true,
          analysis: response.data.spending_summary,
          source: 'banking_integrated',
          timestamp: response.data.timestamp
        };
      } catch (bankingError) {
        console.warn('Banking API spending analysis failed, falling back to AI agent:', bankingError.message);

        // Fallback to AI agent with transaction data
        const response = await aiApi.post('/user/spending-analysis', {
          user_id: userContext.userId || 'user001',
          transactions: userContext.transactions || []
        });

        return {
          success: true,
          analysis: response.data.analysis,
          source: 'ai_agent_direct',
          timestamp: response.data.timestamp
        };
      }
    } catch (error) {
      console.error('Spending analysis failed:', error);
      throw new Error(`Spending analysis service unavailable: ${error.response?.data?.error || error.message}`);
    }
  },

  // Get Grocery Deals
  async getGroceryDeals(location = 'toronto') {
    try {
      const response = await aiApi.get(`/grocery-deals/${location}`);

      return {
        success: true,
        deals: response.data.deals,
        location: response.data.location,
        timestamp: response.data.timestamp
      };
    } catch (error) {
      console.error('Grocery deals failed:', error);
      throw new Error(`Grocery deals service unavailable: ${error.response?.data?.error || error.message}`);
    }
  },

  // Smart service selection based on user role and request type
  async smartRequest(requestType, data = {}, userContext = {}) {
    const strategies = {
      'chat': () => this.chat(data.message, userContext),
      'financial_advice': () => this.getFinancialAdvice(userContext),
      'security_analysis': () => this.getSecurityAnalysis(userContext),
      'spending_analysis': () => this.analyzeSpending(userContext),
      'grocery_deals': () => this.getGroceryDeals(userContext.location)
    };

    const strategy = strategies[requestType];
    if (!strategy) {
      throw new Error(`Unknown request type: ${requestType}`);
    }

    try {
      console.log(`🧠 AI Smart Request: ${requestType}`, { userContext, data });
      const result = await strategy();
      console.log(`✅ AI Smart Response: ${requestType}`, result);
      return result;
    } catch (error) {
      console.error(`❌ AI Smart Request Failed: ${requestType}`, error);
      throw error;
    }
  },

  // Batch requests for dashboard
  async getDashboardData(userRole = 'user', userContext = {}) {
    try {
      if (userRole === 'admin') {
        const [healthCheck, securityDashboard, securityAnalysis] = await Promise.allSettled([
          this.checkHealth(),
          this.getSecurityDashboard(),
          this.getSecurityAnalysis(userContext)
        ]);

        return {
          health: healthCheck.status === 'fulfilled' ? healthCheck.value : null,
          security: securityDashboard.status === 'fulfilled' ? securityDashboard.value : null,
          analysis: securityAnalysis.status === 'fulfilled' ? securityAnalysis.value : null,
          userRole: 'admin'
        };
      } else {
        const [healthCheck, financialAdvice, spendingAnalysis, groceryDeals] = await Promise.allSettled([
          this.checkHealth(),
          this.getFinancialAdvice(userContext),
          this.analyzeSpending(userContext),
          this.getGroceryDeals(userContext.location)
        ]);

        return {
          health: healthCheck.status === 'fulfilled' ? healthCheck.value : null,
          financial: financialAdvice.status === 'fulfilled' ? financialAdvice.value : null,
          spending: spendingAnalysis.status === 'fulfilled' ? spendingAnalysis.value : null,
          deals: groceryDeals.status === 'fulfilled' ? groceryDeals.value : null,
          userRole: 'user'
        };
      }
    } catch (error) {
      console.error('Dashboard data failed:', error);
      throw new Error(`Dashboard data unavailable: ${error.message}`);
    }
  }
};

export default aiService;