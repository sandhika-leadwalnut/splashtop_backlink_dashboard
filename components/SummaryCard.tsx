import { ReactNode } from "react";

interface SummaryCardProps {
  icon: ReactNode;
  title: string;
  value: string;
  description: string;
}

const SummaryCard = ({ icon, title, value, description }: SummaryCardProps) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md flex items-center space-x-4 transition hover:shadow-lg">
      <div className="flex-shrink-0">{icon}</div>
      <div>
        <p className="text-black text-sm font-bold">{title}</p>
        <p className="text-2xl font-bold text-black">{value}</p>
        <p className="text-gray-400 text-xs">{description}</p>
      </div>
    </div>
  );
};

export default SummaryCard;
