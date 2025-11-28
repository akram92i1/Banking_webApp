import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const data = [
  { month: 'Jan', income: 5000, expenses: 3000, transfers: 1000 },
  { month: 'Feb', income: 5500, expenses: 3200, transfers: 1200 },
  { month: 'Mar', income: 6000, expenses: 3500, transfers: 1100 },
  { month: 'Apr', income: 5800, expenses: 3300, transfers: 1300 },
  { month: 'May', income: 6100, expenses: 3700, transfers: 1250 },
];

const StatsCard = () => {
  // Custom tooltip component with glass effect
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-card rounded-2xl p-4 border border-white/20">
          <p className="text-glass font-semibold mb-2">{`${label} 2024`}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm text-glass-muted">
              <span className="inline-block w-3 h-3 rounded-full mr-2" style={{ backgroundColor: entry.color }}></span>
              {`${entry.name}: $${entry.value?.toLocaleString()}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-card rounded-3xl p-6 relative overflow-hidden group animate-float animation-delay-1000">
      {/* Floating background elements */}
      <div className="absolute -top-6 -right-6 w-24 h-24 bg-gradient-to-br from-emerald-400/20 to-cyan-400/20 rounded-full blur-xl animate-pulse-soft"></div>
      <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-2xl animate-pulse-soft animation-delay-2000"></div>
      
      {/* Shimmer effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>

      <div className="relative z-10">
        {/* Header with enhanced styling */}
        <div className="flex items-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-400 via-cyan-500 to-blue-600 flex items-center justify-center shadow-xl animate-pulse-soft">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {/* Glow effect */}
            <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-400 via-cyan-500 to-blue-600 opacity-50 blur-lg"></div>
          </div>
          <div>
            <h2 className="text-2xl font-bold text-glass bg-gradient-to-r from-white via-emerald-100 to-cyan-100 bg-clip-text text-transparent">
              Monthly Overview
            </h2>
            <p className="text-glass-muted text-sm">Financial performance last 5 months</p>
          </div>
        </div>

        {/* Chart container with glass background */}
        <div className="glass-card rounded-2xl p-4" style={{ width: '100%', height: 420 }}>
          <ResponsiveContainer>
            <BarChart 
              data={data} 
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              barCategoryGap="20%"
            >
              <defs>
                {/* Gradient definitions for bars */}
                <linearGradient id="incomeGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10B981" stopOpacity={0.8}/>
                  <stop offset="100%" stopColor="#047857" stopOpacity={0.6}/>
                </linearGradient>
                <linearGradient id="expensesGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#EF4444" stopOpacity={0.8}/>
                  <stop offset="100%" stopColor="#B91C1C" stopOpacity={0.6}/>
                </linearGradient>
                <linearGradient id="transfersGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="100%" stopColor="#1D4ED8" stopOpacity={0.6}/>
                </linearGradient>
              </defs>
              
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke="rgba(255,255,255,0.1)"
                opacity={0.3}
              />
              <XAxis 
                dataKey="month" 
                stroke="rgba(255,255,255,0.7)"
                fontSize={12}
                fontWeight="500"
              />
              <YAxis 
                stroke="rgba(255,255,255,0.7)"
                fontSize={12}
                tickFormatter={(value) => `$${(value/1000).toFixed(0)}k`}
              />
              <Tooltip 
                content={<CustomTooltip />}
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
              />
              <Legend 
                wrapperStyle={{ 
                  color: 'rgba(255,255,255,0.8)', 
                  fontSize: '14px',
                  fontWeight: '500'
                }}
              />
              <Bar 
                dataKey="income" 
                fill="url(#incomeGradient)" 
                name="Income" 
                radius={[4, 4, 0, 0]}
              />
              <Bar 
                dataKey="expenses" 
                fill="url(#expensesGradient)" 
                name="Expenses" 
                radius={[4, 4, 0, 0]}
              />
              <Bar 
                dataKey="transfers" 
                fill="url(#transfersGradient)" 
                name="Transfers" 
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Summary stats with glass cards */}
        <div className="grid grid-cols-3 gap-4 mt-6">
          <div className="glass-card rounded-2xl p-4 text-center animate-float animation-delay-1000">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-green-500 mx-auto mb-2 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11l5-5m0 0l5 5m-5-5v12" />
              </svg>
            </div>
            <p className="text-glass-muted text-xs uppercase tracking-wider">Avg Income</p>
            <p className="text-glass font-bold text-lg">$5.88k</p>
          </div>
          
          <div className="glass-card rounded-2xl p-4 text-center animate-float animation-delay-2000">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-400 to-pink-500 mx-auto mb-2 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 13l-5 5m0 0l-5-5m5 5V6" />
              </svg>
            </div>
            <p className="text-glass-muted text-xs uppercase tracking-wider">Avg Expenses</p>
            <p className="text-glass font-bold text-lg">$3.34k</p>
          </div>
          
          <div className="glass-card rounded-2xl p-4 text-center animate-float animation-delay-3000">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-400 to-purple-500 mx-auto mb-2 flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>
            <p className="text-glass-muted text-xs uppercase tracking-wider">Avg Transfers</p>
            <p className="text-glass font-bold text-lg">$1.17k</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatsCard;
