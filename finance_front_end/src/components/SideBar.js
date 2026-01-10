// components/Sidebar.js
import { FaWallet, FaUser, FaCog, FaQuestionCircle, FaSignOutAlt, FaChartPie  } from 'react-icons/fa';
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
      <div className="w-64 min-h-screen p-6 flex flex-col justify-between relative">
        {/* Glassmorphism background */}
        <div className="absolute inset-0 backdrop-blur-xl bg-white/5"></div>
        
        <div className="relative z-10">
          {/* Logo with glass effect */}
          <div className="glass-card rounded-2xl p-4 mb-8 text-center animate-float">
            <h1 className="text-2xl font-bold flex items-center justify-center gap-3 text-glass">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center shadow-xl">
                <span className="text-xl">💎</span>
              </div>
              <span className="bg-gradient-to-r from-white to-blue-100 bg-clip-text text-transparent">
                Mini Finance
              </span>
            </h1>
          </div>
          
          {/* Navigation with glass cards */}
          <nav className="space-y-3">
            <Link 
              to="/overview" 
              className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:scale-105 transition-all duration-300 relative overflow-hidden"
            >
              {/* Active indicator */}
              <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-400 to-purple-600 rounded-r-full"></div>
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FaChartPie className="text-white" />
              </div>
              <span className="font-semibold">Overview</span>
              {/* Hover shimmer */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            </Link>
            
            <Link 
              to="/wallet" 
              className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:scale-105 transition-all duration-300 relative overflow-hidden animate-float animation-delay-1000"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-cyan-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FaWallet className="text-white" />
              </div>
              <span className="font-semibold">My Wallet</span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            </Link>
            
            <Link 
              to="/profile" 
              className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:scale-105 transition-all duration-300 relative overflow-hidden animate-float animation-delay-2000"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-pink-400 to-rose-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FaUser className="text-white" />
              </div>
              <span className="font-semibold">Profile</span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            </Link>
            
            <Link 
              to="/settings" 
              className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:scale-105 transition-all duration-300 relative overflow-hidden animate-float animation-delay-3000"
            >
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FaCog className="text-white" />
              </div>
              <span className="font-semibold">Settings</span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            </Link>
            
            <button className="glass-card group flex items-center gap-4 text-glass px-6 py-4 rounded-2xl hover:scale-105 transition-all duration-300 relative overflow-hidden w-full animate-float animation-delay-4000">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-400 to-purple-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                <FaQuestionCircle className="text-white" />
              </div>
              <span className="font-semibold">Help Center</span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
            </button>
          </nav>
  
          {/* Upgrade Card with Enhanced Glass Effect */}
          <div className="mt-8 glass-card rounded-3xl p-6 text-center relative overflow-hidden group animate-pulse-soft">
            {/* Background gradient */}
            <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 via-pink-500/20 to-blue-500/20 rounded-3xl"></div>
            
            <div className="relative z-10">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 flex items-center justify-center mx-auto mb-4 shadow-2xl animate-float">
                <FaWallet className="h-8 w-8 text-white" />
                {/* Glow effect */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-purple-400 via-pink-400 to-blue-400 opacity-50 blur-xl animate-pulse"></div>
              </div>
              
              <h3 className="text-glass font-semibold mb-2">Upgrade to Pro</h3>
              <p className="text-glass-muted text-sm mb-4">Get premium features and unlimited transactions</p>
              
              <button className="glass-button w-full py-3 rounded-2xl font-semibold text-glass hover:scale-105 transition-all duration-300 relative overflow-hidden group">
                <span className="relative z-10">Upgrade Now</span>
                <div className="absolute inset-0 bg-gradient-to-r from-purple-400/20 to-pink-400/20 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
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