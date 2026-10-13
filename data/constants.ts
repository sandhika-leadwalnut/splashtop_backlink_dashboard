import { reportMeta, reportKpis, keyFindingsData, qualityStatement, acquisitionSheetUrl } from "./mockdata";

export const REPORT_CONFIG = {
  // From data/report.json (generated from the monthly Word doc)
  reportDate: reportMeta.reportDate,
  reportTitle: reportMeta.reportTitle,
  reportSubtitle: reportMeta.reportSubtitle,
  dataSource: "Ahrefs, GSC",
  country: "US",
  currentMonthName: reportMeta.currentMonthName,
  currentMonthAbbr: reportMeta.currentMonthAbbr,
};

// ============================================================================
// MONTH CONFIGURATION - CENTRALIZED
// ============================================================================
// ⭐ UPDATE ALL MONTH-RELATED DATA HERE ⭐
//
// This is the single source of truth for all month-related data.
// Update these arrays when you need to change the time period.

// Main months array (used for performanceData monthlyData arrays)
// Array indices: 0=Dec'24, 1=Jan'25, 2=Feb'25, ..., 10=Oct'25
export const months: string[] = [
  "Dec'25",
  "Feb'26",
];

// Extended months array (used for trend charts with more historical data)
// Contains 16 months from Jul'24 to Oct'25
export const extendedMonths = [
  "Jul'24",
  "Aug'24",
  "Sep'24",
  "Oct'24",
  "Nov'24",
  "Dec'24",
  "Jan'25",
  "Feb'25",
  "Mar'25",
  "Apr'25",
  "May'25",
  "Jun'25",
  "Jul'25",
  "Aug'25",
  "Sep'25",
  "Oct'25",
  "Nov'25",
  "Dec'25",
  "Feb'26",
  "Mar'26",
  "Apr'26",

 
];

// Month indices for baseline and current comparison
// These reference the 'months' array above
// baseline: index 1 = "Jan'25"
// current: index 11 = "Nov'25"
export const MONTH_INDICES = {
  baseline: 1, // Index in 'months' array for baseline period
  current: 11, // Index in 'months' array for current period
};

// Month labels for display (used in charts and UI)
// These should match the months at MONTH_INDICES.baseline and MONTH_INDICES.current
export const MONTH_LABELS = {
  baseline: reportMeta.baselineLabel, // e.g. "Dec 2025 (Baseline)"
  current: reportMeta.currentLabel, // e.g. "September 2026"
};

export const DASHBOARD_STATS = {
  urlsTracked: reportKpis.urlsTracked,
  totalBacklinks: reportKpis.totalBacklinks,
  keywordsTracked: reportKpis.keywordsTracked,
  PlanTotalBacklinks: reportKpis.planTotalBacklinks,
};

// Icon and colour per position; the text comes from the Word doc (via report.json)
const KEY_FINDING_STYLES = [
  { icon: "fas fa-bullseye", color: "text-teal-600", bgColor: "bg-teal-50" },
  { icon: "fas fa-shield-alt", color: "text-purple-600", bgColor: "bg-purple-50" },
  { icon: "fas fa-chart-line", color: "text-blue-600", bgColor: "bg-blue-50" },
  { icon: "fas fa-arrow-trend-up", color: "text-green-600", bgColor: "bg-green-50" },
];

export const KEY_FINDINGS = keyFindingsData.map((f, i) => ({
  title: "",
  description: f.description,
  ...KEY_FINDING_STYLES[i % KEY_FINDING_STYLES.length],
}));


export const BUSINESS_IMPACT_CONFIG = {
  topKeywordsCount: 18,
  // chartTitle: "Critical Keywords",
  chartSubtitle: "Critical keywords Performance",
  insightText: [
  "Remote access and remote desktop keywords continue to deliver strong visibility, with 'remote access (5)' maintaining a top 5 position, while 'remote desktop (12)' returns to its Dec’25 position.",
  "Competitor keywords continue to strengthen, with 'anydesk pricing (4)' and 'teamviewer alternative (5)' ranking in the top 5, while 'teamviewer pricing (5)' maintains its top 5 position and 'anydesk alternative (7)' moves into the top 10.'teamviewer pricing (5)' now ranking in the top 5, while 'teamviewer alternative (9)' maintains a first-page position. ",
  "Patch management is showing significant improvement, moving from position 62 to 8 and securing a first-page ranking. "
],
  trendChartTitle: "Ranking Performance Trend",
  trendKeyTakeaway:
    "Remote Desktop Software: 10 backlinks added in June boosted its ranking to page 1. \n\nRemote Access: 30 backlinks were added in Jan, helping maintain a stable position on page 1.",
};

export const REFERRING_DOMAINS_CONFIG = {
  qualityStatement, // calculated from the DA split
};

export const IMPLEMENTATION_CONFIG = {
  sheetUrl: acquisitionSheetUrl,
  sheetLinkText: "Detailed Monthly Backlink Sheet",
};

export const IMAGE_PATHS = {
  splashtopLogo: "/splashtop_image.png",
  leadwalnutLogo: "/LeadWalnut light logo with tagline 3.png",
};

export const UI_TEXT = {
  keywordPerformance: {
    title: "Keyword Ranking Performance",
    top3Title: "Keywords in Top 5 Positions",
    firstPageTitle: "Keywords on Page 1",
    noKeywords: "No keywords in this category.",
  },
  performanceSummary: {
    title: "Performance Summary - URL wise Breakdown",
  },
  backlinkGrowth: {
    title: "Backlink Acquisition - Monthly Growth Trend",
  },
  referringDomains: {
    title: "Backlink Quality Assurance",
    subtitle: "Referring Domains DA",
  },
  businessImpact: {
    title: "Business Impact of Backlinks",
  },
  implementationDetails: {
    title: "Backlink Acquisition Details",
  },
  backlinkBestPractices: {
    title: "Backlink Best Practices",
  },
};
