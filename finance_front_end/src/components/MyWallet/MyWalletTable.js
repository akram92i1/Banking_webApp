import React, { useState, useEffect } from "react";
import { useAuth } from '../../contexts/AuthContext';
import bankingService from '../../services/bankingService';
import { FaMoon, FaSun, FaSearch, FaSort, FaSortUp, FaSortDown, FaFilter } from 'react-icons/fa';

const getStatusClass = (status, theme) => {
  const isDark = theme === 'dark';
  switch (status) {
    case "COMPLETED":
    case "SUCCESS":
      return isDark ? "text-emerald-300 bg-emerald-500/20" : "text-emerald-700 bg-emerald-100";
    case "PENDING":
      return isDark ? "text-yellow-300 bg-yellow-500/20" : "text-yellow-700 bg-yellow-100";
    case "CANCELLED":
    case "FAILED":
      return isDark ? "text-red-300 bg-red-500/20" : "text-red-700 bg-red-100";
    default:
      return isDark ? "text-slate-300 bg-slate-500/20" : "text-slate-700 bg-slate-100";
  }
};

const MyWalletTable = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentBalance, setCurrentBalance] = useState(0);

  // New State for Data Table
  const [theme, setTheme] = useState('dark'); // 'dark' or 'light'
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);
  const [sortConfig, setSortConfig] = useState({ key: 'createdAt', direction: 'desc' });
  const [filterType, setFilterType] = useState('ALL');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      // Fetch more transactions to demonstrate pagination
      const transactionsResult = await bankingService.getCurrentUserTransactions(50);
      if (transactionsResult.success) {
        setTransactions(transactionsResult.data);
      } else {
        setError(transactionsResult.message || 'Failed to fetch transactions');
      }

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

  // --- Helpers ---
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  };

  const formatAmount = (amount, transactionType, fromAccount, toAccount) => {
    const val = parseFloat(amount || 0);
    const formatted = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(Math.abs(val));

    const currentUserEmail = user?.email;
    const fromAccountEmail = fromAccount?.user?.email || fromAccount?.userEmail;
    const toAccountEmail = toAccount?.user?.email || toAccount?.userEmail;

    // Determine sign
    let sign = '+';
    let isPositive = true;

    if (transactionType === 'WITHDRAWAL') {
      sign = '-'; isPositive = false;
    } else if (transactionType === 'DEPOSIT') {
      sign = '+'; isPositive = true;
    } else if (fromAccountEmail === currentUserEmail) {
      sign = '-'; isPositive = false;
    }

    return { text: `${sign} ${formatted}`, isPositive };
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const handleTransactionAction = async (transactionId, status) => {
    try {
      // Optimistic update could go here, but for safety we'll just reload
      const result = await bankingService.updateTransactionStatus(transactionId, status);
      if (result.success) {
        fetchData();
      } else {
        alert('Failed: ' + result.message);
      }
    } catch (e) {
      alert('Error updating transaction');
    }
  };

  // --- Processing Data ---
  let processedData = [...transactions];

  // 1. Filter
  if (filterType !== 'ALL') {
    processedData = processedData.filter(t => t.transactionType === filterType);
  }
  if (searchTerm) {
    const lower = searchTerm.toLowerCase();
    processedData = processedData.filter(t =>
      (t.description || '').toLowerCase().includes(lower) ||
      (t.transactionType || '').toLowerCase().includes(lower) ||
      (t.amount || '').toString().includes(lower)
    );
  }

  // 2. Sort
  processedData.sort((a, b) => {
    const aValue = a[sortConfig.key] || '';
    const bValue = b[sortConfig.key] || '';

    if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  // 3. Paginate
  const totalPages = Math.ceil(processedData.length / itemsPerPage);
  const paginatedData = processedData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // --- Dynamic Styles ---
  const styles = {
    wrapper: theme === 'dark'
      ? "glass-card rounded-3xl p-8 overflow-hidden relative"
      : "bg-white rounded-3xl p-8 shadow-xl border border-slate-200 relative",
    textPrimary: theme === 'dark' ? "text-glass" : "text-slate-800",
    textSecondary: theme === 'dark' ? "text-glass-muted" : "text-slate-500",
    textHeader: theme === 'dark' ? "text-glass-muted" : "text-slate-500",
    input: theme === 'dark'
      ? "glass-input text-glass border-white/10 placeholder-slate-400 focus:ring-blue-500/50"
      : "bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:ring-blue-500/20",
    tableHeaderRow: theme === 'dark' ? "border-b border-white/10" : "border-b border-slate-200 bg-slate-50/50",
    tableRow: theme === 'dark' ? "border-b border-white/5 hover:bg-white/5" : "border-b border-slate-100 hover:bg-slate-50",
    buttonPrimary: "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/30",
    buttonSecondary: theme === 'dark' ? "glass-button text-glass" : "bg-white border border-slate-200 text-slate-700 hover:bg-slate-50",
    iconContainer: theme === 'dark' ? "bg-white/10 text-white" : "bg-blue-100 text-blue-600",
  };

  if (loading && transactions.length === 0) {
    return (
      <div className={styles.wrapper}>
        <div className="animate-pulse flex space-x-4">
          <div className="flex-1 space-y-6 py-1">
            <div className="h-4 bg-slate-400/20 rounded w-3/4"></div>
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-4">
                <div className="h-4 bg-slate-400/20 rounded col-span-2"></div>
                <div className="h-4 bg-slate-400/20 rounded col-span-1"></div>
              </div>
              <div className="h-4 bg-slate-400/20 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.wrapper} transition-colors duration-300`}>

      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h2 className={`text-3xl font-bold mb-1 ${styles.textPrimary}`}>My Wallet</h2>
          <p className={styles.textSecondary}>Manage your transactions</p>
        </div>

        {/* Toggle Theme */}
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          className={`p-3 rounded-xl transition-all ${theme === 'dark' ? 'bg-slate-800 text-yellow-400 hover:bg-slate-700' : 'bg-indigo-100 text-indigo-600 hover:bg-indigo-200'}`}
          title="Toggle Theme"
        >
          {theme === 'dark' ? <FaSun className="w-5 h-5" /> : <FaMoon className="w-5 h-5" />}
        </button>
      </div>

      {/* Controls Bar */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        {/* Search */}
        <div className="relative flex-1">
          <FaSearch className={`absolute left-4 top-1/2 -translate-y-1/2 ${styles.textSecondary}`} />
          <input
            type="text"
            placeholder="Search transactions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-all ${styles.input}`}
          />
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {['ALL', 'TRANSFER', 'DEPOSIT'].map(type => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${filterType === type
                ? styles.buttonPrimary
                : styles.buttonSecondary
                }`}
            >
              {type === 'ALL' ? 'All' : type.charAt(0) + type.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Data Table */}
      <div className={`rounded-2xl overflow-hidden border ${theme === 'dark' ? 'border-white/10' : 'border-slate-200'}`}>
        <div className="overflow-x-auto">
          <table className="min-w-full text-left">
            <thead>
              <tr className={styles.tableHeaderRow}>
                {['Date', 'Description', 'Type', 'Amount', 'Status'].map((header) => {
                  const keyMap = { 'Date': 'createdAt', 'Description': 'description', 'Type': 'transactionType', 'Amount': 'amount', 'Status': 'status' };
                  const sortKey = keyMap[header];

                  return (
                    <th
                      key={header}
                      onClick={() => handleSort(sortKey)}
                      className={`px-6 py-4 text-xs font-semibold uppercase tracking-wider cursor-pointer select-none hover:opacity-80 transition-opacity ${styles.textHeader}`}
                    >
                      <div className="flex items-center gap-2">
                        {header}
                        {sortConfig.key === sortKey && (
                          sortConfig.direction === 'asc' ? <FaSortUp /> : <FaSortDown />
                        )}
                        {sortConfig.key !== sortKey && <FaSort className="opacity-30" />}
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody className={theme === 'dark' ? "divide-y divide-white/5" : "divide-y divide-slate-100"}>
              {paginatedData.length > 0 ? (
                paginatedData.map((tx, idx) => {
                  const { text: amountText, isPositive } = formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount);

                  // Determine if incoming (to show actions)
                  const currentUserEmail = user?.email;
                  const toAccountEmail = tx.toAccount?.user?.email || tx.toAccount?.userEmail;
                  const isIncoming = toAccountEmail === currentUserEmail;

                  return (
                    <tr key={idx} className={`transition-colors duration-200 ${styles.tableRow}`}>
                      <td className={`px-6 py-4 whitespace-nowrap ${styles.textPrimary}`}>
                        <div className="font-medium">{formatDate(tx.createdAt)}</div>
                        <div className={`text-xs ${styles.textSecondary}`}>{formatTime(tx.createdAt)}</div>
                      </td>
                      <td className={`px-6 py-4 ${styles.textPrimary}`}>
                        <div className="flex items-center gap-3">
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${styles.iconContainer}`}>
                            <span className="font-bold text-xs">{(tx.description || 'TX').charAt(0).toUpperCase()}</span>
                          </div>
                          <span className="font-medium truncate max-w-[150px]">{tx.description || 'No Description'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-lg text-xs font-medium border ${theme === 'dark' ? 'border-white/10 bg-white/5 text-glass-muted' : 'border-slate-200 bg-slate-50 text-slate-600'}`}>
                          {tx.transactionType}
                        </span>
                      </td>
                      <td className={`px-6 py-4 font-bold ${isPositive ? 'text-emerald-500' : (theme === 'dark' ? 'text-glass' : 'text-slate-800')}`}>
                        {amountText}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusClass(tx.transactionStatus || tx.status, theme)}`}>
                            {tx.transactionStatus || tx.status || 'PENDING'}
                          </span>

                          {/* Action Buttons for Pending Incoming Transactions */}
                          {isIncoming && (tx.transactionStatus || tx.status) === 'PENDING' && (
                            <div className="flex gap-1">
                              <button
                                onClick={() => handleTransactionAction(tx.transactionId || tx.id, 'COMPLETED')}
                                className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/40 transition-colors"
                                title="Accept Transfer"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleTransactionAction(tx.transactionId || tx.id, 'CANCELLED')}
                                className="p-1.5 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/40 transition-colors"
                                title="Decline Transfer"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                              </button>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colspan="5" className={`px-6 py-12 text-center ${styles.textSecondary}`}>
                    <div className="flex flex-col items-center gap-2">
                      <FaFilter className="w-8 h-8 opacity-20" />
                      <p>No transactions found matching your criteria</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination Controls */}
      {processedData.length > 0 && (
        <div className="flex justify-between items-center mt-6">
          <div className={`text-sm ${styles.textSecondary}`}>
            Showing <span className="font-bold">{Math.min((currentPage - 1) * itemsPerPage + 1, processedData.length)}</span> to <span className="font-bold">{Math.min(currentPage * itemsPerPage, processedData.length)}</span> of <span className="font-bold">{processedData.length}</span> results
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'} ${styles.buttonSecondary}`}
            >
              Previous
            </button>
            <div className="flex gap-1">
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || Math.abs(p - currentPage) <= 1)
                .map((p, i, arr) => (
                  <React.Fragment key={p}>
                    {i > 0 && arr[i - 1] !== p - 1 && <span className={`px-2 py-2 ${styles.textSecondary}`}>...</span>}
                    <button
                      onClick={() => setCurrentPage(p)}
                      className={`w-10 h-10 rounded-xl font-bold transition-all ${currentPage === p ? styles.buttonPrimary : styles.buttonSecondary}`}
                    >
                      {p}
                    </button>
                  </React.Fragment>
                ))
              }
            </div>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'} ${styles.buttonSecondary}`}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyWalletTable;
