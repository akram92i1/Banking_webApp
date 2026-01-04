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
              {/* Main App Background - Sharp Dark Banking Theme */}
              <div className="min-h-screen bg-slate-950 relative overflow-hidden font-sans text-slate-100">

                {/* Subtle Dark Background Accents */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                  {/* Deep Blue Glow Top Right */}
                  <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-blue-900/20 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2"></div>
                  {/* Deep Indigo Glow Bottom Left */}
                  <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-indigo-900/10 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/4"></div>
                </div>

                <div className="flex h-screen relative z-10">
                  {/* Responsive Sidebar - Dark Surface */}
                  <div className="hidden md:block w-64 bg-slate-900 border-r border-slate-800 shadow-xl z-20">
                    <Sidebar />
                  </div>

                  {/* Main Content Area */}
                  <div className="flex-1 flex flex-col relative overflow-hidden">
                    {/* Header - Dark Surface */}
                    <div className="bg-slate-900/95 border-b border-slate-800 sticky top-0 z-30 shadow-sm">
                      <Header />
                    </div>

                    {/* Content Area */}
                    <div className="flex-1 overflow-auto p-4 md:p-8 relative scroll-smooth bg-slate-950">
                      <div className="max-w-7xl mx-auto space-y-6">
                        <Routes>
                          <Route path="/" element={<PageOverview />} />
                          <Route path="/overview" element={<PageOverview />} />
                          <Route path="/wallet" element={<MyWalletTable />} />
                          <Route path="/profile" element={<ProfileCard user={{ avatarUrl: "https://avatar.iran.liara.run/public", profilename: "Akram", email: "tes@test.com", phone: "004534234", }} />} />
                          <Route path="/settings" element={<Settings />} />
                          <Route path="*" element={<Navigate to="/" />} />
                        </Routes>
                      </div>
                    </div>
                  </div>

                  {/* AI Assistant - Floating Widget */}
                  <AIAssistant
                    userRole="user"
                    userId="akram001"
                    location="toronto"
                  />
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
