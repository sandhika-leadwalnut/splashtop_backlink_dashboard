import { PagePerformanceData, PerformanceSummary } from "../data/types";
import { performanceSummary, UI_TEXT } from "../data/index";
import { ImprovingIcon } from "./icons";

interface PerformanceSummaryTableProps {
  data: PagePerformanceData[];
}

const PerformanceSummaryTable = ({ data }: PerformanceSummaryTableProps) => {
  const MoveDisplay = ({
    move,
    type,
  }: {
    move: { keyword: string; change: string } | null;
    type: "best" | "worst";
  }) => {
    if (!move) {
      return type === "worst" ? (
        <span className="text-gray-700">-</span>
      ) : (
        <span className="text-gray-500">N/A</span>
      );
    }
    const color = type === "best" ? "text-green-600" : "text-red-600";
    return (
      <span className={color}>
        {move.keyword} ({move.change})
      </span>
    );
  };
  return (
    <div className="my-10">
      <h2 className="text-2xl font-bold text-gray-800 mb-2">
        {UI_TEXT.performanceSummary.title}
      </h2>
      <div className="mb-4 px-4 py-2 bg-gray-100 rounded-md inline-block">
        <p className="text-sm font-semibold text-gray-700">Source: GSC</p>
      </div>
      <div className="w-full h-px bg-gray-200 mb-6"></div>
      <div className="bg-white shadow-lg rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-[15px]">
            <thead className="bg-slate-50 border-b-2 border-gray-300">
              <tr>
                <th className="p-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider w-[280px]">
                  URL
                </th>
                <th className="p-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                  PA Change
                </th>
                <th className="p-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                  Best Keyword Move
                </th>
                <th className="p-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                  Worst Keyword Move
                </th>
                <th className="p-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                  Overall Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {performanceSummary.map((summary, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td
                    className="p-4 font-medium text-gray-800 max-w-[280px] truncate"
                    title={summary.url}
                  >
                    {summary.url.replace(
                      /^https?:\/\/(www\.)?splashtop\.com/,
                      ""
                    )}
                  </td>
                  <td className="p-4 whitespace-nowrap text-gray-600 font-semibold">
                    {summary.paChange > 0
                      ? `+${summary.paChange}`
                      : summary.paChange}
                  </td>
                  <td className="p-4 whitespace-nowrap font-semibold">
                    <MoveDisplay move={summary.bestKeywordMove} type="best" />
                  </td>
                  <td className="p-4 whitespace-nowrap font-semibold">
                    <MoveDisplay move={summary.worstKeywordMove} type="worst" />
                  </td>
                  <td className="p-4 whitespace-nowrap">
                    {summary.overallStatus === "Need Improvement" && (
                      <span className="inline-flex items-center gap-2 bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-xs font-semibold">
  Need Improvement
</span>
                    )}
                    {summary.overallStatus === "Positive" && (
                      <span className="inline-flex items-center bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">
                        Good
                      </span>
                    )}
                    {summary.overallStatus === "Stable" && (
                      <span className="inline-flex items-center bg-amber-100 text-amber-700 px-3 py-1 rounded-full text-xs font-semibold">
                        Stable
                      </span>
                    )}
                    {summary.overallStatus === "Negative" && (
                      <span className="inline-flex items-center bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs font-semibold">
                        Negative
                      </span>
                    )}
                    {summary.overallStatus !== "Need Improvement" &&
                      summary.overallStatus !== "Positive" &&
                      summary.overallStatus !== "Stable" &&
                      summary.overallStatus !== "Negative" && (
                        <span className="text-gray-600">
                          {summary.overallStatus}
                        </span>
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PerformanceSummaryTable;
