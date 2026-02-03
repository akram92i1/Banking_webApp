// coimport React from 'react';
import { FaSearch, FaBell, FaUser, FaGem, FaChevronDown } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user } = useAuth();

  return (
    <div className="flex flex-col md:flex-row items-center justify-between px-8 py-5 relative z-20 gap-6 md:gap-0">

      {/* Search Input - Sleek & Minimal */}
      <div className="relative w-full md:w-96 group">
        <FaSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-blue-400 transition-colors duration-300" />
        <input
          type="text"
          placeholder="Search for transactions, contacts..."
          className="w-full bg-slate-800/50 hover:bg-slate-800/80 focus:bg-slate-900 border border-slate-700 focus:border-blue-500/50 rounded-2xl pl-12 pr-4 py-3 text-slate-200 placeholder-slate-500 outline-none transition-all duration-300 shadow-inner"
        />
      </div>

      {/* Right Side Actions */}
      <div className="flex items-center gap-6 w-full md:w-auto justify-end">

        {/* PREMIUM ORBS WALLET - The 'Discord Market' X 'Banking' Hybrid */}
        <div className="hidden md:flex items-center gap-4 relative group">
          {/* Main Card Container */}
          <div className="bg-glass-premium rounded-2xl p-1.5 flex items-center pr-5 border-gradient-orb relative overflow-hidden transition-all duration-500 hover:scale-[1.02] cursor-pointer">

            {/* Shimmer Effect Overlay */}
            <div className="absolute inset-0 z-0 animate-shimmy opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

            {/* Orb Icon Container - 3D & Glowing */}
            <div className="relative z-10 w-10 h-10 mr-3 flex items-center justify-center">
              <div className="absolute inset-0 bg-purple-500/20 rounded-full blur-lg animate-pulse-soft"></div>
              <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-600 via-purple-500 to-fuchsia-500 shadow-lg shadow-purple-500/30 flex items-center justify-center animate-orb border border-white/20">
                <FaGem className="text-white text-sm drop-shadow-md" />
              </div>
            </div>

            {/* Text Content */}
            <div className="flex flex-col z-10">
              <span className="text-[10px] font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-300 to-indigo-300 uppercase">
                Orb Balance
              </span>
              <div className="flex items-center gap-1.5">
                <span className="text-lg font-bold text-white tabular-nums tracking-tight">
                  {user?.points?.toLocaleString() || 0}
                </span>
                {/* 'Redeem' Badge */}
                <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-gradient-to-r from-amber-400 to-orange-500 text-slate-900 shadow-sm opacity-80 group-hover:opacity-100 transition-opacity">
                  REDEEM
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <button className="relative w-12 h-12 rounded-2xl bg-slate-800/50 hover:bg-slate-700 border border-slate-700 hover:border-slate-500 flex items-center justify-center text-slate-400 hover:text-white transition-all duration-300 group">
          <FaBell className="text-lg group-hover:swing" />
          <span className="absolute top-3 right-3 w-2.5 h-2.5 bg-red-500 border-2 border-slate-800 rounded-full"></span>
        </button>

        {/* User Profile - Platinum/Banking Style */}
        <div className="flex items-center gap-3 pl-2 pr-1 py-1 rounded-2xl hover:bg-white/5 transition-colors cursor-pointer group">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors">
              {user?.email ? user.email.split('@')[0] : 'User'}
            </p>
            <p className="text-xs font-semibold text-gradient-platinum">
              Platinum Member
            </p>
          </div>

          <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-slate-700 to-slate-800 border border-slate-600 flex items-center justify-center shadow-lg group-hover:border-slate-500 transition-all overflow-hidden relative">
            {user?.photoURL ? (
              <img src={user.photoURL} alt="Profile" className="w-full h-full object-cover" />
            ) : (
              <FaUser className="text-slate-400 text-lg" />
            )}
            {/* Status Dot */}
            <div className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-500 border-2 border-slate-800 rounded-full translate-x-1/3 translate-y-1/3"></div>
          </div>

          <FaChevronDown className="text-xs text-slate-500 group-hover:text-slate-300 transition-colors ml-1" />
        </div>

      </div>
    </div>
  );
}
