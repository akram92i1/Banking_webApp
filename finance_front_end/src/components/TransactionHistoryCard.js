import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import bankingService from '../services/bankingService';

const TransactionHistoryCard = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTransactions();
  }, []);

  const fetchTransactions = async () => {
    try {
      const result = await bankingService.getCurrentUserTransactions(5);
      if (result.success) {
        setTransactions(result.data);
      } else {
        setError(result.message || 'Failed to fetch transactions');
      }
    } catch (error) {
      console.error('Error fetching transactions:', error);
      setError('Failed to fetch transactions');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatAmount = (amount, transactionType, fromAccount, toAccount) => {
    const formattedAmount = new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(Math.abs(amount));

    // Determine if this is incoming or outgoing for the current user
    const currentUserEmail = user?.email;
    const isIncoming = toAccount?.user?.email === currentUserEmail;
    const isOutgoing = fromAccount?.user?.email === currentUserEmail;

    if (isIncoming && !isOutgoing) {
      return { amount: `+${formattedAmount}`, type: 'credit' };
    } else if (isOutgoing && !isIncoming) {
      return { amount: `-${formattedAmount}`, type: 'debit' };
    } else {
      // Default behavior for edge cases
      return { 
        amount: `${amount >= 0 ? '+' : '-'}${formattedAmount}`, 
        type: amount >= 0 ? 'credit' : 'debit' 
      };
    }
  };

  const getTransactionDescription = (transaction) => {
    if (transaction.description) {
      return transaction.description;
    }
    
    // Generate description based on transaction type
    switch (transaction.transactionType) {
      case 'TRANSFER':
        return 'Transfer';
      case 'DEPOSIT':
        return 'Deposit';
      case 'WITHDRAWAL':
        return 'Withdrawal';
      case 'PAYMENT':
        return 'Payment';
      default:
        return 'Transaction';
    }
  };

  if (loading) {
    return (
      <div className="glass-card rounded-3xl p-6 relative overflow-hidden animate-float">
        {/* Loading background orb */}
        <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-xl animate-pulse-soft"></div>
        
        <div className="relative z-10">
          <h2 className="text-xl font-semibold mb-6 text-glass flex items-center gap-3">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            Recent Transactions
          </h2>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="glass-card rounded-2xl p-4 animate-shimmer">
                <div className="flex justify-between items-center">
                  <div className="space-y-2">
                    <div className="h-4 bg-white/20 rounded-xl w-32"></div>
                    <div className="h-3 bg-white/10 rounded-lg w-20"></div>
                    <div className="h-2 bg-white/10 rounded-lg w-16"></div>
                  </div>
                  <div className="h-5 bg-white/20 rounded-xl w-16"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-3xl p-6 relative overflow-hidden group animate-float">
      {/* Floating background elements */}
      <div className="absolute -top-4 -right-4 w-20 h-20 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-xl animate-pulse-soft"></div>
      <div className="absolute -bottom-6 -left-6 w-16 h-16 bg-gradient-to-br from-emerald-400/20 to-cyan-400/20 rounded-full blur-lg animate-pulse-soft animation-delay-2000"></div>
      
      {/* Shimmer effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

      <div className="relative z-10">
        {/* Header with icon */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center shadow-xl">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-glass">Recent Transactions</h2>
        </div>

        {error ? (
          <div className="glass-card rounded-2xl p-4 border-red-400/30 bg-red-500/10">
            <div className="flex items-center text-red-300">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {error}
            </div>
          </div>
        ) : transactions.length === 0 ? (
          <div className="glass-card rounded-2xl p-8 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-gray-400/20 to-gray-600/20 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-glass-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <p className="text-glass-muted">No transactions found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map((tx, index) => {
              const { amount, type } = formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount);
              return (
                <div key={`${tx.transactionId}-${tx.createdAt}`} 
                     className={`glass-card rounded-2xl p-4 hover:scale-102 transition-all duration-300 animate-float`}
                     style={{animationDelay: `${index * 200}ms`}}>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-3">
                      {/* Transaction type icon */}
                      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                        type === 'credit' 
                          ? 'bg-gradient-to-br from-emerald-400 to-green-500' 
                          : 'bg-gradient-to-br from-red-400 to-pink-500'
                      } shadow-lg`}>
                        {type === 'credit' ? (
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                          </svg>
                        )}
                      </div>
                      
                      <div>
                        <p className="font-semibold text-glass text-lg">{getTransactionDescription(tx)}</p>
                        <p className="text-sm text-glass-muted">{formatDate(tx.createdAt)}</p>
                        <div className="flex items-center mt-1">
                          <div className={`w-2 h-2 rounded-full mr-2 ${
                            tx.transactionStatus === 'COMPLETED' ? 'bg-green-400' :
                            tx.transactionStatus === 'PENDING' ? 'bg-yellow-400' : 'bg-red-400'
                          }`}></div>
                          <p className="text-xs text-glass-muted uppercase tracking-wide">{tx.transactionStatus}</p>
                        </div>
                      </div>
                    </div>
                    
                    <div className={`text-lg font-bold px-3 py-1 rounded-xl ${
                      type === 'credit' 
                        ? 'text-emerald-300 bg-emerald-500/20' 
                        : 'text-red-300 bg-red-500/20'
                    }`}>
                      {amount}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default TransactionHistoryCard;
