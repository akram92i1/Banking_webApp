// components/Header.js
import { FaBell, FaUser } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user } = useAuth();

  return (
    <div className="flex items-center justify-between px-6 py-4 relative bg-slate-800/50 border-b border-white/10">

      {/* Search Input with Dark Effect */}
      <div className="w-full max-w-lg relative z-10">
        <div className="relative">
          <input
            type="text"
            placeholder="Search transactions, accounts..."
            className="w-full px-6 py-3 rounded-2xl glass-input text-glass placeholder-slate-400 focus:ring-2 focus:ring-blue-500/30"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="w-6 h-6 rounded-full bg-slate-700 flex items-center justify-center">
              <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="m21 21-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side Icons */}
      <div className="flex items-center gap-6 relative z-10">

        {/* Points/Orbs System - Discord Style */}
        <div className="hidden md:flex items-center gap-2 glass-card rounded-xl px-4 py-2 border border-purple-500/30 relative overflow-hidden group cursor-pointer hover:bg-slate-800/80 transition-all">
          <div className="relative">
            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center animate-orb">
              <svg className="w-3.5 h-3.5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2-1 8 4-10 5-10-5 8-4 2 1z" />
              </svg>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold text-purple-300 uppercase leading-none tracking-wider">Orbs</span>
            <span className="text-sm font-bold text-white leading-none group-hover:text-purple-200 transition-colors">
              {user?.points || 0}
            </span>
          </div>
          {/* Shine effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
        </div>

        <button className="glass-button text-white hover:bg-slate-700 relative p-3 rounded-xl transition-colors">
          <FaBell className="text-xl" />
          <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full"></span>
        </button>

        {/* User Info with Dark Card */}
        <div className="flex items-center gap-4 glass-card rounded-2xl px-4 py-2 hover:bg-slate-700 transition-colors">
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
