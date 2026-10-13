import { ReferringDomainsData } from "./ReferringDomainsBarItem";

export interface MousePosition {
  x: number;
  y: number;
}

interface TooltipProps {
  item: ReferringDomainsData;
  position: MousePosition;
  tooltipOffset: { x: number; y: number };
}

const ReferringDomainsTooltip = ({
  item,
  position,
  tooltipOffset,
}: TooltipProps) => (
  <div
    className="fixed z-50 bg-gray-800 text-white px-3 py-2 rounded-lg shadow-lg pointer-events-none"
    style={{
      left: position.x + tooltipOffset.x,
      top: position.y + tooltipOffset.y,
    }}
  >
    <div className="text-sm font-semibold">{item.name}</div>
    <div className="text-xs">
      Domains: <span className="font-semibold">{item.value}</span>
    </div>
  </div>
);

export default ReferringDomainsTooltip;
