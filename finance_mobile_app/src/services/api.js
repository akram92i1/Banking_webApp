import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

// For Android emulator it needs to be 10.0.2.2. For physical iOS devices, use local IP.
const getBaseUrl = () => {
    if (Platform.OS === 'android') {
        return 'http://10.0.2.2:8082'; // Android Emulator
    }
    // iOS physical device over Wi-Fi needs your computer's local IP address
    return 'http://192.168.0.19:8082';
};

const api = axios.create({
    baseURL: getBaseUrl(),
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

console.log('🔧 API configured with baseURL:', api.defaults.baseURL);

// Request interceptor to add auth token
api.interceptors.request.use(
    async (config) => {
        if (config.method?.toLowerCase() === 'get') {
            console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.params || 'No parameters');
        } else {
            console.log(`🌐 API Request: ${config.method?.toUpperCase()} ${config.url}`, config.data);
        }

        try {
            const token = await AsyncStorage.getItem('token');
            if (token) {
                config.headers.Authorization = `Bearer ${token}`;
                console.log('🔑 Added auth token to request');
            }
        } catch (error) {
            console.error('Error fetching token from AsyncStorage', error);
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

        if (typeof response.data === 'string' && response.data.length > 0) {
            try {
                const parsedData = JSON.parse(response.data);
                response.data = parsedData;
            } catch (parseError) {
                // Ignore
            }
        }

        return response;
    },
    async (error) => {
        console.error(`❌ API Error: ${error.response?.status}`, error.response?.data);
        if (error.response?.status === 401) {
            // Token expired or invalid, clear storage
            await AsyncStorage.removeItem('token');
            await AsyncStorage.removeItem('user');
            // Navigation redirect should be handled globally or in context
        }
        return Promise.reject(error);
    }
);

export default api;
