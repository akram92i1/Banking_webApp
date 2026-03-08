import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { styled } from 'nativewind';

export default function LoginScreen() {
    const { login } = useAuth();
    const [identifier, setIdentifier] = useState('user001@example.com');
    const [password, setPassword] = useState('password123');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async () => {
        try {
            setError('');
            setLoading(true);
            const result = await login({ identifier, password });
            if (!result.success) {
                setError(result.message || 'Login failed');
            }
        } catch (err) {
            setError('An error occurred during login');
        } finally {
            setLoading(false);
        }
    };

    return (
        <SafeAreaView className="flex-1 bg-slate-950">
            <KeyboardAvoidingView
                behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
                className="flex-1 justify-center px-6"
            >
                <View className="items-center mb-10">
                    <View className="mb-4 bg-blue-500/10 p-4 rounded-full">
                        <Ionicons name="wallet" size={48} color="#3b82f6" />
                    </View>
                    <Text className="text-3xl font-bold text-slate-100 tracking-tight">Finova Bank</Text>
                    <Text className="text-slate-400 mt-2 text-center text-sm">Sign in to your intelligent banking experience</Text>
                </View>

                <View className="space-y-4">
                    <View>
                        <Text className="text-sm font-medium text-slate-300 mb-1 ml-1">Email or Card Number</Text>
                        <View className="flex-row items-center bg-slate-900 border border-slate-700/50 rounded-xl px-4 h-14">
                            <Ionicons name="mail" size={20} color="#64748b" />
                            <TextInput
                                className="flex-1 text-slate-100 ml-3 text-base"
                                placeholder="Enter your email"
                                placeholderTextColor="#475569"
                                value={identifier}
                                onChangeText={setIdentifier}
                                autoCapitalize="none"
                            />
                        </View>
                    </View>

                    <View>
                        <Text className="text-sm font-medium text-slate-300 mb-1 ml-1">Password</Text>
                        <View className="flex-row items-center bg-slate-900 border border-slate-700/50 rounded-xl px-4 h-14">
                            <Ionicons name="lock-closed" size={20} color="#64748b" />
                            <TextInput
                                className="flex-1 text-slate-100 ml-3 text-base"
                                placeholder="Enter your password"
                                placeholderTextColor="#475569"
                                secureTextEntry
                                value={password}
                                onChangeText={setPassword}
                            />
                        </View>
                    </View>

                    {error ? <Text className="text-red-400 text-sm text-center">{error}</Text> : null}

                    <TouchableOpacity
                        className="bg-blue-600 rounded-xl mt-4 h-14 items-center justify-center flex-row shadow-lg shadow-blue-600/20"
                        onPress={handleLogin}
                        disabled={loading}
                    >
                        <Text className="text-white font-semibold text-base">{loading ? 'Signing in...' : 'Sign In'}</Text>
                    </TouchableOpacity>
                </View>
            </KeyboardAvoidingView>
        </SafeAreaView>
    );
}
