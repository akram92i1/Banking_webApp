import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const authService = {
    login: async (credentials) => {
        try {
            console.log('Attempting login with:', credentials.identifier);
            const response = await api.post('/api/auth/login', {
                identifier: credentials.identifier,
                password: credentials.password,
            });

            const { token, expirationTime, message } = response.data;

            if (token) {
                await AsyncStorage.setItem('token', token);
                await AsyncStorage.setItem('tokenExpiration', expirationTime.toString());

                const userInfo = {
                    email: credentials.identifier,
                    loginTime: new Date().toISOString(),
                    role: 'USER'
                };
                await AsyncStorage.setItem('user', JSON.stringify(userInfo));

                console.log('Login successful, token stored');
                return { success: true, token, user: userInfo };
            }
            return { success: false, message: 'No token received' };
        } catch (error) {
            console.error('Login error:', error);
            return {
                success: false,
                message: error.response?.data || 'Login failed'
            };
        }
    },

    logout: async () => {
        try {
            await api.post('/api/auth/logout');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            await AsyncStorage.removeItem('token');
            await AsyncStorage.removeItem('user');
            await AsyncStorage.removeItem('tokenExpiration');
        }
    },

    getCurrentUser: async () => {
        try {
            const storedUser = await AsyncStorage.getItem('user');
            if (storedUser) {
                return JSON.parse(storedUser);
            }
            return {
                email: 'Unknown User',
                role: 'USER',
                loginTime: new Date().toISOString()
            };
        } catch (error) {
            console.error('Get user error:', error);
            throw error;
        }
    },

    isAuthenticated: async () => {
        try {
            const token = await AsyncStorage.getItem('token');
            const expiration = await AsyncStorage.getItem('tokenExpiration');

            if (!token || !expiration) return false;

            const currentTime = Date.now();
            const expirationTime = parseInt(expiration);

            if (currentTime >= expirationTime) {
                await AsyncStorage.removeItem('token');
                await AsyncStorage.removeItem('user');
                await AsyncStorage.removeItem('tokenExpiration');
                return false;
            }
            return true;
        } catch (e) {
            return false;
        }
    },

    getToken: async () => {
        return await AsyncStorage.getItem('token');
    },

    getStoredUser: async () => {
        try {
            const user = await AsyncStorage.getItem('user');
            return user ? JSON.parse(user) : null;
        } catch (e) {
            return null;
        }
    },

    testAuth: async () => {
        try {
            const response = await api.get('/api/auth/test');
            return { success: true, message: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Auth test failed' };
        }
    }
};

export default authService;
