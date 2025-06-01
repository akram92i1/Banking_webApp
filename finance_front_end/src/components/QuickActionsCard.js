import React from "react";
import { CreditCard, ScanLine, Send, Download } from "lucide-react";

const actions = [
  { label: "Top up", icon: <CreditCard size={28} /> },
  { label: "Scan & Pay", icon: <ScanLine size={28} /> },
  { label: "Send", icon: <Send size={28} /> },
  { label: "Request", icon: <Download size={28} /> },
];

const QuickActionsCard = () => {
  return (
    <div className="bg-zinc-300 rounded-xl p-6 w-full shadow-md">
      <div className="flex justify-between items-center">
        {actions.map((action, index) => (
          <div
            key={index}
            className="flex flex-col items-center text-slate-800 space-y-2"
          >
            <div className="bg-cream rounded-xl p-3">
              {action.icon}
            </div>
            <span className="text-sm font-medium">{action.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default QuickActionsCard;
