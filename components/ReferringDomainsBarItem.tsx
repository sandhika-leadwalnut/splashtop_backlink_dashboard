export interface ReferringDomainsData {
  name: string;
  value: number;
  color: string;
}

interface BarItemProps {
  item: ReferringDomainsData;
  barWidth: number;
  onMouseEnter: (item: ReferringDomainsData, event: MouseEvent) => void;
  onMouseMove: (event: MouseEvent) => void;
  onMouseLeave: () => void;
}

const ReferringDomainsBarItem = ({
  item,
  barWidth,
  onMouseEnter,
  onMouseMove,
  onMouseLeave,
}: BarItemProps) => (
  <div className="flex items-center">
    <div className="w-20 text-sm text-gray-700 font-medium text-right pr-4">
      {item.name}
    </div>
    <div className="relative flex-1">
      <div className="h-8 bg-gray-50 relative">
        <div
          className="h-full flex items-center justify-end pr-3 text-white text-sm font-semibold transition-all duration-700 ease-out cursor-pointer hover:opacity-80"
          style={{
            backgroundColor: item.color,
            width: `${barWidth}%`,
          }}
          onMouseEnter={(e) => onMouseEnter(item, e)}
          onMouseMove={onMouseMove}
          onMouseLeave={onMouseLeave}
        >
          {item.value}
        </div>
      </div>
    </div>
  </div>
);

export default ReferringDomainsBarItem;
