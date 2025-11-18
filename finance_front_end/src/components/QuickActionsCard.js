import React from "react";
import { CreditCard, ScanLine, Send, Download } from "lucide-react";

const QuickActionsCard = ({ onTransferClick }) => {
  const actions = [
    { 
      label: "Top up", 
      icon: <CreditCard size={28} />,
      onClick: () => alert('Top up feature coming soon!')
    },
    { 
      label: "Scan & Pay", 
      icon: <ScanLine size={28} />,
      onClick: () => alert('Scan & Pay feature coming soon!')
    },
    { 
      label: "Send", 
      icon: <Send size={28} />,
      onClick: onTransferClick || (() => alert('Transfer feature not available'))
    },
    { 
      label: "Request", 
      icon: <Download size={28} />,
      onClick: () => alert('Request money feature coming soon!')
    },
  ];

  return (
    <div className="bg-zinc-300 rounded-xl p-6 w-full shadow-md">
      <h3 className="text-lg font-semibold text-slate-800 mb-4">Quick Actions</h3>
      <div className="flex justify-between items-center">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className="flex flex-col items-center text-slate-800 space-y-2 hover:scale-105 transition-transform duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 rounded-lg p-2"
          >
            <div className="bg-white rounded-xl p-3 shadow-sm hover:shadow-md transition-shadow duration-200">
              {action.icon}
            </div>
            <span className="text-sm font-medium">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActionsCard;
