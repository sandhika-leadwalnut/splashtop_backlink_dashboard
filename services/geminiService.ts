import { GoogleGenAI } from "@google/genai";
import { PagePerformanceData } from "../data/types";

const formatDataForPrompt = (data: PagePerformanceData[]): string => {
  let promptData = "Here is the performance data for several pages:\n\n";

  data.forEach((page) => {
    promptData += `Page URL: ${page.url}\n`;
    page.metrics.forEach((metric) => {
      const latestValue = metric.monthlyData[metric.monthlyData.length - 1];
      promptData += `- Metric: "${metric.name}", Latest Value: ${
        latestValue ?? "N/A"
      }, Overall Growth: ${metric.overallGrowth || "N/A"}\n`;
    });
    promptData += "\n";
  });

  return promptData;
};

export const getPerformanceAnalysis = async (
  data: PagePerformanceData[]
): Promise<string> => {
  if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable not set.");
  }
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

  const formattedData = formatDataForPrompt(data);

  const prompt = `
        You are an expert SEO and data analyst. Based on the following backlink and keyword performance data for Splashtop, provide a concise analysis.

        Data:
        ${formattedData}

        Your analysis should include:
        1.  **Performance Summary:** A brief overview of the general trends (positive, negative, or stable).
        2.  **Top Performers:** Identify 1-2 pages or keywords that are showing strong positive growth.
        3.  **Areas for Improvement:** Point out 1-2 pages or keywords that are declining or stagnant and might need attention.
        4.  **Actionable Insight:** Provide one key recommendation or observation. For example, "The strong performance of 'Remote Access Solution' on the product page suggests high-intent users are finding it; consider creating more content around this keyword."

        Keep your analysis clear, concise, and professional. Use bullet points for readability.
    `;

  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        temperature: 0.3,
      },
    });
    return response.text;
  } catch (error) {
    console.error("Error calling Gemini API:", error);
    if (error instanceof Error) {
      return `An error occurred while communicating with the AI service: ${error.message}`;
    }
    return "An unknown error occurred while communicating with the AI service.";
  }
};
