import { PagePerformanceData, KeywordRankInfo } from "../data/types";
import { ReactNode } from "react";
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Line,
  LabelList,
} from "recharts";
import {
  keywordRankingPerformance,
  MONTH_INDICES,
  REPORT_CONFIG,
  MONTH_LABELS,
  UI_TEXT,
} from "../data/index";

interface KeywordPerformanceProps {
  data: PagePerformanceData[];
}

const KeywordPerformance = ({ data }: KeywordPerformanceProps) => {
  const janIndex = MONTH_INDICES.baseline;
  const sepIndex = MONTH_INDICES.current;

  const processKeywordData = (monthIndex: number) => {
    const keywords: KeywordRankInfo[] = [];
    data.forEach((page) => {
      page.metrics.forEach((metric) => {
        if (metric.isKeyword) {
          const rank = metric.monthlyData[monthIndex];
          if (rank !== null && rank > 0) {
            keywords.push({ keyword: metric.name, url: page.url, rank });
          }
        }
      });
    });
    return keywords;
  };

  const janKeywords = keywordRankingPerformance.firstPage.jan25Data;
  const octKeywords = keywordRankingPerformance.firstPage.oct25Data;
const top3Oct: KeywordRankInfo[] =
  keywordRankingPerformance.topThree.data
    .filter((k) => k.oct25Rank <= 5)
    .map((k) => ({
      keyword: k.keyword,
      url: k.url,
      rank: k.oct25Rank,
    }));
 /*const top3Oct = octKeywords.filter((k) => k.rank <= 3);*/
  const firstPageOct = octKeywords.filter((k) => k.rank <= 10);

  const top3JanCount = janKeywords.filter((k) => k.rank <= 3).length;
  const firstPageJanCount = janKeywords.filter((k) => k.rank <= 10).length;

  const firstPageKeywords = {
    initial: keywordRankingPerformance.firstPage.jan25,
    current: keywordRankingPerformance.firstPage.oct25,
  };

  const top3Data = [
    {
      name: MONTH_LABELS.baseline,
      value: keywordRankingPerformance.topThree.jan25,
    },
    {
      name: MONTH_LABELS.current,
      value: keywordRankingPerformance.topThree.oct25,
    },
  ];

  const firstPageData = [
    {
      name: MONTH_LABELS.baseline,
      value: keywordRankingPerformance.firstPage.jan25,
    },
    {
      name: MONTH_LABELS.current,
      value: keywordRankingPerformance.firstPage.oct25,
    },
  ];

  const top3Improvements = keywordRankingPerformance.topThree.data;

  const KeywordTableCard = ({
    title,
    keywords,
  }: {
    title: string;
    keywords: KeywordRankInfo[];
  }) => {
    const keywordsWithChange = keywords
      .map((keyword) => {
        const janKeyword = janKeywords.find(
          (jk) => jk.keyword === keyword.keyword && jk.url === keyword.url
        );
        const positionChange = janKeyword
          ? janKeyword.rank - keyword.rank
          : null;

        return {
          ...keyword,
          positionChange,
          janRank: janKeyword?.rank || null,
        };
      })
      .sort((a, b) => a.rank - b.rank);

    return (
      <div className="bg-white p-6 rounded-xl shadow-md h-full">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
        {keywordsWithChange.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b-2 border-gray-300">
                <tr>
                  <th className="p-3 text-left text-xs font-bold text-gray-600 uppercase">
                    Keyword/Page
                  </th>
                  <th className="p-3 text-center text-xs font-bold text-gray-600 uppercase">
                    Position Change
                  </th>
                  <th className="p-3 text-center text-xs font-bold text-gray-600 uppercase">
             {REPORT_CONFIG.currentMonthName} Rank
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {keywordsWithChange.map((item, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="p-3">
                      <div>
                        <p className="font-semibold text-gray-700">
                          {item.keyword}
                        </p>
                        <a
                          href={
                            item.url.startsWith("http")
                              ? item.url
                              : `https://${item.url}`
                          }
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-500 hover:underline truncate block"
                        >
                          {item.url.replace("https://", "").replace("www.", "")}
                        </a>
                      </div>
                    </td>
                    <td className="p-3 text-center">
                      {item.positionChange !== null ? (
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                            item.positionChange > 0
                              ? "bg-green-100 text-green-800"
                              : item.positionChange < 0
                              ? "bg-red-100 text-red-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {item.positionChange > 0 ? "+" : ""}
                          {item.positionChange}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-xs">New</span>
                      )}
                    </td>
                    <td className="p-3 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 bg-blue-100 text-blue-700 font-bold rounded-full text-sm">
                        #{item.rank}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500">
            {UI_TEXT.keywordPerformance.noKeywords}
          </p>
        )}
      </div>
    );
  };

  const StatCard = ({
    icon,
    title,
    value,
  }: {
    icon: ReactNode;
    title: string;
    value: string | number;
  }) => (
    <div className="bg-white p-6 rounded-xl shadow-md flex items-center space-x-4">
      {icon}
      <div>
        <p className="text-gray-500">{title}</p>
        <p className="text-4xl font-bold text-gray-800">{value}</p>
      </div>
    </div>
  );

  const TrendChart = ({ title, data }: { title: string; data: any[] }) => {
    const initialValue = (data?.[0]?.value ?? 0) as number;
    const currentValue = (data?.[1]?.value ?? 0) as number;
    const percentChange =
      initialValue === 0
        ? currentValue === 0
          ? 0
          : 100
        : ((currentValue - initialValue) / initialValue) * 100;
    const isPositive = percentChange >= 0;
    const formatted = `${isPositive ? "+" : ""}${Math.round(percentChange)}`;

    return (
      <div className="bg-white p-6 rounded-xl shadow-md h-full">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
        <div style={{ width: "100%", height: 200 }}>
          <ResponsiveContainer>
            <ComposedChart
              data={data}
              margin={{ top: 20, right: 10, left: 60, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
              <YAxis
                allowDecimals={false}
                domain={[0, "dataMax + 2"]}
                 ticks={[0, 2, 4, 8, 12]}
                stroke="#6b7280"
                fontSize={12}
                width={50}
              />
              <Tooltip
                cursor={{ fill: "rgba(239, 246, 255, 0.5)" }}
                contentStyle={{
                  backgroundColor: "rgba(255, 255, 255, 0.9)",
                  border: "1px solid #e0e0e0",
                  borderRadius: "0.5rem",
                }}
                content={({ active, label, payload }) => {
                  if (!active || !payload || payload.length === 0) return null;
                  const barEntry = payload.find(
                    (p: any) => p && p.dataKey === "value" && p.type === "bar"
                  );
                  const value = (
                    barEntry ? barEntry.value : payload[0].value
                  ) as number;
                  return (
                    <div style={{ padding: "6px 10px" }}>
                      <div style={{ fontWeight: 600, fontSize: 12 }}>
                        {label}
                      </div>
                      <div style={{ fontSize: 12 }}>value: {value}</div>
                    </div>
                  );
                }}
              />
              <Bar dataKey="value" fill="#3b82f6" barSize={40}>
                <LabelList
                  dataKey="value"
                  position="top"
                  fill="#111827"
                  fontSize={12}
                />
              </Bar>
              <Line
                type="monotone"
                dataKey="value"
                stroke="#000000"
                strokeWidth={1.5}
                strokeDasharray="4 4"
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  };

  return (
    <div className="mt-10">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        {UI_TEXT.keywordPerformance.title}
      </h2>
      <div className="mb-4 px-4 py-2 bg-gray-100 rounded-md inline-block">
        <p className="text-sm font-semibold text-gray-700">Source: GSC</p>
      </div>
      <div className="w-full h-px bg-gray-200 mb-6"></div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <div className="bg-blue-100 rounded-full p-2 mr-4">
              <i className="fa-solid fa-arrow-right-to-bracket text-xl text-blue-500"></i>
            </div>
            <div>
              <p className="text-sm text-gray-500">Keywords in Top 5</p>
              <p className="text-2xl font-bold">
                {keywordRankingPerformance.topThree.oct25}
              </p>
            </div>
          </div>
        </div>
       
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <div className="bg-blue-100 rounded-full p-3 mr-4">
              <i className="fa-solid fa-check text-xl text-blue-500"></i>
            </div>
            <div>
              <p className="text-sm text-gray-500">First Page Keywords</p>
              <p className="text-2xl font-bold">
                {keywordRankingPerformance.firstPage.oct25}
              </p>
            </div>
          </div>
        </div>
      </div>

       <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
  
        <TrendChart
          title={UI_TEXT.keywordPerformance.top3Title}
          data={top3Data}
        />
        <TrendChart
          title={UI_TEXT.keywordPerformance.firstPageTitle}
          data={firstPageData}
        />
   
      </div> 

      
       <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <KeywordTableCard
          title={UI_TEXT.keywordPerformance.top3Title}
          keywords={top3Oct}
        />
        <KeywordTableCard
          title={UI_TEXT.keywordPerformance.firstPageTitle}
          keywords={firstPageOct}
        />
        </div>
      </div>
   
  );
};

export default KeywordPerformance;
