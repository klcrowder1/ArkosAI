import random
import string
import logging
from collections import defaultdict

import numpy as np
from scipy.spatial import distance as dist

from arkos.config import DetectConfig
from arkos.track import ObjectTracker
from arkos.util import intersection_over_union

logger = logging.getLogger(__name__)


class CentroidTracker(ObjectTracker):
    def __init__(self, config: DetectConfig):
        self.tracked_objects = {}
        self.untracked_object_boxes = []
        self.disappeared = {}
        self.positions = {}
        self.confidence_scores = {}  # Track confidence scores for each object
        self.max_disappeared = config.max_disappeared
        self.detect_config = config

    def register(self, index, obj):
        rand_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
        id = f"{obj['frame_time']}-{rand_id}"
        obj["id"] = id
        obj["start_time"] = obj["frame_time"]
        obj["motionless_count"] = 0
        obj["position_changes"] = 0
        self.tracked_objects[id] = obj
        self.disappeared[id] = 0
        self.confidence_scores[id] = 1.0  # Initialize with high confidence
        self.positions[id] = {
            "xmins": [],
            "ymins": [],
            "xmaxs": [],
            "ymaxs": [],
            "xmin": 0,
            "ymin": 0,
            "xmax": self.detect_config.width,
            "ymax": self.detect_config.height,
        }
        logger.debug(f"Registered new object: {id}, label: {obj['label']}")

    def deregister(self, id):
        logger.debug(f"Deregistering object: {id}")
        del self.tracked_objects[id]
        del self.disappeared[id]
        del self.confidence_scores[id]
        del self.positions[id]

    # tracks the current position of the object based on the last N bounding boxes
    # returns False if the object has moved outside its previous position
    def update_position(self, id, box):
        position = self.positions[id]
        position_box = (
            position["xmin"],
            position["ymin"],
            position["xmax"],
            position["ymax"],
        )

        xmin, ymin, xmax, ymax = box

        # Calculate IoU between current box and position box
        iou = intersection_over_union(position_box, box)

        # if the iou drops below the threshold
        # assume the object has moved to a new position and reset the computed box
        if iou < 0.6:
            self.positions[id] = {
                "xmins": [xmin],
                "ymins": [ymin],
                "xmaxs": [xmax],
                "ymaxs": [ymax],
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax,
            }
            # Reduce confidence slightly when position changes significantly
            self.confidence_scores[id] = max(0.7, self.confidence_scores[id] - 0.1)
            return False

        # if there are less than 10 entries for the position, add the bounding box
        # and recompute the position box
        if len(position["xmins"]) < 10:
            position["xmins"].append(xmin)
            position["ymins"].append(ymin)
            position["xmaxs"].append(xmax)
            position["ymaxs"].append(ymax)
            # by using percentiles here, we hopefully remove outliers
            position["xmin"] = np.percentile(position["xmins"], 15)
            position["ymin"] = np.percentile(position["ymins"], 15)
            position["xmax"] = np.percentile(position["xmaxs"], 85)
            position["ymax"] = np.percentile(position["ymaxs"], 85)
            
            # Increase confidence when position is stable
            self.confidence_scores[id] = min(1.0, self.confidence_scores[id] + 0.05)

        return True

    def is_expired(self, id):
        obj = self.tracked_objects[id]
        # get the max frames for this label type or the default
        max_frames = self.detect_config.stationary.max_frames.objects.get(
            obj["label"], self.detect_config.stationary.max_frames.default
        )

        # if there is no max_frames for this label type, continue
        if max_frames is None:
            return False

        # if the object has exceeded the max_frames setting, deregister
        if (
            obj["motionless_count"] - self.detect_config.stationary.threshold
            > max_frames
        ):
            return True

        return False

    def update(self, id, new_obj):
        self.disappeared[id] = 0
        # update the motionless count if the object has not moved to a new position
        if self.update_position(id, new_obj["box"]):
            self.tracked_objects[id]["motionless_count"] += 1
            if self.is_expired(id):
                self.deregister(id)
                return
        else:
            # register the first position change and then only increment if
            # the object was previously stationary
            if (
                self.tracked_objects[id]["position_changes"] == 0
                or self.tracked_objects[id]["motionless_count"]
                >= self.detect_config.stationary.threshold
            ):
                self.tracked_objects[id]["position_changes"] += 1
            self.tracked_objects[id]["motionless_count"] = 0

        # Add confidence score to the object data
        new_obj["confidence"] = self.confidence_scores[id]
        self.tracked_objects[id].update(new_obj)

    def update_frame_times(self, frame_name, frame_time):
        for id in list(self.tracked_objects.keys()):
            self.tracked_objects[id]["frame_time"] = frame_time
            self.tracked_objects[id]["motionless_count"] += 1
            # Decrease confidence for objects that haven't been seen in this frame
            self.confidence_scores[id] = max(0.1, self.confidence_scores[id] - 0.05)
            if self.is_expired(id):
                self.deregister(id)

    def calculate_distance(self, centroid1, centroid2, box1, box2):
        """
        Enhanced distance calculation that considers both centroid distance and box size similarity
        """
        # Calculate Euclidean distance between centroids
        centroid_distance = np.sqrt(
            (centroid1[0] - centroid2[0]) ** 2 + (centroid1[1] - centroid2[1]) ** 2
        )
        
        # Calculate box size similarity (width and height ratios)
        width1 = box1[2] - box1[0]
        height1 = box1[3] - box1[1]
        width2 = box2[2] - box2[0]
        height2 = box2[3] - box2[1]
        
        # Avoid division by zero
        width_ratio = max(width1, width2) / max(1, min(width1, width2))
        height_ratio = max(height1, height2) / max(1, min(height1, height2))
        
        # Penalize if boxes have very different sizes
        size_penalty = (width_ratio + height_ratio) / 2
        
        # Combine centroid distance with size penalty
        # The weight factors can be tuned for better performance
        combined_distance = centroid_distance * (0.7 + 0.3 * size_penalty)
        
        return combined_distance

    def match_and_update(self, frame_name, frame_time, detections):
        # group by name
        detection_groups = defaultdict(lambda: [])
        for obj in detections:
            detection_groups[obj[0]].append(
                {
                    "label": obj[0],
                    "score": obj[1],
                    "box": obj[2],
                    "area": obj[3],
                    "ratio": obj[4],
                    "region": obj[5],
                    "frame_time": frame_time,
                }
            )

        # update any tracked objects with labels that are not
        # seen in the current objects and deregister if needed
        for obj in list(self.tracked_objects.values()):
            if obj["label"] not in detection_groups:
                if self.disappeared[obj["id"]] >= self.max_disappeared:
                    self.deregister(obj["id"])
                else:
                    self.disappeared[obj["id"]] += 1
                    # Decrease confidence when object disappears
                    self.confidence_scores[obj["id"]] = max(0.1, self.confidence_scores[obj["id"]] - 0.1)

        if len(detections) == 0:
            return

        # track objects for each label type
        for label, group in detection_groups.items():
            current_objects = [
                o for o in self.tracked_objects.values() if o["label"] == label
            ]
            current_ids = [o["id"] for o in current_objects]
            
            # Skip if no current objects of this label
            if len(current_objects) == 0:
                for index, obj in enumerate(group):
                    self.register(index, obj)
                continue
            
            # Prepare distance matrix
            D = np.zeros((len(current_objects), len(group)))
            
            # Compute centroids for current objects
            current_centroids = []
            current_boxes = []
            for obj in current_objects:
                centroid_x = int((obj["box"][0] + obj["box"][2]) / 2.0)
                centroid_y = int((obj["box"][1] + obj["box"][3]) / 2.0)
                current_centroids.append((centroid_x, centroid_y))
                current_boxes.append(obj["box"])
            
            # Compute centroids for new detections
            new_centroids = []
            new_boxes = []
            for obj in group:
                centroid_x = int((obj["box"][0] + obj["box"][2]) / 2.0)
                centroid_y = int((obj["box"][1] + obj["box"][3]) / 2.0)
                obj["centroid"] = (centroid_x, centroid_y)
                new_centroids.append((centroid_x, centroid_y))
                new_boxes.append(obj["box"])
            
            # Fill distance matrix with enhanced distance calculation
            for i, (centroid1, box1) in enumerate(zip(current_centroids, current_boxes)):
                for j, (centroid2, box2) in enumerate(zip(new_centroids, new_boxes)):
                    D[i, j] = self.calculate_distance(centroid1, centroid2, box1, box2)
            
            # Find the best matches
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            # Get unique matches (closest ones)
            _, index = np.unique(cols, return_index=True)
            rows = rows[index]
            cols = cols[index]
            
            # Update matched objects
            for row, col in zip(rows, cols):
                objectID = current_ids[row]
                self.update(objectID, group[col])
            
            # Handle unmatched objects
            unusedRows = set(range(D.shape[0])).difference(rows)
            unusedCols = set(range(D.shape[1])).difference(cols)
            
            # Check for disappeared objects
            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    id = current_ids[row]
                    if self.disappeared[id] >= self.max_disappeared:
                        self.deregister(id)
                    else:
                        self.disappeared[id] += 1
                        # Decrease confidence when object is not matched
                        self.confidence_scores[id] = max(0.1, self.confidence_scores[id] - 0.1)
            # Register new objects
            else:
                for col in unusedCols:
                    self.register(col, group[col])
