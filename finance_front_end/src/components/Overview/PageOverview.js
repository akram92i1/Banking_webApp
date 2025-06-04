import BalanceCard from "../BalanceCard";
import TransactionHistoryCard from "../TransactionHistoryCard";
import QuickActionsCard from "../QuickActionsCard";
import StatsCard from "../StatsCard";
import ExchangeRateCard from "../ExchangeRateCard";

export default function PageOverview() {
    return (
        <div className="p-6 flex-grow overflow-auto">
            <h1 className='text-9xl md:text-2xl font-bold sm:text-4xl'>Overview</h1>
            <h2>Hello Akram, welcome back!</h2>
            <br />
            <BalanceCard />
            <div className="flex w-full gap-6 mt-6">
                <div className="w-1/2">
                    <TransactionHistoryCard />
                    <br />
                    <QuickActionsCard />
                </div>
                <div className="w-1/2">
                    <StatsCard />
                </div>
            </div>
            <div className="mt-6">
                <ExchangeRateCard />
            </div>
        </div>
    );
}