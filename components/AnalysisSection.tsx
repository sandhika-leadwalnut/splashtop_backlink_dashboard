import React, { useState, useCallback } from "react";
import { getPerformanceAnalysis } from "../services/geminiService";
import { PagePerformanceData } from "../data/types";

interface AnalysisSectionProps {
  data: PagePerformanceData[];
}

const AnalysisSection = ({ data }: AnalysisSectionProps) => {
  const [analysis, setAnalysis] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = useCallback(async () => {
    setIsLoading(true);
    setError("");
    setAnalysis("");
    try {
      const result = await getPerformanceAnalysis(data);
      setAnalysis(result);
    } catch (e: unknown) {
      const errorMessage =
        e instanceof Error ? e.message : "An unknown error occurred.";
      setError(`Failed to get analysis: ${errorMessage}`);
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [data]);

  return (
    <div className="mt-10 bg-white shadow-lg rounded-xl p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">
        AI-Powered Performance Analysis
      </h2>
      <p className="text-gray-600 mb-6">
        Click the button below to get an AI-generated summary of the performance
        data, highlighting key trends, opportunities, and areas for improvement.
      </p>

      <button
        onClick={handleAnalyze}
        disabled={isLoading}
        className="bg-blue-600 text-white font-bold py-2 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition flex items-center space-x-2"
      >
        {isLoading ? (
          <i className="fas fa-spinner fa-spin"></i>
        ) : (
          <i className="fas fa-wand-magic-sparkles"></i>
        )}
        <span>{isLoading ? "Analyzing Data..." : "Generate Analysis"}</span>
      </button>

      {error && (
        <div
          className="mt-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md"
          role="alert"
        >
          <p className="font-bold">Error</p>
          <p>{error}</p>
        </div>
      )}

      {analysis && !isLoading && (
        <div className="mt-6 p-5 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-lg font-semibold mb-2 text-gray-700">
            Analysis Results:
          </h3>
          <div
            className="text-gray-700 whitespace-pre-wrap leading-relaxed prose prose-sm max-w-none"
            dangerouslySetInnerHTML={{
              __html: analysis.replace(/\n/g, "<br />"),
            }}
          />
        </div>
      )}
    </div>
  );
};

export default AnalysisSection;
