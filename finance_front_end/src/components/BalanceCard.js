// components/BalanceCard.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import bankingService from '../services/bankingService';

export default function BalanceCard() {
    const { user } = useAuth();
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAccountData();
    }, []);

    const fetchAccountData = async () => {
        try {
            const result = await bankingService.getCurrentUserAccounts();
            if (result.success) {
                setAccounts(result.data);
            } else {
                setError(result.message || 'Failed to fetch account data');
            }
        } catch (error) {
            console.error('Error fetching account data:', error);
            setError('Failed to fetch account data');
        } finally {
            setLoading(false);
        }
    };

    const formatBalance = (balance) => {
        return new Intl.NumberFormat('en-CA', {
            style: 'currency',
            currency: 'CAD'
        }).format(balance);
    };

    const formatAccountNumber = (accountNumber) => {
        if (!accountNumber) return '**** **** **** ****';
        const lastFour = accountNumber.slice(-4);
        return `**** **** **** ${lastFour}`;
    };

    const getCardHolderName = () => {
        if (user?.firstName && user?.lastName) {
            return `${user.firstName} ${user.lastName}`;
        }
        return user?.email?.split('@')[0] || 'User';
    };

    const primaryAccount = accounts.length > 0 ? accounts[0] : null;

    if (loading) {
        return (
            <div className="glass-card rounded-3xl p-8 relative overflow-hidden animate-pulse-soft">
                <div className="animate-shimmer">
                    <div className="h-4 bg-white/20 rounded-2xl w-1/4 mb-3"></div>
                    <div className="h-10 bg-white/20 rounded-2xl w-1/2 mb-6"></div>
                    <div className="h-4 bg-white/20 rounded-2xl w-3/4"></div>
                </div>
                {/* Floating elements during loading */}
                <div className="absolute top-4 right-4 w-16 h-16 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-md animate-float"></div>
            </div>
        );
    }

    return (
      <div className="glass-card rounded-3xl p-8 relative overflow-hidden group hover:scale-105 transition-all duration-500 animate-float">
        {/* Decorative Floating Elements */}
        <div className="absolute -top-8 -right-8 w-32 h-32 bg-gradient-to-br from-emerald-400 to-cyan-400 rounded-full opacity-20 blur-2xl animate-pulse-soft"></div>
        <div className="absolute -bottom-4 -left-4 w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full opacity-20 blur-xl animate-pulse-soft animation-delay-2000"></div>
        
        {/* Shimmer effect on hover */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
  
        {/* Content */}
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm font-medium text-glass-muted tracking-wide uppercase">Your Balance</p>
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-cyan-400 flex items-center justify-center shadow-lg">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
          
          {error ? (
            <div className="glass-card rounded-2xl p-4 border-red-400/30">
              <p className="text-red-300 text-sm flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </p>
            </div>
          ) : (
            <h2 className="text-5xl font-bold text-glass mb-6 tracking-tight">
              <span className="bg-gradient-to-r from-white via-blue-100 to-cyan-100 bg-clip-text text-transparent">
                {primaryAccount ? formatBalance(primaryAccount.balance) : '$0.00'}
              </span>
            </h2>
          )}
  
          <div className="glass-card rounded-2xl p-4 mb-6">
            <div className="text-glass font-mono text-lg tracking-[0.3em] text-center">
              {primaryAccount ? formatAccountNumber(primaryAccount.accountNumber) : '**** **** **** ****'}
            </div>
          </div>
  
          <div className="grid grid-cols-2 gap-4">
            <div className="glass-card rounded-2xl p-4 text-center animate-float animation-delay-1000">
              <p className="text-glass-muted text-xs uppercase tracking-wider mb-1">Account Type</p>
              <p className="font-semibold text-glass">
                {primaryAccount ? primaryAccount.accountType : 'CHECKING'}
              </p>
            </div>
            <div className="glass-card rounded-2xl p-4 text-center animate-float animation-delay-2000">
              <p className="text-glass-muted text-xs uppercase tracking-wider mb-1">Account Holder</p>
              <p className="font-semibold text-glass">{getCardHolderName()}</p>
            </div>
          </div>

          {accounts.length > 1 && (
            <div className="mt-4 text-center">
              <div className="glass-button inline-flex items-center px-4 py-2 rounded-xl text-xs text-glass-muted">
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                +{accounts.length - 1} more account{accounts.length > 2 ? 's' : ''}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }
  