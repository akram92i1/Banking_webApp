import api from './api';

const authService = {
  // Login user
  login: async (credentials) => {
    try {
      console.log('Attempting login with:', credentials.identifier);
      const response = await api.post('/api/auth/login', {
        identifier: credentials.identifier, // email or card number
        password: credentials.password,
      });
      
      console.log('Login response:', response.data);
      
      const { token, expirationTime, message } = response.data;
      
      if (token) {
        // Store token in localStorage
        localStorage.setItem('token', token);
        localStorage.setItem('tokenExpiration', expirationTime.toString());
        
        // Create a basic user object from the credentials for now
        // Since we don't have a profile endpoint yet
        const userInfo = {
          email: credentials.identifier,
          loginTime: new Date().toISOString(),
          role: 'USER'
        };
        localStorage.setItem('user', JSON.stringify(userInfo));
        
        console.log('Login successful, token stored');
        return { success: true, token, user: userInfo };
      }
      
      console.log('No token in response');
      return { success: false, message: 'No token received' };
    } catch (error) {
      console.error('Login error:', error);
      console.error('Error response:', error.response?.data);
      return {
        success: false,
        message: error.response?.data || 'Login failed'
      };
    }
  },

  // Logout user
  logout: async () => {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call result
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('tokenExpiration');
      window.location.href = '/login';
    }
  },

  // Get current user info (requires authentication)
  getCurrentUser: async () => {
    try {
      // First try to get from localStorage
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        return JSON.parse(storedUser);
      }

      // If not in localStorage, return a basic user object
      // since we don't have a profile endpoint yet
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

  // Check if user is authenticated
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    const expiration = localStorage.getItem('tokenExpiration');
    
    if (!token || !expiration) {
      return false;
    }
    
    // Check if token is expired
    const currentTime = Date.now();
    const expirationTime = parseInt(expiration);
    
    if (currentTime >= expirationTime) {
      // Token expired, clear storage
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('tokenExpiration');
      return false;
    }
    
    return true;
  },

  // Get stored token
  getToken: () => {
    return localStorage.getItem('token');
  },

  // Get stored user
  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // Test authentication status
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