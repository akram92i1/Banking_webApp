import React from "react";
import { View, Text, TouchableOpacity, Alert } from "react-native";
import { Ionicons } from "@expo/vector-icons";

export default function QuickActionsCard({ onTransferClick }) {
    const actions = [
        {
            label: "Top up",
            icon: "card-outline",
            onClick: () => Alert.alert("Coming Soon", "Top up feature coming soon!")
        },
        {
            label: "Scan",
            icon: "scan-outline",
            onClick: () => Alert.alert("Coming Soon", "Scan & Pay feature coming soon!")
        },
        {
            label: "Send",
            icon: "send-outline",
            onClick: onTransferClick || (() => Alert.alert("Not Available", "Transfer feature not available"))
        },
        {
            label: "Request",
            icon: "download-outline",
            onClick: () => Alert.alert("Coming Soon", "Request money feature coming soon!")
        },
    ];

    return (
        <View className="mb-8">
            <Text className="text-white text-lg font-semibold mb-4">Quick Actions</Text>
            <View className="flex-row justify-between">
                {actions.map((action, index) => (
                    <View key={index} className="items-center">
                        <TouchableOpacity
                            onPress={action.onClick}
                            className="w-16 h-16 bg-slate-900 border border-slate-800 rounded-2xl items-center justify-center mb-2 active:bg-blue-600/30"
                        >
                            <Ionicons
                                name={action.icon}
                                size={24}
                                color="#60a5fa"
                            />
                        </TouchableOpacity>
                        <Text className="text-slate-400 text-xs font-medium">{action.label}</Text>
                    </View>
                ))}
            </View>
        </View>
    );
}
