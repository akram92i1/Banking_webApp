import React from 'react';

const CardFooterInfo = () => {
  return (
    <div className="bg-green-50 p-6 rounded-lg shadow-md flex justify-between items-end mt-4">
      <div>
        <p className="text-sm text-gray-600">Valid Date</p>
        <p className="text-sm font-semibold">12/2028</p>
      </div>

      <div className="text-center">
        <p className="text-sm text-gray-600">Your Balance</p>
        <p className="text-2xl font-bold">$254,800</p>
        <p className="text-sm tracking-widest">**** **** **** 2560</p>
      </div>

      <div className="text-right">
        <p className="text-sm text-gray-600">Card Holder</p>
        <p className="text-sm font-semibold">Thomas</p>
      </div>
    </div>
  );
};

export default CardFooterInfo;
