import { LineChart, Line, ResponsiveContainer, YAxis } from "recharts";

interface SparklineProps {
  data: (number | null)[];
  isKeyword?: boolean;
}

interface ChartDataPoint {
  name: number;
  value: number;
}

// Constants
const SPARKLINE_CONFIG = {
  height: 32,
  margin: { top: 5, right: 5, left: 5, bottom: 5 },
  strokeWidth: 2,
  minDataPoints: 2,
} as const;

const COLORS = {
  keyword: "#f59e0b",
  default: "#3b82f6",
} as const;

// Utility functions
const transformData = (data: (number | null)[]): ChartDataPoint[] => {
  return data
    .map((value, index) => ({ name: index, value }))
    .filter((d): d is ChartDataPoint => d.value !== null);
};

const calculateDomain = (data: ChartDataPoint[]): [number, number] => {
  const values = data.map((d) => d.value);
  return [Math.min(...values), Math.max(...values)];
};

const Sparkline = ({ data, isKeyword = false }: SparklineProps) => {
  const chartData = transformData(data);

  if (chartData.length < SPARKLINE_CONFIG.minDataPoints) {
    return (
      <div className="h-8 w-full flex items-center justify-center text-gray-400 text-xs">
        N/A
      </div>
    );
  }

  const domain = calculateDomain(chartData);
  const color = isKeyword ? COLORS.keyword : COLORS.default;

  return (
    <ResponsiveContainer width="100%" height={SPARKLINE_CONFIG.height}>
      <LineChart data={chartData} margin={SPARKLINE_CONFIG.margin}>
        <YAxis hide domain={domain} />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={SPARKLINE_CONFIG.strokeWidth}
          dot={false}
          connectNulls={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default Sparkline;
