import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import bankingService from '../../services/bankingService';
import BalanceCard from "../BalanceCard";
import TransactionHistoryCard from "../TransactionHistoryCard";
import QuickActionsCard from "../QuickActionsCard";
import StatsCard from "../StatsCard";
import ExchangeRateCard from "../ExchangeRateCard";
import EmailTransfer from "../EmailTransfer";

export default function PageOverview() {
    const { user } = useAuth();
    const [showTransferModal, setShowTransferModal] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('checking');
    
    useEffect(() => {
        // Test API connection when component mounts
        testAPIConnection();
    }, []);

    const testAPIConnection = async () => {
        try {
            const result = await bankingService.testConnectedUser();
            if (result.success) {
                setConnectionStatus('connected');
                console.log('API Connection successful:', result.data);
            } else {
                setConnectionStatus('error');
                console.error('API Connection failed:', result.message);
            }
        } catch (error) {
            setConnectionStatus('error');
            console.error('API Connection error:', error);
        }
    };

    const handleTransferComplete = (transferData) => {
        console.log('Transfer completed:', transferData);
        // Refresh the page to update balances and transactions
        window.location.reload();
    };

    const getWelcomeMessage = () => {
        const username = user?.email ? user.email.split('@')[0] : 'User';
        return `Hello ${username}, welcome back!`;
    };

    return (
        <div className="p-6 flex-grow overflow-auto relative">
            {/* Floating background elements */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-10 right-1/4 w-32 h-32 bg-blue-400 rounded-full opacity-10 blur-2xl animate-pulse-soft"></div>
                <div className="absolute bottom-1/3 left-1/4 w-40 h-40 bg-purple-400 rounded-full opacity-10 blur-3xl animate-pulse-soft animation-delay-2000"></div>
            </div>

            {/* Header with glass effect */}
            <div className="glass-card rounded-3xl p-6 mb-6 relative overflow-hidden animate-float">
                <div className="flex items-center justify-between">
                    <div className="relative z-10">
                        <h1 className='text-3xl md:text-4xl font-bold text-glass bg-gradient-to-r from-white via-blue-100 to-purple-100 bg-clip-text text-transparent'>
                            Overview
                        </h1>
                        <h2 className="text-glass-muted mt-2 text-lg">{getWelcomeMessage()}</h2>
                    </div>
                    
                    {/* API Connection Status with glass effect */}
                    <div className="glass-card rounded-2xl px-4 py-2 flex items-center gap-3 animate-float animation-delay-1000">
                        <div className="relative">
                            <div className={`w-4 h-4 rounded-full ${
                                connectionStatus === 'connected' ? 'bg-emerald-400' : 
                                connectionStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400'
                            } shadow-lg`}></div>
                            {connectionStatus === 'connected' && (
                                <div className="absolute inset-0 w-4 h-4 bg-emerald-400 rounded-full opacity-75 animate-ping"></div>
                            )}
                        </div>
                        <span className="text-sm text-glass font-medium">
                            {connectionStatus === 'connected' ? 'API Connected' : 
                             connectionStatus === 'error' ? 'API Error' : 'Checking API...'}
                        </span>
                    </div>
                </div>
                
                {/* Shimmer effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-shimmer"></div>
            </div>
            
            <BalanceCard />
            
            {/* Main content grid with glass spacing */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
                <div className="space-y-6">
                    <TransactionHistoryCard />
                    <QuickActionsCard onTransferClick={() => setShowTransferModal(true)} />
                </div>
                <div>
                    <StatsCard />
                </div>
            </div>
            
            <div className="mt-6">
                <ExchangeRateCard />
            </div>

            {/* Email Transfer Modal */}
            <EmailTransfer 
                isOpen={showTransferModal}
                onClose={() => setShowTransferModal(false)}
                onTransferComplete={handleTransferComplete}
            />
        </div>
    );
}