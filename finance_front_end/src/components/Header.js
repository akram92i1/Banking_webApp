// components/Header.js
import { FaBell } from 'react-icons/fa';

export default function Header() {
  return (
    <div className="flex items-center justify-between px-6 py-4 bg-white border-b">
      {/* Search Input */}
      <div className="w-full max-w-lg">
        <input
          type="text"
          placeholder="Search"
          className="w-full px-4 py-2 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
      </div>

      {/* Right Side Icons */}
      <div className="flex items-center gap-6">
        <button className="text-gray-600 hover:text-gray-800 relative">
          <FaBell className="text-xl" />
          <span className="absolute top-0 right-0 h-2 w-2 bg-red-500 rounded-full" />
        </button>
        <img
          src="/avatar.png"
          alt="Profile"
          className="w-10 h-10 rounded-full object-cover border-2 border-gray-300"
        />
      </div>
    </div>
  );
}
