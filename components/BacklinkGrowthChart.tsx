import { UI_TEXT } from "../data/index";
import {
  ResponsiveContainer,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  LabelList,
} from "recharts";

interface ChartData {
  name: string;
  "Total Backlinks": number;
}

interface BacklinkGrowthChartProps {
  data: ChartData[];
}

const BacklinkGrowthChart = ({ data }: BacklinkGrowthChartProps) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md transition hover:shadow-lg mb-8">
      <h2 className="text-xl font-bold text-gray-800 mb-4">
        {UI_TEXT.backlinkGrowth.title}
      </h2>

      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <BarChart
            data={data}
            margin={{
              top: 20,
              right: 20,
              left: 30,
              bottom: 20,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />

            <XAxis dataKey="name" stroke="#6b7280" />

            <YAxis
              stroke="#6b7280"
              label={{
                value: "Total Backlinks",
                angle: -90,
                position: "insideLeft",
                offset: -20,
                style: { textAnchor: "middle", fill: "#6b7280" },
              }}
            />

            <Tooltip />

            <Legend verticalAlign="bottom" />

            <Bar
              dataKey="Total Backlinks"
              fill="#3b82f6"
              barSize={60}
              radius={[6, 6, 0, 0]}
            >
              <LabelList
                dataKey="Total Backlinks"
                position="top"
                style={{ fill: "#374151", fontWeight: 600 }}
              />
            </Bar>

          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default BacklinkGrowthChart;