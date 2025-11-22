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
      <div className="bg-gray-100 shadow-md rounded-lg p-6 mt-6">
        <h2 className="text-xl font-semibold mb-4">History</h2>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="flex justify-between">
                <div>
                  <div className="h-4 bg-gray-300 rounded w-32 mb-1"></div>
                  <div className="h-3 bg-gray-300 rounded w-20"></div>
                </div>
                <div className="h-4 bg-gray-300 rounded w-16"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 shadow-md rounded-lg p-6 mt-6">
      <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
      {error ? (
        <p className="text-red-500 text-sm">{error}</p>
      ) : transactions.length === 0 ? (
        <p className="text-gray-500 text-sm">No transactions found</p>
      ) : (
        <ul className="divide-y divide-gray-200">
          {transactions.map((tx) => {
            const { amount, type } = formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount);
            return (
              <li key={`${tx.transactionId}-${tx.createdAt}`} className="py-3 flex justify-between items-center">
                <div>
                  <p className="font-medium text-gray-800">{getTransactionDescription(tx)}</p>
                  <p className="text-sm text-gray-500">{formatDate(tx.createdAt)}</p>
                  <p className="text-xs text-gray-400">{tx.transactionStatus}</p>
                </div>
                <div
                  className={`text-sm font-semibold ${
                    type === 'credit' ? 'text-green-600' : 'text-red-500'
                  }`}
                >
                  {amount}
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default TransactionHistoryCard;
