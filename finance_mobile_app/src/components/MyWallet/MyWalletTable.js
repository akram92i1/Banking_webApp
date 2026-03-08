import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, TextInput, Modal, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import bankingService from '../../services/bankingService';

export default function MyWalletTable() {
    const { user } = useAuth();
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const [searchTerm, setSearchTerm] = useState('');
    const [filterType, setFilterType] = useState('ALL');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const transactionsResult = await bankingService.getCurrentUserTransactions(50); // Get more for filtering
            if (transactionsResult.success) {
                setTransactions(transactionsResult.data);
            } else {
                setError(transactionsResult.message || 'Failed to fetch transactions');
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            setError('Failed to fetch wallet data');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    };

    const formatTime = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    };

    const formatAmount = (amount, transactionType, fromAccount, toAccount) => {
        const val = parseFloat(amount || 0);
        const formatted = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' }).format(Math.abs(val));

        const currentUserEmail = user?.email;
        const fromAccountEmail = fromAccount?.user?.email || fromAccount?.userEmail;

        let sign = '+';
        let isPositive = true;

        if (transactionType === 'WITHDRAWAL') {
            sign = '-'; isPositive = false;
        } else if (transactionType === 'DEPOSIT') {
            sign = '+'; isPositive = true;
        } else if (fromAccountEmail === currentUserEmail) {
            sign = '-'; isPositive = false;
        }

        return { text: `${sign} ${formatted}`, isPositive };
    };

    const handleTransactionAction = async (transactionId, status) => {
        try {
            const result = await bankingService.updateTransactionStatus(transactionId, status);
            if (result.success) {
                fetchData();
            } else {
                Alert.alert('Failed', result.message);
            }
        } catch (e) {
            Alert.alert('Error', 'Failed to update transaction');
        }
    };

    // Process data
    let processedData = [...transactions];

    if (filterType !== 'ALL') {
        processedData = processedData.filter(t => t.transactionType === filterType);
    }
    if (searchTerm) {
        const lower = searchTerm.toLowerCase();
        processedData = processedData.filter(t =>
            (t.description || '').toLowerCase().includes(lower) ||
            (t.transactionType || '').toLowerCase().includes(lower)
        );
    }

    const getStatusColor = (status) => {
        switch (status) {
            case 'COMPLETED': case 'SUCCESS': return 'text-emerald-400 bg-emerald-500/20';
            case 'PENDING': return 'text-yellow-400 bg-yellow-500/20';
            case 'CANCELLED': case 'FAILED': return 'text-red-400 bg-red-500/20';
            default: return 'text-slate-400 bg-slate-500/20';
        }
    };

    if (loading) {
        return (
            <View className="bg-slate-900 rounded-3xl p-6 border border-slate-800 min-h-[300px] items-center justify-center">
                <ActivityIndicator size="large" color="#60a5fa" />
            </View>
        )
    }

    return (
        <View className="bg-slate-900 rounded-3xl p-4 border border-slate-800 mb-8">
            {/* Header and Controls */}
            <View className="mb-6">
                <Text className="text-white text-xl font-bold mb-4">Transaction History</Text>

                {/* Search Bar */}
                <View className="flex-row items-center bg-slate-800 rounded-xl px-4 py-2 mb-4 border border-slate-700">
                    <Ionicons name="search" size={20} color="#94a3b8" />
                    <TextInput
                        className="flex-1 text-white ml-2 py-2"
                        placeholder="Search transactions..."
                        placeholderTextColor="#64748b"
                        value={searchTerm}
                        onChangeText={setSearchTerm}
                    />
                </View>

                {/* Filter Pills */}
                <ScrollView horizontal showsHorizontalScrollIndicator={false} className="flex-row">
                    {['ALL', 'TRANSFER', 'DEPOSIT'].map(type => (
                        <TouchableOpacity
                            key={type}
                            onPress={() => setFilterType(type)}
                            className={`mr-2 px-4 py-2 rounded-xl transition-colors ${filterType === type ? 'bg-blue-600' : 'bg-slate-800 border border-slate-700'
                                }`}
                        >
                            <Text className={`font-semibold ${filterType === type ? 'text-white' : 'text-slate-400'}`}>
                                {type === 'ALL' ? 'All' : type.charAt(0) + type.slice(1).toLowerCase()}
                            </Text>
                        </TouchableOpacity>
                    ))}
                </ScrollView>
            </View>

            {/* Transaction List */}
            {processedData.length > 0 ? (
                processedData.map((tx, idx) => {
                    const { text: amountText, isPositive } = formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount);
                    const currentUserEmail = user?.email;
                    const toAccountEmail = tx.toAccount?.user?.email || tx.toAccount?.userEmail;
                    const isIncoming = toAccountEmail === currentUserEmail;

                    return (
                        <View key={idx} className="flex-row justify-between items-center py-4 border-b border-slate-800">
                            <View className="flex-row items-center flex-1 pr-2">
                                <View className="w-10 h-10 bg-slate-800 rounded-xl items-center justify-center mr-3 border border-white/5">
                                    <Text className="text-white font-bold text-lg">{(tx.description || 'TX').charAt(0).toUpperCase()}</Text>
                                </View>
                                <View className="flex-1">
                                    <Text className="text-white font-medium mb-1" numberOfLines={1}>{tx.description || 'No Description'}</Text>
                                    <Text className="text-slate-500 text-xs">{formatDate(tx.createdAt)} • {formatTime(tx.createdAt)}</Text>
                                </View>
                            </View>

                            <View className="items-end">
                                <Text className={`font-bold mb-1 ${isPositive ? 'text-emerald-400' : 'text-white'}`}>{amountText}</Text>
                                <Text className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${getStatusColor(tx.transactionStatus || tx.status)}`}>
                                    {tx.transactionStatus || tx.status || 'PENDING'}
                                </Text>

                                {/* Action Buttons for Pending Incoming */}
                                {isIncoming && (tx.transactionStatus || tx.status) === 'PENDING' && (
                                    <View className="flex-row gap-2 mt-2">
                                        <TouchableOpacity
                                            onPress={() => handleTransactionAction(tx.transactionId || tx.id, 'COMPLETED')}
                                            className="w-8 h-8 rounded-full bg-emerald-500/20 items-center justify-center border border-emerald-500/30"
                                        >
                                            <Ionicons name="checkmark" size={16} color="#34d399" />
                                        </TouchableOpacity>
                                        <TouchableOpacity
                                            onPress={() => handleTransactionAction(tx.transactionId || tx.id, 'CANCELLED')}
                                            className="w-8 h-8 rounded-full bg-red-500/20 items-center justify-center border border-red-500/30"
                                        >
                                            <Ionicons name="close" size={16} color="#f87171" />
                                        </TouchableOpacity>
                                    </View>
                                )}
                            </View>
                        </View>
                    );
                })
            ) : (
                <View className="py-12 items-center justify-center">
                    <Ionicons name="filter" size={40} color="#334155" />
                    <Text className="text-slate-500 mt-4 text-center">No transactions found{'\n'}matching your criteria</Text>
                </View>
            )}
        </View>
    );
}
