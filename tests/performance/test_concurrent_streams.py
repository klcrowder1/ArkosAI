"""
Performance tests for concurrent stream processing in Arkos AI.

This module tests the performance of Arkos AI when processing multiple concurrent streams.
"""

import os
import time
import pytest
import numpy as np
import cv2
import threading
import queue
import psutil
import gc
from unittest.mock import MagicMock, patch

# Import the modules to test
from arkos.camera.rtsp_stream import RTSPStream
from arkos.camera.camera import Camera
from arkos.object_detection.video_analytics import VideoAnalytics


class TestConcurrentStreams:
    """Test suite for concurrent stream processing performance."""

    @pytest.fixture
    def camera_streams(self, rtsp_simulator, default_config):
        """Create multiple camera streams for testing."""
        streams = []
        
        # Create streams for different camera types
        camera_types = ["standard", "ptz", "audio", "multi_object", "license_plate"]
        
        for i, camera_type in enumerate(camera_types):
            camera_name = f"{camera_type}_camera"
            
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
        
        yield streams
        
        # Clean up
        for stream in streams:
            stream.stop()

    @pytest.fixture
    def video_analytics_engines(self, camera_streams, mock_detector, mock_tracker, default_config):
        """Create multiple video analytics engines for testing."""
        engines = []
        
        for stream in camera_streams:
            # Get the appropriate config
            camera_name = stream.camera_name
            if camera_name in default_config["cameras"]:
                config = default_config["cameras"][camera_name]
            else:
                config = default_config["cameras"]["test_camera"].copy()
            
            # Create the analytics engine
            analytics = VideoAnalytics(
                camera_name=camera_name,
                config=config,
                detector=mock_detector,
                tracker=mock_tracker,
            )
            
            engines.append(analytics)
        
        return engines

    @pytest.mark.benchmark
    def test_concurrent_stream_processing(self, camera_streams, video_analytics_engines, wait_for_condition, benchmark):
        """Test the performance of processing multiple streams concurrently."""
        # Start all streams
        for stream in camera_streams:
            stream.start()
        
        # Wait for all streams to connect
        for stream in camera_streams:
            def is_connected(s=stream):
                return s.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10)
        
        # Create a function to process all streams
        def process_all_streams():
            results = []
            
            for i, (stream, analytics) in enumerate(zip(camera_streams, video_analytics_engines)):
                # Get a frame
                frame = stream.get_frame()
                
                # Process the frame
                if frame is not None:
                    result = analytics.process_frame(frame, time.time())
                    results.append(result)
            
            return results
        
        # Run the benchmark
        result = benchmark(process_all_streams)
        
        # Check that the benchmark completed successfully
        assert result is not None
        
        # Stop all streams
        for stream in camera_streams:
            stream.stop()

    @pytest.mark.benchmark
    def test_concurrent_stream_processing_with_threads(self, camera_streams, video_analytics_engines, wait_for_condition, benchmark):
        """Test the performance of processing multiple streams concurrently using threads."""
        # Start all streams
        for stream in camera_streams:
            stream.start()
        
        # Wait for all streams to connect
        for stream in camera_streams:
            def is_connected(s=stream):
                return s.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10)
        
        # Create a function to process a stream in a thread
        def process_stream(stream, analytics, result_queue):
            # Get a frame
            frame = stream.get_frame()
            
            # Process the frame
            if frame is not None:
                result = analytics.process_frame(frame, time.time())
                result_queue.put(result)
            else:
                result_queue.put(None)
        
        # Create a function to process all streams using threads
        def process_all_streams_threaded():
            threads = []
            result_queue = queue.Queue()
            
            # Create and start threads
            for i, (stream, analytics) in enumerate(zip(camera_streams, video_analytics_engines)):
                thread = threading.Thread(
                    target=process_stream,
                    args=(stream, analytics, result_queue)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Collect results
            results = []
            while not result_queue.empty():
                result = result_queue.get()
                if result is not None:
                    results.append(result)
            
            return results
        
        # Run the benchmark
        result = benchmark(process_all_streams_threaded)
        
        # Check that the benchmark completed successfully
        assert result is not None
        
        # Stop all streams
        for stream in camera_streams:
            stream.stop()

    @pytest.mark.benchmark
    def test_memory_usage_with_concurrent_streams(self, camera_streams, video_analytics_engines, wait_for_condition):
        """Test memory usage when processing multiple streams concurrently."""
        # Start all streams
        for stream in camera_streams:
            stream.start()
        
        # Wait for all streams to connect
        for stream in camera_streams:
            def is_connected(s=stream):
                return s.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10)
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
        
        # Process streams for a period of time
        num_frames = 100
        memory_usage = []
        
        for _ in range(num_frames):
            # Process all streams
            for stream, analytics in zip(camera_streams, video_analytics_engines):
                # Get a frame
                frame = stream.get_frame()
                
                # Process the frame
                if frame is not None:
                    analytics.process_frame(frame, time.time())
            
            # Record memory usage
            gc.collect()  # Force garbage collection
            current_memory = process.memory_info().rss / 1024 / 1024  # Convert to MB
            memory_usage.append(current_memory)
            
            # Sleep briefly to avoid maxing out CPU
            time.sleep(0.01)
        
        # Calculate memory usage statistics
        avg_memory = sum(memory_usage) / len(memory_usage)
        max_memory = max(memory_usage)
        memory_growth = max_memory - initial_memory
        
        # Print memory usage statistics
        print(f"Initial memory usage: {initial_memory:.2f} MB")
        print(f"Average memory usage: {avg_memory:.2f} MB")
        print(f"Maximum memory usage: {max_memory:.2f} MB")
        print(f"Memory growth: {memory_growth:.2f} MB")
        
        # Check that memory growth is within acceptable limits
        assert memory_growth < 1000, f"Memory growth of {memory_growth:.2f} MB exceeds limit of 1000 MB"
        
        # Stop all streams
        for stream in camera_streams:
            stream.stop()

    @pytest.mark.benchmark
    def test_cpu_usage_with_concurrent_streams(self, camera_streams, video_analytics_engines, wait_for_condition):
        """Test CPU usage when processing multiple streams concurrently."""
        # Start all streams
        for stream in camera_streams:
            stream.start()
        
        # Wait for all streams to connect
        for stream in camera_streams:
            def is_connected(s=stream):
                return s.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10)
        
        # Get initial CPU usage
        process = psutil.Process(os.getpid())
        initial_cpu = process.cpu_percent(interval=0.1)
        
        # Process streams for a period of time
        num_frames = 100
        cpu_usage = []
        
        for _ in range(num_frames):
            # Process all streams
            for stream, analytics in zip(camera_streams, video_analytics_engines):
                # Get a frame
                frame = stream.get_frame()
                
                # Process the frame
                if frame is not None:
                    analytics.process_frame(frame, time.time())
            
            # Record CPU usage
            current_cpu = process.cpu_percent(interval=0.1)
            cpu_usage.append(current_cpu)
        
        # Calculate CPU usage statistics
        avg_cpu = sum(cpu_usage) / len(cpu_usage)
        max_cpu = max(cpu_usage)
        
        # Print CPU usage statistics
        print(f"Initial CPU usage: {initial_cpu:.2f}%")
        print(f"Average CPU usage: {avg_cpu:.2f}%")
        print(f"Maximum CPU usage: {max_cpu:.2f}%")
        
        # Check that CPU usage is within acceptable limits
        # Note: This is a soft assertion as CPU usage can vary widely based on the system
        assert max_cpu <= 100, f"CPU usage of {max_cpu:.2f}% exceeds 100%"
        
        # Stop all streams
        for stream in camera_streams:
            stream.stop()

    @pytest.mark.benchmark
    def test_frame_processing_rate(self, camera_streams, video_analytics_engines, wait_for_condition):
        """Test the frame processing rate with multiple concurrent streams."""
        # Start all streams
        for stream in camera_streams:
            stream.start()
        
        # Wait for all streams to connect
        for stream in camera_streams:
            def is_connected(s=stream):
                return s.is_connected()
            
            assert wait_for_condition(is_connected, timeout=10)
        
        # Process streams for a period of time
        duration = 10  # seconds
        start_time = time.time()
        frame_count = 0
        
        while time.time() - start_time < duration:
            # Process all streams
            for stream, analytics in zip(camera_streams, video_analytics_engines):
                # Get a frame
                frame = stream.get_frame()
                
                # Process the frame
                if frame is not None:
                    analytics.process_frame(frame, time.time())
                    frame_count += 1
        
        # Calculate frame processing rate
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        
        # Print frame processing rate
        print(f"Processed {frame_count} frames in {elapsed_time:.2f} seconds")
        print(f"Frame processing rate: {fps:.2f} FPS")
        
        # Check that frame processing rate is within acceptable limits
        # This will depend on the system, but we expect at least 1 FPS per stream
        min_expected_fps = len(camera_streams)
        assert fps >= min_expected_fps, f"Frame processing rate of {fps:.2f} FPS is below minimum expected rate of {min_expected_fps} FPS"
        
        # Stop all streams
        for stream in camera_streams:
            stream.stop()

    @pytest.mark.benchmark
    def test_scaling_with_number_of_streams(self, rtsp_simulator, default_config, mock_detector, mock_tracker, wait_for_condition):
        """Test how performance scales with the number of concurrent streams."""
        # Define the number of streams to test
        stream_counts = [1, 2, 3, 4, 5]
        
        # Store results for each stream count
        results = {}
        
        for count in stream_counts:
            # Create streams
            streams = []
            analytics_engines = []
            
            for i in range(count):
                # Use a different camera type for each stream if possible
                camera_types = ["standard", "ptz", "audio", "multi_object", "license_plate"]
                camera_type = camera_types[i % len(camera_types)]
                camera_name = f"{camera_type}_camera_{i}"
                
                # Use the appropriate config or create one if it doesn't exist
                if camera_type + "_camera" in default_config["cameras"]:
                    config = default_config["cameras"][camera_type + "_camera"].copy()
                else:
                    config = default_config["cameras"]["test_camera"].copy()
                
                # Create the stream
                stream = RTSPStream(
                    camera_name=camera_name,
                    rtsp_url=rtsp_simulator[f"{camera_type}_url"],
                    config=config,
                )
                
                # Create the analytics engine
                analytics = VideoAnalytics(
                    camera_name=camera_name,
                    config=config,
                    detector=mock_detector,
                    tracker=mock_tracker,
                )
                
                streams.append(stream)
                analytics_engines.append(analytics)
            
            try:
                # Start all streams
                for stream in streams:
                    stream.start()
                
                # Wait for all streams to connect
                for stream in streams:
                    def is_connected(s=stream):
                        return s.is_connected()
                    
                    assert wait_for_condition(is_connected, timeout=10)
                
                # Measure processing time for a fixed number of frames
                num_frames = 50
                start_time = time.time()
                
                for _ in range(num_frames):
                    # Process all streams
                    for stream, analytics in zip(streams, analytics_engines):
                        # Get a frame
                        frame = stream.get_frame()
                        
                        # Process the frame
                        if frame is not None:
                            analytics.process_frame(frame, time.time())
                
                # Calculate processing time
                elapsed_time = time.time() - start_time
                fps = (num_frames * count) / elapsed_time
                
                # Store results
                results[count] = {
                    "elapsed_time": elapsed_time,
                    "fps": fps,
                    "fps_per_stream": fps / count,
                }
                
                # Print results
                print(f"{count} streams: {elapsed_time:.2f} seconds, {fps:.2f} FPS, {fps / count:.2f} FPS per stream")
            
            finally:
                # Stop all streams
                for stream in streams:
                    stream.stop()
        
        # Check that performance scales reasonably with the number of streams
        # We expect some degradation as the number of streams increases
        for i in range(1, len(stream_counts)):
            prev_count = stream_counts[i-1]
            curr_count = stream_counts[i]
            
            prev_fps_per_stream = results[prev_count]["fps_per_stream"]
            curr_fps_per_stream = results[curr_count]["fps_per_stream"]
            
            # We expect the FPS per stream to decrease, but not by more than 50%
            degradation = (prev_fps_per_stream - curr_fps_per_stream) / prev_fps_per_stream
            
            print(f"Performance degradation from {prev_count} to {curr_count} streams: {degradation * 100:.2f}%")
            assert degradation <= 0.5, f"Performance degradation of {degradation * 100:.2f}% exceeds limit of 50%"
