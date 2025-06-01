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
  return (
    <div className="bg-blue-100 shadow-md rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Monthly Overview</h2>
      <div style={{ width: '100%', height: 400 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="income" fill="#10B981" name="Income" />
            <Bar dataKey="expenses" fill="#EF4444" name="Expenses" />
            <Bar dataKey="transfers" fill="#3B82F6" name="Transfers" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default StatsCard;
