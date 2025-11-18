import React from "react";

const transactions = [
  {
    date: "July 5, 2023",
    time: "10:00 PM",
    description: "Shopping",
    type: "C2C Transfer",
    amount: "- $100.00",
    balance: "$5,500.00",
    status: "Pending",
  },
  {
    date: "July 2, 2023",
    time: "10:42 AM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "+ $250",
    balance: "$5,600.00",
    status: "Success",
  },
  {
    date: "June 28, 2023",
    time: "8:20 PM",
    description: "Billing",
    type: "Goverment",
    amount: "+$50",
    balance: "$5,350.00",
    status: "Success",
  },
  {
    date: "June 24, 2023",
    time: "10:48 PM",
    description: "Shopee",
    type: "QR Code",
    amount: "-$380",
    balance: "$5,300.00",
    status: "Cancelled",
  },
  {
    date: "June 12, 2023",
    time: "12:30 AM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "+$250",
    balance: "$4,920.00",
    status: "Success",
  },
  {
    date: "May 31, 2023",
    time: "2:40 PM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "+$50",
    balance: "$4,920.00",
    status: "Success",
  },
  {
    date: "May 22, 2023",
    time: "8:50 AM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "+$50",
    balance: "$4,920.00",
    status: "Success",
  },
  {
    date: "May 20, 2023",
    time: "6:45 PM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "-$500",
    balance: "$4,920.00",
    status: "Pending",
  },
  {
    date: "April 28, 2023",
    time: "11:20 AM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "+$856",
    balance: "$4,920.00",
    status: "Success",
  },
  {
    date: "April 16, 2023",
    time: "11:00 PM",
    description: "Food Delivery",
    type: "Mobile Reload",
    amount: "+$50",
    balance: "$4,920.00",
    status: "Pending",
  },
];

const getStatusClass = (status) => {
  switch (status) {
    case "Success":
      return "text-green-600 bg-green-100";
    case "Pending":
      return "text-yellow-700 bg-yellow-100";
    case "Cancelled":
      return "text-red-600 bg-red-100";
    default:
      return "";
  }
};

const MyWalletTable = () => {
  return (
    <div className="bg-white rounded-xl shadow p-6 overflow-x-auto">
      <h2 className="text-xl font-semibold text-slate-800 mb-4">My Wallet</h2>
      <table className="min-w-full text-sm text-left text-slate-700">
        <thead className="bg-slate-100 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-2">Date</th>
            <th className="px-4 py-2">Time</th>
            <th className="px-4 py-2">Description</th>
            <th className="px-4 py-2">Payment Type</th>
            <th className="px-4 py-2">Amount</th>
            <th className="px-4 py-2">Balance</th>
            <th className="px-4 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, index) => (
            <tr key={index} className="border-b hover:bg-slate-50">
              <td className="px-4 py-2">{tx.date}</td>
              <td className="px-4 py-2">{tx.time}</td>
              <td className="px-4 py-2">{tx.description}</td>
              <td className="px-4 py-2">{tx.type}</td>
              <td className="px-4 py-2">{tx.amount}</td>
              <td className="px-4 py-2">{tx.balance}</td>
              <td className="px-4 py-2">
                <span className={`px-2 py-1 rounded-md text-xs font-medium ${getStatusClass(tx.status)}`}>
                  {tx.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination (static example) */}
      <div className="flex justify-between items-center mt-4 text-sm text-slate-600">
        <span>Prev</span>
        <div className="space-x-2">
          <button className="px-3 py-1 rounded bg-slate-200">1</button>
          <button className="px-3 py-1 rounded bg-slate-100">2</button>
          <button className="px-3 py-1 rounded bg-slate-100">3</button>
          <button className="px-3 py-1 rounded bg-slate-100">4</button>
        </div>
        <span>Next</span>
      </div>
    </div>
  );
};

export default MyWalletTable;
