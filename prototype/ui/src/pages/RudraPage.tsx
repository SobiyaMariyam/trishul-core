import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Cloud, TrendingUp, AlertTriangle, CheckCircle, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const RudraPage = () => {
  const [timeRange, setTimeRange] = useState("6");

  const mockForecastData6Months = [
    { month: "Jul 2025", actual: 180, forecast: 185 },
    { month: "Aug 2025", actual: 220, forecast: 225 },
    { month: "Sep 2025", actual: 195, forecast: 190 },
    { month: "Oct 2025", actual: null, forecast: 210 },
    { month: "Nov 2025", actual: null, forecast: 245 },
    { month: "Dec 2025", actual: null, forecast: 200 },
  ];

  const mockForecastData12Months = [
    { month: "Jul 2025", actual: 180, forecast: 185 },
    { month: "Aug 2025", actual: 220, forecast: 225 },
    { month: "Sep 2025", actual: 195, forecast: 190 },
    { month: "Oct 2025", actual: null, forecast: 210 },
    { month: "Nov 2025", actual: null, forecast: 245 },
    { month: "Dec 2025", actual: null, forecast: 200 },
    { month: "Jan 2026", actual: null, forecast: 230 },
    { month: "Feb 2026", actual: null, forecast: 215 },
    { month: "Mar 2026", actual: null, forecast: 250 },
    { month: "Apr 2026", actual: null, forecast: 235 },
    { month: "May 2026", actual: null, forecast: 270 },
    { month: "Jun 2026", actual: null, forecast: 260 },
  ];

  const currentForecastData =
    timeRange === "6" ? mockForecastData6Months : mockForecastData12Months;

  const mockAlerts = [
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
              <div className="w-8 h-8 bg-gradient-rudra rounded-lg flex items-center justify-center">
                <Cloud className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-rudra">Rudra – CloudGuard</h1>
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
              Rudra empowers FinOps teams by providing visibility into cloud usage and predicting
              monthly costs using AI. Import your usage data, view cost forecasts, and set up alerts
              to stay under budget.
            </p>
          </div>

          {/* Controls */}
          <Card className="border-rudra/20">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="w-5 h-5 text-rudra" />
                <span>Cost Forecast</span>
              </CardTitle>
              <CardDescription>
                AI-powered cloud cost predictions based on historical usage patterns.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center space-x-4">
                <label className="text-sm font-medium">Forecast Range:</label>
                <Select value={timeRange} onValueChange={setTimeRange}>
                  <SelectTrigger className="w-40">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="6">6 months</SelectItem>
                    <SelectItem value="12">12 months</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Chart */}
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={currentForecastData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                    <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="actual"
                      stroke="hsl(var(--trishul-primary))"
                      strokeWidth={2}
                      dot={{ fill: "hsl(var(--trishul-primary))" }}
                      name="Actual Cost ($)"
                    />
                    <Line
                      type="monotone"
                      dataKey="forecast"
                      stroke="hsl(var(--rudra))"
                      strokeWidth={2}
                      strokeDasharray="5 5"
                      dot={{ fill: "hsl(var(--rudra))" }}
                      name="Forecast ($)"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Alerts */}
          <Card className="border-rudra/20">
            <CardHeader>
              <CardTitle className="text-rudra">Cost Alerts</CardTitle>
              <CardDescription>
                Proactive notifications about budget thresholds and spending anomalies.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAlerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border/50 hover:border-border transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      {alert.type === "warning" && (
                        <AlertTriangle className="w-5 h-5 text-yellow-500" />
                      )}
                      {alert.type === "success" && (
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      )}
                      {alert.type === "info" && <TrendingUp className="w-5 h-5 text-blue-500" />}
                      <span className="text-foreground">{alert.message}</span>
                    </div>
                    <Badge
                      variant={
                        alert.severity === "high"
                          ? "destructive"
                          : alert.severity === "medium"
                            ? "secondary"
                            : "outline"
                      }
                    >
                      {alert.severity}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default RudraPage;
