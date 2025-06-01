import React from 'react';

const transactions = [
  {
    id: 1,
    name: 'Spotify Subscription',
    date: 'May 10, 2025',
    amount: '-$12.99',
    type: 'debit',
  },
  {
    id: 2,
    name: 'Freelance Payment',
    date: 'May 8, 2025',
    amount: '+$500.00',
    type: 'credit',
  },
  {
    id: 3,
    name: 'Amazon Purchase',
    date: 'May 6, 2025',
    amount: '-$89.90',
    type: 'debit',
  },
];

const TransactionHistoryCard = () => {
  return (
    <div className="bg-gray-100 shadow-md rounded-lg p-6 mt-6">
      <h2 className="text-xl font-semibold mb-4">History</h2>
      <ul className="divide-y divide-gray-200">
        {transactions.map((tx) => (
          <li key={tx.id} className="py-3 flex justify-between items-center">
            <div>
              <p className="font-medium text-gray-800">{tx.name}</p>
              <p className="text-sm text-gray-500">{tx.date}</p>
            </div>
            <div
              className={`text-sm font-semibold ${
                tx.type === 'credit' ? 'text-green-600' : 'text-red-500'
              }`}
            >
              {tx.amount}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TransactionHistoryCard;
