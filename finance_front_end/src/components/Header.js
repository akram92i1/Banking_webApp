// components/Header.js
import { FaBell, FaUser } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';

export default function Header() {
  const { user } = useAuth();

  return (
    <div className="flex items-center justify-between px-6 py-4 bg-white border-b">
      {/* Search Input */}
      <div className="w-full max-w-lg">
        <input
          type="text"
          placeholder="Search transactions, accounts..."
          className="w-full px-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
      </div>

      {/* Right Side Icons */}
      <div className="flex items-center gap-6">
        <button className="text-gray-600 hover:text-gray-800 relative">
          <FaBell className="text-xl" />
          <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full" />
        </button>
        
        {/* User Info */}
        <div className="flex items-center gap-3">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">
              {user?.email ? user.email.split('@')[0] : 'User'}
            </p>
            <p className="text-xs text-gray-500">
              {user?.role || 'Member'}
            </p>
          </div>
          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold">
            {user?.email ? user.email.charAt(0).toUpperCase() : <FaUser />}
          </div>
        </div>
      </div>
    </div>
  );
}
