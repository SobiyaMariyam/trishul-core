import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";

interface LoginDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const LoginDialog = ({ open, onOpenChange }: LoginDialogProps) => {
  const [email, setEmail] = useState("");
  const [organization, setOrganization] = useState("");
  const { toast } = useToast();
  const emailInputRef = useRef<HTMLInputElement>(null);

  // Define handleCancel early to use in useEffect
  const handleCancel = useCallback(() => {
    onOpenChange(false);
    setEmail("");
    setOrganization("");
  }, [onOpenChange]);

  // Focus management
  useEffect(() => {
    if (open && emailInputRef.current) {
      // Delay to ensure dialog is rendered
      setTimeout(() => {
        emailInputRef.current?.focus();
      }, 100);
    }
  }, [open]);

  // ESC key handling
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape" && open) {
        handleCancel();
      }
    };

    if (open) {
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open, handleCancel]);

  const handleSave = () => {
    if (!email || !organization) {
      toast({
        title: "Missing Information",
        description: "Please fill in both email and organization name.",
        variant: "destructive",
      });
      return;
    }

    // Store tenant info in localStorage
    const tenantInfo = { email, organization, timestamp: Date.now() };
    localStorage.setItem("trishul-tenant", JSON.stringify(tenantInfo));

    toast({
      title: "Tenant Information Saved",
      description: `Welcome ${organization}! Your information has been stored locally.`,
    });

    onOpenChange(false);
    setEmail("");
    setOrganization("");
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") {
      handleSave();
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="sm:max-w-md"
        aria-labelledby="login-dialog-title"
        aria-describedby="login-dialog-description"
      >
        <DialogHeader>
          <DialogTitle id="login-dialog-title" className="text-xl">
            Tenant Login
          </DialogTitle>
          <DialogDescription id="login-dialog-description" className="text-base">
            Enter your tenant identity to access Trishul AI modules. This information is stored
            locally for personalization and not sent to the server yet.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 pt-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email (tenant email ID)</Label>
            <Input
              ref={emailInputRef}
              id="email"
              type="email"
              placeholder="admin@yourcompany.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={handleKeyDown}
              aria-describedby="email-description"
              aria-required="true"
            />
            <div id="email-description" className="sr-only">
              Enter your organization's admin email address
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="organization">Organization Name</Label>
            <Input
              id="organization"
              placeholder="Your Company Ltd"
              value={organization}
              onChange={(e) => setOrganization(e.target.value)}
              onKeyDown={handleKeyDown}
              aria-describedby="org-description"
              aria-required="true"
            />
            <div id="org-description" className="sr-only">
              Enter your organization or company name
            </div>
          </div>
        </div>
        <div className="flex justify-end space-x-2 pt-4">
          <Button variant="outline" onClick={handleCancel} aria-label="Cancel and close dialog">
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={!email || !organization}
            aria-label="Save tenant information"
          >
            Save
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
