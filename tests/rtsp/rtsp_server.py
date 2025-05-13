#!/usr/bin/env python3
"""
RTSP Server for Arkos AI Testing

This script provides an RTSP server for streaming test videos for Arkos AI testing.
It uses GStreamer to create RTSP streams from test videos.
"""

import os
import sys
import argparse
import signal
import time
import threading
import logging
import gi
from pathlib import Path

# Add GStreamer modules
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rtsp_server')


class RTSPServer:
    """RTSP server for streaming test videos."""

    def __init__(self, videos_dir: Path, host: str = '0.0.0.0', port: int = 8554):
        """Initialize the RTSP server.
        
        Args:
            videos_dir: Directory containing test videos
            host: Host to bind the server to
            port: Port to bind the server to
        """
        self.videos_dir = videos_dir
        self.host = host
        self.port = port
        self.server = None
        self.loop = None
        self.factory = None
        self.mount_points = None
        self.streams = {}
        self.running = False

        # Initialize GStreamer
        Gst.init(None)

    def start(self):
        """Start the RTSP server."""
        logger.info(f"Starting RTSP server on {self.host}:{self.port}")
        
        # Create GLib main loop
        self.loop = GLib.MainLoop()
        
        # Create RTSP server
        self.server = GstRtspServer.RTSPServer()
        self.server.set_address(self.host)
        self.server.set_service(str(self.port))
        
        # Create mount points
        self.mount_points = self.server.get_mount_points()
        
        # Create factory for standard camera
        self._create_standard_stream()
        
        # Create factory for PTZ camera
        self._create_ptz_stream()
        
        # Create factory for audio camera
        self._create_audio_stream()
        
        # Create factory for multi-object camera
        self._create_multi_object_stream()
        
        # Create factory for license plate camera
        self._create_license_plate_stream()
        
        # Attach server to default context
        self.server.attach(None)
        
        # Set running flag
        self.running = True
        
        # Start main loop
        logger.info("RTSP server started")
        try:
            self.loop.run()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        finally:
            self.stop()

    def stop(self):
        """Stop the RTSP server."""
        if self.running:
            logger.info("Stopping RTSP server")
            
            # Quit main loop
            if self.loop and self.loop.is_running():
                self.loop.quit()
            
            # Unmount all streams
            for path in self.streams.keys():
                self.mount_points.remove_factory(path)
            
            # Clear streams
            self.streams.clear()
            
            # Set running flag
            self.running = False
            
            logger.info("RTSP server stopped")

    def _create_standard_stream(self):
        """Create a standard camera stream."""
        # Get video file
        video_path = self.videos_dir / "standard.mp4"
        if not video_path.exists():
            logger.warning(f"Standard video file not found: {video_path}")
            return
        
        # Create factory
        factory = GstRtspServer.RTSPMediaFactory()
        
        # Set launch string
        launch_str = (
            f"filesrc location={video_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency ! "
            "rtph264pay name=pay0 pt=96"
        )
        factory.set_launch(launch_str)
        
        # Set shared flag
        factory.set_shared(True)
        
        # Mount factory
        path = "/standard"
        self.mount_points.add_factory(path, factory)
        self.streams[path] = factory
        
        logger.info(f"Created standard camera stream: rtsp://{self.host}:{self.port}{path}")

    def _create_ptz_stream(self):
        """Create a PTZ camera stream."""
        # Get video file
        video_path = self.videos_dir / "ptz.mp4"
        if not video_path.exists():
            logger.warning(f"PTZ video file not found: {video_path}")
            return
        
        # Create factory
        factory = GstRtspServer.RTSPMediaFactory()
        
        # Set launch string
        launch_str = (
            f"filesrc location={video_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency ! "
            "rtph264pay name=pay0 pt=96"
        )
        factory.set_launch(launch_str)
        
        # Set shared flag
        factory.set_shared(True)
        
        # Mount factory
        path = "/ptz"
        self.mount_points.add_factory(path, factory)
        self.streams[path] = factory
        
        logger.info(f"Created PTZ camera stream: rtsp://{self.host}:{self.port}{path}")

    def _create_audio_stream(self):
        """Create an audio camera stream."""
        # Get video file
        video_path = self.videos_dir / "audio.mp4"
        audio_path = self.videos_dir.parent / "sample_audio" / "dog_bark.wav"
        if not video_path.exists():
            logger.warning(f"Audio video file not found: {video_path}")
            return
        if not audio_path.exists():
            logger.warning(f"Audio file not found: {audio_path}")
            return
        
        # Create factory
        factory = GstRtspServer.RTSPMediaFactory()
        
        # Set launch string
        launch_str = (
            f"filesrc location={video_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency ! "
            "rtph264pay name=pay0 pt=96 "
            f"filesrc location={audio_path} ! "
            "decodebin ! "
            "audioconvert ! "
            "audioresample ! "
            "opusenc ! "
            "rtpopuspay name=pay1 pt=97"
        )
        factory.set_launch(launch_str)
        
        # Set shared flag
        factory.set_shared(True)
        
        # Mount factory
        path = "/audio"
        self.mount_points.add_factory(path, factory)
        self.streams[path] = factory
        
        logger.info(f"Created audio camera stream: rtsp://{self.host}:{self.port}{path}")

    def _create_multi_object_stream(self):
        """Create a multi-object camera stream."""
        # Get video file
        video_path = self.videos_dir / "multi_object.mp4"
        if not video_path.exists():
            logger.warning(f"Multi-object video file not found: {video_path}")
            return
        
        # Create factory
        factory = GstRtspServer.RTSPMediaFactory()
        
        # Set launch string
        launch_str = (
            f"filesrc location={video_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency ! "
            "rtph264pay name=pay0 pt=96"
        )
        factory.set_launch(launch_str)
        
        # Set shared flag
        factory.set_shared(True)
        
        # Mount factory
        path = "/multi-object"
        self.mount_points.add_factory(path, factory)
        self.streams[path] = factory
        
        logger.info(f"Created multi-object camera stream: rtsp://{self.host}:{self.port}{path}")

    def _create_license_plate_stream(self):
        """Create a license plate camera stream."""
        # Get video file
        video_path = self.videos_dir / "license_plate.mp4"
        if not video_path.exists():
            logger.warning(f"License plate video file not found: {video_path}")
            return
        
        # Create factory
        factory = GstRtspServer.RTSPMediaFactory()
        
        # Set launch string
        launch_str = (
            f"filesrc location={video_path} ! "
            "decodebin ! "
            "videoconvert ! "
            "x264enc tune=zerolatency ! "
            "rtph264pay name=pay0 pt=96"
        )
        factory.set_launch(launch_str)
        
        # Set shared flag
        factory.set_shared(True)
        
        # Mount factory
        path = "/license-plate"
        self.mount_points.add_factory(path, factory)
        self.streams[path] = factory
        
        logger.info(f"Created license plate camera stream: rtsp://{self.host}:{self.port}{path}")


class ONVIFSimulator:
    """ONVIF simulator for PTZ camera."""

    def __init__(self, host: str = '0.0.0.0', port: int = 8556):
        """Initialize the ONVIF simulator.
        
        Args:
            host: Host to bind the server to
            port: Port to bind the server to
        """
        self.host = host
        self.port = port
        self.server = None
        self.running = False

    def start(self):
        """Start the ONVIF simulator."""
        logger.info(f"Starting ONVIF simulator on {self.host}:{self.port}")
        
        # Import required modules
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import xml.etree.ElementTree as ET
        
        # Define request handler
        class ONVIFRequestHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                
                # Parse XML request
                try:
                    root = ET.fromstring(post_data)
                    namespace = root.tag.split('}')[0] + '}'
                    body = root.find('.//{' + namespace + '}Body')
                    
                    if body is not None:
                        # Get request type
                        request_type = None
                        for child in body:
                            request_type = child.tag.split('}')[-1]
                            break
                        
                        # Handle request
                        if request_type == 'GetDeviceInformation':
                            self._handle_get_device_information()
                        elif request_type == 'GetProfiles':
                            self._handle_get_profiles()
                        elif request_type == 'GetStatus':
                            self._handle_get_status()
                        elif request_type == 'ContinuousMove':
                            self._handle_continuous_move()
                        elif request_type == 'Stop':
                            self._handle_stop()
                        elif request_type == 'GotoPreset':
                            self._handle_goto_preset()
                        else:
                            self._handle_unknown_request()
                    else:
                        self._handle_unknown_request()
                except Exception as e:
                    logger.error(f"Error parsing ONVIF request: {e}")
                    self._handle_unknown_request()
            
            def _handle_get_device_information(self):
                """Handle GetDeviceInformation request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <tds:GetDeviceInformationResponse>
                            <tds:Manufacturer>Arkos AI</tds:Manufacturer>
                            <tds:Model>PTZ Simulator</tds:Model>
                            <tds:FirmwareVersion>1.0.0</tds:FirmwareVersion>
                            <tds:SerialNumber>ARKOS-PTZ-SIM-001</tds:SerialNumber>
                            <tds:HardwareId>ARKOS-PTZ-SIM-HW-001</tds:HardwareId>
                        </tds:GetDeviceInformationResponse>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _handle_get_profiles(self):
                """Handle GetProfiles request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <trt:GetProfilesResponse>
                            <trt:Profiles fixed="true" token="Profile_1">
                                <tt:Name>MainStream</tt:Name>
                                <tt:VideoSourceConfiguration token="VideoSourceConfig_1">
                                    <tt:Name>VideoSourceConfig_1</tt:Name>
                                    <tt:UseCount>1</tt:UseCount>
                                    <tt:SourceToken>VideoSource_1</tt:SourceToken>
                                    <tt:Bounds height="720" width="1280" y="0" x="0"/>
                                </tt:VideoSourceConfiguration>
                                <tt:VideoEncoderConfiguration token="VideoEncoderConfig_1">
                                    <tt:Name>VideoEncoderConfig_1</tt:Name>
                                    <tt:UseCount>1</tt:UseCount>
                                    <tt:Encoding>H264</tt:Encoding>
                                    <tt:Resolution>
                                        <tt:Width>1280</tt:Width>
                                        <tt:Height>720</tt:Height>
                                    </tt:Resolution>
                                    <tt:Quality>5</tt:Quality>
                                    <tt:RateControl>
                                        <tt:FrameRateLimit>30</tt:FrameRateLimit>
                                        <tt:EncodingInterval>1</tt:EncodingInterval>
                                        <tt:BitrateLimit>4096</tt:BitrateLimit>
                                    </tt:RateControl>
                                    <tt:H264>
                                        <tt:GovLength>30</tt:GovLength>
                                        <tt:H264Profile>Main</tt:H264Profile>
                                    </tt:H264>
                                </tt:VideoEncoderConfiguration>
                                <tt:PTZConfiguration token="PTZConfig_1">
                                    <tt:Name>PTZConfig_1</tt:Name>
                                    <tt:UseCount>1</tt:UseCount>
                                    <tt:NodeToken>PTZNode_1</tt:NodeToken>
                                </tt:PTZConfiguration>
                            </trt:Profiles>
                        </trt:GetProfilesResponse>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _handle_get_status(self):
                """Handle GetStatus request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <tptz:GetStatusResponse>
                            <tptz:PTZStatus>
                                <tt:Position>
                                    <tt:PanTilt x="0.0" y="0.0"/>
                                    <tt:Zoom x="0.0"/>
                                </tt:Position>
                                <tt:MoveStatus>
                                    <tt:PanTilt>IDLE</tt:PanTilt>
                                    <tt:Zoom>IDLE</tt:Zoom>
                                </tt:MoveStatus>
                                <tt:Error>false</tt:Error>
                                <tt:UtcTime>2023-05-13T12:00:00Z</tt:UtcTime>
                            </tptz:PTZStatus>
                        </tptz:GetStatusResponse>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _handle_continuous_move(self):
                """Handle ContinuousMove request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <tptz:ContinuousMoveResponse>
                        </tptz:ContinuousMoveResponse>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _handle_stop(self):
                """Handle Stop request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <tptz:StopResponse>
                        </tptz:StopResponse>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _handle_goto_preset(self):
                """Handle GotoPreset request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <tptz:GotoPresetResponse>
                        </tptz:GotoPresetResponse>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _handle_unknown_request(self):
                """Handle unknown request."""
                response = """<?xml version="1.0" encoding="UTF-8"?>
                <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://www.w3.org/2003/05/soap-envelope">
                    <SOAP-ENV:Body>
                        <SOAP-ENV:Fault>
                            <SOAP-ENV:Code>
                                <SOAP-ENV:Value>SOAP-ENV:Sender</SOAP-ENV:Value>
                            </SOAP-ENV:Code>
                            <SOAP-ENV:Reason>
                                <SOAP-ENV:Text xml:lang="en">Unknown request</SOAP-ENV:Text>
                            </SOAP-ENV:Reason>
                        </SOAP-ENV:Fault>
                    </SOAP-ENV:Body>
                </SOAP-ENV:Envelope>
                """
                self._send_response(response)
            
            def _send_response(self, response):
                """Send SOAP response."""
                self.send_response(200)
                self.send_header('Content-Type', 'application/soap+xml; charset=utf-8')
                self.send_header('Content-Length', str(len(response)))
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
        
        # Create server
        self.server = HTTPServer((self.host, self.port), ONVIFRequestHandler)
        
        # Set running flag
        self.running = True
        
        # Start server in a thread
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        logger.info("ONVIF simulator started")

    def stop(self):
        """Stop the ONVIF simulator."""
        if self.running:
            logger.info("Stopping ONVIF simulator")
            
            # Shutdown server
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            
            # Set running flag
            self.running = False
            
            logger.info("ONVIF simulator stopped")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="RTSP server for Arkos AI testing")
    parser.add_argument("--videos-dir", default="tests/fixtures/sample_videos", help="Directory containing test videos")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8554, help="Port to bind the server to")
    parser.add_argument("--onvif-port", type=int, default=8556, help="Port to bind the ONVIF simulator to")
    args = parser.parse_args()
    
    # Create videos directory if it doesn't exist
    videos_dir = Path(args.videos_dir)
    videos_dir.mkdir(exist_ok=True, parents=True)
    
    # Create RTSP server
    rtsp_server = RTSPServer(videos_dir, args.host, args.port)
    
    # Create ONVIF simulator
    onvif_simulator = ONVIFSimulator(args.host, args.onvif_port)
    
    # Handle signals
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        rtsp_server.stop()
        onvif_simulator.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start ONVIF simulator
    onvif_simulator.start()
    
    # Start RTSP server
    rtsp_server.start()


if __name__ == "__main__":
    main()
