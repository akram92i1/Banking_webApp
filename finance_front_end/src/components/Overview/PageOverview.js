import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import bankingService from '../../services/bankingService';
import BalanceCard from "../BalanceCard";
import TransactionHistoryCard from "../TransactionHistoryCard";
import QuickActionsCard from "../QuickActionsCard";
import StatsCard from "../StatsCard";
import ExchangeRateCard from "../ExchangeRateCard";
import TransferMoney from "../TransferMoney";

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
        // You can refresh balance/transaction data here
        // or trigger a refetch of account data
    };

    const getWelcomeMessage = () => {
        const username = user?.email ? user.email.split('@')[0] : 'User';
        return `Hello ${username}, welcome back!`;
    };

    return (
        <div className="p-6 flex-grow overflow-auto">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h1 className='text-2xl md:text-3xl font-bold'>Overview</h1>
                    <h2 className="text-gray-600 mt-1">{getWelcomeMessage()}</h2>
                </div>
                
                {/* API Connection Status */}
                <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${
                        connectionStatus === 'connected' ? 'bg-green-500' : 
                        connectionStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                    }`}></div>
                    <span className="text-sm text-gray-500">
                        {connectionStatus === 'connected' ? 'API Connected' : 
                         connectionStatus === 'error' ? 'API Error' : 'Checking API...'}
                    </span>
                </div>
            </div>
            
            <BalanceCard />
            <div className="flex w-full gap-6 mt-6">
                <div className="w-1/2">
                    <TransactionHistoryCard />
                    <br />
                    <QuickActionsCard onTransferClick={() => setShowTransferModal(true)} />
                </div>
                <div className="w-1/2">
                    <StatsCard />
                </div>
            </div>
            <div className="mt-6">
                <ExchangeRateCard />
            </div>

            {/* Transfer Money Modal */}
            <TransferMoney 
                isOpen={showTransferModal}
                onClose={() => setShowTransferModal(false)}
                onTransferComplete={handleTransferComplete}
            />
        </div>
    );
}