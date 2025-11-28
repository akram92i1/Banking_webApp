import React, { useState, useEffect } from "react";
import { useAuth } from '../../contexts/AuthContext';
import bankingService from '../../services/bankingService';

const getStatusClass = (status) => {
  switch (status) {
    case "COMPLETED":
    case "SUCCESS":
      return "text-green-600 bg-green-100";
    case "PENDING":
      return "text-yellow-700 bg-yellow-100";
    case "CANCELLED":
    case "FAILED":
      return "text-red-600 bg-red-100";
    default:
      return "";
  }
};

const MyWalletTable = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentBalance, setCurrentBalance] = useState(0);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // Fetch transactions
      const transactionsResult = await bankingService.getCurrentUserTransactions(20);
      if (transactionsResult.success) {
        setTransactions(transactionsResult.data);
      } else {
        setError(transactionsResult.message || 'Failed to fetch transactions');
      }

      // Fetch current balance
      const accountsResult = await bankingService.getCurrentUserAccounts();
      if (accountsResult.success && accountsResult.data.length > 0) {
        const primaryAccount = accountsResult.data[0];
        setCurrentBalance(primaryAccount.balance);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch wallet data');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatAmount = (amount, transactionType, fromAccount, toAccount) => {
    const formattedAmount = new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(Math.abs(amount || 0));

    // Determine if this is incoming or outgoing for the current user
    const currentUserEmail = user?.email;
    
    // Handle cases where fromAccount or toAccount might be null or have different structures
    const fromAccountEmail = fromAccount?.user?.email || fromAccount?.userEmail || null;
    const toAccountEmail = toAccount?.user?.email || toAccount?.userEmail || null;
    
    const isIncoming = toAccountEmail === currentUserEmail;
    const isOutgoing = fromAccountEmail === currentUserEmail;

    if (isIncoming && !isOutgoing) {
      return `+ ${formattedAmount}`;
    } else if (isOutgoing && !isIncoming) {
      return `- ${formattedAmount}`;
    } else {
      // For other transaction types like deposits, withdrawals
      switch (transactionType) {
        case 'DEPOSIT':
          return `+ ${formattedAmount}`;
        case 'WITHDRAWAL':
          return `- ${formattedAmount}`;
        default:
          return `${amount >= 0 ? '+' : '-'} ${formattedAmount}`;
      }
    }
  };

  const getTransactionDescription = (transaction) => {
    if (transaction.description) {
      return transaction.description;
    }
    
    switch (transaction.transactionType) {
      case 'TRANSFER':
        return 'Transfer';
      case 'DEPOSIT':
        return 'Deposit';
      case 'WITHDRAWAL':
        return 'Withdrawal';
      case 'PAYMENT':
        return 'Payment';
      case 'INTERAC':
        return 'Transfer'; // Map INTERAC to Transfer since backend uses TRANSFER
      default:
        return 'Transaction';
    }
  };

  const getPaymentType = (transactionType) => {
    switch (transactionType) {
      case 'TRANSFER':
        return 'Bank Transfer';
      case 'INTERAC':
        return 'Bank Transfer'; // Map INTERAC to Bank Transfer since backend uses TRANSFER
      case 'DEPOSIT':
        return 'Deposit';
      case 'WITHDRAWAL':
        return 'Withdrawal';
      case 'PAYMENT':
        return 'Payment';
      default:
        return transactionType || 'Transaction';
    }
  };

  // Calculate balance at time of transaction (simplified - in real app this would be stored)
  const calculateBalanceAtTransaction = (transactionIndex) => {
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(currentBalance);
  };

  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-8 overflow-hidden relative animate-float">
        {/* Loading background orbs */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-2xl animate-pulse-soft"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-xl animate-pulse-soft animation-delay-2000"></div>
        
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-400 via-pink-500 to-blue-600 flex items-center justify-center animate-shimmer">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-glass">My Wallet</h2>
          </div>
          
          <div className="space-y-4">
            <div className="h-6 bg-white/20 rounded-2xl w-full animate-shimmer"></div>
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-white/10 rounded-2xl w-full animate-shimmer" style={{animationDelay: `${i * 200}ms`}}></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-3xl p-8 overflow-hidden relative group animate-float">
      {/* Floating background elements */}
      <div className="absolute -top-8 -right-8 w-40 h-40 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse-soft"></div>
      <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-2xl animate-pulse-soft animation-delay-2000"></div>
      <div className="absolute top-1/2 right-1/4 w-24 h-24 bg-gradient-to-br from-emerald-400/20 to-green-400/20 rounded-full blur-xl animate-pulse-soft animation-delay-4000"></div>
      
      {/* Shimmer effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

      <div className="relative z-10">
        {/* Header with enhanced glass effect */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 via-pink-500 to-blue-600 flex items-center justify-center shadow-2xl animate-pulse-soft">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-400 via-pink-500 to-blue-600 opacity-50 blur-xl"></div>
          </div>
          <div>
            <h2 className="text-4xl font-bold text-glass bg-gradient-to-r from-white via-purple-100 to-pink-100 bg-clip-text text-transparent">
              My Wallet
            </h2>
            <p className="text-glass-muted text-lg">Transaction History & Balance</p>
          </div>
        </div>
        
        {error ? (
          <div className="glass-card rounded-2xl p-6 border-red-400/30 bg-red-500/10 mb-6">
            <div className="flex items-center text-red-300">
              <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium">{error}</span>
            </div>
          </div>
        ) : transactions.length === 0 ? (
          <div className="glass-card rounded-3xl p-12 text-center">
            <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-gray-400/20 to-gray-600/20 flex items-center justify-center mx-auto mb-6">
              <svg className="w-12 h-12 text-glass-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-2xl text-glass-muted font-medium">No transactions found</p>
            <p className="text-glass-muted mt-2">Your transaction history will appear here</p>
          </div>
        ) : (
          <>
            {/* Modern glass table container */}
            <div className="glass-card rounded-2xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm text-left">
                  <thead>
                    <tr className="glass border-b border-white/10">
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Date</th>
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Time</th>
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Description</th>
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Type</th>
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Amount</th>
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Balance</th>
                      <th className="px-6 py-4 text-xs font-semibold text-glass-muted uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((tx, index) => (
                      <tr key={`${tx.transactionId || tx.id || index}-${tx.createdAt || index}`} 
                          className="border-b border-white/5 hover:bg-white/5 transition-colors duration-200">
                        <td className="px-6 py-4 text-glass font-medium">{formatDate(tx.createdAt || tx.processedAt || new Date().toISOString())}</td>
                        <td className="px-6 py-4 text-glass-muted">{formatTime(tx.createdAt || tx.processedAt || new Date().toISOString())}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
                              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                              </svg>
                            </div>
                            <span className="text-glass font-medium">{getTransactionDescription(tx)}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="glass-card px-3 py-1 rounded-xl text-xs font-medium text-glass-muted">
                            {getPaymentType(tx.transactionType)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="font-bold text-lg text-glass">
                            {formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount)}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-glass font-medium">{calculateBalanceAtTransaction(index)}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-xl text-xs font-semibold ${
                            (tx.transactionStatus || tx.status || 'PENDING') === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-300' :
                            (tx.transactionStatus || tx.status || 'PENDING') === 'PENDING' ? 'bg-yellow-500/20 text-yellow-300' :
                            'bg-red-500/20 text-red-300'
                          }`}>
                            {tx.transactionStatus || tx.status || 'PENDING'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Enhanced glass pagination */}
            <div className="flex justify-between items-center mt-8">
              <button className="glass-button px-6 py-3 rounded-2xl text-glass font-medium hover:scale-105 transition-all duration-300">
                ← Previous
              </button>
              <div className="flex items-center space-x-2">
                {[1, 2, 3, 4].map((page, index) => (
                  <button key={page} 
                          className={`w-10 h-10 rounded-xl font-semibold transition-all duration-300 ${
                            index === 0 
                              ? 'bg-gradient-to-r from-blue-400 to-purple-500 text-white shadow-lg' 
                              : 'glass-button text-glass hover:scale-110'
                          }`}>
                    {page}
                  </button>
                ))}
              </div>
              <button className="glass-button px-6 py-3 rounded-2xl text-glass font-medium hover:scale-105 transition-all duration-300">
                Next →
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default MyWalletTable;
