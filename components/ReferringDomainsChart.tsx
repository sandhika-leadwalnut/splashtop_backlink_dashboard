import React, { useState, useCallback, useMemo } from "react";
import { REFERRING_DOMAINS_CONFIG, UI_TEXT } from "../data/index";
import ReferringDomainsChartHeader from "./ReferringDomainsChartHeader";
import ReferringDomainsBarItem, {
  ReferringDomainsData,
} from "./ReferringDomainsBarItem";
import ReferringDomainsScaleAxis from "./ReferringDomainsScaleAxis";
import ReferringDomainsLegend from "./ReferringDomainsLegend";
import ReferringDomainsTooltip, {
  MousePosition,
} from "./ReferringDomainsTooltip";
import {
  CHART_CONFIG,
  calculateScaleMax,
  generateScalePoints,
  calculateBarWidth,
} from "./ReferringDomainsChartUtils";

interface ReferringDomainsChartProps {
  data: ReferringDomainsData[];
}

const ReferringDomainsChart: React.FC<ReferringDomainsChartProps> = ({
  data,
}) => {
  const [hoveredItem, setHoveredItem] = useState<ReferringDomainsData | null>(
    null
  );
  const [mousePosition, setMousePosition] = useState<MousePosition>({
    x: 0,
    y: 0,
  });

  const scaleMax = useMemo(() => {
    const maxValue = Math.max(...data.map((d) => d.value));
    return calculateScaleMax(maxValue);
  }, [data]);

  const scalePoints = useMemo(() => generateScalePoints(scaleMax), [scaleMax]);

  const handleMouseEnter = useCallback(
    (item: ReferringDomainsData, event: React.MouseEvent) => {
      setHoveredItem(item);
      setMousePosition({ x: event.clientX, y: event.clientY });
    },
    []
  );

  const handleMouseMove = useCallback((event: React.MouseEvent) => {
    setMousePosition({ x: event.clientX, y: event.clientY });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setHoveredItem(null);
  }, []);

  return (
    <div className="bg-white p-6 rounded-xl shadow-md mb-8">
      <ReferringDomainsChartHeader
        title={UI_TEXT.referringDomains.title}
        subtitle={UI_TEXT.referringDomains.subtitle}
      />
      <div className="mb-4 px-4 py-2 bg-gray-100 rounded-md inline-block">
        <p className="text-sm font-semibold text-gray-700">Source: Ahrefs</p>
      </div>

      <div className="relative">
        <div className="space-y-6 mb-6">
          {data.map((item, index) => {
            const barWidth = calculateBarWidth(item.value, scaleMax);
            return (
              <ReferringDomainsBarItem
                item={item}
                barWidth={barWidth}
                onMouseEnter={handleMouseEnter}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
              />
            );
          })}
        </div>
        <ReferringDomainsScaleAxis points={scalePoints} />
      </div>

      <ReferringDomainsLegend items={data} />

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm text-black font-bold text-center">
          {REFERRING_DOMAINS_CONFIG.qualityStatement}
        </p>
      </div>

      {hoveredItem && (
        <ReferringDomainsTooltip
          item={hoveredItem}
          position={mousePosition}
          tooltipOffset={CHART_CONFIG.tooltipOffset}
        />
      )}
    </div>
  );
};

export default ReferringDomainsChart;
