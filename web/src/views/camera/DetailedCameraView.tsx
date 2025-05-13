import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { CameraConfig, ArkosConfig } from "@/types/arkosConfig";
import { ResponsiveLayout, ResponsiveContainer } from "@/components/layout/ResponsiveLayout";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { IoMdArrowRoundBack } from "react-icons/io";
import { LuCalendar, LuClock, LuSettings, LuInfo, LuActivity, LuVideo } from "react-icons/lu";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { isDesktop, isMobile } from "react-device-detect";
import LivePlayer from "@/components/player/LivePlayer";
import { LivePlayerMode } from "@/types/live";

type DetailedCameraViewProps = {
  config?: ArkosConfig;
  camera: CameraConfig;
};

export default function DetailedCameraView({
  config,
  camera,
}: DetailedCameraViewProps) {
  const { t } = useTranslation(["views/camera"]);
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Camera state
  const [activeTab, setActiveTab] = useState<string>("live");
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  
  // Window visibility tracking for optimizing video playback
  const [windowVisible, setWindowVisible] = useState(true);
  
  useEffect(() => {
    const handleVisibilityChange = () => {
      setWindowVisible(document.visibilityState === "visible");
    };
    
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);
  
  // Camera settings
  const streamName = useMemo(() => {
    return Object.values(camera.live.streams)[0] || "";
  }, [camera]);
  
  // Camera stats
  const [cameraStats, setCameraStats] = useState({
    uptime: "3 days, 4 hours",
    fps: 15,
    resolution: `${camera.detect.width}x${camera.detect.height}`,
    bandwidth: "1.2 Mbps",
    storage: "45.3 GB",
    events: {
      today: 12,
      week: 87,
      month: 342
    }
  });
  
  return (
    <ResponsiveContainer className="h-full" maxWidth="full">
      <ResponsiveLayout className="h-full" direction="column" gap="medium">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Button
              className="flex items-center gap-2.5 rounded-lg"
              aria-label={t("label.back", { ns: "common" })}
              size="sm"
              onClick={() => navigate(-1)}
            >
              <IoMdArrowRoundBack className="size-5 text-secondary-foreground" />
              {isDesktop && (
                <div className="text-primary">
                  {t("button.back", { ns: "common" })}
                </div>
              )}
            </Button>
            
            <h1 className="text-xl font-semibold">{camera.name.replace(/_/g, ' ')}</h1>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate(`/settings?camera=${camera.name}`)}
              className="flex items-center gap-2"
            >
              <LuSettings className="size-4" />
              {isDesktop && <span>{t("settings")}</span>}
            </Button>
          </div>
        </div>
        
        {/* Tabs */}
        <Tabs defaultValue="live" value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="grid grid-cols-4 w-full max-w-md mx-auto">
            <TabsTrigger value="live" className="flex items-center gap-1">
              <LuVideo className="size-4" />
              <span>{t("tabs.live")}</span>
            </TabsTrigger>
            <TabsTrigger value="recordings" className="flex items-center gap-1">
              <LuCalendar className="size-4" />
              <span>{t("tabs.recordings")}</span>
            </TabsTrigger>
            <TabsTrigger value="events" className="flex items-center gap-1">
              <LuActivity className="size-4" />
              <span>{t("tabs.events")}</span>
            </TabsTrigger>
            <TabsTrigger value="info" className="flex items-center gap-1">
              <LuInfo className="size-4" />
              <span>{t("tabs.info")}</span>
            </TabsTrigger>
          </TabsList>
          
          {/* Live Tab */}
          <TabsContent value="live" className="flex-1 flex flex-col">
            <div 
              ref={containerRef}
              className="relative aspect-video w-full bg-black rounded-lg overflow-hidden"
            >
              <LivePlayer
                className="rounded-lg bg-black md:rounded-2xl"
                windowVisible={windowVisible && activeTab === "live"}
                cameraConfig={camera}
                preferredLiveMode="mse"
                autoLive={true}
                showStillWithoutActivity={true}
                useWebGL={false}
                playInBackground={false}
                showStats={false}
                streamName={streamName}
                playAudio={false}
                containerRef={containerRef}
              />
            </div>
            
            {/* Camera Controls */}
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-2">
              <Card>
                <CardHeader className="p-3">
                  <CardTitle className="text-sm">{t("controls.motion")}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{t("status")}:</span>
                    <span className="text-sm font-medium text-green-500">{t("enabled")}</span>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="p-3">
                  <CardTitle className="text-sm">{t("controls.recording")}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{t("status")}:</span>
                    <span className="text-sm font-medium text-green-500">{t("enabled")}</span>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="p-3">
                  <CardTitle className="text-sm">{t("controls.detection")}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{t("status")}:</span>
                    <span className="text-sm font-medium text-green-500">{t("enabled")}</span>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="p-3">
                  <CardTitle className="text-sm">{t("controls.snapshots")}</CardTitle>
                </CardHeader>
                <CardContent className="p-3 pt-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">{t("status")}:</span>
                    <span className="text-sm font-medium text-green-500">{t("enabled")}</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          {/* Recordings Tab */}
          <TabsContent value="recordings" className="flex-1">
            <div className="h-full flex items-center justify-center">
              <p>{t("recordings.notImplemented")}</p>
            </div>
          </TabsContent>
          
          {/* Events Tab */}
          <TabsContent value="events" className="flex-1">
            <div className="h-full flex items-center justify-center">
              <p>{t("events.notImplemented")}</p>
            </div>
          </TabsContent>
          
          {/* Info Tab */}
          <TabsContent value="info" className="flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle>{t("info.general")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.name")}:</dt>
                      <dd>{camera.name}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.type")}:</dt>
                      <dd>{camera.type}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.resolution")}:</dt>
                      <dd>{cameraStats.resolution}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.fps")}:</dt>
                      <dd>{cameraStats.fps}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.uptime")}:</dt>
                      <dd>{cameraStats.uptime}</dd>
                    </div>
                  </dl>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t("info.storage")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.totalStorage")}:</dt>
                      <dd>{cameraStats.storage}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.retentionDays")}:</dt>
                      <dd>{camera.record.retain.days}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.retentionMode")}:</dt>
                      <dd>{camera.record.retain.mode}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.bandwidth")}:</dt>
                      <dd>{cameraStats.bandwidth}</dd>
                    </div>
                  </dl>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t("info.events")}</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.eventsToday")}:</dt>
                      <dd>{cameraStats.events.today}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.eventsWeek")}:</dt>
                      <dd>{cameraStats.events.week}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">{t("info.eventsMonth")}:</dt>
                      <dd>{cameraStats.events.month}</dd>
                    </div>
                  </dl>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>{t("info.zones")}</CardTitle>
                </CardHeader>
                <CardContent>
                  {Object.keys(camera.zones).length > 0 ? (
                    <ul className="space-y-1">
                      {Object.keys(camera.zones).map((zoneName) => (
                        <li key={zoneName} className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{
                              backgroundColor: `rgb(${camera.zones[zoneName].color.join(',')})`
                            }}
                          />
                          <span>{zoneName}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>{t("info.noZones")}</p>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </ResponsiveLayout>
    </ResponsiveContainer>
  );
}
