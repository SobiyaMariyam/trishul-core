import { ScanRow, ApiResponse } from "../types";

// Mock data
const mockScanHistory: ScanRow[] = [
  {
    scanId: "SCN-001",
    target: "example.com",
    status: "completed",
    finishedAt: "2025-09-06",
    vulnerabilities: 3,
  },
  {
    scanId: "SCN-002",
    target: "testserver.local",
    status: "completed",
    finishedAt: "2025-09-05",
    vulnerabilities: 1,
  },
  {
    scanId: "SCN-003",
    target: "api.example.org",
    status: "running",
    finishedAt: "-",
    vulnerabilities: 0,
  },
];

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const kavachApi = {
  async createScan(file: File): Promise<ApiResponse<{ scanId: string }>> {
    await delay(1000);
    const scanId = `SCN-${String(Math.floor(Math.random() * 999)).padStart(3, "0")}`;

    // Add to mock history
    mockScanHistory.unshift({
      scanId,
      target: file.name.replace(/\.[^/.]+$/, ""), // Remove file extension
      status: "running",
      finishedAt: "-",
      vulnerabilities: 0,
    });

    return {
      success: true,
      data: { scanId },
      message: "Scan initiated successfully",
    };
  },

  async getScans(): Promise<ApiResponse<ScanRow[]>> {
    await delay(500);
    return {
      success: true,
      data: mockScanHistory,
    };
  },

  async getReport(scanId: string): Promise<ApiResponse<Blob>> {
    await delay(800);
    // Simulate PDF report generation
    const reportContent = `Vulnerability Report for ${scanId}\n\nGenerated: ${new Date().toISOString()}`;
    const blob = new Blob([reportContent], { type: "text/plain" });

    return {
      success: true,
      data: blob,
      message: "Report generated successfully",
    };
  },
};
