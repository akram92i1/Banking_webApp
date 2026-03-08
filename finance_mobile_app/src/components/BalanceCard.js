import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import bankingService from '../services/bankingService';

export default function BalanceCard() {
    const { user } = useAuth();
    const [accounts, setAccounts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchAccountData();
    }, []);

    const fetchAccountData = async () => {
        try {
            const result = await bankingService.getCurrentUserAccounts();
            if (result.success) {
                setAccounts(result.data);
            } else {
                setError(result.message || 'Failed to fetch account data');
            }
        } catch (error) {
            console.error('Error fetching account data:', error);
            setError('Failed to fetch account data');
        } finally {
            setLoading(false);
        }
    };

    const formatBalance = (balance) => {
        return new Intl.NumberFormat('en-CA', {
            style: 'currency',
            currency: 'CAD'
        }).format(balance);
    };

    const formatAccountNumber = (accountNumber) => {
        if (!accountNumber) return '**** **** **** ****';
        const lastFour = accountNumber.slice(-4);
        return `**** **** **** ${lastFour}`;
    };

    const getCardHolderName = () => {
        if (user?.firstName && user?.lastName) {
            return `${user.firstName} ${user.lastName}`;
        }
        return user?.email?.split('@')[0] || 'User';
    };

    const primaryAccount = accounts.length > 0 ? accounts[0] : null;

    if (loading) {
        return (
            <View className="bg-slate-900/80 rounded-3xl p-6 border border-slate-800 mb-6 shadow-xl items-center justify-center min-h-[200px]">
                <ActivityIndicator size="large" color="#60a5fa" />
            </View>
        );
    }

    return (
        <View className="bg-slate-900/80 rounded-3xl p-6 border border-slate-800 mb-6 shadow-xl relative overflow-hidden">
            {/* Decorative blurs */}
            <View className="absolute -top-10 -right-10 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl"></View>

            <View className="flex-row justify-between items-center mb-4">
                <Text className="text-slate-400 text-sm font-medium uppercase tracking-widest">Your Balance</Text>
                <View className="w-8 h-8 rounded-full bg-blue-500/20 items-center justify-center">
                    <Ionicons name="card-outline" size={16} color="#60a5fa" />
                </View>
            </View>

            {error ? (
                <View className="bg-red-500/10 rounded-xl p-3 border border-red-500/30 mb-4">
                    <Text className="text-red-400 text-sm">{error}</Text>
                </View>
            ) : (
                <Text className="text-white text-4xl font-bold tracking-tight mb-6">
                    {primaryAccount ? formatBalance(primaryAccount.balance) : '$0.00'}
                </Text>
            )}

            <View className="bg-slate-800/50 rounded-2xl p-4 mb-4 items-center border border-slate-700/50">
                <Text className="text-white text-lg font-mono tracking-widest">
                    {primaryAccount ? formatAccountNumber(primaryAccount.accountNumber) : '**** **** **** ****'}
                </Text>
            </View>

            <View className="flex-row justify-between">
                <View className="bg-slate-800/50 rounded-xl p-3 flex-1 mr-2 items-center border border-slate-700/50">
                    <Text className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Account Type</Text>
                    <Text className="text-white font-medium">{primaryAccount ? primaryAccount.accountType : 'CHECKING'}</Text>
                </View>
                <View className="bg-slate-800/50 rounded-xl p-3 flex-1 ml-2 items-center border border-slate-700/50">
                    <Text className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Holder</Text>
                    <Text className="text-white font-medium">{getCardHolderName()}</Text>
                </View>
            </View>

            {accounts.length > 1 && (
                <View className="items-center mt-4 pt-4 border-t border-slate-800">
                    <Text className="text-slate-500 text-xs font-medium">+{accounts.length - 1} more account{accounts.length > 2 ? 's' : ''}</Text>
                </View>
            )}
        </View>
    );
}
