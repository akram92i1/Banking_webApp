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
            <div className="bg-green-50 rounded-xl p-6 relative overflow-hidden shadow-md">
                <div className="animate-pulse">
                    <div className="h-4 bg-gray-300 rounded w-1/4 mb-2"></div>
                    <div className="h-8 bg-gray-300 rounded w-1/2 mb-4"></div>
                    <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                </div>
            </div>
        );
    }

    return (
      <div className="bg-green-50 rounded-xl p-6 relative overflow-hidden shadow-md">
        {/* Decorative Circle */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-red-500 rounded-full mix-blend-multiply opacity-70 -mr-12 -mt-12"></div>
        <div className="absolute top-0 right-0 w-24 h-24 bg-yellow-400 rounded-full mix-blend-multiply opacity-80 -mr-6 -mt-6"></div>
  
        {/* Content */}
        <div className="relative z-10">
          <p className="text-sm font-medium text-gray-600">Your Balance</p>
          {error ? (
            <p className="text-red-500 text-sm">{error}</p>
          ) : (
            <h2 className="text-4xl font-extrabold text-gray-900">
              {primaryAccount ? formatBalance(primaryAccount.balance) : '$0.00'}
            </h2>
          )}
  
          <div className="mt-2 text-gray-800 tracking-widest font-semibold">
            {primaryAccount ? formatAccountNumber(primaryAccount.accountNumber) : '**** **** **** ****'}
          </div>
  
          <div className="mt-4 flex justify-between items-center text-sm">
            <div>
              <p className="text-gray-500">Account Type</p>
              <p className="font-medium text-gray-800">
                {primaryAccount ? primaryAccount.accountType : 'CHECKING'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-gray-500">Account Holder</p>
              <p className="font-medium text-gray-800">{getCardHolderName()}</p>
            </div>
          </div>

          {accounts.length > 1 && (
            <div className="mt-2 text-xs text-gray-500">
              +{accounts.length - 1} more account{accounts.length > 2 ? 's' : ''}
            </div>
          )}
        </div>
      </div>
    );
  }
  