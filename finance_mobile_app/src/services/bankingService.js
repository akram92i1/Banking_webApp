import api from './api';

const bankingService = {
    getAllUsers: async () => {
        try {
            const response = await api.get('/api/users');
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch users' };
        }
    },

    getUserById: async (userId) => {
        try {
            const response = await api.get(`/api/users/${userId}`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch user' };
        }
    },

    sendMoney: async (transferData) => {
        try {
            const response = await api.post('/api/bank-transactions/send', transferData);
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.message || error.response?.data || 'Failed to send money'
            };
        }
    },

    receiveMoney: async (receiveData) => {
        try {
            const response = await api.get('/api/bank-transactions/receive', { data: receiveData });
            return { success: true, data: response.data };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.message || error.response?.data || 'Failed to receive money'
            };
        }
    },

    testConnectedUser: async () => {
        try {
            const response = await api.get('/api/bank-transactions/testConnectedUser');
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to test connection' };
        }
    },

    getUserAccounts: async (userId) => {
        try {
            const response = await api.get(`/api/accounts/user/${userId}`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch accounts' };
        }
    },

    getUserTransactions: async (userId, limit = 10) => {
        try {
            const response = await api.get(`/api/transactions/user/${userId}?limit=${limit}`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch transactions' };
        }
    },

    getAccountBalance: async (accountId) => {
        try {
            const response = await api.get(`/api/accounts/${accountId}/balance`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch balance' };
        }
    },

    getCurrentUserAccounts: async () => {
        try {
            const response = await api.get('/api/accounts/current-user');
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch accounts' };
        }
    },

    getCurrentUserTransactions: async (limit = 10) => {
        try {
            const response = await api.get(`/api/transactions/current-user?limit=${limit}`);
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to fetch transactions' };
        }
    },

    updateTransactionStatus: async (transactionId, status) => {
        try {
            const response = await api.put(`/api/transactions/${transactionId}/status`, null, {
                params: { status }
            });
            return { success: true, data: response.data };
        } catch (error) {
            return { success: false, message: error.response?.data || 'Failed to update transaction status' };
        }
    }
};

export default bankingService;
