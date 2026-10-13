import React from "react";
import Header from "./components/Header";
import SummaryCard from "./components/SummaryCard";
import {
  performanceData,
  referringDomainsData,
  monthlyBacklinkGrowth,
  DASHBOARD_STATS,
  REPORT_CONFIG,
} from "./data/index";
import { UrlIcon, LinkIcon, KeywordIcon } from "./components/icons";
import BacklinkGrowthChart from "./components/BacklinkGrowthChart";
import KeywordPerformance from "./components/KeywordPerformance";
import PerformanceSummaryTable from "./components/PerformanceSummaryTable";
import ReferringDomainsChart from "./components/ReferringDomainsChart";
import BusinessImpactOfBacklinks from "./components/BusinessImpactOfBacklinks";
import ImplementationDetails from "./components/ImplementationDetails";
import KeyFindings from "./components/KeyFindings";
import BacklinkBestPractices from "./components/BacklinkBestPractices";
import HighlightsSection from "./components/HighlightsSection";

const App: React.FC = () => {
  const totalBacklinks = performanceData
    .flatMap(
      (p) =>
        p.metrics
          .find((m) => m.name === "Total Backlinks")
          ?.monthlyData.slice(-1)[0] || 0
    )
    .reduce((sum, current) => sum + (current || 0), 0);

  const totalKeywords = performanceData
    .flatMap((p) => p.metrics.filter((m) => m.isKeyword).length)
    .reduce((sum, current) => sum + current, 0);

  const backlinkChartData = monthlyBacklinkGrowth.map((d) => ({
    name: d.month.split("'")[0],
    "Total Backlinks": d.backlinks,
  }));

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      <Header />
      <main className="max-w-7xl mx-auto px-5 md:px-8 py-4 md:py-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <SummaryCard
            icon={
              <i className="fa-solid fa-file-lines text-3xl text-blue-500"></i>
            }
            title="URLs Tracked"
            value={DASHBOARD_STATS.urlsTracked.toString()}
            description="Total pages monitored"
          />
          <SummaryCard
            icon={<UrlIcon />}
            title="Keywords Tracked"
            value={DASHBOARD_STATS.keywordsTracked.toString()}
            description="Total keywords monitored"
          />
          <SummaryCard
            icon={<i className="fa-solid fa-search text-3xl text-blue-500"></i>}
            title={`Plan Total Backlinks (Till ${REPORT_CONFIG.currentMonthAbbr})`}
            value={DASHBOARD_STATS.PlanTotalBacklinks.toString()}
            description=""
          />
          <SummaryCard
            icon={<LinkIcon />}
            title={`Actual Total Backlinks (Till ${REPORT_CONFIG.currentMonthAbbr})`}
            value={DASHBOARD_STATS.totalBacklinks.toString()}
            description=""
          />
        </div>

        <BusinessImpactOfBacklinks />

        <ReferringDomainsChart data={referringDomainsData} />

        <BacklinkGrowthChart data={backlinkChartData} />

        <KeywordPerformance data={performanceData} />

        <PerformanceSummaryTable data={performanceData} />

        <ImplementationDetails />

        <KeyFindings />
        <HighlightsSection />

         <BacklinkBestPractices /> 
      </main>
    </div>
  );
};

export default App;
