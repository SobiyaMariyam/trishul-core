import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Eye, Upload, Play, CheckCircle, XCircle, Download, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import { DetectionResults, QcHistoryRow } from "@/types";

const TrinetraPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [detectionResults, setDetectionResults] = useState<DetectionResults | null>(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [qcHistory, setQcHistory] = useState<QcHistoryRow[]>([
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
  ]);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setDetectionResults(null);
    }
  };

  const handleRunDetection = () => {
    if (!selectedFile) return;

    setIsDetecting(true);
    // Simulate detection process
    setTimeout(() => {
      const defectsFound = Math.floor(Math.random() * 4); // 0-3 defects
      setDetectionResults({
        defectsFound,
        confidence: 0.85 + Math.random() * 0.15, // 85-100%
        processingTime: "1.2s",
        boundingBoxes:
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
            : [],
      });
      setIsDetecting(false);
    }, 2500);
  };

  const handleQcDecision = (decision: "pass" | "fail") => {
    if (!selectedFile) return;

    const newEntry = {
      id: qcHistory.length + 1,
      filename: selectedFile.name,
      decision,
      timestamp: new Date().toLocaleString(),
      defects: detectionResults?.defectsFound || 0,
    };

    setQcHistory([newEntry, ...qcHistory]);

    // Reset for next inspection
    setSelectedFile(null);
    setDetectionResults(null);
  };

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Header */}
      <header className="border-b border-border/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link to="/" className="inline-flex">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-trinetra rounded-lg flex items-center justify-center">
                <Eye className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-trinetra">Trinetra – Vision QC</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Intro */}
          <div className="text-center max-w-3xl mx-auto">
            <p className="text-lg text-foreground/80 leading-relaxed">
              Trinetra leverages AI and computer vision to detect defects in real-time from
              manufacturing lines. Upload an image or video, run detection, and decide pass/fail
              instantly.
            </p>
          </div>

          {/* Upload and Detection */}
          <div className="grid md:grid-cols-2 gap-8">
            {/* Upload Section */}
            <Card className="border-trinetra/20">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Upload className="w-5 h-5 text-trinetra" />
                  <span>Upload Media</span>
                </CardTitle>
                <CardDescription>
                  Upload an image or video file for AI-powered quality inspection.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="relative border-2 border-dashed border-trinetra/30 rounded-lg p-8 text-center hover:border-trinetra/50 transition-colors cursor-pointer">
                  <Upload className="w-12 h-12 text-trinetra/60 mx-auto mb-4" />
                  <div className="space-y-2">
                    <p className="text-foreground">Drop your image/video here or click to browse</p>
                    <p className="text-sm text-muted-foreground">
                      Supported: JPG, PNG, MP4, AVI (Max 50MB)
                    </p>
                  </div>
                  <input
                    type="file"
                    accept="image/*,video/*"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                  />
                </div>
                {selectedFile && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                      <span className="text-sm font-medium">{selectedFile.name}</span>
                      <Badge variant="secondary">Ready</Badge>
                    </div>
                    <Button
                      variant="trinetra"
                      onClick={handleRunDetection}
                      className="w-full"
                      disabled={isDetecting || !!detectionResults}
                      aria-label="Run AI detection on uploaded file"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      {isDetecting ? "Detecting..." : "Run Detection"}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Detection Results */}
            <Card className="border-trinetra/20">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="w-5 h-5 text-trinetra" />
                  <span>Detection Results</span>
                </CardTitle>
                <CardDescription>
                  AI analysis results with defect detection and confidence scores.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isDetecting ? (
                  <div className="text-center py-12">
                    <div className="animate-pulse text-trinetra">
                      <Eye className="w-16 h-16 mx-auto mb-2" />
                      <p>AI is analyzing your file...</p>
                    </div>
                  </div>
                ) : !detectionResults ? (
                  <div className="text-center py-12 text-muted-foreground">
                    Upload a file and run detection to see results here.
                  </div>
                ) : (
                  <div className="space-y-6">
                    {/* Mock Image with Dynamic Bounding Boxes */}
                    <div className="relative bg-muted rounded-lg p-4 min-h-[300px] flex items-center justify-center overflow-hidden">
                      <div className="text-muted-foreground text-center">
                        <Eye className="w-16 h-16 mx-auto mb-2 opacity-50" />
                        <p>Image Preview with AI Detection</p>
                      </div>

                      {/* Dynamic Bounding Boxes */}
                      {detectionResults.boundingBoxes.map((box) => (
                        <div
                          key={box.id}
                          className="absolute border-2 border-trinetra rounded bg-trinetra/10 text-xs"
                          style={{
                            left: `${box.x}%`,
                            top: `${box.y}%`,
                            width: `${box.width}%`,
                            height: `${box.height}%`,
                          }}
                        >
                          <span className="text-trinetra font-medium bg-white px-1 rounded">
                            {box.label} ({(box.confidence * 100).toFixed(0)}%)
                          </span>
                        </div>
                      ))}
                    </div>

                    {/* Results */}
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center p-4 bg-muted rounded-lg">
                        <div className="text-2xl font-bold text-trinetra">
                          {detectionResults.defectsFound}
                        </div>
                        <div className="text-sm text-muted-foreground">Defects Found</div>
                      </div>
                      <div className="text-center p-4 bg-muted rounded-lg">
                        <div className="text-2xl font-bold text-trishul">
                          {(detectionResults.confidence * 100).toFixed(0)}%
                        </div>
                        <div className="text-sm text-muted-foreground">Confidence</div>
                      </div>
                    </div>

                    {/* Pass/Fail Buttons */}
                    <div className="flex space-x-4">
                      <Button
                        variant="outline"
                        onClick={() => handleQcDecision("pass")}
                        className="flex-1 border-green-500 text-green-500 hover:bg-green-500 hover:text-white"
                        aria-label="Mark quality control as passed"
                      >
                        <CheckCircle className="w-4 h-4 mr-2" />
                        Pass
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => handleQcDecision("fail")}
                        className="flex-1 border-red-500 text-red-500 hover:bg-red-500 hover:text-white"
                        aria-label="Mark quality control as failed"
                      >
                        <XCircle className="w-4 h-4 mr-2" />
                        Fail
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* QC History */}
          <Card className="border-trinetra/20">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-trinetra">Quality Control History</CardTitle>
                <CardDescription>
                  Track all inspections and decisions for audit trails and quality metrics.
                </CardDescription>
              </div>
              <Button variant="outline" disabled>
                <Download className="w-4 h-4 mr-2" />
                Export QC Summary
              </Button>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Filename</TableHead>
                    <TableHead>Decision</TableHead>
                    <TableHead>Defects</TableHead>
                    <TableHead>Timestamp</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {qcHistory.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="font-medium">{entry.filename}</TableCell>
                      <TableCell>
                        <Badge
                          variant={entry.decision === "pass" ? "default" : "destructive"}
                          className={entry.decision === "pass" ? "bg-green-500" : ""}
                        >
                          {entry.decision.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>{entry.defects}</TableCell>
                      <TableCell className="text-muted-foreground">{entry.timestamp}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default TrinetraPage;
