## Kavach (Scanner)
POST /scans -> 201
{
  "scanId": "scn_01",
  "status": "queued",
  "submittedAt": "2025-09-03T10:00:00Z"
}

GET /scans/:id -> 200
{
  "scanId": "scn_01",
  "status": "done",
  "targets": ["1.2.3.4"],
  "finishedAt": "2025-09-03T10:10:00Z"
}

## Rudra (Forecast)
GET /costs/forecast?months=6 -> 200
{
  "currency": "USD",
  "forecast": [
    {"month": "2025-09", "predicted": 212.4},
    {"month": "2025-10", "predicted": 189.7}
  ],
  "alerts": [{"type": "budget", "message": "Likely to exceed $200 in Oct"}]
}

## Trinetra (Inference)
POST /trinetra/infer -> 200
{
  "modelId": "mdl_yolov8_s1",
  "detections": [
    {"label": "scratch", "score": 0.87, "bbox":{"x":120,"y":95,"w":60,"h":30}}
  ],
  "overlayHint": "bbox",
  "suggestedDecision": "fail"
}

POST /trinetra/decision -> 201
{ "inferenceId": "inf_01", "decision": "fail", "notes": "deep scratch" }
