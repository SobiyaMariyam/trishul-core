import { DetectionResults, QcHistoryRow, ApiResponse } from "../types";

// Mock QC history - mutable for adding new entries
// eslint-disable-next-line prefer-const
let mockQcHistory: QcHistoryRow[] = [
  {
    id: 1,
    filename: "product_batch_001.jpg",
    decision: "pass",
    timestamp: "2025-09-06 14:30:22",
    defects: 0,
  },
  {
    id: 2,
    filename: "component_test_045.mp4",
    decision: "fail",
    timestamp: "2025-09-06 13:15:11",
    defects: 2,
  },
  {
    id: 3,
    filename: "assembly_line_check.jpg",
    decision: "pass",
    timestamp: "2025-09-06 12:45:33",
    defects: 0,
  },
];

// Simulate API delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const trinetraApi = {
  async inferImage(file: File): Promise<ApiResponse<DetectionResults>> {
    await delay(2500);

    const defectsFound = Math.floor(Math.random() * 4); // 0-3 defects
    const boundingBoxes =
      defectsFound > 0
        ? Array.from({ length: defectsFound }, (_, i) => ({
            id: i,
            x: 20 + Math.random() * 60, // Random positions
            y: 15 + Math.random() * 60,
            width: 15 + Math.random() * 20,
            height: 10 + Math.random() * 15,
            label: ["scratch", "dent", "discoloration", "crack"][Math.floor(Math.random() * 4)],
            confidence: 0.7 + Math.random() * 0.3,
          }))
        : [];

    const results: DetectionResults = {
      defectsFound,
      confidence: 0.85 + Math.random() * 0.15, // 85-100%
      processingTime: "1.2s",
      boundingBoxes,
    };

    return {
      success: true,
      data: results,
      message: "Image analysis completed successfully",
    };
  },

  async saveDecision(payload: {
    filename: string;
    decision: "pass" | "fail";
    defects: number;
  }): Promise<ApiResponse<QcHistoryRow>> {
    await delay(300);

    const newEntry: QcHistoryRow = {
      id: mockQcHistory.length + 1,
      filename: payload.filename,
      decision: payload.decision,
      timestamp: new Date().toLocaleString(),
      defects: payload.defects,
    };

    mockQcHistory.unshift(newEntry);

    return {
      success: true,
      data: newEntry,
      message: "QC decision saved successfully",
    };
  },

  async getQcHistory(): Promise<ApiResponse<QcHistoryRow[]>> {
    await delay(400);
    return {
      success: true,
      data: mockQcHistory,
    };
  },
};
