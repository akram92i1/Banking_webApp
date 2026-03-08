import React from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';
import BalanceCard from '../components/BalanceCard';
import QuickActionsCard from '../components/QuickActionsCard';
import TransactionHistoryCard from '../components/TransactionHistoryCard';

export default function OverviewScreen() {
    const { user } = useAuth();

    return (
        <SafeAreaView className="flex-1 bg-slate-950">
            <ScrollView className="flex-1 px-4 pt-6">

                {/* Header Section */}
                <View className="flex-row justify-between items-center mb-8">
                    <View>
                        <Text className="text-slate-400 text-sm">Welcome back</Text>
                        <Text className="text-white text-2xl font-bold">{user?.email || 'User'}</Text>
                    </View>
                    <TouchableOpacity className="bg-slate-800 p-2 rounded-full border border-slate-700">
                        <Ionicons name="notifications-outline" size={24} color="#f8fafc" />
                    </TouchableOpacity>
                </View>

                {/* Dynamic Balance Card */}
                <BalanceCard />

                {/* Dynamic Quick Actions */}
                <QuickActionsCard onTransferClick={() => console.log('Open Transfer')} />

                {/* Dynamic Recent Transactions */}
                <TransactionHistoryCard />

            </ScrollView>
        </SafeAreaView>
    );
}
