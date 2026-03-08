import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity, TextInput, ScrollView, Animated, KeyboardAvoidingView, Platform, Modal, Keyboard, Easing } from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import Markdown from 'react-native-markdown-display';
import aiService from '../services/aiService';

// Tabs Component for the bottom
const TabBar = ({ activeTab, setActiveTab }) => (
    <View className="bg-slate-800 border-t border-slate-700 p-2 flex-row justify-around safe-area-bottom">
        <TouchableOpacity
            onPress={() => setActiveTab('chat')}
            className={`p-2 rounded-lg items-center ${activeTab === 'chat' ? 'bg-blue-600/20' : ''}`}
        >
            <Ionicons name="chatbubbles" size={24} color={activeTab === 'chat' ? '#60a5fa' : '#94a3b8'} />
            <Text className={`text-[10px] mt-1 ${activeTab === 'chat' ? 'text-blue-400 font-bold' : 'text-slate-500'}`}>Chat</Text>
        </TouchableOpacity>
        <TouchableOpacity
            onPress={() => setActiveTab('advice')}
            className={`p-2 rounded-lg items-center ${activeTab === 'advice' ? 'bg-emerald-500/20' : ''}`}
        >
            <Ionicons name="trending-up" size={24} color={activeTab === 'advice' ? '#34d399' : '#94a3b8'} />
            <Text className={`text-[10px] mt-1 ${activeTab === 'advice' ? 'text-emerald-400 font-bold' : 'text-slate-500'}`}>Advice</Text>
        </TouchableOpacity>
        <TouchableOpacity
            onPress={() => setActiveTab('simulator')}
            className={`p-2 rounded-lg items-center ${activeTab === 'simulator' ? 'bg-purple-500/20' : ''}`}
        >
            <Ionicons name="calculator" size={24} color={activeTab === 'simulator' ? '#c084fc' : '#94a3b8'} />
            <Text className={`text-[10px] mt-1 ${activeTab === 'simulator' ? 'text-purple-400 font-bold' : 'text-slate-500'}`}>Simulator</Text>
        </TouchableOpacity>
    </View>
);

const ThinkingIndicator = () => {
    const pulseAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        Animated.loop(
            Animated.sequence([
                Animated.timing(pulseAnim, { toValue: 1, duration: 800, useNativeDriver: true, easing: Easing.inOut(Easing.ease) }),
                Animated.timing(pulseAnim, { toValue: 0, duration: 800, useNativeDriver: true, easing: Easing.inOut(Easing.ease) })
            ])
        ).start();
    }, []);

    return (
        <View className="flex-row items-center p-3 bg-slate-800 rounded-xl border border-slate-700 self-start ml-4 mb-4">
            <Animated.View style={{ opacity: pulseAnim }} className="flex-row space-x-1 mr-3">
                <View className="w-2 h-2 bg-blue-500 rounded-full" />
                <View className="w-2 h-2 bg-purple-500 rounded-full" />
                <View className="w-2 h-2 bg-pink-500 rounded-full" />
            </Animated.View>
            <Text className="text-xs font-medium text-slate-400">Thinking...</Text>
        </View>
    );
};

export default function AIAssistant({ userRole = 'user', userId = 'user001', location = 'toronto' }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat');
    const [messages, setMessages] = useState([]);
    const [adviceMessages, setAdviceMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('checking');

    // Animations
    const fabScale = useRef(new Animated.Value(1)).current;
    const scrollY = useRef(new Animated.Value(0)).current;
    const insets = useSafeAreaInsets();

    const chatScrollRef = useRef(null);
    const adviceScrollRef = useRef(null);

    useEffect(() => {
        // Pulsing FAB animation
        if (!isOpen) {
            Animated.loop(
                Animated.sequence([
                    Animated.timing(fabScale, { toValue: 1.05, duration: 1500, useNativeDriver: true }),
                    Animated.timing(fabScale, { toValue: 1, duration: 1500, useNativeDriver: true })
                ])
            ).start();
        }
    }, [isOpen]);

    useEffect(() => {
        if (isOpen && messages.length === 0) {
            initializeAI();
        }
    }, [isOpen]);

    const initializeAI = async () => {
        try {
            setConnectionStatus('checking');
            const health = await aiService.checkHealth();
            setConnectionStatus('connected');

            setMessages([{
                id: 1,
                text: "💰 Hello! I'm your Banking AI. I have secure access to your account data. How can I help you optimize your finances today?",
                sender: 'ai',
                timestamp: new Date()
            }]);

            setAdviceMessages([{
                id: 1,
                text: "🛒 Hello! I am your Financial Advisor. What is your weekly budget and how often do you shop?",
                sender: 'ai',
                timestamp: new Date()
            }]);
        } catch (error) {
            setConnectionStatus('error');
            setMessages([{ id: 1, text: "⚠️ Neural Link Unstable. Retrying connection...", sender: 'ai', timestamp: new Date(), isError: true }]);
        }
    };

    const sendMessage = async (isAdvice = false) => {
        if (!inputMessage.trim()) return;

        const userMessage = { id: Date.now(), text: inputMessage, sender: 'user', timestamp: new Date() };

        if (isAdvice) setAdviceMessages(prev => [...prev, userMessage]);
        else setMessages(prev => [...prev, userMessage]);

        setInputMessage('');
        setIsLoading(true);

        try {
            const userContext = { userId, userRole, location, preferences: { theme: 'banking' } };

            let result;
            if (isAdvice) {
                result = await aiService.adviceChat(userMessage.text, userContext);
            } else {
                result = await aiService.chat(userMessage.text, userContext);
            }

            const aiMessage = { id: Date.now() + 1, text: result.response, sender: 'ai', timestamp: new Date() };

            if (isAdvice) setAdviceMessages(prev => [...prev, aiMessage]);
            else setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            const errorMsg = { id: Date.now() + 1, text: `Error: ${error.message}.`, sender: 'ai', timestamp: new Date(), isError: true };
            if (isAdvice) setAdviceMessages(prev => [...prev, errorMsg]);
            else setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsLoading(false);
        }
    };

    const markdownStyles = {
        body: { color: '#f8fafc', fontSize: 15, lineHeight: 24, paddingBottom: 0 },
        strong: { fontWeight: 'bold', color: '#60a5fa' },
        em: { fontStyle: 'italic' },
        code_inline: { backgroundColor: '#1e293b', padding: 4, borderRadius: 4, fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace' },
        paragraph: { marginTop: 0, marginBottom: 8 }
    };

    // Island Indicator for iOS
    const DynamicIslandIndicator = () => {
        if (Platform.OS !== 'ios' || !isOpen || insets.top < 40) return null; // Only for notched/island iPhones
        return (
            <View className="absolute top-0 w-full items-center z-50 pointer-events-none" style={{ height: insets.top }}>
                <View className="mt-2" style={{ transform: [{ scale: 0.9 }] }}>
                    {isLoading ? (
                        <View className="bg-slate-900 rounded-full py-1.5 px-4 border border-blue-500/30 flex-row items-center shadow-lg shadow-blue-500/20">
                            <View className="w-1.5 h-1.5 bg-blue-400 rounded-full mr-1.5 animate-pulse" />
                            <View className="w-1.5 h-1.5 bg-purple-400 rounded-full mr-1.5 animate-pulse" style={{ animationDelay: '0.2s' }} />
                            <View className="w-1.5 h-1.5 bg-pink-400 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                        </View>
                    ) : (
                        <View className="bg-slate-900 rounded-full py-1.5 px-3 border border-slate-700/50 flex-row items-center shadow-lg shadow-black/50">
                            <Ionicons name="hardware-chip" size={12} color="#60a5fa" />
                            <Text className="text-[10px] text-blue-400 font-bold ml-1 tracking-widest">AI ACTIVE</Text>
                        </View>
                    )}
                </View>
            </View>
        );
    };

    const renderChatList = (chats, scrollView) => (
        <ScrollView
            ref={scrollView}
            onContentSizeChange={() => scrollView.current?.scrollToEnd({ animated: true })}
            className="flex-1 p-4"
            showsVerticalScrollIndicator={false}
        >
            {chats.map((msg) => (
                <View key={msg.id} className={`mb-4 max-w-[85%] ${msg.sender === 'user' ? 'self-end' : 'self-start'}`}>
                    <View className={`p-3 rounded-2xl shadow-sm ${msg.sender === 'user'
                        ? (activeTab === 'advice' ? 'bg-emerald-600 rounded-tr-sm' : 'bg-blue-600 rounded-tr-sm')
                        : msg.isError
                            ? 'bg-red-500/20 border border-red-500/30 rounded-tl-sm'
                            : 'bg-slate-800 border border-slate-700 rounded-tl-sm'
                        }`}>
                        {msg.sender === 'user' ? (
                            <Text className="text-white text-[15px] leading-6">{msg.text}</Text>
                        ) : (
                            <Markdown style={{ ...markdownStyles, strong: { color: activeTab === 'advice' ? '#34d399' : '#60a5fa' } }}>{msg.text}</Markdown>
                        )}
                    </View>
                    <Text className={`text-[10px] text-slate-500 mt-1 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {msg.sender === 'ai' ? 'AI' : 'You'}
                    </Text>
                </View>
            ))}
            {isLoading && <ThinkingIndicator />}
            <View style={{ height: 20 }} />
        </ScrollView>
    );

    return (
        <>
            {/* Animated FAB View */}
            {!isOpen && (
                <Animated.View style={{ transform: [{ scale: fabScale }] }} className="absolute bottom-6 right-6 z-50">
                    <TouchableOpacity
                        onPress={() => setIsOpen(true)}
                        activeOpacity={0.8}
                        className="w-16 h-16 bg-gradient-to-tr from-blue-700 to-purple-600 bg-blue-600 rounded-full items-center justify-center shadow-2xl border-2 border-white/20"
                    >
                        <Ionicons name="hardware-chip" size={32} color="#ffffff" />
                        <View className="absolute top-1 right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-blue-600" />
                    </TouchableOpacity>
                </Animated.View>
            )}

            {/* Expanded Full-Screen Modal */}
            <Modal visible={isOpen} animationType="slide" transparent={false} onRequestClose={() => setIsOpen(false)}>
                <View className="flex-1 bg-slate-950">
                    <DynamicIslandIndicator />
                    <SafeAreaView edges={['top', 'bottom']} className="flex-1">
                        <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} className="flex-1">

                            {/* Header */}
                            <View className="flex-row items-center justify-between p-4 bg-slate-900 border-b border-slate-800 shadow-md z-10">
                                <View className="flex-row items-center gap-3">
                                    <View className={`w-10 h-10 rounded-xl items-center justify-center ${activeTab === 'advice' ? 'bg-emerald-500/20' : 'bg-blue-600/20'}`}>
                                        <Ionicons name="hardware-chip" size={24} color={activeTab === 'advice' ? '#34d399' : '#60a5fa'} />
                                    </View>
                                    <View>
                                        <Text className="text-white font-bold tracking-wide text-lg">
                                            {activeTab === 'advice' ? 'FINANCIAL ADVISOR' : 'BANKING AI'}
                                        </Text>
                                        <View className="flex-row items-center gap-1">
                                            <View className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'}`} />
                                            <Text className="text-slate-400 text-[10px] uppercase tracking-wider">
                                                {connectionStatus === 'connected' ? 'Neural Link Active' : 'Offline'}
                                            </Text>
                                        </View>
                                    </View>
                                </View>
                                <TouchableOpacity onPress={() => setIsOpen(false)} className="w-10 h-10 items-center justify-center bg-slate-800 rounded-full">
                                    <Ionicons name="close" size={24} color="#94a3b8" />
                                </TouchableOpacity>
                            </View>

                            {/* Main Content Area */}
                            <View className="flex-1 bg-slate-900 relative">
                                {/* Decorative background pattern */}
                                <View className="absolute inset-0 opacity-5">
                                    <View className="w-64 h-64 bg-blue-500 rounded-full blur-3xl absolute -top-32 -left-32" />
                                    <View className="w-64 h-64 bg-purple-500 rounded-full blur-3xl absolute -bottom-32 -right-32" />
                                </View>

                                {activeTab === 'chat' && renderChatList(messages, chatScrollRef)}
                                {activeTab === 'advice' && renderChatList(adviceMessages, adviceScrollRef)}
                                {activeTab === 'simulator' && (
                                    <View className="flex-1 items-center justify-center p-8">
                                        <Ionicons name="calculator-outline" size={64} color="#475569" className="mb-4" />
                                        <Text className="text-slate-400 text-center text-lg font-medium">Savings Simulator</Text>
                                        <Text className="text-slate-500 text-center mt-2">Mobile implementation coming soon.</Text>
                                    </View>
                                )}
                            </View>

                            {/* Input Area (Only for chat and advice) */}
                            {activeTab !== 'simulator' && (
                                <View className="p-3 bg-slate-900 border-t border-slate-800">
                                    <View className="flex-row items-end bg-slate-800/80 rounded-3xl border border-slate-700 pr-2 pl-4 py-1">
                                        <TextInput
                                            className="flex-1 text-white text-[15px] pt-3 pb-3 max-h-32 leading-6"
                                            placeholder={activeTab === 'advice' ? "Ask for financial advice..." : "Ask me anything..."}
                                            placeholderTextColor="#64748b"
                                            value={inputMessage}
                                            onChangeText={setInputMessage}
                                            multiline
                                            scrollEnabled
                                        />
                                        <TouchableOpacity
                                            onPress={() => sendMessage(activeTab === 'advice')}
                                            disabled={!inputMessage.trim() || isLoading}
                                            className={`w-10 h-10 rounded-full items-center justify-center mb-1 ml-2 ${inputMessage.trim() && !isLoading
                                                ? (activeTab === 'advice' ? 'bg-emerald-600' : 'bg-blue-600')
                                                : 'bg-slate-700'
                                                }`}
                                        >
                                            <Ionicons name="arrow-up" size={20} color={inputMessage.trim() && !isLoading ? '#ffffff' : '#94a3b8'} />
                                        </TouchableOpacity>
                                    </View>
                                </View>
                            )}

                            {/* Tab Bar Container */}
                            <TabBar activeTab={activeTab} setActiveTab={setActiveTab} />
                        </KeyboardAvoidingView>
                    </SafeAreaView>
                </View>
            </Modal>
        </>
    );
}
