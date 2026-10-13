import React from "react";

interface ChartHeaderProps {
  title: string;
  subtitle: string;
}

const ReferringDomainsChartHeader: React.FC<ChartHeaderProps> = ({
  title,
  subtitle,
}) => (
  <div className="mb-6">
    <h2 className="text-xl font-bold text-gray-800">{title}</h2>
    <h3 className="text-lg font-semibold text-gray-700 mt-2">{subtitle}</h3>
  </div>
);

export default ReferringDomainsChartHeader;
