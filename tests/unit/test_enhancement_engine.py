"""
Unit tests for enhancement engine module
"""

import cv2
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from arkos.enhancement.enhancement_engine import EnhancementEngine
from arkos.enhancement.zoom_overlay import ZoomOverlay
from arkos.enhancement.detail_enhancer import DetailEnhancer


class TestEnhancementEngine:
    """Tests for the EnhancementEngine class"""

    def test_init(self):
        """Test initialization of EnhancementEngine"""
        config = {
            "enhancement": {
                "enabled": True,
                "zoom_overlay": {
                    "enabled": True,
                    "scale_factor": 2.0,
                    "position": "top_right",
                    "size": 0.3,
                    "border_color": [0, 255, 0],
                    "border_thickness": 2,
                },
                "detail_enhancement": {
                    "enabled": True,
                    "method": "clahe",
                    "clip_limit": 2.0,
                    "tile_grid_size": [8, 8],
                },
            }
        }
        
        engine = EnhancementEngine(config)
        
        assert engine.enabled is True
        assert engine.zoom_overlay is not None
        assert engine.detail_enhancer is not None

    def test_disabled_engine(self):
        """Test EnhancementEngine when disabled"""
        config = {
            "enhancement": {
                "enabled": False,
            }
        }
        
        engine = EnhancementEngine(config)
        
        assert engine.enabled is False
        assert engine.zoom_overlay is None
        assert engine.detail_enhancer is None

    def test_process_frame(self):
        """Test processing a frame with enhancements"""
        config = {
            "enhancement": {
                "enabled": True,
                "zoom_overlay": {
                    "enabled": True,
                    "scale_factor": 2.0,
                    "position": "top_right",
                    "size": 0.3,
                    "border_color": [0, 255, 0],
                    "border_thickness": 2,
                },
                "detail_enhancement": {
                    "enabled": True,
                    "method": "clahe",
                    "clip_limit": 2.0,
                    "tile_grid_size": [8, 8],
                },
            }
        }
        
        # Create mock zoom overlay and detail enhancer
        mock_zoom_overlay = MagicMock()
        mock_detail_enhancer = MagicMock()
        
        # Create engine with mocks
        engine = EnhancementEngine(config)
        engine.zoom_overlay = mock_zoom_overlay
        engine.detail_enhancer = mock_detail_enhancer
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Create test detection
        detection = {
            "label": "person",
            "confidence": 0.95,
            "box": [100, 200, 300, 400],  # x, y, w, h
        }
        
        # Mock enhancement methods
        mock_detail_enhancer.enhance.return_value = frame.copy()
        mock_zoom_overlay.add_overlay.return_value = frame.copy()
        
        # Process frame
        enhanced_frame = engine.process_frame(frame, [detection])
        
        # Check that enhancement methods were called
        mock_detail_enhancer.enhance.assert_called_once()
        mock_zoom_overlay.add_overlay.assert_called_once()
        
        # Check that frame was returned
        assert enhanced_frame is not None
        assert enhanced_frame.shape == frame.shape

    def test_process_frame_no_detections(self):
        """Test processing a frame with no detections"""
        config = {
            "enhancement": {
                "enabled": True,
                "zoom_overlay": {
                    "enabled": True,
                    "scale_factor": 2.0,
                    "position": "top_right",
                    "size": 0.3,
                    "border_color": [0, 255, 0],
                    "border_thickness": 2,
                },
                "detail_enhancement": {
                    "enabled": True,
                    "method": "clahe",
                    "clip_limit": 2.0,
                    "tile_grid_size": [8, 8],
                },
            }
        }
        
        # Create mock zoom overlay and detail enhancer
        mock_zoom_overlay = MagicMock()
        mock_detail_enhancer = MagicMock()
        
        # Create engine with mocks
        engine = EnhancementEngine(config)
        engine.zoom_overlay = mock_zoom_overlay
        engine.detail_enhancer = mock_detail_enhancer
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Mock enhancement methods
        mock_detail_enhancer.enhance.return_value = frame.copy()
        
        # Process frame with no detections
        enhanced_frame = engine.process_frame(frame, [])
        
        # Check that detail enhancement was called but zoom overlay was not
        mock_detail_enhancer.enhance.assert_called_once()
        mock_zoom_overlay.add_overlay.assert_not_called()
        
        # Check that frame was returned
        assert enhanced_frame is not None
        assert enhanced_frame.shape == frame.shape

    def test_disabled_components(self):
        """Test EnhancementEngine with disabled components"""
        config = {
            "enhancement": {
                "enabled": True,
                "zoom_overlay": {
                    "enabled": False,
                },
                "detail_enhancement": {
                    "enabled": False,
                },
            }
        }
        
        engine = EnhancementEngine(config)
        
        assert engine.enabled is True
        assert engine.zoom_overlay is None
        assert engine.detail_enhancer is None
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Create test detection
        detection = {
            "label": "person",
            "confidence": 0.95,
            "box": [100, 200, 300, 400],  # x, y, w, h
        }
        
        # Process frame
        enhanced_frame = engine.process_frame(frame, [detection])
        
        # Check that frame was returned unchanged
        assert enhanced_frame is not None
        assert enhanced_frame.shape == frame.shape
        assert np.array_equal(enhanced_frame, frame)


class TestZoomOverlay:
    """Tests for the ZoomOverlay class"""

    def test_init(self):
        """Test initialization of ZoomOverlay"""
        config = {
            "scale_factor": 2.0,
            "position": "top_right",
            "size": 0.3,
            "border_color": [0, 255, 0],
            "border_thickness": 2,
        }
        
        overlay = ZoomOverlay(config)
        
        assert overlay.scale_factor == 2.0
        assert overlay.position == "top_right"
        assert overlay.size == 0.3
        assert np.array_equal(overlay.border_color, [0, 255, 0])
        assert overlay.border_thickness == 2

    def test_add_overlay(self):
        """Test adding zoom overlay to a frame"""
        config = {
            "scale_factor": 2.0,
            "position": "top_right",
            "size": 0.3,
            "border_color": [0, 255, 0],
            "border_thickness": 2,
        }
        
        overlay = ZoomOverlay(config)
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Create test detection
        detection = {
            "label": "person",
            "confidence": 0.95,
            "box": [100, 200, 300, 400],  # x, y, w, h
        }
        
        # Add overlay
        result = overlay.add_overlay(frame, detection)
        
        # Check that result is not None
        assert result is not None
        assert result.shape == frame.shape
        
        # Check that overlay was added (frame should be modified)
        assert not np.array_equal(result, frame)

    def test_calculate_overlay_position(self):
        """Test calculating overlay position"""
        config = {
            "scale_factor": 2.0,
            "position": "top_right",
            "size": 0.3,
            "border_color": [0, 255, 0],
            "border_thickness": 2,
        }
        
        overlay = ZoomOverlay(config)
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Calculate overlay size
        overlay_width = int(frame.shape[1] * overlay.size)
        overlay_height = int(frame.shape[0] * overlay.size)
        
        # Test top_right position
        overlay.position = "top_right"
        x, y = overlay._calculate_position(frame, overlay_width, overlay_height)
        assert x == frame.shape[1] - overlay_width
        assert y == 0
        
        # Test top_left position
        overlay.position = "top_left"
        x, y = overlay._calculate_position(frame, overlay_width, overlay_height)
        assert x == 0
        assert y == 0
        
        # Test bottom_right position
        overlay.position = "bottom_right"
        x, y = overlay._calculate_position(frame, overlay_width, overlay_height)
        assert x == frame.shape[1] - overlay_width
        assert y == frame.shape[0] - overlay_height
        
        # Test bottom_left position
        overlay.position = "bottom_left"
        x, y = overlay._calculate_position(frame, overlay_width, overlay_height)
        assert x == 0
        assert y == frame.shape[0] - overlay_height

    def test_extract_roi(self):
        """Test extracting region of interest"""
        config = {
            "scale_factor": 2.0,
            "position": "top_right",
            "size": 0.3,
            "border_color": [0, 255, 0],
            "border_thickness": 2,
        }
        
        overlay = ZoomOverlay(config)
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Create test detection
        detection = {
            "box": [100, 200, 300, 400],  # x, y, w, h
        }
        
        # Extract ROI
        roi = overlay._extract_roi(frame, detection)
        
        # Check ROI dimensions
        assert roi.shape[0] == 400  # height
        assert roi.shape[1] == 300  # width
        assert roi.shape[2] == 3    # channels


class TestDetailEnhancer:
    """Tests for the DetailEnhancer class"""

    def test_init(self):
        """Test initialization of DetailEnhancer"""
        config = {
            "method": "clahe",
            "clip_limit": 2.0,
            "tile_grid_size": [8, 8],
        }
        
        enhancer = DetailEnhancer(config)
        
        assert enhancer.method == "clahe"
        assert enhancer.clip_limit == 2.0
        assert enhancer.tile_grid_size == (8, 8)

    @patch("arkos.enhancement.detail_enhancer.cv2.createCLAHE")
    def test_enhance_clahe(self, mock_create_clahe):
        """Test enhancing a frame with CLAHE"""
        config = {
            "method": "clahe",
            "clip_limit": 2.0,
            "tile_grid_size": [8, 8],
        }
        
        enhancer = DetailEnhancer(config)
        
        # Create mock CLAHE
        mock_clahe = MagicMock()
        mock_create_clahe.return_value = mock_clahe
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Mock CLAHE apply
        mock_clahe.apply.return_value = np.zeros((720, 1280), dtype=np.uint8)
        
        # Enhance frame
        result = enhancer.enhance(frame)
        
        # Check that CLAHE was created and applied
        mock_create_clahe.assert_called_once_with(clipLimit=2.0, tileGridSize=(8, 8))
        assert mock_clahe.apply.call_count == 3  # Once for each channel
        
        # Check that result is not None
        assert result is not None
        assert result.shape == frame.shape

    def test_enhance_histogram_equalization(self):
        """Test enhancing a frame with histogram equalization"""
        config = {
            "method": "histogram_equalization",
        }
        
        enhancer = DetailEnhancer(config)
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Enhance frame
        result = enhancer.enhance(frame)
        
        # Check that result is not None
        assert result is not None
        assert result.shape == frame.shape

    def test_enhance_unsharp_mask(self):
        """Test enhancing a frame with unsharp mask"""
        config = {
            "method": "unsharp_mask",
            "kernel_size": 5,
            "sigma": 1.0,
            "amount": 1.5,
            "threshold": 0,
        }
        
        enhancer = DetailEnhancer(config)
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Enhance frame
        result = enhancer.enhance(frame)
        
        # Check that result is not None
        assert result is not None
        assert result.shape == frame.shape

    def test_enhance_invalid_method(self):
        """Test enhancing a frame with an invalid method"""
        config = {
            "method": "invalid_method",
        }
        
        enhancer = DetailEnhancer(config)
        
        # Create test frame
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Enhance frame
        result = enhancer.enhance(frame)
        
        # Check that original frame is returned
        assert result is not None
        assert result.shape == frame.shape
        assert np.array_equal(result, frame)
