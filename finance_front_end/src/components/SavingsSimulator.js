import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Target, TrendingUp, ShoppingBag, Gift, ArrowRight } from 'lucide-react';

const SavingsSimulator = ({ userId = 'user001' }) => {
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [simulating, setSimulating] = useState(false);
    const [simulatorMessage, setSimulatorMessage] = useState('');

    // Fake inputs for simulation
    const [amount, setAmount] = useState('65.00');
    const [merchant, setMerchant] = useState('Maxi');

    const fetchDashboard = async () => {
        try {
            const res = await axios.get(`http://localhost:5000/api/simulator/dashboard/${userId}`);
            setDashboard(res.data);
        } catch (error) {
            console.error('Failed to fetch simulator dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboard();
    }, [userId]);

    const handleSimulate = async () => {
        if (!amount || isNaN(amount)) return;

        setSimulating(true);
        setSimulatorMessage('');

        try {
            const res = await axios.post('http://localhost:5000/api/simulator/log-grocery', {
                user_id: userId,
                amount: parseFloat(amount),
                merchant: merchant
            });

            setSimulatorMessage(res.data.message);
            await fetchDashboard(); // refresh data
        } catch (error) {
            setSimulatorMessage('Failed to simulate transaction.');
        } finally {
            setSimulating(false);

            // Clear message after 4s
            setTimeout(() => setSimulatorMessage(''), 4000);
        }
    };

    if (loading && !dashboard) {
        return <div className="p-4 text-center text-slate-400">Loading Simulator...</div>;
    }

    const isProfitable = dashboard?.investment_portfolio?.market_change_pct >= 0;

    return (
        <div className="bg-slate-900 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
            <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-6 text-white relative">
                <h2 className="text-xl font-bold mb-1 flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Savings & Investment Simulator
                </h2>
                <p className="text-emerald-100 text-sm">Gamified Auto-Investing from Grocery Savings</p>

                {/* Decorative element */}
                <div className="absolute right-[-20px] top-[-20px] opacity-20 transform rotate-12">
                    <TrendingUp size={120} />
                </div>
            </div>

            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Left Col: Simulation Controls */}
                <div className="space-y-4">
                    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
                        <h3 className="font-semibold text-white text-sm mb-3 flex items-center gap-2">
                            <ShoppingBag className="w-4 h-4 text-blue-400" />
                            Simulate Grocery Shopping
                        </h3>

                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-slate-400 block mb-1">Store Name</label>
                                <input
                                    type="text"
                                    value={merchant}
                                    onChange={e => setMerchant(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm text-white focus:border-emerald-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-slate-400 block mb-1">Total Spent ($)</label>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={e => setAmount(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-600 rounded p-2 text-sm text-white focus:border-emerald-500 outline-none"
                                />
                            </div>
                            <button
                                onClick={handleSimulate}
                                disabled={simulating}
                                className="w-full py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-medium rounded-lg transition-colors flex justify-center items-center gap-2 disabled:opacity-50"
                            >
                                {simulating ? 'Processing...' : 'Run Simulation'}
                                {!simulating && <ArrowRight className="w-4 h-4" />}
                            </button>

                            {simulatorMessage && (
                                <div className="text-sm text-center py-2 px-3 bg-emerald-900/40 text-emerald-400 rounded-lg border border-emerald-800 animate-fade-in-up">
                                    {simulatorMessage}
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 flex justify-between items-center">
                        <div>
                            <p className="text-xs text-slate-400">Mock Checking Account</p>
                            <p className="text-lg font-bold text-white">${dashboard?.bank_balance?.toFixed(2)}</p>
                        </div>
                    </div>
                </div>

                {/* Right Col: Virtual Portfolio */}
                <div className="bg-slate-800 rounded-xl p-5 border border-slate-700 relative overflow-hidden flex flex-col justify-center">

                    {/* Subtle background glow */}
                    <div className={`absolute top-0 right-0 w-32 h-32 rounded-full filter blur-[50px] opacity-20 ${isProfitable ? 'bg-emerald-500' : 'bg-red-500'}`}></div>

                    <h3 className="font-semibold text-white text-sm mb-6 flex items-center gap-2 z-10">
                        <Gift className="w-4 h-4 text-purple-400" />
                        Virtual Investment Portfolio
                    </h3>

                    <div className="text-center z-10 mb-8">
                        <p className="text-xs text-slate-400 mb-1 tracking-widest uppercase">Total Value</p>
                        <h1 className="text-4xl font-black text-white mb-2">
                            ${dashboard?.investment_portfolio?.live_value?.toFixed(2)}
                        </h1>
                        <div className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${isProfitable ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                            <TrendingUp className={`w-3 h-3 ${!isProfitable && 'transform rotate-180'}`} />
                            {isProfitable ? '+' : ''}{dashboard?.investment_portfolio?.market_change_pct}% Today
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4 border-t border-slate-700 pt-4 z-10">
                        <div>
                            <p className="text-xs text-slate-500">Asset Tracking</p>
                            <p className="font-medium text-slate-200">{dashboard?.investment_portfolio?.symbol} (S&P 500 ETF)</p>
                        </div>
                        <div>
                            <p className="text-xs text-slate-500">Total Saved & Contributed</p>
                            <p className="font-medium text-slate-200">${dashboard?.investment_portfolio?.total_contributed?.toFixed(2)}</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default SavingsSimulator;
