import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

const getBaseUrl = (port) => {
    if (Platform.OS === 'android') {
        return `http://10.0.2.2:${port}/api`;
    }
    // iOS physical device over Wi-Fi needs your computer's local IP address
    return `http://192.168.0.19:${port}/api`;
};

const aiApi = axios.create({
    baseURL: getBaseUrl(5000),
    timeout: 300000,
    headers: {
        'Content-Type': 'application/json',
    },
});

const bankingApi = axios.create({
    baseURL: getBaseUrl(8082),
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

const setupInterceptors = () => {
    [aiApi, bankingApi].forEach(api => {
        api.interceptors.request.use(
            async (config) => {
                try {
                    const token = await AsyncStorage.getItem('token');
                    if (token) {
                        config.headers.Authorization = `Bearer ${token}`;
                    }
                } catch (error) {
                    // ignore
                }
                console.log(`🤖 AI Service Request: ${config.method?.toUpperCase()} ${config.url}`);
                return config;
            },
            (error) => Promise.reject(error)
        );

        api.interceptors.response.use(
            (response) => {
                console.log(`✅ AI Service Response: ${response.status} for ${response.config.method?.toUpperCase()} ${response.config.url}`);
                return response;
            },
            async (error) => {
                console.error(`❌ AI Service Error: ${error.response?.status}`, error.response?.data);
                if (error.response?.status === 401) {
                    await AsyncStorage.removeItem('token');
                    await AsyncStorage.removeItem('user');
                }
                return Promise.reject(error);
            }
        );
    });
};

setupInterceptors();

const aiService = {
    // ... (Identical structure to web, adapting API calls)
    async checkHealth() {
        try {
            const [aiHealth, bankingAiHealth] = await Promise.allSettled([
                aiApi.get('/health'),
                bankingApi.get('/health') // Assuming banking also has health
            ]);
            return {
                aiAgent: aiHealth.status === 'fulfilled' ? aiHealth.value.data : { status: 'unavailable' },
                bankingIntegration: bankingAiHealth.status === 'fulfilled' ? bankingAiHealth.value.data : { status: 'unavailable' }
            };
        } catch (error) {
            return { aiAgent: { status: 'error' }, bankingIntegration: { status: 'error' } };
        }
    },

    async chat(message, userContext = {}) {
        try {
            try {
                const response = await bankingApi.post('/chat', {
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
            throw new Error(`Chat service unavailable`);
        }
    },

    async adviceChat(message, userContext = {}) {
        try {
            const response = await aiApi.post('/advice-chat', {
                message,
                user_id: userContext.userId || 'user001',
                user_role: userContext.userRole || 'user',
                location: userContext.location || 'toronto',
                preferences: userContext.preferences || {}
            });
            return {
                success: true,
                response: response.data.response,
                source: 'ai_agent_advice',
                timestamp: response.data.timestamp
            };
        } catch (error) {
            throw new Error(`Advice Chat service unavailable`);
        }
    },

    async getFinancialAdvice(userContext = {}) {
        try {
            try {
                const response = await bankingApi.post('/financial-advice', {
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
                const response = await aiApi.post('/user/financial-advice', {
                    user_id: userContext.userId || 'user001',
                    location: userContext.location || 'toronto',
                    spending_data: userContext.spendingData || { week1: 120.50 },
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
            throw new Error(`Financial advice service unavailable`);
        }
    },

    async getSecurityAnalysis(userContext = {}) {
        try {
            try {
                const response = await bankingApi.post('/security-analysis', {
                    location: userContext.location || 'toronto'
                });
                return {
                    success: true,
                    analysis: response.data.analysis,
                    system_data: response.data.system_data,
                    source: 'banking_integrated'
                };
            } catch (e) {
                const response = await aiApi.post('/admin/security-analysis', {
                    user_id: userContext.userId || 'admin001',
                    location: userContext.location || 'toronto'
                });
                return {
                    success: true,
                    analysis: response.data.analysis,
                    system_data: response.data.system_data,
                    source: 'ai_agent_direct'
                };
            }
        } catch (error) {
            throw new Error(`Security analysis service unavailable`);
        }
    },

    async getSecurityDashboard() {
        try {
            const response = await aiApi.get('/admin/dashboard');
            return { success: true, dashboard: response.data.dashboard };
        } catch (error) {
            throw new Error(`Security dashboard unavailable`);
        }
    },

    async analyzeSpending(userContext = {}) {
        try {
            try {
                const response = await bankingApi.get('/user/spending-summary');
                return { success: true, analysis: response.data.spending_summary, source: 'banking_integrated' };
            } catch (e) {
                const response = await aiApi.post('/user/spending-analysis', {
                    email: userContext.email || userContext.userId || 'user@example.com',
                    transactions: userContext.transactions || []
                });
                return { success: true, analysis: response.data.analysis, source: 'ai_agent_direct' };
            }
        } catch (error) {
            throw new Error(`Spending analysis unavailable`);
        }
    },

    async getGroceryDeals(location = 'toronto') {
        try {
            const response = await aiApi.get(`/grocery-deals/${location}`);
            return { success: true, deals: response.data.deals, location: response.data.location };
        } catch (error) {
            throw new Error(`Grocery deals unavailable`);
        }
    }
};

export default aiService;
