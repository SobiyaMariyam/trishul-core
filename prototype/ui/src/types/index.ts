// Core type definitions for Trishul AI platform

export interface ScanRow {
  scanId: string;
  target: string;
  status: "completed" | "running" | "failed";
  finishedAt: string;
  vulnerabilities: number;
}

export interface ForecastPoint {
  month: string;
  actual: number | null;
  forecast: number;
}

export interface AlertMessage {
  id: number;
  type: "warning" | "success" | "info" | "error";
  message: string;
  severity: "low" | "medium" | "high";
}

export interface DetectionBox {
  id: number;
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}

export interface QcHistoryRow {
  id: number;
  filename: string;
  decision: "pass" | "fail";
  timestamp: string;
  defects: number;
}

export interface DetectionResults {
  defectsFound: number;
  confidence: number;
  processingTime: string;
  boundingBoxes: DetectionBox[];
}

// API-compatible interfaces for future backend integration
export interface TenantInfo {
  id: string;
  name: string;
  industry: string;
  subscriptionTier: "basic" | "pro" | "enterprise";
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user" | "viewer";
  tenantId: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}
