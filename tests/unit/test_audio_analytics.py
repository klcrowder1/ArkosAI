"""
Unit tests for audio analytics module
"""

import os
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from arkos.audio_analytics.audio_detector import AudioDetector
from arkos.audio_analytics.audio_processor import AudioProcessor
from arkos.audio_analytics.audio_event_manager import AudioEventManager


class TestAudioDetector:
    """Tests for the AudioDetector class"""

    def test_init(self):
        """Test initialization of AudioDetector"""
        detector = AudioDetector(
            model_path="test_model.tflite",
            labelmap_path="test_labelmap.txt",
            sample_rate=16000,
            threshold=0.5,
        )
        assert detector.sample_rate == 16000
        assert detector.threshold == 0.5
        assert detector.model_path == "test_model.tflite"
        assert detector.labelmap_path == "test_labelmap.txt"

    @patch("arkos.audio_analytics.audio_detector.tf.lite.Interpreter")
    def test_load_model(self, mock_interpreter_class):
        """Test loading model"""
        # Mock TFLite interpreter
        mock_interpreter = MagicMock()
        mock_interpreter_class.return_value = mock_interpreter
        
        # Create detector
        detector = AudioDetector(
            model_path="test_model.tflite",
            labelmap_path="test_labelmap.txt",
            sample_rate=16000,
            threshold=0.5,
        )
        
        # Load model
        detector._load_model()
        
        # Check that interpreter was created
        mock_interpreter_class.assert_called_once_with(model_path="test_model.tflite")
        
        # Check that interpreter was allocated and invoked
        mock_interpreter.allocate_tensors.assert_called_once()

    def test_load_labelmap(self, tmp_path):
        """Test loading labelmap"""
        # Create a temporary labelmap file
        labelmap_path = tmp_path / "test_labelmap.txt"
        with open(labelmap_path, "w") as f:
            f.write("dog_bark\ncar_alarm\nglass_break\ngunshot\n")
        
        # Create detector
        detector = AudioDetector(
            model_path="test_model.tflite",
            labelmap_path=str(labelmap_path),
            sample_rate=16000,
            threshold=0.5,
        )
        
        # Load labelmap
        detector._load_labelmap()
        
        # Check labels
        assert detector.labels == ["dog_bark", "car_alarm", "glass_break", "gunshot"]
        assert len(detector.labels) == 4

    @patch("arkos.audio_analytics.audio_detector.AudioDetector._load_model")
    @patch("arkos.audio_analytics.audio_detector.AudioDetector._load_labelmap")
    def test_detect_audio_events(self, mock_load_labelmap, mock_load_model):
        """Test audio event detection"""
        # Create detector
        detector = AudioDetector(
            model_path="test_model.tflite",
            labelmap_path="test_labelmap.txt",
            sample_rate=16000,
            threshold=0.5,
        )
        
        # Mock interpreter and labels
        detector.interpreter = MagicMock()
        detector.labels = ["dog_bark", "car_alarm", "glass_break", "gunshot"]
        
        # Mock input and output tensors
        input_details = [{"index": 0}]
        output_details = [{"index": 1}]
        detector.interpreter.get_input_details.return_value = input_details
        detector.interpreter.get_output_details.return_value = output_details
        
        # Mock output tensor with detections
        def mock_get_tensor(index):
            if index == 1:
                # Return probabilities for each class
                return np.array([[0.9, 0.1, 0.2, 0.05]])
            return None
        
        detector.interpreter.get_tensor.side_effect = mock_get_tensor
        
        # Create test audio data
        audio_data = np.random.rand(16000).astype(np.float32)  # 1 second of audio
        
        # Detect audio events
        detections = detector.detect(audio_data)
        
        # Check detections
        assert len(detections) == 1, f"Expected 1 detection, got {len(detections)}"
        assert detections[0]["label"] == "dog_bark", f"Expected 'dog_bark', got {detections[0]['label']}"
        assert detections[0]["confidence"] == 0.9, f"Expected confidence 0.9, got {detections[0]['confidence']}"

    @patch("arkos.audio_analytics.audio_detector.AudioDetector._load_model")
    @patch("arkos.audio_analytics.audio_detector.AudioDetector._load_labelmap")
    def test_threshold_filtering(self, mock_load_labelmap, mock_load_model):
        """Test threshold filtering of detections"""
        # Create detector with high threshold
        detector = AudioDetector(
            model_path="test_model.tflite",
            labelmap_path="test_labelmap.txt",
            sample_rate=16000,
            threshold=0.95,  # High threshold
        )
        
        # Mock interpreter and labels
        detector.interpreter = MagicMock()
        detector.labels = ["dog_bark", "car_alarm", "glass_break", "gunshot"]
        
        # Mock input and output tensors
        input_details = [{"index": 0}]
        output_details = [{"index": 1}]
        detector.interpreter.get_input_details.return_value = input_details
        detector.interpreter.get_output_details.return_value = output_details
        
        # Mock output tensor with detections
        def mock_get_tensor(index):
            if index == 1:
                # Return probabilities for each class
                return np.array([[0.9, 0.1, 0.2, 0.05]])
            return None
        
        detector.interpreter.get_tensor.side_effect = mock_get_tensor
        
        # Create test audio data
        audio_data = np.random.rand(16000).astype(np.float32)  # 1 second of audio
        
        # Detect audio events
        detections = detector.detect(audio_data)
        
        # Check that no detections pass the threshold
        assert len(detections) == 0, f"Expected 0 detections, got {len(detections)}"


class TestAudioProcessor:
    """Tests for the AudioProcessor class"""

    def test_init(self):
        """Test initialization of AudioProcessor"""
        processor = AudioProcessor(
            sample_rate=16000,
            frame_length=1.0,
            frame_overlap=0.5,
        )
        assert processor.sample_rate == 16000
        assert processor.frame_length == 1.0
        assert processor.frame_overlap == 0.5
        assert processor.frame_samples == 16000
        assert processor.hop_samples == 8000

    def test_preprocess_audio(self):
        """Test audio preprocessing"""
        # Create processor
        processor = AudioProcessor(
            sample_rate=16000,
            frame_length=1.0,
            frame_overlap=0.5,
        )
        
        # Create test audio data (2 seconds)
        audio_data = np.random.rand(32000).astype(np.float32)
        
        # Preprocess audio
        frames = processor.preprocess(audio_data)
        
        # Check frames
        assert len(frames) == 3, f"Expected 3 frames, got {len(frames)}"
        assert frames[0].shape == (16000,), f"Expected shape (16000,), got {frames[0].shape}"
        assert frames[1].shape == (16000,), f"Expected shape (16000,), got {frames[1].shape}"
        assert frames[2].shape == (16000,), f"Expected shape (16000,), got {frames[2].shape}"

    def test_extract_features(self):
        """Test feature extraction"""
        # Create processor
        processor = AudioProcessor(
            sample_rate=16000,
            frame_length=1.0,
            frame_overlap=0.5,
        )
        
        # Create test audio data (1 second)
        audio_data = np.random.rand(16000).astype(np.float32)
        
        # Extract features
        features = processor.extract_features(audio_data)
        
        # Check features
        assert features.ndim == 2, f"Expected 2D array, got {features.ndim}D"
        assert features.shape[1] > 0, "Features should have at least one column"

    @patch("arkos.audio_analytics.audio_processor.librosa.feature.mfcc")
    def test_mfcc_features(self, mock_mfcc):
        """Test MFCC feature extraction"""
        # Mock MFCC function
        mock_mfcc.return_value = np.random.rand(20, 100)
        
        # Create processor
        processor = AudioProcessor(
            sample_rate=16000,
            frame_length=1.0,
            frame_overlap=0.5,
        )
        
        # Create test audio data (1 second)
        audio_data = np.random.rand(16000).astype(np.float32)
        
        # Extract features
        features = processor.extract_mfcc(audio_data)
        
        # Check that MFCC was called
        mock_mfcc.assert_called_once()
        
        # Check features
        assert features.shape == (20, 100), f"Expected shape (20, 100), got {features.shape}"


class TestAudioEventManager:
    """Tests for the AudioEventManager class"""

    @patch("arkos.audio_analytics.audio_event_manager.AudioDetector")
    @patch("arkos.audio_analytics.audio_event_manager.AudioProcessor")
    def test_init(self, mock_processor_class, mock_detector_class):
        """Test initialization of AudioEventManager"""
        # Mock detector and processor
        mock_detector = MagicMock()
        mock_processor = MagicMock()
        mock_detector_class.return_value = mock_detector
        mock_processor_class.return_value = mock_processor
        
        # Create config
        config = {
            "audio_analytics": {
                "enabled": True,
                "model_path": "test_model.tflite",
                "labelmap_path": "test_labelmap.txt",
                "sample_rate": 16000,
                "threshold": 0.5,
                "frame_length": 1.0,
                "frame_overlap": 0.5,
            }
        }
        
        # Create manager
        manager = AudioEventManager(config)
        
        # Check that detector and processor were created
        mock_detector_class.assert_called_once()
        mock_processor_class.assert_called_once()
        
        # Check manager properties
        assert manager.enabled is True
        assert manager.detector == mock_detector
        assert manager.processor == mock_processor

    @patch("arkos.audio_analytics.audio_event_manager.AudioDetector")
    @patch("arkos.audio_analytics.audio_event_manager.AudioProcessor")
    def test_process_audio(self, mock_processor_class, mock_detector_class):
        """Test processing audio data"""
        # Mock detector and processor
        mock_detector = MagicMock()
        mock_processor = MagicMock()
        mock_detector_class.return_value = mock_detector
        mock_processor_class.return_value = mock_processor
        
        # Mock processor to return frames
        mock_processor.preprocess.return_value = [
            np.random.rand(16000).astype(np.float32),
            np.random.rand(16000).astype(np.float32),
        ]
        
        # Mock detector to return detections
        mock_detector.detect.side_effect = [
            [{"label": "dog_bark", "confidence": 0.9}],
            [{"label": "car_alarm", "confidence": 0.8}],
        ]
        
        # Create config
        config = {
            "audio_analytics": {
                "enabled": True,
                "model_path": "test_model.tflite",
                "labelmap_path": "test_labelmap.txt",
                "sample_rate": 16000,
                "threshold": 0.5,
                "frame_length": 1.0,
                "frame_overlap": 0.5,
            }
        }
        
        # Create manager
        manager = AudioEventManager(config)
        
        # Create test audio data (2 seconds)
        audio_data = np.random.rand(32000).astype(np.float32)
        
        # Process audio
        events = manager.process_audio(audio_data)
        
        # Check that processor and detector were called
        mock_processor.preprocess.assert_called_once_with(audio_data)
        assert mock_detector.detect.call_count == 2
        
        # Check events
        assert len(events) == 2, f"Expected 2 events, got {len(events)}"
        assert events[0]["label"] == "dog_bark", f"Expected 'dog_bark', got {events[0]['label']}"
        assert events[1]["label"] == "car_alarm", f"Expected 'car_alarm', got {events[1]['label']}"

    @patch("arkos.audio_analytics.audio_event_manager.AudioDetector")
    @patch("arkos.audio_analytics.audio_event_manager.AudioProcessor")
    def test_disabled_manager(self, mock_processor_class, mock_detector_class):
        """Test manager when disabled"""
        # Create config with audio analytics disabled
        config = {
            "audio_analytics": {
                "enabled": False,
                "model_path": "test_model.tflite",
                "labelmap_path": "test_labelmap.txt",
                "sample_rate": 16000,
                "threshold": 0.5,
                "frame_length": 1.0,
                "frame_overlap": 0.5,
            }
        }
        
        # Create manager
        manager = AudioEventManager(config)
        
        # Check that detector and processor were not created
        mock_detector_class.assert_not_called()
        mock_processor_class.assert_not_called()
        
        # Create test audio data
        audio_data = np.random.rand(32000).astype(np.float32)
        
        # Process audio
        events = manager.process_audio(audio_data)
        
        # Check that no events were returned
        assert len(events) == 0, f"Expected 0 events, got {len(events)}"

    @patch("arkos.audio_analytics.audio_event_manager.AudioDetector")
    @patch("arkos.audio_analytics.audio_event_manager.AudioProcessor")
    def test_event_filtering(self, mock_processor_class, mock_detector_class):
        """Test filtering of audio events"""
        # Mock detector and processor
        mock_detector = MagicMock()
        mock_processor = MagicMock()
        mock_detector_class.return_value = mock_detector
        mock_processor_class.return_value = mock_processor
        
        # Mock processor to return frames
        mock_processor.preprocess.return_value = [
            np.random.rand(16000).astype(np.float32),
        ]
        
        # Mock detector to return detections
        mock_detector.detect.return_value = [
            {"label": "dog_bark", "confidence": 0.9},
            {"label": "car_alarm", "confidence": 0.8},
            {"label": "glass_break", "confidence": 0.7},
        ]
        
        # Create config with event filtering
        config = {
            "audio_analytics": {
                "enabled": True,
                "model_path": "test_model.tflite",
                "labelmap_path": "test_labelmap.txt",
                "sample_rate": 16000,
                "threshold": 0.5,
                "frame_length": 1.0,
                "frame_overlap": 0.5,
                "events_of_interest": ["dog_bark", "glass_break"],
            }
        }
        
        # Create manager
        manager = AudioEventManager(config)
        
        # Create test audio data
        audio_data = np.random.rand(16000).astype(np.float32)
        
        # Process audio
        events = manager.process_audio(audio_data)
        
        # Check events
        assert len(events) == 2, f"Expected 2 events, got {len(events)}"
        event_labels = [event["label"] for event in events]
        assert "dog_bark" in event_labels, "Missing 'dog_bark' event"
        assert "glass_break" in event_labels, "Missing 'glass_break' event"
        assert "car_alarm" not in event_labels, "'car_alarm' event should be filtered out"
