import api from './api';

const bankingService = {
  // Get all users
  getAllUsers: async () => {
    try {
      const response = await api.get('/api/users');
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get users error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch users' };
    }
  },

  // Get user by ID
  getUserById: async (userId) => {
    try {
      const response = await api.get(`/api/users/${userId}`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get user error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch user' };
    }
  },

  // Create new user
  createUser: async (userData) => {
    try {
      const response = await api.post('/api/users', userData);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Create user error:', error);
      return { success: false, message: error.response?.data || 'Failed to create user' };
    }
  },

  // Update user
  updateUser: async (userId, userData) => {
    try {
      const response = await api.put(`/api/users/${userId}`, userData);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Update user error:', error);
      return { success: false, message: error.response?.data || 'Failed to update user' };
    }
  },

  // Delete user
  deleteUser: async (userId) => {
    try {
      await api.delete(`/api/users/${userId}`);
      return { success: true };
    } catch (error) {
      console.error('Delete user error:', error);
      return { success: false, message: error.response?.data || 'Failed to delete user' };
    }
  },

  // Bank Transactions
  sendMoney: async (transferData) => {
    try {
      const response = await api.post('/api/bank-transactions/send', transferData);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Send money error:', error);
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data || 'Failed to send money'
      };
    }
  },

  // Receive pending money
  receiveMoney: async (receiveData) => {
    try {
      const response = await api.get('/api/bank-transactions/receive', { data: receiveData });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Receive money error:', error);
      return {
        success: false,
        message: error.response?.data?.message || error.response?.data || 'Failed to receive money'
      };
    }
  },

  // Test connected user
  testConnectedUser: async () => {
    try {
      const response = await api.get('/api/bank-transactions/testConnectedUser');
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Test connected user error:', error);
      return { success: false, message: error.response?.data || 'Failed to test connection' };
    }
  },

  // Get user accounts (you might need to create this endpoint in backend)
  getUserAccounts: async (userId) => {
    try {
      const response = await api.get(`/api/accounts/user/${userId}`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get accounts error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch accounts' };
    }
  },

  // Get user transactions (you might need to create this endpoint in backend)
  getUserTransactions: async (userId, limit = 10) => {
    try {
      const response = await api.get(`/api/transactions/user/${userId}?limit=${limit}`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get transactions error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch transactions' };
    }
  },

  // Get account balance
  getAccountBalance: async (accountId) => {
    try {
      const response = await api.get(`/api/accounts/${accountId}/balance`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get balance error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch balance' };
    }
  },

  // Get current user's accounts
  getCurrentUserAccounts: async () => {
    try {
      console.log("####### DEBUG: Getting accounts for current user");
      const response = await api.get('/api/accounts/current-user');
      console.log("Response---->", response);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get current user accounts error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch accounts' };
    }
  },

  // Get current user's transactions
  getCurrentUserTransactions: async (limit = 10) => {
    try {
      const response = await api.get(`/api/transactions/current-user?limit=${limit}`);
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Get current user transactions error:', error);
      return { success: false, message: error.response?.data || 'Failed to fetch transactions' };
    }
  },

  // Update transaction status (Accept/Refuse)
  updateTransactionStatus: async (transactionId, status) => {
    try {
      const response = await api.put(`/api/transactions/${transactionId}/status`, null, {
        params: { status }
      });
      return { success: true, data: response.data };
    } catch (error) {
      console.error('Update transaction status error:', error);
      return { success: false, message: error.response?.data || 'Failed to update transaction status' };
    }
  }
};

export default bankingService;