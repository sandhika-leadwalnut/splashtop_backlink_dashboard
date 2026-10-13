import { ReferringDomainsData } from "./ReferringDomainsBarItem";

interface LegendProps {
  items: ReferringDomainsData[];
}

const ReferringDomainsLegend = ({ items }: LegendProps) => (
  <div className="flex justify-center gap-6 mt-6">
    {items.map((item, index) => (
      <div key={index} className="flex items-center gap-2">
        <div className="w-3 h-3" style={{ backgroundColor: item.color }} />
        <span className="text-sm text-gray-600">{item.name}</span>
      </div>
    ))}
  </div>
);

export default ReferringDomainsLegend;
