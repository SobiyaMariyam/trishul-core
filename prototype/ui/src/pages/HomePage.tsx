import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoginDialog } from "@/components/LoginDialog";
import Navigation from "@/components/Navigation";
import {
  Shield,
  Cloud,
  Eye,
  CheckCircle,
  Users,
  Award,
  Mail,
  Phone,
  MapPin,
  Github,
  Twitter,
  Linkedin,
  ArrowRight,
  Play,
} from "lucide-react";
import { Link } from "react-router-dom";
import trishulLogo from "@/assets/trishul-logo.png";

const HomePage = () => {
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-hero">
      {/* Navigation */}
      <Navigation onLoginClick={() => setLoginOpen(true)} />

      {/* Hero Section */}
      <section
        id="hero"
        className="relative container mx-auto px-4 pt-40 pb-32 text-center overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-trishul-red/5 via-trishul-gold/5 to-transparent"></div>
        <div className="relative max-w-5xl mx-auto">
          <div className="inline-flex items-center gap-2 bg-primary/10 px-4 py-2 rounded-full mb-8 animate-fade-in">
            <Award className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">Next-Generation AI Platform</span>
          </div>
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-8 bg-gradient-brand bg-clip-text text-transparent leading-tight animate-fade-in">
            Trishul AI
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-primary font-semibold mb-6 animate-fade-in">
            Three Blades. One Power.
          </p>
          <p className="text-base sm:text-lg md:text-xl text-muted-foreground max-w-4xl mx-auto mb-12 leading-relaxed animate-fade-in">
            Unify <span className="text-primary font-semibold">Cyber Defense</span>,{" "}
            <span className="text-primary font-semibold">Cloud Governance</span>, and{" "}
            <span className="text-primary font-semibold">AI-Driven Quality Control</span> into one
            powerful enterprise suite.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-fade-in">
            <Button
              size="lg"
              className="bg-gradient-brand hover:shadow-brand text-lg px-8 py-4 group"
              aria-label="Get started with Trishul AI platform"
            >
              Get Started
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              variant="outline"
              size="lg"
              className="text-lg px-8 py-4 group"
              aria-label="Watch product demonstration video"
            >
              <Play className="w-5 h-5 mr-2" />
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
          <div className="text-center group">
            <div className="text-3xl font-bold text-primary mb-2 group-hover:scale-110 transition-transform">
              99.9%
            </div>
            <div className="text-sm text-muted-foreground">Uptime</div>
          </div>
          <div className="text-center group">
            <div className="text-3xl font-bold text-primary mb-2 group-hover:scale-110 transition-transform">
              500+
            </div>
            <div className="text-sm text-muted-foreground">Enterprise Clients</div>
          </div>
          <div className="text-center group">
            <div className="text-3xl font-bold text-primary mb-2 group-hover:scale-110 transition-transform">
              1M+
            </div>
            <div className="text-sm text-muted-foreground">Threats Blocked</div>
          </div>
          <div className="text-center group">
            <div className="text-3xl font-bold text-primary mb-2 group-hover:scale-110 transition-transform">
              50%
            </div>
            <div className="text-sm text-muted-foreground">Cost Savings</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-foreground mb-4">Why Choose Trishul AI?</h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Experience the power of integrated AI solutions designed for modern enterprises
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-16">
          <div className="text-center p-6 group hover:bg-card/50 rounded-xl transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-primary rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <CheckCircle className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Enterprise Ready</h3>
            <p className="text-muted-foreground">
              Scalable, secure, and compliant with enterprise standards
            </p>
          </div>
          <div className="text-center p-6 group hover:bg-card/50 rounded-xl transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-brand rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Multi-Tenant</h3>
            <p className="text-muted-foreground">
              Seamless multi-tenant architecture for all organization sizes
            </p>
          </div>
          <div className="text-center p-6 group hover:bg-card/50 rounded-xl transition-all duration-300">
            <div className="w-16 h-16 bg-gradient-kavach rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
              <Award className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-xl font-semibold mb-3">AI-Powered</h3>
            <p className="text-muted-foreground">
              Advanced AI algorithms for predictive insights and automation
            </p>
          </div>
        </div>
      </section>

      {/* Products Section */}
      <section id="products" className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-foreground mb-4">Our Three Powerful Modules</h2>
          <p className="text-xl text-muted-foreground">
            Choose the perfect solution for your needs
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Kavach Card */}
          <Card className="relative overflow-hidden border-kavach/20 hover:border-kavach/40 transition-all duration-500 hover:shadow-kavach hover:-translate-y-2 group bg-card/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-kavach opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
            <CardHeader className="space-y-6 relative z-10">
              <div className="w-16 h-16 bg-gradient-kavach rounded-xl flex items-center justify-center group-hover:scale-110 transition-all duration-300 shadow-lg">
                <Shield className="w-8 h-8 text-white" />
              </div>
              <div>
                <CardTitle className="text-kavach text-2xl mb-3">
                  Kavach – Cyber Defense Suite
                </CardTitle>
                <CardDescription className="text-base leading-relaxed mb-2">
                  Advanced vulnerability management with automated scans, real-time threat
                  detection, and comprehensive security reports.
                </CardDescription>
                <div className="text-sm font-medium text-kavach bg-kavach/10 px-3 py-1 rounded-full inline-block">
                  🛡️ Protect against 99.9% of known threats
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-kavach" />
                  <span>Automated Vulnerability Scans</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-kavach" />
                  <span>Real-time Threat Detection</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-kavach" />
                  <span>Compliance Reporting</span>
                </div>
              </div>
              <Link to="/kavach">
                <Button
                  variant="kavach"
                  className="w-full py-3 text-lg font-semibold group"
                  aria-label="Launch Kavach Cyber Defense Suite"
                >
                  Launch Kavach
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Rudra Card */}
          <Card className="relative overflow-hidden border-rudra/20 hover:border-rudra/40 transition-all duration-500 hover:shadow-rudra hover:-translate-y-2 group bg-card/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-rudra opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
            <CardHeader className="space-y-6 relative z-10">
              <div className="w-16 h-16 bg-gradient-rudra rounded-xl flex items-center justify-center group-hover:scale-110 transition-all duration-300 shadow-lg">
                <Cloud className="w-8 h-8 text-white" />
              </div>
              <div>
                <CardTitle className="text-rudra text-2xl mb-3">Rudra – CloudGuard</CardTitle>
                <CardDescription className="text-base leading-relaxed mb-2">
                  Intelligent cloud cost management with predictive analytics, configuration
                  monitoring, and automated alerts.
                </CardDescription>
                <div className="text-sm font-medium text-rudra bg-rudra/10 px-3 py-1 rounded-full inline-block">
                  ☁️ Reduce cloud costs by up to 50%
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-rudra" />
                  <span>Cost Forecasting</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-rudra" />
                  <span>Configuration Monitoring</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-rudra" />
                  <span>Proactive Alerts</span>
                </div>
              </div>
              <Link to="/rudra">
                <Button
                  variant="rudra"
                  className="w-full py-3 text-lg font-semibold group"
                  aria-label="Launch Rudra CloudGuard cost management"
                >
                  Launch Rudra
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Trinetra Card */}
          <Card className="relative overflow-hidden border-trinetra/20 hover:border-trinetra/40 transition-all duration-500 hover:shadow-trinetra hover:-translate-y-2 group bg-card/50 backdrop-blur-sm">
            <div className="absolute inset-0 bg-gradient-trinetra opacity-0 group-hover:opacity-5 transition-opacity duration-500"></div>
            <CardHeader className="space-y-6 relative z-10">
              <div className="w-16 h-16 bg-gradient-trinetra rounded-xl flex items-center justify-center group-hover:scale-110 transition-all duration-300 shadow-lg">
                <Eye className="w-8 h-8 text-white" />
              </div>
              <div>
                <CardTitle className="text-trinetra text-2xl mb-3">Trinetra – Vision QC</CardTitle>
                <CardDescription className="text-base leading-relaxed mb-2">
                  AI-powered quality control with computer vision, real-time defect detection, and
                  manufacturing excellence.
                </CardDescription>
                <div className="text-sm font-medium text-trinetra bg-trinetra/10 px-3 py-1 rounded-full inline-block">
                  👁️ Achieve 99.5% defect detection accuracy
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="space-y-3 mb-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-trinetra" />
                  <span>Real-time Inspection</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-trinetra" />
                  <span>Defect Detection</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-trinetra" />
                  <span>Quality Analytics</span>
                </div>
              </div>
              <Link to="/trinetra">
                <Button
                  variant="trinetra"
                  className="w-full py-3 text-lg font-semibold group"
                  aria-label="Launch Trinetra Vision QC quality control"
                >
                  Launch Trinetra
                  <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-foreground mb-6">About Trishul AI</h2>
          <p className="text-xl text-muted-foreground leading-relaxed mb-8">
            Named after the divine trident, Trishul AI embodies the power of three unified forces.
            Our platform brings together the essential pillars of modern enterprise technology:
            security, cloud management, and quality assurance.
          </p>
          <div className="grid md:grid-cols-3 gap-8 mt-16">
            <div className="text-center">
              <div className="text-4xl mb-4">🛡️</div>
              <h3 className="text-xl font-semibold mb-2">Security First</h3>
              <p className="text-muted-foreground">
                Built with enterprise-grade security standards
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-semibold mb-2">Lightning Fast</h3>
              <p className="text-muted-foreground">Optimized for performance and scalability</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="text-xl font-semibold mb-2">Precision Focused</h3>
              <p className="text-muted-foreground">Accurate insights and actionable intelligence</p>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="bg-muted/30 backdrop-blur-sm border-t border-border/50">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-foreground mb-6">Ready to Get Started?</h2>
            <p className="text-xl text-muted-foreground mb-12">
              Join hundreds of enterprises already using Trishul AI to secure, optimize, and excel.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Button size="lg" className="bg-gradient-brand hover:shadow-brand text-lg px-8 py-4">
                Start Free Trial
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-4">
                Schedule Demo
              </Button>
            </div>
            <div className="grid md:grid-cols-3 gap-8 max-w-3xl mx-auto">
              <div className="text-center">
                <Mail className="w-8 h-8 mx-auto mb-3 text-primary" />
                <div className="font-medium text-foreground">Email Us</div>
                <div className="text-muted-foreground">hello@trishulai.com</div>
              </div>
              <div className="text-center">
                <Phone className="w-8 h-8 mx-auto mb-3 text-primary" />
                <div className="font-medium text-foreground">Call Us</div>
                <div className="text-muted-foreground">+1 (555) 123-4567</div>
              </div>
              <div className="text-center">
                <MapPin className="w-8 h-8 mx-auto mb-3 text-primary" />
                <div className="font-medium text-foreground">Visit Us</div>
                <div className="text-muted-foreground">San Francisco, CA</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted/50 backdrop-blur-sm border-t border-border/50">
        <div className="container mx-auto px-4 py-16">
          <div className="grid md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <img src={trishulLogo} alt="Trishul AI Logo" className="w-10 h-10 object-contain" />
                <div>
                  <h3 className="text-xl font-bold text-primary">Trishul AI</h3>
                  <p className="text-xs text-primary/80 font-medium">Three Blades. One Power.</p>
                </div>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                Empowering enterprises with AI-driven security, cloud governance, and quality
                control solutions.
              </p>
              <div className="flex space-x-4">
                <Button variant="ghost" size="icon" className="hover:text-primary">
                  <Twitter className="w-5 h-5" />
                </Button>
                <Button variant="ghost" size="icon" className="hover:text-primary">
                  <Linkedin className="w-5 h-5" />
                </Button>
                <Button variant="ghost" size="icon" className="hover:text-primary">
                  <Github className="w-5 h-5" />
                </Button>
              </div>
            </div>

            {/* Products */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-foreground">Products</h4>
              <div className="space-y-3">
                <Link
                  to="/kavach"
                  className="block text-muted-foreground hover:text-kavach transition-colors"
                >
                  Kavach - Cyber Defense
                </Link>
                <Link
                  to="/rudra"
                  className="block text-muted-foreground hover:text-rudra transition-colors"
                >
                  Rudra - CloudGuard
                </Link>
                <Link
                  to="/trinetra"
                  className="block text-muted-foreground hover:text-trinetra transition-colors"
                >
                  Trinetra - Vision QC
                </Link>
              </div>
            </div>

            {/* Company */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-foreground">Company</h4>
              <div className="space-y-3">
                <button
                  onClick={() =>
                    document.getElementById("about")?.scrollIntoView({ behavior: "smooth" })
                  }
                  className="block text-left text-muted-foreground hover:text-primary transition-colors"
                >
                  About Us
                </button>
                <a
                  href="#"
                  className="block text-muted-foreground hover:text-primary transition-colors"
                >
                  Careers
                </a>
                <a
                  href="#"
                  className="block text-muted-foreground hover:text-primary transition-colors"
                >
                  Blog
                </a>
                <a
                  href="#"
                  className="block text-muted-foreground hover:text-primary transition-colors"
                >
                  Press
                </a>
              </div>
            </div>

            {/* Contact */}
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-foreground">Contact</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Mail className="w-4 h-4" />
                  <span>hello@trishulai.com</span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Phone className="w-4 h-4" />
                  <span>+1 (555) 123-4567</span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <MapPin className="w-4 h-4" />
                  <span>San Francisco, CA</span>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-border/50 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-muted-foreground text-sm">
              © 2024 Trishul AI. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a
                href="#"
                className="text-muted-foreground hover:text-primary text-sm transition-colors"
              >
                Privacy Policy
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary text-sm transition-colors"
              >
                Terms of Service
              </a>
              <a
                href="#"
                className="text-muted-foreground hover:text-primary text-sm transition-colors"
              >
                Security
              </a>
            </div>
          </div>
        </div>
      </footer>

      <LoginDialog open={loginOpen} onOpenChange={setLoginOpen} />
    </div>
  );
};

export default HomePage;
