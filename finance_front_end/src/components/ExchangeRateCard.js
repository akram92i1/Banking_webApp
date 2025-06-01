import React from "react";

const exchangeRates = [
  {
    flag: "🇺🇸",
    currency: "USD",
    label: "1 US Dollar",
    sell: "1.0931",
    buy: "1.0822",
  },
  {
    flag: "🇸🇬",
    currency: "SGD",
    label: "1 Singapore Dollar",
    sell: "0.6901",
    buy: "0.6201",
  },
  {
    flag: "🇬🇧",
    currency: "GPD",
    label: "1 British Pound",
    sell: "1.1520",
    buy: "1.1412",
  },
  {
    flag: "🇦🇺",
    currency: "AUD",
    label: "1 Australian Dollar",
    sell: "0.6110",
    buy: "0.5110",
  },
  {
    flag: "🇪🇺",
    currency: "EUR",
    label: "1 Euro",
    sell: "1.1020",
    buy: "1.1010",
  },
];

const ExchangeRateCard = () => {
  return (
    <div className="bg-cyan-100 rounded-xl p-6 w-full shadow-md">
      <h2 className="text-2xl font-bold text-slate-800 mb-4">Exchange Rate</h2>
      <div className="space-y-4">
        {exchangeRates.map((rate, index) => (
          <div
            key={index}
            className="flex justify-between items-center border-b last:border-b-0 pb-2"
          >
            <div className="flex items-center gap-4">
              <div className="text-3xl">{rate.flag}</div>
              <div>
                <p className="text-lg font-semibold">{rate.currency}</p>
                <p className="text-sm text-slate-700">{rate.label}</p>
              </div>
            </div>
            <div className="text-right text-sm text-slate-800">
              <p>
                <span className="font-medium">SELL</span> {rate.sell}
              </p>
              <p>
                <span className="font-medium">BUY</span> {rate.buy}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExchangeRateCard;
