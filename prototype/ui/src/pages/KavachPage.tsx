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
import { Shield, Upload, Download, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

const KavachPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isScanning, setIsScanning] = useState(false);

  const mockScanHistory = [
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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleScanNow = () => {
    if (!selectedFile) return;

    setIsScanning(true);
    // Simulate scanning process
    setTimeout(() => {
      setIsScanning(false);
      // Could add toast notification here: "Scan completed! Check history for results."
    }, 3000);
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
              <div className="w-8 h-8 bg-gradient-kavach rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-kavach">Kavach – Cyber Defense Suite</h1>
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
              Kavach helps security analysts quickly identify vulnerabilities in networks and
              systems. Upload your target list, run scans, and download instant PDF reports for
              compliance and audits.
            </p>
          </div>

          {/* Upload Section */}
          <Card className="border-kavach/20">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="w-5 h-5 text-kavach" />
                <span>Upload Target List</span>
              </CardTitle>
              <CardDescription>
                Upload a CSV file containing IP addresses or domain names to scan for
                vulnerabilities.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="relative border-2 border-dashed border-kavach/30 rounded-lg p-8 text-center hover:border-kavach/50 transition-colors cursor-pointer">
                <Upload className="w-12 h-12 text-kavach/60 mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-foreground">Drop your CSV file here or click to browse</p>
                  <p className="text-sm text-muted-foreground">
                    Format: Each line should contain one target (IP or domain)
                  </p>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                />
              </div>
              {selectedFile && (
                <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <span className="text-sm font-medium">{selectedFile.name}</span>
                  <Badge variant="secondary">Ready</Badge>
                </div>
              )}
              <div className="flex justify-center">
                <Button
                  variant="kavach"
                  disabled={!selectedFile || isScanning}
                  onClick={handleScanNow}
                  className="px-8"
                  aria-label="Start vulnerability scan of uploaded file"
                >
                  <Shield className="w-4 h-4 mr-2" />
                  {isScanning ? "Scanning..." : "Scan Now"}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Scan History */}
          <Card className="border-kavach/20">
            <CardHeader>
              <CardTitle className="text-kavach">Scan History</CardTitle>
              <CardDescription>
                View and download reports from previous vulnerability scans.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Scan ID</TableHead>
                    <TableHead>Target</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Vulnerabilities</TableHead>
                    <TableHead>Finished</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockScanHistory.map((scan) => (
                    <TableRow key={scan.scanId}>
                      <TableCell className="font-medium">{scan.scanId}</TableCell>
                      <TableCell>{scan.target}</TableCell>
                      <TableCell>
                        <Badge variant={scan.status === "completed" ? "default" : "secondary"}>
                          {scan.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {scan.vulnerabilities > 0 ? (
                          <Badge variant="destructive">{scan.vulnerabilities}</Badge>
                        ) : (
                          <Badge variant="secondary">0</Badge>
                        )}
                      </TableCell>
                      <TableCell>{scan.finishedAt}</TableCell>
                      <TableCell>
                        {scan.status === "completed" && (
                          <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-2" />
                            Report
                          </Button>
                        )}
                      </TableCell>
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

export default KavachPage;
