// components/Sidebar.js
import { FaWallet, FaUser, FaCog, FaQuestionCircle, FaSignOutAlt, FaChartPie  } from 'react-icons/fa';
import  {Link} from 'react-router-dom'
export default function Sidebar() {
    return (
      <div className="bg-white w-64 min-h-screen p-4 flex flex-col justify-between border-r">
        <div>
          <h1 className="text-xl font-bold flex items-center gap-2 mb-6">
            <span>🧊</span> Mini Finance
          </h1>
          <nav className="space-y-3">
            <Link to="/overview" className="flex items-center gap-3 text-white bg-red-500 px-4 py-2 rounded-md w-full">
              <FaChartPie /> Overview
            </Link>
            <Link to="/wallet" className="flex items-center gap-3 text-gray-600 hover:text-black">
              <FaWallet /> My Wallet
            </Link>
            <button className="flex items-center gap-3 text-gray-600 hover:text-black">
              <FaUser /> Profile
            </button>
            <button className="flex items-center gap-3 text-gray-600 hover:text-black">
              <FaCog /> Settings
            </button>
            <button className="flex items-center gap-3 text-gray-600 hover:text-black">
              <FaQuestionCircle /> Help Center
            </button>
          </nav>
  
          <div className="mt-10 bg-gray-100 p-4 rounded-xl flex flex-col items-center">
             <FaWallet className=' h-10 w-10 text-blue-600' /> 
            <button className="bg-teal-300 mt-3  text-white px-4 py-1 rounded-full text-xl">Upgrade</button>
          </div>
        </div>
        <button className="flex items-center gap-2 text-gray-600 hover:text-black mt-6">
          <FaSignOutAlt /> Logout
        </button>
      </div>
    );
  }