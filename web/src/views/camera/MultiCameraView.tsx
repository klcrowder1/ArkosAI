import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { CameraConfig, ArkosConfig } from "@/types/arkosConfig";
import { ResponsiveLayout, ResponsiveContainer, ResponsiveGrid } from "@/components/layout/ResponsiveLayout";
import { Button } from "@/components/ui/button";
import { IoMdArrowRoundBack } from "react-icons/io";
import { LuGrid, LuLayoutDashboard } from "react-icons/lu";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { isDesktop, isMobile } from "react-device-detect";
import LivePlayer from "@/components/player/LivePlayer";
import { LivePlayerMode } from "@/types/live";

type MultiCameraViewProps = {
  config?: ArkosConfig;
  cameras: CameraConfig[];
  groupName?: string;
};

export default function MultiCameraView({
  config,
  cameras,
  groupName = "All Cameras",
}: MultiCameraViewProps) {
  const { t } = useTranslation(["views/camera"]);
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Layout state
  const [layout, setLayout] = useState<"grid" | "dashboard">("grid");
  const [columns, setColumns] = useState<number>(2);
  
  // Adjust columns based on screen size
  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width < 640) {
        setColumns(1);
      } else if (width < 1024) {
        setColumns(2);
      } else if (width < 1536) {
        setColumns(3);
      } else {
        setColumns(4);
      }
    };
    
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);
  
  // Camera visibility tracking
  const [visibleCameras, setVisibleCameras] = useState<string[]>([]);
  const visibleCameraObserver = useRef<IntersectionObserver | null>(null);
  
  useEffect(() => {
    const visibleCameras = new Set<string>();
    visibleCameraObserver.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const camera = (entry.target as HTMLElement).dataset.camera;

          if (!camera) {
            return;
          }

          if (entry.isIntersecting) {
            visibleCameras.add(camera);
          } else {
            visibleCameras.delete(camera);
          }

          setVisibleCameras([...visibleCameras]);
        });
      },
      { threshold: 0.5 },
    );

    return () => {
      visibleCameraObserver.current?.disconnect();
    };
  }, []);
  
  const cameraRef = useCallback(
    (node: HTMLElement | null) => {
      if (!visibleCameraObserver.current) {
        return;
      }

      try {
        if (node) visibleCameraObserver.current.observe(node);
      } catch (e) {
        // no op
      }
    },
    [visibleCameraObserver.current],
  );
  
  // Window visibility tracking for optimizing video playback
  const [windowVisible, setWindowVisible] = useState(true);
  
  useEffect(() => {
    const handleVisibilityChange = () => {
      setWindowVisible(document.visibilityState === "visible");
    };
    
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, []);
  
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
            
            <h1 className="text-xl font-semibold">{groupName}</h1>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={layout === "grid" ? "secondary" : "outline"}
              size="sm"
              onClick={() => setLayout("grid")}
              className="flex items-center gap-2"
            >
              <LuGrid className="size-4" />
              {isDesktop && <span>{t("layout.grid")}</span>}
            </Button>
            
            <Button
              variant={layout === "dashboard" ? "secondary" : "outline"}
              size="sm"
              onClick={() => setLayout("dashboard")}
              className="flex items-center gap-2"
            >
              <LuLayoutDashboard className="size-4" />
              {isDesktop && <span>{t("layout.dashboard")}</span>}
            </Button>
          </div>
        </div>
        
        {/* Camera Grid */}
        {layout === "grid" && (
          <ResponsiveGrid columns={columns as 1 | 2 | 3 | 4} gap="medium" className="flex-1">
            {cameras.map((camera) => (
              <div 
                key={camera.name}
                className="aspect-video relative"
                onClick={() => navigate(`/camera/${camera.name}`)}
              >
                <LivePlayer
                  cameraRef={cameraRef}
                  className="rounded-lg bg-black md:rounded-2xl"
                  windowVisible={windowVisible && visibleCameras.includes(camera.name)}
                  cameraConfig={camera}
                  preferredLiveMode="mse"
                  autoLive={true}
                  showStillWithoutActivity={true}
                  useWebGL={false}
                  playInBackground={false}
                  showStats={false}
                  streamName={Object.values(camera.live.streams)[0] || ""}
                  playAudio={false}
                />
                <div className="absolute bottom-2 left-2 bg-black/60 px-2 py-1 rounded text-white text-sm">
                  {camera.name.replace(/_/g, ' ')}
                </div>
              </div>
            ))}
          </ResponsiveGrid>
        )}
        
        {/* Dashboard Layout */}
        {layout === "dashboard" && (
          <div className="flex-1 relative" ref={containerRef}>
            {/* This would be replaced with a DraggableGridLayout component */}
            <div className="absolute inset-0 flex items-center justify-center">
              <p className="text-lg">Dashboard layout would go here</p>
            </div>
          </div>
        )}
      </ResponsiveLayout>
    </ResponsiveContainer>
  );
}

// Helper function for camera ref callback
function useCallback<T extends (...args: any[]) => any>(
  callback: T,
  deps: React.DependencyList
): T {
  return React.useCallback(callback, deps);
}
