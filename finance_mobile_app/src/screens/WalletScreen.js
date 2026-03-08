import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import MyWalletTable from '../components/MyWallet/MyWalletTable';
import { useAuth } from '../contexts/AuthContext';
import bankingService from '../services/bankingService';

export default function WalletScreen() {
    const { user } = useAuth();
    const [balance, setBalance] = useState(0);
    const [accountNumber, setAccountNumber] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAccountDetails();
    }, []);

    const fetchAccountDetails = async () => {
        try {
            const result = await bankingService.getCurrentUserAccounts();
            if (result.success && result.data.length > 0) {
                setBalance(result.data[0].balance);
                setAccountNumber(result.data[0].accountNumber);
            }
        } catch (e) {
            console.error(e);
        } finally {
            setLoading(false);
        }
    };

    const formatBalance = (amount) => {
        return new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(amount);
    };

    const lastFour = accountNumber ? accountNumber.slice(-4) : '****';
    const cardHolder = user?.firstName ? `${user.firstName} ${user.lastName}`.toUpperCase() : (user?.email?.split('@')[0] || 'USER').toUpperCase();
    return (
        <SafeAreaView className="flex-1 bg-slate-950">
            <ScrollView className="flex-1 px-4 pt-6">
                <Text className="text-white text-2xl font-bold mb-6">My Wallet</Text>

                <View className="bg-slate-900 rounded-2xl p-6 border border-slate-800 mb-4 items-center">
                    <Text className="text-slate-400 mb-2 uppercase tracking-widest text-xs font-semibold">Available Balance</Text>
                    {loading ? (
                        <ActivityIndicator size="small" color="#60a5fa" />
                    ) : (
                        <Text className="text-white text-3xl font-bold">{formatBalance(balance)}</Text>
                    )}
                </View>

                <View className="bg-slate-900 rounded-2xl p-6 border border-slate-800 relative overflow-hidden mb-8">
                    {/* Card Design */}
                    <View className="absolute top-0 right-0 w-32 h-32 bg-blue-600/20 rounded-full blur-2xl -translate-y-10 translate-x-10"></View>

                    <Text className="text-white/60 mb-8 font-medium tracking-widest">FINOVA BANK</Text>
                    <Text className="text-white text-xl font-mono tracking-widest mb-4">**** **** **** {lastFour}</Text>

                    <View className="flex-row justify-between">
                        <View>
                            <Text className="text-white/60 text-xs mb-1 uppercase tracking-wider">Card Holder</Text>
                            <Text className="text-white font-medium">{cardHolder}</Text>
                        </View>
                        <View>
                            <Text className="text-white/60 text-xs mb-1 uppercase tracking-wider">Expires</Text>
                            <Text className="text-white font-medium">12/28</Text>
                        </View>
                    </View>
                </View>

                <MyWalletTable />
            </ScrollView>
        </SafeAreaView>
    );
}
