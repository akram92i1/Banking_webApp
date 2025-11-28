import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { FaEye, FaEyeSlash, FaUser, FaLock } from 'react-icons/fa';
import { Navigate } from 'react-router-dom';

const Login = () => {
  const [credentials, setCredentials] = useState({
    identifier: '', // email or card number
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login, isAuthenticated, loading } = useAuth();

  // Redirect if already authenticated
  if (isAuthenticated && !loading) {
    return <Navigate to="/" replace />;
  }

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    // Basic validation
    if (!credentials.identifier || !credentials.password) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    try {
      console.log('🔐 Starting login process...');
      const result = await login(credentials);
      console.log('🔐 Login result:', result);
      
      if (!result.success) {
        console.log('❌ Login failed:', result.message);
        setError(result.message || 'Login failed');
      } else {
        console.log('✅ Login successful, should redirect...');
      }
      // If successful, the AuthContext will handle the redirect
    } catch (error) {
      console.error('❌ Login exception:', error);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse"></div>
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse animation-delay-2000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-pink-400 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-pulse animation-delay-4000"></div>
      </div>

      <div className="max-w-md w-full mx-4 relative z-10">
        <div className="glass-card rounded-3xl p-8 space-y-8 backdrop-blur-2xl border border-white/20 shadow-2xl animate-float">
          {/* Header with Enhanced Glass Effect */}
          <div className="text-center">
            <div className="mx-auto w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 flex items-center justify-center mb-6 shadow-2xl animate-pulse-soft">
              <span className="text-4xl">💎</span>
              {/* Glow effect */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-400 via-purple-500 to-pink-500 opacity-50 blur-xl animate-pulse"></div>
            </div>
            
            <h1 className="text-3xl font-bold text-glass mb-2">
              <span className="bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent">
                Mini Finance
              </span>
            </h1>
            <h2 className="text-xl font-semibold text-glass mb-2">
              Welcome Back
            </h2>
            <p className="text-glass-muted">
              Sign in to access your account
            </p>
          </div>

          {/* Login Form with Glass Effects */}
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              {/* Email/Card Number Field */}
              <div>
                <label htmlFor="identifier" className="block text-sm font-medium text-glass-muted mb-2">
                  Email or Card Number
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                    <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                      <FaUser className="h-3 w-3 text-white" />
                    </div>
                  </div>
                  <input
                    id="identifier"
                    name="identifier"
                    type="text"
                    autoComplete="username"
                    required
                    className="glass-input w-full pl-14 pr-4 py-4 rounded-2xl text-glass placeholder-white/50 focus:ring-2 focus:ring-white/30 transition-all duration-300"
                    placeholder="Enter your email or card number"
                    value={credentials.identifier}
                    onChange={handleChange}
                  />
                </div>
              </div>

              {/* Password Field */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-glass-muted mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none z-10">
                    <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center">
                      <FaLock className="h-3 w-3 text-white" />
                    </div>
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    className="glass-input w-full pl-14 pr-14 py-4 rounded-2xl text-glass placeholder-white/50 focus:ring-2 focus:ring-white/30 transition-all duration-300"
                    placeholder="Enter your password"
                    value={credentials.password}
                    onChange={handleChange}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-4 flex items-center z-10 glass-button rounded-r-2xl px-3 hover:bg-white/10 transition-all duration-300"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center">
                      {showPassword ? (
                        <FaEyeSlash className="h-3 w-3 text-white" />
                      ) : (
                        <FaEye className="h-3 w-3 text-white" />
                      )}
                    </div>
                  </button>
                </div>
              </div>
            </div>

            {/* Error Message with Glass Effect */}
            {error && (
              <div className="glass-card rounded-2xl p-4 border-red-400/30 bg-red-500/10 animate-float">
                <div className="flex items-center">
                  <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-red-400 to-pink-500 flex items-center justify-center mr-3">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="text-red-300 text-sm font-medium">{error}</p>
                </div>
              </div>
            )}

            {/* Submit Button with Enhanced Glass Effect */}
            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="group relative w-full flex justify-center py-4 px-6 border border-transparent font-semibold rounded-2xl text-white bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:scale-105 focus:outline-none focus:ring-4 focus:ring-white/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none transition-all duration-300 overflow-hidden shadow-2xl"
              >
                {/* Button background glow */}
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 opacity-50 blur-xl"></div>
                
                {/* Shimmer effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
                
                <span className="relative z-10 flex items-center">
                  {isLoading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Signing in...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                      </svg>
                      Sign in
                    </>
                  )}
                </span>
              </button>
            </div>

            {/* Additional Links with Glass Effect */}
            <div className="text-center">
              <a href="#" className="text-sm text-glass-muted hover:text-glass transition-colors duration-300 glass-button inline-block px-4 py-2 rounded-xl">
                Forgot your password?
              </a>
            </div>
          </form>

          {/* Footer with Glass Effect */}
          <div className="text-center">
            <div className="glass-card rounded-2xl p-4">
              <span className="text-sm text-glass-muted">
                Don't have an account?{' '}
                <a href="#" className="text-glass hover:text-white transition-colors duration-300 font-semibold">
                  Contact support
                </a>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;