import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Header from './components/Header';
import Sidebar from './components/SideBar';
import MyWalletTable from './components/MyWallet/MyWalletTable';
import PageOverview from './components/Overview/PageOverview';
import ProfileCard from './components/ProfileCard';
import Settings from './components/Settings';
import AIAssistant from './components/AIAssistant';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected routes */}
          <Route path="/*" element={
            <ProtectedRoute>
              {/* Main App Background with Glass Effect */}
              <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-800 relative overflow-hidden">
                {/* Animated Background Elements */}
                <div className="absolute inset-0">
                  <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse"></div>
                  <div className="absolute top-1/3 right-1/4 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-2000"></div>
                  <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-pink-400 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-pulse animation-delay-4000"></div>
                </div>

                <div className="flex h-screen relative z-10">
                  {/* Sidebar with Glass Effect */}
                  <div className="w-1/5 backdrop-blur-xl bg-white/10 border-r border-white/20 shadow-2xl">
                    <Sidebar />
                  </div>

                  {/* Main Content Area */}
                  <div className="flex-1 flex flex-col">
                    {/* Header with Glass Effect */}
                    <div className="backdrop-blur-xl bg-white/5 border-b border-white/10">
                      <Header />
                    </div>

                    {/* Content Area - Direct without extra frame */}
                    <div className="p-6 flex-grow overflow-auto">
                      <Routes>
                        <Route path="/" element={<PageOverview />} />
                        <Route path="/overview" element={<PageOverview />} />
                        <Route path="/wallet" element={<MyWalletTable />} />
                        <Route path="/profile" element={<ProfileCard user={{avatarUrl:"https://avatar.iran.liara.run/public",profilename:"Akram", email:"tes@test.com",phone:"004534234",}} />} />
                        <Route path="/settings" element={<Settings />} />
                        <Route path="*" element={<Navigate to="/" />} />
                      </Routes>
                    </div>
                  </div>
                  
                  {/* AI Assistant with Glass Effect */}
                  <div className="backdrop-blur-xl bg-white/5 border-l border-white/10 shadow-2xl">
                    <AIAssistant 
                      userRole="user" 
                      userId="akram001" 
                      location="toronto" 
                    />
                  </div>
                </div>
              </div>
            </ProtectedRoute>
          } />
        </Routes>
      </Router> 
    </AuthProvider>
  );
}

export default App;
