import { ForecastPoint, AlertMessage, ApiResponse } from "../types";

// Mock data generators
const generateForecastData = (months: number): ForecastPoint[] => {
  const baseData6Months: ForecastPoint[] = [
    { month: "Jul 2025", actual: 180, forecast: 185 },
    { month: "Aug 2025", actual: 220, forecast: 225 },
    { month: "Sep 2025", actual: 195, forecast: 190 },
    { month: "Oct 2025", actual: null, forecast: 210 },
    { month: "Nov 2025", actual: null, forecast: 245 },
    { month: "Dec 2025", actual: null, forecast: 200 },
  ];

  const extendedData: ForecastPoint[] = [
    ...baseData6Months,
    { month: "Jan 2026", actual: null, forecast: 230 },
    { month: "Feb 2026", actual: null, forecast: 215 },
    { month: "Mar 2026", actual: null, forecast: 250 },
    { month: "Apr 2026", actual: null, forecast: 235 },
    { month: "May 2026", actual: null, forecast: 270 },
    { month: "Jun 2026", actual: null, forecast: 260 },
  ];

  return months === 6 ? baseData6Months : extendedData;
};

const mockAlerts: AlertMessage[] = [
  {
    id: 1,
    type: "warning",
    message: "⚠ Forecast exceeds $200 in Nov 2025",
    severity: "high",
  },
  {
    id: 2,
    type: "success",
    message: "✅ Current usage within budget",
    severity: "low",
  },
  {
    id: 3,
    type: "info",
    message: "📊 EC2 instances showing 15% increase trend",
    severity: "medium",
  },
];

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const rudraApi = {
  async getForecast(months: 6 | 12 = 6): Promise<ApiResponse<ForecastPoint[]>> {
    await delay(600);
    return {
      success: true,
      data: generateForecastData(months),
      message: `${months}-month forecast generated successfully`,
    };
  },

  async getAlerts(): Promise<ApiResponse<AlertMessage[]>> {
    await delay(300);
    return {
      success: true,
      data: mockAlerts,
    };
  },

  async updateBudgetAlert(threshold: number): Promise<ApiResponse<void>> {
    await delay(400);
    return {
      success: true,
      message: `Budget alert threshold updated to $${threshold}`,
    };
  },
};
