"""Utilities for config file manipulation."""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cv2
import numpy as np
import yaml

from arkos.const import CONFIG_DIR

logger = logging.getLogger(__name__)


def find_config_file() -> str:
    """Find the config file."""
    if os.path.exists(f"{CONFIG_DIR}/config.yml"):
        return f"{CONFIG_DIR}/config.yml"
    elif os.path.exists(f"{CONFIG_DIR}/config.yaml"):
        return f"{CONFIG_DIR}/config.yaml"
    else:
        return f"{CONFIG_DIR}/config.yml"


def migrate_arkos_config(config_file: str) -> None:
    """Migrate the config file to the latest version."""
    pass


def get_relative_coordinates(
    coordinates: Union[str, List[str]], frame_shape: Tuple[int, int]
) -> Optional[List[List[int]]]:
    """Convert coordinates to relative coordinates."""
    if not coordinates:
        return None

    if isinstance(coordinates, list):
        return [
            get_relative_coordinates(coordinate, frame_shape)[0]
            for coordinate in coordinates
        ]

    height, width = frame_shape

    # convert a string of coordinates to a list of coordinates
    coordinate_list = []
    for pair in coordinates.split(","):
        x, y = pair.split()
        # convert to int and normalize
        if "%" in x:
            x_normal = int(float(x.strip("%")) * width / 100)
        else:
            x_normal = int(float(x))

        if "%" in y:
            y_normal = int(float(y.strip("%")) * height / 100)
        else:
            y_normal = int(float(y))
        coordinate_list.append([x_normal, y_normal])

    return [coordinate_list]


def convert_area_to_pixels(
    area: Union[int, str], frame_shape: Tuple[int, int]
) -> int:
    """Convert area to pixels."""
    height, width = frame_shape
    if isinstance(area, str) and area.endswith("%"):
        area_ratio = float(area.strip("%")) / 100
        return int(area_ratio * width * height)
    return int(area)


class StreamInfoRetriever:
    """Retrieve stream info from ffmpeg."""

    def __init__(self):
        self._cache = {}

    def get_stream_info(self, ffmpeg_config, path) -> Dict[str, Any]:
        """Get stream info from ffmpeg."""
        if path in self._cache:
            return self._cache[path]

        import subprocess

        ffprobe_cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_tag_string",
            "-of",
            "json",
            path,
        ]

        if ffmpeg_config.hwaccel_args:
            ffprobe_cmd.extend(ffmpeg_config.hwaccel_args.split(" "))

        process = subprocess.run(
            ffprobe_cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        if process.returncode != 0:
            logger.error(f"Error getting stream info: {process.stderr}")
            return {}

        import json

        try:
            info = json.loads(process.stdout)
            if "streams" in info and len(info["streams"]) > 0:
                stream = info["streams"][0]
                self._cache[path] = {
                    "width": stream.get("width"),
                    "height": stream.get("height"),
                    "fourcc": stream.get("codec_tag_string"),
                }
                return self._cache[path]
        except json.JSONDecodeError:
            logger.error(f"Error parsing stream info: {process.stdout}")
            return {}

        return {}
