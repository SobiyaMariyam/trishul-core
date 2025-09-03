# Trishul AI — Sobiya Phase 1: Frontend + ML/QC Scope

## Personas
- Security Analyst (Kavach): trigger scans, view & download reports
- FinOps Analyst (Rudra): view forecast, see alerts, import CSV
- QC Operator (Trinetra): upload image/video, run detection, pass/fail decision
- QC Lead: review history, export CSV/PDF summaries

## Screens (MVP you will build later)
- Global Layout: Top tabs → Kavach | Rudra | Trinetra
- Kavach:
  - Upload Targets CSV (UI only)
  - “Scan Now” button (calls backend later)
  - Scan History table (dummy JSON in Phase 2)
  - PDF/HTML Report viewer (embed)
- Rudra:
  - Month range selector
  - Forecast line chart (dummy data first)
  - Alert badges
  - “Import Usage CSV” (mock)
- Trinetra:
  - File upload (image)
  - Detection overlay canvas
  - Pass/Fail decision buttons
  - History list (dummy first)

## Non-Functional (UI)
- Accessibility: keyboard focus, alt text for charts
- Responsiveness: ≤480, ≤1024, >1024 breakpoints
- Performance: lazy-load report viewer and charts
