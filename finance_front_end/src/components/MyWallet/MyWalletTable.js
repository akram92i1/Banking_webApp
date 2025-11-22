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
    }).format(Math.abs(amount));

    // Determine if this is incoming or outgoing for the current user
    const currentUserEmail = user?.email;
    const isIncoming = toAccount?.user?.email === currentUserEmail;
    const isOutgoing = fromAccount?.user?.email === currentUserEmail;

    if (isIncoming && !isOutgoing) {
      return `+ ${formattedAmount}`;
    } else if (isOutgoing && !isIncoming) {
      return `- ${formattedAmount}`;
    } else {
      return `${amount >= 0 ? '+' : '-'} ${formattedAmount}`;
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
        return 'Interac Transfer';
      default:
        return 'Transaction';
    }
  };

  const getPaymentType = (transactionType) => {
    switch (transactionType) {
      case 'TRANSFER':
        return 'Bank Transfer';
      case 'INTERAC':
        return 'Interac Transfer';
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
      <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
        <h2 className="text-xl font-semibold text-slate-800 mb-4">My Wallet</h2>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-full mb-4"></div>
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-4 bg-gray-300 rounded w-full mb-2"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">My Wallet</h2>
      
      {error ? (
        <div className="text-red-500 text-sm mb-4">{error}</div>
      ) : transactions.length === 0 ? (
        <div className="text-gray-500 text-center py-8">No transactions found</div>
      ) : (
        <>
          <table className="min-w-full text-sm text-left text-slate-700">
            <thead className="bg-slate-100 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-2">Date</th>
                <th className="px-4 py-2">Time</th>
                <th className="px-4 py-2">Description</th>
                <th className="px-4 py-2">Payment Type</th>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Balance</th>
                <th className="px-4 py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((tx, index) => (
                <tr key={`${tx.transactionId}-${tx.createdAt}`} className="border-b hover:bg-slate-50">
                  <td className="px-4 py-2">{formatDate(tx.createdAt)}</td>
                  <td className="px-4 py-2">{formatTime(tx.createdAt)}</td>
                  <td className="px-4 py-2">{getTransactionDescription(tx)}</td>
                  <td className="px-4 py-2">{getPaymentType(tx.transactionType)}</td>
                  <td className="px-4 py-2">{formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount)}</td>
                  <td className="px-4 py-2">{calculateBalanceAtTransaction(index)}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded-md text-xs font-medium ${getStatusClass(tx.transactionStatus)}`}>
                      {tx.transactionStatus}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination (static example) */}
          <div className="flex justify-between items-center mt-4 text-sm text-slate-600">
            <span>Prev</span>
            <div className="space-x-2">
              <button className="px-3 py-1 rounded bg-slate-200">1</button>
              <button className="px-3 py-1 rounded bg-slate-100">2</button>
              <button className="px-3 py-1 rounded bg-slate-100">3</button>
              <button className="px-3 py-1 rounded bg-slate-100">4</button>
            </div>
            <span>Next</span>
          </div>
        </>
      )}
    </div>
  );
};

export default MyWalletTable;
