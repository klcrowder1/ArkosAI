from abc import ABC, abstractmethod
from typing import Tuple

from frigate.config.camera.motion import MotionConfig


class MotionDetector(ABC):
    @abstractmethod
    def __init__(
        self,
        frame_shape: Tuple[int, int, int],
        config: MotionConfig,
        fps: int,
        **kwargs
    ):
        pass

    @abstractmethod
    def detect(self, frame):
        pass

    @abstractmethod
    def is_calibrating(self):
        pass

    @abstractmethod
    def stop(self):
        pass

# Import detector implementations to make them available when importing from frigate.motion
from frigate.motion.frigate_motion import FrigateMotionDetector
from frigate.motion.improved_motion import ImprovedMotionDetector
from frigate.motion.optimized_motion import OptimizedMotionDetector

__all__ = ["MotionDetector", "FrigateMotionDetector", "ImprovedMotionDetector", "OptimizedMotionDetector"]
