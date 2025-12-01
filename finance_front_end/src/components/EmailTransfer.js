import React, { useState } from 'react';
import { FaPaperPlane, FaTimes, FaEnvelope, FaDollarSign } from 'react-icons/fa';
import bankingService from '../services/bankingService';

const EmailTransfer = ({ isOpen, onClose, onTransferComplete }) => {
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
        setSuccess(`🎉 Email transfer sent successfully! ${transferData.recipientEmail} will receive a notification to accept $${transferData.amount}.`);
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
        
        // Close modal after 3 seconds to allow user to read success message
        setTimeout(() => {
          onClose();
        }, 3000);
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <FaEnvelope className="text-blue-600 w-5 h-5" />
            <h2 className="text-xl font-semibold text-gray-900">
              Send Money via Email
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {/* Info Banner */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-md text-sm mb-6">
          <div className="flex items-center gap-2">
            <FaEnvelope className="w-4 h-4" />
            <span className="font-medium">Just like Interac e-Transfer!</span>
          </div>
          <p className="mt-1 text-xs text-blue-600">
            Send money using just an email address. The recipient will be notified to accept the transfer.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FaEnvelope className="inline w-4 h-4 mr-1" />
              Recipient Email *
            </label>
            <input
              type="email"
              name="recipientEmail"
              value={transferData.recipientEmail}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="recipient@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <FaDollarSign className="inline w-4 h-4 mr-1" />
              Amount *
            </label>
            <input
              type="number"
              name="amount"
              step="0.01"
              min="0.01"
              value={transferData.amount}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="0.00"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Transfer Type *
            </label>
            <select
              name="transactionType"
              value={transferData.transactionType}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="TRANSFER">📧 Transfer</option>
              <option value="INTERNAL">🏦 Internal Transfer</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Message (Optional)
            </label>
            <textarea
              name="description"
              value={transferData.description}
              onChange={handleChange}
              rows="3"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="What's this transfer for? (e.g., Dinner split, rent payment)"
            />
          </div>

          {/* Error/Success Messages */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              <strong>❌ Error:</strong> {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm">
              <strong>✅ Success:</strong> {success}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-3 rounded-lg hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all font-medium"
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
                  Send Money
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EmailTransfer;