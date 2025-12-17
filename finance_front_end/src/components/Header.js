// components/Header.js
import { FaBell, FaUser } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user } = useAuth();

  return (
    <div className="flex items-center justify-between px-6 py-4 relative">
      {/* Glassmorphism background overlay */}
      <div className="absolute inset-0 backdrop-blur-xl bg-white/5 border-b border-white/10"></div>
      
      {/* Search Input with Glass Effect */}
      <div className="w-full max-w-lg relative z-10">
        <div className="relative">
          <input
            type="text"
            placeholder="Search transactions, accounts..."
            className="w-full px-6 py-3 rounded-2xl glass-input text-glass placeholder-white/50 focus:ring-2 focus:ring-white/30"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
              <svg className="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side Icons with Glass Effect */}
      <div className="flex items-center gap-6 relative z-10">
        <button className="glass-button text-white hover:text-white relative p-3 rounded-xl animate-float">
          <FaBell className="text-xl" />
          <span className="absolute -top-1 -right-1 h-3 w-3 bg-gradient-to-r from-pink-500 to-red-500 rounded-full animate-pulse">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          </span>
        </button>
        
        {/* User Info with Glass Card */}
        <div className="flex items-center gap-4 glass-card rounded-2xl px-4 py-2 animate-float animation-delay-1000">
          <div className="text-right">
            <p className="text-sm font-semibold text-glass">
              {user?.email ? user.email.split('@')[0] : 'User'}
            </p>
            <p className="text-xs text-glass-muted">
              {user?.role || 'Member'}
            </p>
          </div>
          <div className="relative">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-xl animate-pulse-soft">
              {user?.email ? user.email.charAt(0).toUpperCase() : <FaUser />}
            </div>
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-400 to-purple-600 opacity-50 blur-lg"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
