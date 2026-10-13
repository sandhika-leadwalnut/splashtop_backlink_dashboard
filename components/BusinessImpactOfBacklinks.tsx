import {
  ResponsiveContainer,
  ComposedChart,
  BarChart,
  LineChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  Line,
  Cell,
} from "recharts";
import {
  keywordImpactRows,
  remoteAccessTrendData,
  remoteDesktopSoftwareTrendData,
  extendedMonths,
  BUSINESS_IMPACT_CONFIG,
  MONTH_LABELS,
  UI_TEXT,
  businessImpactCategories,
} from "../data/index";

const InsightBox = ({ text }: { text: string }) => (
 <div className="flex justify-center mt-2 mb-6">
    <div className="max-w-3xl w-full p-4 rounded-lg border border-gray-200 bg-gray-50">
      <div className="flex items-start gap-3">
        <i className="fa-solid fa-arrow-trend-up text-green-600 mt-1"></i>

        <ul className="text-gray-700 font-semibold list-disc ml-5">
          <li>{text}</li>
        </ul>
      </div>
    </div>
  </div>
);
const remoteAccessData = remoteAccessTrendData.map((pos, i) => ({
  month: extendedMonths[i],
  pos,
}));

const remoteDesktopSoftwareData = remoteDesktopSoftwareTrendData.map(
  (pos, i) => ({
    month: extendedMonths[i],
    pos,
  })
);

const formatChartData = (rows: any[]) =>
  rows.map((row) => ({
    keyword: row.keyword,
    jan25: row.baseline,
    oct25: row.dec25,
  }));
// const BusinessImpactOfBacklinks = () => {
//   return (
//     <div className="bg-white p-6 rounded-xl shadow-md mb-8">
//       <div className="mb-4">
//         <h2 className="text-xl font-bold text-gray-800">
//           {UI_TEXT.businessImpact.title}
//         </h2>
//         {/* <h3 className="text-lg font-semibold text-gray-700 mt-2">
//           {BUSINESS_IMPACT_CONFIG.chartTitle}
//         </h3> */}
//         <div className="mt-3 px-4 py-2 bg-gray-100 rounded-md inline-block">
//           <p className="text-sm font-semibold text-gray-700">Source: GSC</p>
//         </div>
//       </div>

//       <div className="mb-6">
//         <div style={{ width: "100%", height: 500 }}>
//           <ResponsiveContainer>
//             <ComposedChart
//               data={keywordImpactRows
//                 .map((row) => ({
//                   keyword: row.keyword,
//                   jan25: row.baseline,
//                   oct25: row.dec25,
//                 }))}
//               margin={{ top: 80, right: 30, left: 30, bottom: 100 }}
//               barCategoryGap="25%"
//             >
//               <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
//              <XAxis
//   dataKey="keyword"
//   interval={0}
//   height={110}
//   tick={(props) => {
//     const { x, y, payload } = props;

//     const words = payload.value.split(" ");
//     const lines: string[] = [];
//     let line = "";

//     words.forEach((word: string) => {
//       if ((line + word).length > 12) {
//         lines.push(line);
//         line = word + " ";
//       } else {
//         line += word + " ";
//       }
//     });

//     lines.push(line);

//     return (
//       <g transform={`translate(${x},${y})`}>
//         <text
//           x={0}
//           y={10}
//           textAnchor="middle"
//           fill="#374151"
//           fontSize={10}
//           fontWeight="bold"
//         >
//           {lines.map((l, i) => (
//             <tspan key={i} x={0} dy={i === 0 ? 0 : 12}>
//               {l}
//             </tspan>
//           ))}
//         </text>
//       </g>
//     );
//   }}
// />
//               <YAxis
//                 label={{
//                   value: "Position",
//                   angle: -90,
//                   position: "insideLeft",
//                   style: { fontWeight: "bold" },
//                 }}
//                 domain={[0, 80]}
//                 tick={{ fontWeight: "bold" }}
//               />
//               <Tooltip />
//               <Legend
//                 verticalAlign="bottom"
//                 align="center"
//                 wrapperStyle={{ paddingTop: "10px" }}
//                 iconType="rect"
//               />
//               <text
//                 x="50%"
//                 y="15"
//                 textAnchor="middle"
//                 style={{
//                   fontSize: "16px",
//                   fontWeight: "bold",
//                   fill: "#9c51b6",
//                 }}
//               >
//                 {BUSINESS_IMPACT_CONFIG.chartSubtitle}
//               </text>
//               <Bar
//                 dataKey="jan25"
//                 fill="#3b82f6"
//                 name={MONTH_LABELS.baseline}
//                 barSize={30}
//                 radius={[4, 4, 0, 0]}
//                 label={{
//                   position: "top",
//                   style: {
//                     fontSize: "10px",
//                     fontWeight: "bold",
//                     fill: "#1f2937",
//                   },
//                 }}
//               />
//               <Bar
//                 dataKey="oct25"
//                 fill="#059669"
//                 name={MONTH_LABELS.current}
//                 barSize={30}
//                 radius={[4, 4, 0, 0]}
//                 label={{
//                   position: "top",
//                   style: {
//                     fontSize: "10px",
//                     fontWeight: "bold",
//                     fill: "#1f2937",
//                   },
//                 }}
//               />
//             </ComposedChart>
//           </ResponsiveContainer>
//         </div>
//       </div>

//       <div className="mt-4">
//         <div className="p-4 rounded-lg border border-gray-200 bg-gray-50">
//           <div className="flex items-start gap-3">
//             <i className="fa-solid fa-arrow-trend-up text-green-600"></i>
//             <p className="text-gray-700 font-bold">
//               {BUSINESS_IMPACT_CONFIG.insightText}
//             </p>
//           </div>
//         </div>
//       </div>

//       {/* RANKING PERFORMANCE TREND — COMMENTED OUT
//       <div className="mt-8">
//         <h3 className="text-lg font-semibold text-gray-800 mb-2">
//           {BUSINESS_IMPACT_CONFIG.trendChartTitle}
//         </h3>
//         <div className="mb-4 px-4 py-2 bg-gray-100 rounded-md inline-block">
//           <p className="text-sm font-semibold text-gray-700">Source: Semrush</p>
//         </div>
//         <div className="mb-4 p-4 rounded-lg border border-gray-200 bg-gray-50">
//           <div className="flex items-start gap-3">
//             <i className="fa-solid fa-lightbulb text-yellow-600 mt-1"></i>
//             <div className="text-gray-700">
//               <p>
//                 <strong>Remote Desktop Software: 10 backlinks</strong> added in June boosted its ranking to page 1.
//               </p>
//               <p className="mt-2">
//                 <strong>Remote Access: 30 backlinks</strong> were added in Jan, helping maintain a stable position on page 1.
//               </p>
//               <p className="mt-2">
//                  <strong>As on Feb'26 both the keywords are off page 1 due to inconsistent backlink acquisition</strong>
//               </p>
//             </div>
//           </div>
//         </div>
//         <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//           <div className="bg-white rounded-lg border p-4">
//             <h4 className="text-base font-semibold text-blue-700 mb-2">
//               Remote Access
//             </h4>
//             <div style={{ width: "100%", height: 300 }}>
//               <ResponsiveContainer>
//                 <LineChart
//                   data={remoteAccessData}
//                   margin={{ top: 5, right: 10, left: 45, bottom: 10 }}
//                 >
//                   <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
//                   <XAxis
//                     dataKey="month"
//                     tick={{ fontSize: 11 }}
//                     angle={-25}
//                     textAnchor="end"
//                     height={45}
//                   />
//                   <YAxis
//                     width={56}
//                     label={{
//                       value: "Keyword Position",
//                       angle: -90,
//                       position: "insideLeft",
//                       offset: 6,
//                       style: { fill: "#6b7280", fontSize: 11 },
//                     }}
//                     domain={[0, 40]}
//                     tick={{ fontSize: 11 }}
//                   />
//                   <Tooltip />
//                   <Line
//                     type="monotone"
//                     dataKey="pos"
//                     stroke="#3b82f6"
//                     strokeWidth={3}
//                     activeDot={{ r: 6 }}
//                     dot={{ r: 3 }}
//                   />
//                 </LineChart>
//               </ResponsiveContainer>
//             </div>
//           </div>
//           <div className="bg-white rounded-lg border p-4">
//             <h4 className="text-base font-semibold text-blue-700 mb-2">
//               Remote Desktop Software
//             </h4>
//             <div style={{ width: "100%", height: 300 }}>
//               <ResponsiveContainer>
//                 <LineChart
//                   data={remoteDesktopSoftwareData}
//                   margin={{ top: 5, right: 10, left: 45, bottom: 10 }}
//                 >
//                   <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
//                   <XAxis
//                     dataKey="month"
//                     tick={{ fontSize: 11 }}
//                     angle={-25}
//                     textAnchor="end"
//                     height={45}
//                   />
//                   <YAxis
//                     width={56}
//                     label={{
//                       value: "Keyword Position",
//                       angle: -90,
//                       position: "insideLeft",
//                       offset: 6,
//                       style: { fill: "#6b7280", fontSize: 11 },
//                     }}
//                     domain={[0, 40]}
//                     tick={{ fontSize: 11 }}
//                   />
//                   <Tooltip />
//                   <Line
//                     type="monotone"
//                     dataKey="pos"
//                     stroke="#3b82f6"
//                     strokeWidth={3}
//                     activeDot={{ r: 6 }}
//                     dot={{ r: 3 }}
//                   />
//                 </LineChart>
//               </ResponsiveContainer>
//             </div>
//           </div>
//         </div>
//       </div>
//       */}
//     </div>
//   );
// };

const KeywordChart = ({ title, rows }: any) => (
  <div className="mb-2">
    <h3 className="text-center font-semibold text-purple-600 mb-4">
      {title}
    </h3>

    <div style={{ width: "100%", height: 400 }}>
      <ResponsiveContainer>
        <ComposedChart
          data={formatChartData(rows)}
          margin={{ top: 60, right: 30, left: 30, bottom: 40 }}
          barCategoryGap="25%"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
<XAxis
  dataKey="keyword"
  interval={0}
  height={110}
  tick={(props) => {
    const { x, y, payload } = props;

    const words = payload.value.split(" ");
    const lines: string[] = [];
    let line = "";

    words.forEach((word: string) => {
      if ((line + word).length > 12) {
        lines.push(line);
        line = word + " ";
      } else {
        line += word + " ";
      }
    });

    lines.push(line);

    return (
      <g transform={`translate(${x},${y})`}>
        <text
          x={0}
          y={10}
          textAnchor="middle"
          fill="#374151"
          fontSize={10}
          fontWeight="bold"
        >
          {lines.map((l, i) => (
            <tspan key={i} x={0} dy={i === 0 ? 0 : 12}>
              {l}
            </tspan>
          ))}
        </text>
      </g>
    );
  }}
/>

          <YAxis
            label={{
              value: "Position",
              angle: -90,
              position: "insideLeft",
              style: { fontWeight: "bold" },
            }}
            domain={[0, 120]}
          />

          <Tooltip />

          <Legend
            verticalAlign="bottom"
            align="center"
            iconType="rect"
          />

          <Bar
            dataKey="jan25"
            fill="#3b82f6"
            name={MONTH_LABELS.baseline}
            barSize={30}
            radius={[4, 4, 0, 0]}
            label={{
              position: "top",
              style: {
                fontSize: "10px",
                fontWeight: "bold",
                fill: "#1f2937",
              },
            }}
          />

          <Bar
            dataKey="oct25"
            fill="#059669"
            name={MONTH_LABELS.current}
            barSize={30}
            radius={[4, 4, 0, 0]}
            label={{
              position: "top",
              style: {
                fontSize: "10px",
                fontWeight: "bold",
                fill: "#1f2937",
              },
            }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  </div>
);

const BusinessImpactOfBacklinks = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-md mb-8">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          {UI_TEXT.businessImpact.title}
        </h2>

        <div className="mt-3 px-4 py-2 bg-gray-100 rounded-md inline-block">
          <p className="text-sm font-semibold text-gray-700">
            Source: GSC
          </p>
        </div>
      </div>

      {/* One chart + insight per category (from data/report.json) */}
      {businessImpactCategories.map((category, index) => (
        <div key={index}>
          <KeywordChart title={category.title} rows={category.rows} />
          <InsightBox text={category.insight} />
        </div>
      ))}
      {/* Insight Box */}
      {/* <div className="mt-4">
        <div className="p-4 rounded-lg border border-gray-200 bg-gray-50">
          <div className="flex items-start gap-3">
            <i className="fa-solid fa-arrow-trend-up text-green-600"></i>

            <ul className="text-gray-700 font-bold list-disc ml-6 space-y-2">
  {BUSINESS_IMPACT_CONFIG.insightText.map((text: string, index: number) => (
    <li key={index}>{text}</li>
  ))}
</ul>
          </div>
        </div> */}
      </div>
    // </div>
  );
};




export default BusinessImpactOfBacklinks;
