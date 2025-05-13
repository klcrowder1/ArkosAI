import { useEffect, useMemo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { CameraConfig, ArkosConfig } from "@/types/arkosConfig";
import { ResponsiveLayout, ResponsiveContainer } from "@/components/layout/ResponsiveLayout";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { format } from "date-fns";
import { IoMdArrowRoundBack } from "react-icons/io";
import { LuCalendar, LuClock, LuPlay, LuPause, LuSkipBack, LuSkipForward } from "react-icons/lu";
import { useNavigate } from "react-router-dom";
import { cn } from "@/lib/utils";
import { isDesktop, isMobile } from "react-device-detect";

type TimelineViewProps = {
  config?: ArkosConfig;
  camera: CameraConfig;
  date?: Date;
};

export default function TimelineView({
  config,
  camera,
  date = new Date(),
}: TimelineViewProps) {
  const { t } = useTranslation(["views/timeline"]);
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Timeline state
  const [currentTime, setCurrentTime] = useState<Date>(date);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);
  const [timelinePosition, setTimelinePosition] = useState<number>(0);
  
  // Recording segments (this would be fetched from the API in a real implementation)
  const recordingSegments = useMemo(() => {
    // Mock data - in a real implementation, this would be fetched from the API
    return [
      { startTime: new Date(date.getTime() - 3600000), endTime: new Date(date.getTime() - 3300000), type: 'motion' },
      { startTime: new Date(date.getTime() - 2400000), endTime: new Date(date.getTime() - 2100000), type: 'alert' },
      { startTime: new Date(date.getTime() - 1200000), endTime: new Date(date.getTime() - 900000), type: 'continuous' },
    ];
  }, [date]);
  
  // Handle playback
  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentTime(prev => new Date(prev.getTime() + 1000 * playbackSpeed));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isPlaying, playbackSpeed]);
  
  // Update timeline position when current time changes
  useEffect(() => {
    // Calculate position as percentage of day
    const startOfDay = new Date(currentTime);
    startOfDay.setHours(0, 0, 0, 0);
    const msInDay = 24 * 60 * 60 * 1000;
    const msSinceStartOfDay = currentTime.getTime() - startOfDay.getTime();
    const position = (msSinceStartOfDay / msInDay) * 100;
    setTimelinePosition(position);
  }, [currentTime]);
  
  // Handle timeline scrubbing
  const handleTimelineChange = (value: number[]) => {
    const position = value[0];
    setTimelinePosition(position);
    
    // Calculate new time based on position
    const startOfDay = new Date(currentTime);
    startOfDay.setHours(0, 0, 0, 0);
    const msInDay = 24 * 60 * 60 * 1000;
    const newTime = new Date(startOfDay.getTime() + (position / 100) * msInDay);
    setCurrentTime(newTime);
  };
  
  // Handle playback controls
  const togglePlayback = () => setIsPlaying(!isPlaying);
  const skipForward = () => setCurrentTime(new Date(currentTime.getTime() + 30000)); // Skip 30 seconds
  const skipBackward = () => setCurrentTime(new Date(currentTime.getTime() - 30000)); // Skip 30 seconds back
  
  return (
    <ResponsiveContainer className="h-full" maxWidth="full">
      <ResponsiveLayout className="h-full" direction="column" gap="medium">
        {/* Header */}
        <div className="flex items-center justify-between">
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
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" className="flex items-center gap-2">
              <LuCalendar className="size-4" />
              <span>{format(currentTime, 'yyyy-MM-dd')}</span>
            </Button>
            <Button variant="outline" size="sm" className="flex items-center gap-2">
              <LuClock className="size-4" />
              <span>{format(currentTime, 'HH:mm:ss')}</span>
            </Button>
          </div>
        </div>
        
        {/* Video Player Area */}
        <div 
          ref={containerRef}
          className="relative aspect-video w-full bg-black rounded-lg overflow-hidden"
        >
          {/* This would be replaced with an actual video player component */}
          <div className="absolute inset-0 flex items-center justify-center text-white">
            <p className="text-lg">Camera: {camera.name}</p>
          </div>
        </div>
        
        {/* Playback Controls */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-center gap-4">
            <Button 
              variant="ghost" 
              size="icon"
              onClick={skipBackward}
              aria-label={t("controls.skipBackward")}
            >
              <LuSkipBack className="size-6" />
            </Button>
            
            <Button 
              variant="primary" 
              size="icon"
              onClick={togglePlayback}
              aria-label={isPlaying ? t("controls.pause") : t("controls.play")}
              className="h-12 w-12 rounded-full"
            >
              {isPlaying ? (
                <LuPause className="size-6" />
              ) : (
                <LuPlay className="size-6" />
              )}
            </Button>
            
            <Button 
              variant="ghost" 
              size="icon"
              onClick={skipForward}
              aria-label={t("controls.skipForward")}
            >
              <LuSkipForward className="size-6" />
            </Button>
          </div>
          
          {/* Timeline */}
          <div className="relative mt-2">
            <div className="absolute inset-0 flex">
              {recordingSegments.map((segment, index) => {
                const startOfDay = new Date(date);
                startOfDay.setHours(0, 0, 0, 0);
                const msInDay = 24 * 60 * 60 * 1000;
                
                const startPosition = ((segment.startTime.getTime() - startOfDay.getTime()) / msInDay) * 100;
                const endPosition = ((segment.endTime.getTime() - startOfDay.getTime()) / msInDay) * 100;
                const width = endPosition - startPosition;
                
                return (
                  <div 
                    key={index}
                    className={cn(
                      "absolute h-full",
                      segment.type === 'motion' ? "bg-blue-500/50" : 
                      segment.type === 'alert' ? "bg-red-500/50" : 
                      "bg-green-500/50"
                    )}
                    style={{
                      left: `${startPosition}%`,
                      width: `${width}%`
                    }}
                  />
                );
              })}
            </div>
            
            <Slider
              value={[timelinePosition]}
              min={0}
              max={100}
              step={0.1}
              onValueChange={handleTimelineChange}
              className="z-10"
            />
          </div>
          
          {/* Playback Speed */}
          <div className="flex items-center justify-center gap-2 mt-2">
            <Button 
              variant={playbackSpeed === 0.5 ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setPlaybackSpeed(0.5)}
            >
              0.5x
            </Button>
            <Button 
              variant={playbackSpeed === 1 ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setPlaybackSpeed(1)}
            >
              1x
            </Button>
            <Button 
              variant={playbackSpeed === 2 ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setPlaybackSpeed(2)}
            >
              2x
            </Button>
            <Button 
              variant={playbackSpeed === 4 ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setPlaybackSpeed(4)}
            >
              4x
            </Button>
          </div>
        </div>
      </ResponsiveLayout>
    </ResponsiveContainer>
  );
}
