import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { LuShieldCheck } from "react-icons/lu";
import axios from "axios";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import ActivityIndicator from "@/components/indicators/activity-indicator";
import { AuthContext } from "@/context/auth-context";
import { baseUrl } from "@/api/baseUrl";

interface TwoFactorAuthFormProps {
  userId: string;
  username: string;
  onCancel: () => void;
}

export default function TwoFactorAuthForm({ userId, username, onCancel }: TwoFactorAuthFormProps) {
  const { t } = useTranslation(["components/auth"]);
  const [verificationCode, setVerificationCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { login } = React.useContext(AuthContext);

  const handleVerify = async () => {
    if (!verificationCode || verificationCode.length < 6) return;
    
    setIsLoading(true);
    try {
      await axios.post("/api/2fa/verify", {
        code: verificationCode,
      });
      
      // Get user profile after successful 2FA verification
      const profileRes = await axios.get("/profile", { withCredentials: true });
      
      // Login the user
      login({
        username: profileRes.data.username,
        role: profileRes.data.role || "viewer",
      });
      
      // Redirect to home page
      window.location.href = baseUrl;
    } catch (error) {
      toast.error(t("2fa.errors.verificationFailed"), {
        position: "top-center",
      });
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleVerify();
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <LuShieldCheck className="text-primary h-5 w-5" />
          {t("2fa.login.title")}
        </CardTitle>
        <CardDescription>
          {t("2fa.login.description", { username })}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            {t("2fa.login.enterCode")}
          </p>
          <Input
            type="text"
            placeholder="000000"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            onKeyDown={handleKeyDown}
            maxLength={6}
            className="text-center text-lg"
            autoFocus
          />
        </div>
      </CardContent>
      
      <CardFooter className="flex gap-2">
        <Button 
          variant="outline" 
          onClick={onCancel}
          className="flex-1"
          disabled={isLoading}
        >
          {t("button.back", { ns: "common" })}
        </Button>
        <Button 
          variant="default" 
          onClick={handleVerify}
          disabled={!verificationCode || verificationCode.length < 6 || isLoading}
          className="flex-1"
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <ActivityIndicator className="h-4 w-4" />
              <span>{t("2fa.login.verifying")}</span>
            </div>
          ) : (
            t("2fa.login.verify")
          )}
        </Button>
      </CardFooter>
    </Card>
  );
}
