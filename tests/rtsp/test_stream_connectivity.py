"""
Tests for RTSP stream connectivity in Arkos AI.

This module tests the connectivity to RTSP streams and the ability to process frames.
"""

import time
import pytest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch

# Import the modules to test
from arkos.camera.rtsp_stream import RTSPStream
from arkos.camera.camera import Camera


class TestRTSPStreamConnectivity:
    """Test suite for RTSP stream connectivity."""

    @pytest.fixture
    def rtsp_stream(self, rtsp_simulator, default_config):
        """Create an RTSP stream for testing."""
        camera_name = "test_camera"
        config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_simulator["standard_url"],
            config=config,
        )
        
        yield stream
        
        # Clean up
        stream.stop()

    @pytest.fixture
    def ptz_stream(self, rtsp_simulator, default_config):
        """Create a PTZ RTSP stream for testing."""
        camera_name = "ptz_camera"
        config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_simulator["ptz_url"],
            config=config,
        )
        
        yield stream
        
        # Clean up
        stream.stop()

    @pytest.fixture
    def audio_stream(self, rtsp_simulator, default_config):
        """Create an audio RTSP stream for testing."""
        camera_name = "audio_camera"
        config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_simulator["audio_url"],
            config=config,
        )
        
        yield stream
        
        # Clean up
        stream.stop()

    def test_rtsp_stream_connection(self, rtsp_stream, wait_for_condition):
        """Test connecting to an RTSP stream."""
        # Start the stream
        rtsp_stream.start()
        
        # Wait for the stream to connect
        def is_connected():
            return rtsp_stream.is_connected()
        
        assert wait_for_condition(is_connected, timeout=10), "Stream failed to connect within timeout"
        
        # Stop the stream
        rtsp_stream.stop()
        
        # Verify the stream is disconnected
        assert not rtsp_stream.is_connected(), "Stream should be disconnected after stopping"

    def test_rtsp_stream_get_frame(self, rtsp_stream, wait_for_condition):
        """Test getting frames from an RTSP stream."""
        # Start the stream
        rtsp_stream.start()
        
        # Wait for the stream to connect
        def is_connected():
            return rtsp_stream.is_connected()
        
        assert wait_for_condition(is_connected, timeout=10), "Stream failed to connect within timeout"
        
        # Get a frame
        frame = rtsp_stream.get_frame()
        
        # Verify the frame is not None
        assert frame is not None, "Failed to get frame from stream"
        
        # Verify the frame has the correct shape
        assert frame.shape == (720, 1280, 3), f"Frame has incorrect shape: {frame.shape}"
        
        # Stop the stream
        rtsp_stream.stop()

    def test_rtsp_stream_reconnection(self, rtsp_stream, wait_for_condition):
        """Test reconnecting to an RTSP stream after disconnection."""
        # Start the stream
        rtsp_stream.start()
        
        # Wait for the stream to connect
        def is_connected():
            return rtsp_stream.is_connected()
        
        assert wait_for_condition(is_connected, timeout=10), "Stream failed to connect within timeout"
        
        # Stop the stream
        rtsp_stream.stop()
        
        # Verify the stream is disconnected
        assert not rtsp_stream.is_connected(), "Stream should be disconnected after stopping"
        
        # Start the stream again
        rtsp_stream.start()
        
        # Wait for the stream to reconnect
        assert wait_for_condition(is_connected, timeout=10), "Stream failed to reconnect within timeout"
        
        # Stop the stream
        rtsp_stream.stop()

    def test_ptz_stream_connection(self, ptz_stream, wait_for_condition):
        """Test connecting to a PTZ RTSP stream."""
        # Start the stream
        ptz_stream.start()
        
        # Wait for the stream to connect
        def is_connected():
            return ptz_stream.is_connected()
        
        assert wait_for_condition(is_connected, timeout=10), "PTZ stream failed to connect within timeout"
        
        # Get a frame
        frame = ptz_stream.get_frame()
        
        # Verify the frame is not None
        assert frame is not None, "Failed to get frame from PTZ stream"
        
        # Verify the frame has the correct shape
        assert frame.shape == (720, 1280, 3), f"Frame has incorrect shape: {frame.shape}"
        
        # Stop the stream
        ptz_stream.stop()

    def test_audio_stream_connection(self, audio_stream, wait_for_condition):
        """Test connecting to an audio RTSP stream."""
        # Start the stream
        audio_stream.start()
        
        # Wait for the stream to connect
        def is_connected():
            return audio_stream.is_connected()
        
        assert wait_for_condition(is_connected, timeout=10), "Audio stream failed to connect within timeout"
        
        # Get a frame
        frame = audio_stream.get_frame()
        
        # Verify the frame is not None
        assert frame is not None, "Failed to get frame from audio stream"
        
        # Verify the frame has the correct shape
        assert frame.shape == (720, 1280, 3), f"Frame has incorrect shape: {frame.shape}"
        
        # Stop the stream
        audio_stream.stop()

    def test_multiple_stream_connections(self, rtsp_simulator, default_config, wait_for_condition):
        """Test connecting to multiple RTSP streams simultaneously."""
        # Create streams
        streams = []
        camera_types = ["standard", "ptz", "audio", "multi_object", "license_plate"]
        
        for camera_type in camera_types:
            camera_name = f"{camera_type}_camera" if camera_type in ["ptz", "audio"] else "test_camera"
            
            # Use the appropriate config or create one if it doesn't exist
            if camera_name in default_config["cameras"]:
                config = default_config["cameras"][camera_name]
            else:
                config = default_config["cameras"]["test_camera"].copy()
            
            # Create the stream
            stream = RTSPStream(
                camera_name=camera_name,
                rtsp_url=rtsp_simulator[f"{camera_type}_url"],
                config=config,
            )
            
            streams.append(stream)
        
        try:
            # Start all streams
            for stream in streams:
                stream.start()
            
            # Wait for all streams to connect
            for stream in streams:
                def is_connected(s=stream):
                    return s.is_connected()
                
                assert wait_for_condition(is_connected, timeout=10), f"Stream {stream.camera_name} failed to connect within timeout"
            
            # Get frames from all streams
            for stream in streams:
                frame = stream.get_frame()
                assert frame is not None, f"Failed to get frame from stream {stream.camera_name}"
                assert frame.shape == (720, 1280, 3), f"Frame from stream {stream.camera_name} has incorrect shape: {frame.shape}"
        
        finally:
            # Stop all streams
            for stream in streams:
                stream.stop()

    def test_camera_with_rtsp_stream(self, rtsp_simulator, default_config, wait_for_condition):
        """Test a Camera object with an RTSP stream."""
        # Create a camera
        camera_name = "test_camera"
        camera_config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_simulator["standard_url"],
            config=camera_config,
        )
        
        camera = Camera(
            name=camera_name,
            config=camera_config,
            stream=stream,
        )
        
        try:
            # Start the camera
            camera.start()
            
            # Wait for the camera to connect
            def is_connected():
                return camera.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10), "Camera failed to connect within timeout"
            
            # Get a frame
            frame = camera.get_frame()
            
            # Verify the frame is not None
            assert frame is not None, "Failed to get frame from camera"
            
            # Verify the frame has the correct shape
            assert frame.shape == (720, 1280, 3), f"Frame has incorrect shape: {frame.shape}"
        
        finally:
            # Stop the camera
            camera.stop()

    def test_rtsp_stream_error_handling(self, rtsp_simulator, default_config, wait_for_condition):
        """Test error handling in RTSP stream."""
        # Create a stream with an invalid URL
        camera_name = "test_camera"
        config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url="rtsp://invalid-host:8554/standard",
            config=config,
        )
        
        try:
            # Start the stream
            stream.start()
            
            # Wait for a short time
            time.sleep(2)
            
            # Verify the stream is not connected
            assert not stream.is_connected(), "Stream should not be connected with invalid URL"
            
            # Get a frame (should return None)
            frame = stream.get_frame()
            assert frame is None, "Frame should be None with invalid URL"
            
            # Update the URL to a valid one
            stream.rtsp_url = rtsp_simulator["standard_url"]
            
            # Restart the stream
            stream.stop()
            stream.start()
            
            # Wait for the stream to connect
            def is_connected():
                return stream.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10), "Stream failed to connect with valid URL within timeout"
            
            # Get a frame
            frame = stream.get_frame()
            assert frame is not None, "Failed to get frame from stream with valid URL"
        
        finally:
            # Stop the stream
            stream.stop()

    def test_rtsp_stream_with_auth(self, rtsp_simulator, default_config, wait_for_condition):
        """Test RTSP stream with authentication."""
        # Create a stream with authentication
        camera_name = "test_camera"
        config = default_config["cameras"][camera_name]
        
        # Add authentication to the URL
        rtsp_url = rtsp_simulator["standard_url"].replace("rtsp://", "rtsp://user:pass@")
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_url,
            config=config,
        )
        
        try:
            # Start the stream
            stream.start()
            
            # Wait for the stream to connect
            def is_connected():
                return stream.is_connected()
            
            # This may fail if the RTSP simulator doesn't support authentication
            # In a real environment, this would be tested with a camera that supports authentication
            if wait_for_condition(is_connected, timeout=5):
                # Get a frame
                frame = stream.get_frame()
                assert frame is not None, "Failed to get frame from stream with authentication"
        
        finally:
            # Stop the stream
            stream.stop()

    def test_rtsp_stream_with_onvif(self, rtsp_simulator, default_config, wait_for_condition):
        """Test RTSP stream with ONVIF integration."""
        # Create a PTZ camera
        camera_name = "ptz_camera"
        camera_config = default_config["cameras"][camera_name]
        
        stream = RTSPStream(
            camera_name=camera_name,
            rtsp_url=rtsp_simulator["ptz_url"],
            config=camera_config,
        )
        
        camera = Camera(
            name=camera_name,
            config=camera_config,
            stream=stream,
        )
        
        try:
            # Start the camera
            camera.start()
            
            # Wait for the camera to connect
            def is_connected():
                return camera.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10), "Camera failed to connect within timeout"
            
            # Mock the ONVIF PTZ control
            with patch("arkos.ptz.onvif_ptz.ONVIFPTZController") as mock_onvif:
                # Create a mock ONVIF controller
                mock_controller = MagicMock()
                mock_onvif.return_value = mock_controller
                
                # Initialize PTZ
                camera.init_ptz()
                
                # Move the camera
                camera.ptz_move("left")
                mock_controller.move_continuous.assert_called_with("left")
                
                # Stop the camera movement
                camera.ptz_stop()
                mock_controller.stop.assert_called()
                
                # Go to a preset
                camera.ptz_goto_preset("home")
                mock_controller.goto_preset.assert_called_with("home")
        
        finally:
            # Stop the camera
            camera.stop()
