/**
 * Dashboard data.
 *
 * ⚠️ Do not edit numbers here by hand. ⚠️
 * Every monthly value lives in data/report.json, which is generated from the
 * monthly Word doc by:  python3 scripts/update_dashboard.py "<doc>.docx"
 * This file only reshapes report.json into what the components expect.
 */
import report from "./report.json";
import { PagePerformanceData, PerformanceSummary } from "./types";

// Performance Summary table (one row per tracked URL)
export const performanceSummary: PerformanceSummary[] =
  report.performanceSummary as PerformanceSummary[];

// Referring domains by DA
export const referringDomainsData = report.referringDomains.data;

// Monthly backlinks added (Backlink Acquisition chart)
export const monthlyBacklinkGrowth = report.monthlyBacklinkGrowth;

// Keyword Ranking Performance (Top 5 and Page 1). Field names kept for the components:
// jan25 = baseline month, oct25 = current month.
const kr = report.keywordRanking;
export const keywordRankingPerformance = {
  topThree: {
    jan25: kr.topFive.baseline,
    oct25: kr.topFive.current,
    data: kr.topFive.keywords.map((k) => ({
      url: k.url,
      keyword: k.keyword,
      jan25Rank: k.baselineRank,
      oct25Rank: k.currentRank,
    })),
  },
  firstPage: {
    jan25: kr.firstPage.baseline,
    oct25: kr.firstPage.current,
    jan25Data: kr.firstPage.baselineKeywords,
    oct25Data: kr.firstPage.currentKeywords,
  },
};

// Old per-URL monthly arrays are no longer used for display.
export const performanceData: PagePerformanceData[] = [];

export const dashboardStats = {
  urlsTracked: report.kpis.urlsTracked,
  totalBacklinks: report.kpis.totalBacklinks,
  keywordsTracked: report.kpis.keywordsTracked,
  dataSource: "Semrush, GSC, Moz",
};

// Business Impact charts: one entry per category (baseline vs current rank per keyword)
export interface KeywordImpactRow {
  keyword: string;
  baseline: number | null;
  dec25: number | null; // current month
}

export const businessImpactCategories = report.businessImpact.map((c) => ({
  title: c.title,
  insight: c.insight,
  rows: c.rows.map((r) => ({ keyword: r.keyword, baseline: r.baseline, dec25: r.current })),
}));

export const keywordImpactRows: KeywordImpactRow[] = businessImpactCategories.flatMap((c) => c.rows);

// Not shown on the dashboard any more (trend charts are switched off).
export const remoteAccessTrendData: number[] = [];
export const remoteDesktopSoftwareTrendData: number[] = [];

export const keyFindingsData = report.keyFindings;
export const highlightsData = report.highlights;
export const llmHighlightsData = report.llmHighlights;
export const reportMeta = report.meta;
export const reportKpis = report.kpis;
export const qualityStatement = report.referringDomains.qualityStatement;
export const acquisitionSheetUrl = report.acquisitionSheetUrl ?? "";
