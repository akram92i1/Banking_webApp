import React from 'react';
import { View, Text, ScrollView, Switch } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function SettingsScreen() {
    const [notifications, setNotifications] = React.useState(true);
    const [darkMode, setDarkMode] = React.useState(true);
    const [faceId, setFaceId] = React.useState(true);

    return (
        <SafeAreaView className="flex-1 bg-slate-950">
            <ScrollView className="flex-1 px-4 pt-6">
                <Text className="text-white text-2xl font-bold mb-6">Settings</Text>

                <Text className="text-slate-400 uppercase text-xs font-bold mb-3 mt-4 tracking-wider">Preferences</Text>
                <View className="bg-slate-900 rounded-2xl p-4 border border-slate-800">
                    <View className="flex-row items-center justify-between py-2 border-b border-slate-800">
                        <View className="flex-row items-center">
                            <Ionicons name="notifications-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Push Notifications</Text>
                        </View>
                        <Switch value={notifications} onValueChange={setNotifications} trackColor={{ false: '#334155', true: '#3b82f6' }} />
                    </View>
                    <View className="flex-row items-center justify-between py-2 border-b border-slate-800">
                        <View className="flex-row items-center">
                            <Ionicons name="moon-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Dark Mode</Text>
                        </View>
                        <Switch value={darkMode} onValueChange={setDarkMode} trackColor={{ false: '#334155', true: '#3b82f6' }} />
                    </View>
                    <View className="flex-row items-center justify-between py-2">
                        <View className="flex-row items-center">
                            <Ionicons name="scan-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Face ID / Biometrics</Text>
                        </View>
                        <Switch value={faceId} onValueChange={setFaceId} trackColor={{ false: '#334155', true: '#3b82f6' }} />
                    </View>
                </View>

                <Text className="text-slate-400 uppercase text-xs font-bold mb-3 mt-8 tracking-wider">Support</Text>
                <View className="bg-slate-900 rounded-2xl p-4 border border-slate-800">
                    <View className="flex-row items-center justify-between py-3 border-b border-slate-800">
                        <View className="flex-row items-center">
                            <Ionicons name="help-circle-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Help Center</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color="#475569" />
                    </View>
                    <View className="flex-row items-center justify-between py-3">
                        <View className="flex-row items-center">
                            <Ionicons name="document-text-outline" size={20} color="#94a3b8" />
                            <Text className="text-white ml-3">Terms & Conditions</Text>
                        </View>
                        <Ionicons name="chevron-forward" size={20} color="#475569" />
                    </View>
                </View>

            </ScrollView>
        </SafeAreaView>
    );
}
