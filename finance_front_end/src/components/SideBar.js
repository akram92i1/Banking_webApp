// components/Sidebar.js
import { FaWallet, FaUser, FaCog, FaQuestionCircle, FaSignOutAlt, FaChartPie } from 'react-icons/fa';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Sidebar() {
  const { logout, user } = useAuth();

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
    }
  };
  return (
    <div className="w-64 min-h-screen p-6 flex flex-col justify-between relative bg-slate-900 border-r border-white/10">

      <div className="relative z-10">
        {/* Logo */}
        <div className="glass-card rounded-2xl p-4 mb-8 text-center">
          <h1 className="text-2xl font-bold flex items-center justify-center gap-3 text-glass">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg">
              <span className="text-xl">💎</span>
            </div>
            <span className="text-white">
              Mini Finance
            </span>
          </h1>
        </div>

        {/* Navigation */}
        <nav className="space-y-3">
          <Link
            to="/overview"
            className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:bg-slate-800 transition-all duration-300 relative overflow-hidden"
          >
            <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <FaChartPie className="text-white" />
            </div>
            <span className="font-semibold">Overview</span>
          </Link>

          <Link
            to="/wallet"
            className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:bg-slate-800 transition-all duration-300 relative overflow-hidden"
          >
            <div className="w-8 h-8 rounded-xl bg-emerald-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <FaWallet className="text-white" />
            </div>
            <span className="font-semibold">My Wallet</span>
          </Link>

          <Link
            to="/profile"
            className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:bg-slate-800 transition-all duration-300 relative overflow-hidden"
          >
            <div className="w-8 h-8 rounded-xl bg-pink-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <FaUser className="text-white" />
            </div>
            <span className="font-semibold">Profile</span>
          </Link>

          <Link
            to="/settings"
            className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:bg-slate-800 transition-all duration-300 relative overflow-hidden"
          >
            <div className="w-8 h-8 rounded-xl bg-amber-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <FaCog className="text-white" />
            </div>
            <span className="font-semibold">Settings</span>
          </Link>

          <button className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:bg-slate-800 transition-all duration-300 relative overflow-hidden w-full">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 flex items-center justify-center group-hover:scale-105 transition-transform">
              <FaQuestionCircle className="text-white" />
            </div>
            <span className="font-semibold">Help Center</span>
          </button>
        </nav>

        {/* Upgrade Card with Enhanced Glass Effect */}
        <div className="mt-8 glass-card rounded-3xl p-6 text-center relative overflow-hidden group">
          {/* Background gradient */}
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-blue-500/20 rounded-3xl"></div>

          <div className="relative z-10">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 flex items-center justify-center mx-auto mb-4 shadow-2xl">
              <FaWallet className="h-8 w-8 text-white" />
            </div>

            <h3 className="text-glass font-semibold mb-2">Upgrade to Pro</h3>
            <p className="text-glass-muted text-sm mb-4">Get premium features and unlimited transactions</p>

            <button className="glass-button w-full py-3 rounded-2xl font-semibold text-glass hover:scale-105 transition-all duration-300 relative overflow-hidden group">
              <span className="relative z-10">Upgrade Now</span>
            </button>
          </div>
        </div>
      </div>

      {/* Logout Button with Glass Effect */}
      <button
        onClick={handleLogout}
        className="glass-button flex items-center justify-center gap-3 text-glass px-6 py-4 rounded-2xl hover:text-red-300 hover:bg-red-500/10 transition-all duration-300 relative z-10 group"
      >
        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-red-400 to-pink-400 flex items-center justify-center group-hover:scale-110 transition-transform">
          <FaSignOutAlt className="text-white text-sm" />
        </div>
        <span className="font-semibold">Logout</span>
      </button>
    </div>
  );
}