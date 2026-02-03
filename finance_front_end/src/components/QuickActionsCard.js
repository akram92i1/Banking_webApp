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
    <div className="glass-card rounded-3xl p-6 w-full shadow-md">
      <h3 className="text-lg font-semibold text-glass mb-4">Quick Actions</h3>
      <div className="flex justify-between items-center">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className="flex flex-col items-center text-glass-muted space-y-2 hover:scale-105 transition-transform duration-200 focus:outline-none rounded-2xl p-2 group"
          >
            <div className="bg-slate-800 rounded-2xl p-4 shadow-sm group-hover:bg-blue-600 transition-colors duration-200 border border-white/5">
              <div className="text-blue-400 group-hover:text-white transition-colors">
                {action.icon}
              </div>
            </div>
            <span className="text-sm font-medium">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default QuickActionsCard;
