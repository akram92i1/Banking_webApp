import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/SideBar';
import MyWalletTable from './components/MyWallet/MyWalletTable';
import PageOverview from './components/Overview/PageOverview';
import ProfileCard from './components/ProfileCard';
import Settings from './components/Settings';
function App() {
  return (
    <Router>
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-1/5 border-r">
          <Sidebar />
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Header */}
          <Header />

          {/* Content Area Below Header */}
          <div className="p-6 flex-grow overflow-auto">
            <Routes>
              <Route path="/" element={<PageOverview />} /> {/* Default route   */}
              <Route path="/overview" element={<PageOverview />} />
              <Route path="/wallet" element={<MyWalletTable />} />
              <Route path="*" element={<Navigate to="/" />} /> {/* Catch-all */}
              <Route path="/profile" element={<ProfileCard user={{avatarUrl:"https://avatar.iran.liara.run/public",profilename:"Akram", email:"tes@test.com",phone:"004534234",}} />}  />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router> 
  );
}

export default App;
