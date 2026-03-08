import React, { useState, useEffect } from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import bankingService from '../services/bankingService';

export default function TransactionHistoryCard() {
    const { user } = useAuth();
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchTransactions();
    }, []);

    const fetchTransactions = async () => {
        try {
            const result = await bankingService.getCurrentUserTransactions(5);
            if (result.success) {
                setTransactions(result.data);
            } else {
                setError(result.message || 'Failed to fetch transactions');
            }
        } catch (error) {
            console.error('Error fetching transactions:', error);
            setError('Failed to fetch transactions');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const formatAmount = (amount, transactionType, fromAccount, toAccount) => {
        const formattedAmount = new Intl.NumberFormat('en-CA', {
            style: 'currency',
            currency: 'CAD'
        }).format(Math.abs(amount));

        const currentUserEmail = user?.email;
        const isIncoming = toAccount?.user?.email === currentUserEmail;
        const isOutgoing = fromAccount?.user?.email === currentUserEmail;

        if (isIncoming && !isOutgoing) {
            return { amount: `+${formattedAmount}`, type: 'credit' };
        } else if (isOutgoing && !isIncoming) {
            return { amount: `-${formattedAmount}`, type: 'debit' };
        } else {
            return {
                amount: `${amount >= 0 ? '+' : '-'}${formattedAmount}`,
                type: amount >= 0 ? 'credit' : 'debit'
            };
        }
    };

    const getTransactionDescription = (transaction) => {
        if (transaction.description) return transaction.description;

        switch (transaction.transactionType) {
            case 'TRANSFER': return 'Transfer';
            case 'DEPOSIT': return 'Deposit';
            case 'WITHDRAWAL': return 'Withdrawal';
            case 'PAYMENT': return 'Payment';
            default: return 'Transaction';
        }
    };

    if (loading) {
        return (
            <View className="mb-6">
                <Text className="text-white text-lg font-semibold mb-4">Recent Transactions</Text>
                <ActivityIndicator size="small" color="#60a5fa" className="py-8" />
            </View>
        );
    }

    return (
        <View className="mb-6">
            <Text className="text-white text-lg font-semibold mb-4">Recent Transactions</Text>

            {error ? (
                <View className="bg-red-500/10 rounded-xl p-4 border border-red-500/30">
                    <Text className="text-red-400">{error}</Text>
                </View>
            ) : transactions.length === 0 ? (
                <View className="bg-slate-900/50 p-6 rounded-2xl items-center border border-slate-800/50">
                    <Ionicons name="receipt-outline" size={32} color="#475569" className="mb-2" />
                    <Text className="text-slate-400">No transactions found</Text>
                </View>
            ) : (
                <View className="space-y-3">
                    {transactions.map((tx) => {
                        const { amount, type } = formatAmount(tx.amount, tx.transactionType, tx.fromAccount, tx.toAccount);
                        const isCompleted = tx.transactionStatus === 'COMPLETED';

                        return (
                            <View
                                key={`${tx.transactionId}-${tx.createdAt}`}
                                className="flex-row items-center justify-between bg-slate-900/80 p-4 rounded-2xl mb-3 border border-slate-800"
                            >
                                <View className="flex-row items-center flex-1">
                                    <View className={`w-10 h-10 rounded-full items-center justify-center mr-3 ${type === 'credit' ? 'bg-emerald-500/20' : 'bg-rose-500/20'
                                        }`}>
                                        <Ionicons
                                            name={type === 'credit' ? 'arrow-down' : 'arrow-up'}
                                            size={20}
                                            color={type === 'credit' ? '#34d399' : '#fb7185'}
                                        />
                                    </View>
                                    <View className="flex-1 pr-2">
                                        <Text className="text-white font-medium" numberOfLines={1}>{getTransactionDescription(tx)}</Text>
                                        <View className="flex-row items-center mt-1">
                                            <Text className="text-slate-500 text-xs mr-2">{formatDate(tx.createdAt)}</Text>
                                            <View className={`w-1.5 h-1.5 rounded-full mr-1 ${isCompleted ? 'bg-green-400' : 'bg-yellow-400'
                                                }`} />
                                            <Text className="text-slate-500 text-[10px] uppercase">{tx.transactionStatus}</Text>
                                        </View>
                                    </View>
                                </View>
                                <Text className={`font-bold ${type === 'credit' ? 'text-emerald-400' : 'text-slate-200'}`}>
                                    {amount}
                                </Text>
                            </View>
                        );
                    })}
                </View>
            )}
        </View>
    );
}
