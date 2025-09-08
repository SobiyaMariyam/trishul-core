import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Menu, X, ChevronUp } from "lucide-react";
import { Link } from "react-router-dom";
import trishulLogo from "@/assets/trishul-logo.png";

interface NavigationProps {
  onLoginClick: () => void;
}

const Navigation = ({ onLoginClick }: NavigationProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY;
      setScrolled(scrollTop > 50);
      setShowScrollTop(scrollTop > 500);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
    setMobileOpen(false);
  };

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const navItems = [
    { name: "Home", action: () => scrollToSection("hero") },
    { name: "Features", action: () => scrollToSection("features") },
    { name: "Products", action: () => scrollToSection("products") },
    { name: "About", action: () => scrollToSection("about") },
    { name: "Contact", action: () => scrollToSection("contact") },
  ];

  return (
    <>
      {/* Main Navigation */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-background/95 backdrop-blur-md border-b border-border/50 shadow-sm"
            : "bg-transparent"
        }`}
      >
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div
              className="flex items-center space-x-3 cursor-pointer"
              onClick={() => scrollToSection("hero")}
            >
              <img src={trishulLogo} alt="Trishul AI Logo" className="w-12 h-12 object-contain" />
              <div>
                <h1 className="text-2xl font-bold text-trishul-red">Trishul AI</h1>
                <p className="text-xs text-trishul-gold font-medium">Three Blades. One Power.</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              {navItems.map((item) => (
                <button
                  key={item.name}
                  onClick={item.action}
                  className="text-foreground/80 hover:text-primary transition-colors font-medium"
                >
                  {item.name}
                </button>
              ))}
            </nav>

            {/* Desktop Actions */}
            <div className="hidden md:flex items-center space-x-3">
              <ThemeToggle />
              <Button variant="outline" onClick={onLoginClick} className="hover:bg-primary/10">
                Tenant Login
              </Button>
              <Button className="bg-gradient-brand hover:shadow-brand">Get Started</Button>
            </div>

            {/* Mobile Menu Button */}
            <div className="md:hidden flex items-center space-x-2">
              <ThemeToggle />
              <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
                <SheetTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <Menu className="w-6 h-6" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="right" className="w-80">
                  <div className="flex flex-col h-full">
                    <div className="flex items-center justify-between pb-6 border-b">
                      <div className="flex items-center space-x-3">
                        <img
                          src={trishulLogo}
                          alt="Trishul AI Logo"
                          className="w-10 h-10 object-contain"
                        />
                        <div>
                          <h3 className="font-bold text-primary">Trishul AI</h3>
                          <p className="text-xs text-primary/80">Three Blades. One Power.</p>
                        </div>
                      </div>
                    </div>

                    <nav className="flex-1 py-6">
                      <div className="space-y-4">
                        {navItems.map((item) => (
                          <button
                            key={item.name}
                            onClick={item.action}
                            className="block w-full text-left text-lg font-medium text-foreground/80 hover:text-primary transition-colors py-2"
                          >
                            {item.name}
                          </button>
                        ))}
                      </div>
                    </nav>

                    <div className="border-t pt-6 space-y-3">
                      <Button
                        variant="outline"
                        onClick={() => {
                          onLoginClick();
                          setMobileOpen(false);
                        }}
                        className="w-full"
                      >
                        Tenant Login
                      </Button>
                      <Button className="w-full bg-gradient-brand hover:shadow-brand">
                        Get Started
                      </Button>
                    </div>
                  </div>
                </SheetContent>
              </Sheet>
            </div>
          </div>
        </div>
      </header>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <Button
          onClick={scrollToTop}
          size="icon"
          className="fixed bottom-6 right-6 z-40 bg-gradient-brand hover:shadow-brand rounded-full shadow-lg"
        >
          <ChevronUp className="w-5 h-5" />
        </Button>
      )}
    </>
  );
};

export default Navigation;
