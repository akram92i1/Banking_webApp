import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8082/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add debugging
console.log('🔧 API configured with baseURL:', api.defaults.baseURL);

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    // Better logging for GET vs POST requests
    if (config.method?.toLowerCase() === 'get') {
      console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params || 'No parameters');
    } else {
      console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
    }
    console.log("config structure ", config);
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔑 Added auth token to request');
    }
    return config;
  },
  (error) => {
    console.error('❌ Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} for ${response.config.method?.toUpperCase()} ${response.config.url}`);
    console.log('📦 Response Data:', response.data);
    console.log('📊 Data Type:', typeof response.data, 'Length:', Array.isArray(response.data) ? response.data.length : 'N/A');

    // Check if response is a string that should be JSON
    if (typeof response.data === 'string' && response.data.length > 0) {
      try {
        const parsedData = JSON.parse(response.data);
        console.log('🔧 Successfully parsed string response to JSON:', parsedData);
        response.data = parsedData;
      } catch (parseError) {
        console.warn('⚠️ Failed to parse string response as JSON:', parseError);
        console.log('📄 Raw string content:', response.data.substring(0, 200) + '...');
      }
    }

    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status}`, error.response?.data);
    if (error.response?.status === 401) {
      // Token expired or invalid, clear storage and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;