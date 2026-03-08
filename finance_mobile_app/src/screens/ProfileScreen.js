import React from 'react';
import { View, Text, ScrollView, TouchableOpacity, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';

export default function ProfileScreen() {
    const { user, logout } = useAuth();

    return (
        <SafeAreaView className="flex-1 bg-slate-950">
            <ScrollView className="flex-1 px-4 pt-6">
                <Text className="text-white text-2xl font-bold mb-6">Profile</Text>

                <View className="items-center mb-8">
                    <View className="w-24 h-24 bg-slate-800 rounded-full mb-4 items-center justify-center border-2 border-slate-700">
                        <Ionicons name="person" size={40} color="#64748b" />
                    </View>
                    <Text className="text-white text-xl font-bold">{user?.email || 'User'}</Text>
                    <Text className="text-slate-400 mt-1">Free Plan</Text>
                </View>

                <View className="bg-slate-900 rounded-2xl p-4 border border-slate-800 mb-6">
                    <TouchableOpacity className="flex-row items-center justify-between py-3 border-b border-slate-800">
                        <View className="flex-row items-center">
                            <Ionicons name="person-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Personal Details</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color="#475569" />
                    </TouchableOpacity>
                    <TouchableOpacity className="flex-row items-center justify-between py-3 border-b border-slate-800">
                        <View className="flex-row items-center">
                            <Ionicons name="card-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Payment Methods</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color="#475569" />
                    </TouchableOpacity>
                    <TouchableOpacity className="flex-row items-center justify-between py-3">
                        <View className="flex-row items-center">
                            <Ionicons name="shield-checkmark-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Security Setup</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color="#475569" />
                    </TouchableOpacity>
                </View>

                <TouchableOpacity
                    className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 flex-row justify-center items-center"
                    onPress={logout}
                >
                    <Ionicons name="log-out-outline" size={20} color="#ef4444" />
                    <Text className="text-red-400 font-medium ml-2">Log Out</Text>
                </TouchableOpacity>
            </ScrollView>
        </SafeAreaView>
    );
}
