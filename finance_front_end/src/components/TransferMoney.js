import React, { useState } from 'react';
import { FaPaperPlane, FaTimes } from 'react-icons/fa';
import bankingService from '../services/bankingService';

import { useAuth } from '../contexts/AuthContext';

const TransferMoney = ({ isOpen, onClose, onTransferComplete }) => {
  const { earnPoints } = useAuth();
  const [transferData, setTransferData] = useState({
    recipientEmail: '',
    amount: '',
    description: '',
    transactionType: 'TRANSFER'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setTransferData({
      ...transferData,
      [e.target.name]: e.target.value
    });
    // Clear messages when user types
    if (error) setError('');
    if (success) setSuccess('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    setSuccess('');

    // Basic validation
    if (!transferData.recipientEmail || !transferData.amount) {
      setError('Please fill in all required fields');
      setIsLoading(false);
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(transferData.recipientEmail)) {
      setError('Please enter a valid email address');
      setIsLoading(false);
      return;
    }

    if (parseFloat(transferData.amount) <= 0) {
      setError('Amount must be greater than 0');
      setIsLoading(false);
      return;
    }

    try {
      const result = await bankingService.sendMoney(transferData);

      if (result.success) {
        // Earn points
        earnPoints(50);

        setSuccess('Email transfer sent successfully! The recipient will be notified to accept the transfer. (+50 Orbs)');
        setTransferData({
          recipientEmail: '',
          amount: '',
          description: '',
          transactionType: 'TRANSFER'
        });

        // Notify parent component
        if (onTransferComplete) {
          onTransferComplete(result.data);
        }

        // Close modal after 2 seconds
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        setError(result.message || 'Transfer failed');
      }
    } catch (error) {
      setError('An unexpected error occurred. Please try again.');
      console.error('Transfer error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="glass-card rounded-3xl p-6 w-full max-w-md mx-4 border border-white/10 relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-glass">
            Send Money via Email
          </h2>
          <button
            onClick={onClose}
            className="text-glass-muted hover:text-white transition-colors"
          >
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-3 py-2 rounded-md text-sm mb-4">
          📧 Send money using just an email address - like Interac e-Transfer!
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-glass-muted mb-1">
              Recipient Email *
            </label>
            <input
              type="email"
              name="recipientEmail"
              value={transferData.recipientEmail}
              onChange={handleChange}
              className="glass-input w-full px-4 py-3 rounded-xl border border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass placeholder-slate-500"
              placeholder="recipient@example.com"
              required
            />
            <p className="text-xs text-glass-muted mt-1">
              The recipient will receive a notification to accept the transfer
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-glass-muted mb-1">
              Amount *
            </label>
            <input
              type="number"
              name="amount"
              step="0.01"
              min="0"
              value={transferData.amount}
              onChange={handleChange}
              className="glass-input w-full px-4 py-3 rounded-xl border border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass placeholder-slate-500"
              placeholder="0.00"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-glass-muted mb-1">
              Transfer Type *
            </label>
            <select
              name="transactionType"
              value={transferData.transactionType}
              onChange={handleChange}
              className="glass-input w-full px-4 py-3 rounded-xl border border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass bg-slate-900"
              required
            >
              <option value="TRANSFER" className="bg-slate-900 text-glass">Transfer</option>
              <option value="INTERNAL" className="bg-slate-900 text-glass">Internal Transfer</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-glass-muted mb-1">
              Description (Optional)
            </label>
            <textarea
              name="description"
              value={transferData.description}
              onChange={handleChange}
              rows="3"
              className="glass-input w-full px-4 py-3 rounded-xl border border-white/10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-glass placeholder-slate-500 resize-none"
              placeholder="What's this transfer for?"
            />
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md text-sm">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-3 py-2 rounded-md text-sm">
              {success}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 border border-white/10 text-glass-muted rounded-xl hover:bg-white/5 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-3 rounded-xl hover:shadow-lg hover:shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all font-medium"
            >
              {isLoading ? (
                <>
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Sending...
                </>
              ) : (
                <>
                  <FaPaperPlane className="w-4 h-4" />
                  Transfer
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TransferMoney;