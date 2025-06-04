// components/BalanceCard.js

export default function BalanceCard() {
    return (
      <div className="bg-green-50  rounded-xl p-6 relative overflow-hidden shadow-md">
        {/* Decorative Circle */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-red-500 rounded-full mix-blend-multiply opacity-70 -mr-12 -mt-12"></div>
        <div className="absolute top-0 right-0 w-24 h-24 bg-yellow-400 rounded-full mix-blend-multiply opacity-80 -mr-6 -mt-6"></div>
  
        {/* Content */}
        <div className="relative z-10">
          <p className="text-sm font-medium text-gray-600">Your Balance</p>
          <h2 className="text-4xl font-extrabold text-gray-900">$254,800</h2>
  
          <div className="mt-2 text-gray-800 tracking-widest font-semibold">
            **** **** **** 2560
          </div>
  
          <div className="mt-4 flex justify-between items-center text-sm">
            <div>
              <p className="text-gray-500">Valid Date</p>
              <p className="font-medium text-gray-800">12/2028</p>
            </div>
            <div className="text-right">
              <p className="text-gray-500">Card Holder</p>
              <p className="font-medium text-gray-800">Thomas</p>
            </div>
          </div>
        </div>
      </div>
    );
  }
  