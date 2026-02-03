import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is authenticated on app start
    const checkAuthStatus = () => {
      try {
        const isAuth = authService.isAuthenticated();
        const storedUser = authService.getStoredUser();

        if (isAuth && storedUser) {
          setIsAuthenticated(true);
          setUser(storedUser);
        } else {
          setIsAuthenticated(false);
          setUser(null);
        }
      } catch (error) {
        console.error('Auth check error:', error);
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (credentials) => {
    try {
      console.log('🔄 AuthContext: Starting login...');
      setLoading(true);
      const result = await authService.login(credentials);
      console.log('🔄 AuthContext: Login service result:', result);

      if (result.success) {
        console.log('✅ AuthContext: Setting user and authenticated state');
        setUser(result.user);
        setIsAuthenticated(true);
        console.log('✅ AuthContext: Login complete, user authenticated');
        return { success: true };
      } else {
        console.log('❌ AuthContext: Login failed:', result.message);
        return { success: false, message: result.message };
      }
    } catch (error) {
      console.error('❌ AuthContext: Login error:', error);
      return { success: false, message: 'Login failed' };
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      await authService.logout();
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error('Logout error:', error);
      // Still clear local state even if API call fails
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const updateUser = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
  };

  const earnPoints = (amount) => {
    if (!user) return;

    console.log(`💎 AuthContext: Earning ${amount} points`);
    const currentPoints = user.points || 0;
    const newPoints = currentPoints + amount;

    const updatedUser = { ...user, points: newPoints };
    updateUser(updatedUser);

    return newPoints;
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
    updateUser,
    earnPoints
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;