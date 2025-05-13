import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LuShieldCheck, LuShieldOff, LuAlertCircle, LuCheckCircle2 } from "react-icons/lu";
import axios from "axios";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import ActivityIndicator from "@/components/indicators/activity-indicator";

interface TwoFactorAuthProps {
  userId: string;
  onStatusChange?: (enabled: boolean) => void;
}

export default function TwoFactorAuth({ userId, onStatusChange }: TwoFactorAuthProps) {
  const { t } = useTranslation(["components/auth"]);
  const [status, setStatus] = useState<{ enabled: boolean; device: any | null }>({ enabled: false, device: null });
  const [isLoading, setIsLoading] = useState(true);
  const [setupData, setSetupData] = useState<{ secret: string; qr_code: string; device_id: string } | null>(null);
  const [verificationCode, setVerificationCode] = useState("");
  const [disableCode, setDisableCode] = useState("");
  const [activeTab, setActiveTab] = useState("status");

  // Fetch 2FA status
  const fetchStatus = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get("/api/2fa/status");
      setStatus(response.data);
      if (onStatusChange) {
        onStatusChange(response.data.enabled);
      }
    } catch (error) {
      toast.error(t("2fa.errors.statusFailed"), {
        position: "top-center",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Setup 2FA
  const setupTwoFactor = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post("/api/2fa/setup");
      setSetupData(response.data);
      setActiveTab("setup");
    } catch (error) {
      toast.error(t("2fa.errors.setupFailed"), {
        position: "top-center",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Verify 2FA setup
  const verifySetup = async () => {
    if (!setupData) return;
    
    try {
      setIsLoading(true);
      await axios.post("/api/2fa/verify-setup", {
        device_id: setupData.device_id,
        code: verificationCode,
      });
      
      toast.success(t("2fa.success.setupComplete"), {
        position: "top-center",
      });
      
      setVerificationCode("");
      setSetupData(null);
      fetchStatus();
      setActiveTab("status");
    } catch (error) {
      toast.error(t("2fa.errors.verificationFailed"), {
        position: "top-center",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Disable 2FA
  const disableTwoFactor = async () => {
    try {
      setIsLoading(true);
      await axios.post("/api/2fa/disable", {
        code: disableCode,
      });
      
      toast.success(t("2fa.success.disabled"), {
        position: "top-center",
      });
      
      setDisableCode("");
      fetchStatus();
      setActiveTab("status");
    } catch (error) {
      toast.error(t("2fa.errors.disableFailed"), {
        position: "top-center",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Load status on component mount
  useEffect(() => {
    fetchStatus();
  }, []);

  if (isLoading && !setupData && !status.device) {
    return (
      <div className="flex justify-center items-center p-8">
        <ActivityIndicator />
      </div>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {status.enabled ? (
            <LuShieldCheck className="text-success h-5 w-5" />
          ) : (
            <LuShieldOff className="text-muted-foreground h-5 w-5" />
          )}
          {t("2fa.title")}
        </CardTitle>
        <CardDescription>
          {t("2fa.description")}
        </CardDescription>
      </CardHeader>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="status">{t("2fa.tabs.status")}</TabsTrigger>
          {status.enabled ? (
            <TabsTrigger value="disable">{t("2fa.tabs.disable")}</TabsTrigger>
          ) : (
            <TabsTrigger value="setup">{t("2fa.tabs.setup")}</TabsTrigger>
          )}
        </TabsList>
        
        <TabsContent value="status">
          <CardContent className="pt-6">
            {status.enabled ? (
              <Alert variant="success" className="bg-success/10 border-success/20">
                <LuCheckCircle2 className="h-4 w-4 text-success" />
                <AlertTitle>{t("2fa.status.enabled.title")}</AlertTitle>
                <AlertDescription>
                  {t("2fa.status.enabled.description")}
                </AlertDescription>
              </Alert>
            ) : (
              <Alert variant="warning" className="bg-warning/10 border-warning/20">
                <LuAlertCircle className="h-4 w-4 text-warning" />
                <AlertTitle>{t("2fa.status.disabled.title")}</AlertTitle>
                <AlertDescription>
                  {t("2fa.status.disabled.description")}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
          <CardFooter>
            {status.enabled ? (
              <Button 
                variant="destructive" 
                onClick={() => setActiveTab("disable")}
                className="w-full"
              >
                {t("2fa.actions.disable")}
              </Button>
            ) : (
              <Button 
                variant="default" 
                onClick={setupTwoFactor}
                className="w-full"
              >
                {t("2fa.actions.enable")}
              </Button>
            )}
          </CardFooter>
        </TabsContent>
        
        <TabsContent value="setup">
          <CardContent className="space-y-4 pt-6">
            {setupData ? (
              <>
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">{t("2fa.setup.step1")}</h3>
                  <p className="text-sm text-muted-foreground">
                    {t("2fa.setup.scanQrCode")}
                  </p>
                  <div className="flex justify-center my-4">
                    <img 
                      src={`data:image/png;base64,${setupData.qr_code}`} 
                      alt="QR Code for 2FA setup" 
                      className="border border-border p-2 rounded-md"
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">{t("2fa.setup.step2")}</h3>
                  <p className="text-sm text-muted-foreground">
                    {t("2fa.setup.enterCode")}
                  </p>
                  <div className="flex gap-2">
                    <Input
                      type="text"
                      placeholder="000000"
                      value={verificationCode}
                      onChange={(e) => setVerificationCode(e.target.value)}
                      maxLength={6}
                      className="text-center text-lg"
                    />
                  </div>
                </div>
                
                <div className="pt-2">
                  <Alert variant="info" className="bg-info/10 border-info/20">
                    <AlertTitle>{t("2fa.setup.backupTitle")}</AlertTitle>
                    <AlertDescription>
                      {t("2fa.setup.backupDescription")}
                      <div className="mt-2 p-2 bg-muted rounded-md font-mono text-xs break-all">
                        {setupData.secret}
                      </div>
                    </AlertDescription>
                  </Alert>
                </div>
              </>
            ) : (
              <div className="flex justify-center items-center p-8">
                <ActivityIndicator />
              </div>
            )}
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={() => {
                setActiveTab("status");
                setSetupData(null);
              }}
              className="flex-1"
            >
              {t("button.cancel", { ns: "common" })}
            </Button>
            <Button 
              variant="default" 
              onClick={verifySetup}
              disabled={!verificationCode || verificationCode.length < 6}
              className="flex-1"
            >
              {t("2fa.actions.verify")}
            </Button>
          </CardFooter>
        </TabsContent>
        
        <TabsContent value="disable">
          <CardContent className="space-y-4 pt-6">
            <div className="space-y-2">
              <h3 className="text-lg font-medium">{t("2fa.disable.title")}</h3>
              <p className="text-sm text-muted-foreground">
                {t("2fa.disable.description")}
              </p>
              <div className="flex gap-2">
                <Input
                  type="text"
                  placeholder="000000"
                  value={disableCode}
                  onChange={(e) => setDisableCode(e.target.value)}
                  maxLength={6}
                  className="text-center text-lg"
                />
              </div>
            </div>
            
            <Alert variant="warning" className="bg-warning/10 border-warning/20">
              <LuAlertCircle className="h-4 w-4 text-warning" />
              <AlertTitle>{t("2fa.disable.warningTitle")}</AlertTitle>
              <AlertDescription>
                {t("2fa.disable.warningDescription")}
              </AlertDescription>
            </Alert>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={() => setActiveTab("status")}
              className="flex-1"
            >
              {t("button.cancel", { ns: "common" })}
            </Button>
            <Button 
              variant="destructive" 
              onClick={disableTwoFactor}
              disabled={!disableCode || disableCode.length < 6}
              className="flex-1"
            >
              {t("2fa.actions.confirmDisable")}
            </Button>
          </CardFooter>
        </TabsContent>
      </Tabs>
    </Card>
  );
}
