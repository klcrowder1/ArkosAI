"""
Integration tests for timeline generation
"""

import pytest
import time
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from arkos.timeline import TimelineManager


@pytest.mark.integration
class TestTimelineGeneration:
    """Integration tests for timeline generation"""
    
    @pytest.fixture
    def timeline_system(self, test_config, test_database):
        """Fixture to set up a timeline system for testing"""
        # Create timeline manager
        timeline_manager = TimelineManager(test_config, test_database)
        
        return {
            "timeline_manager": timeline_manager,
            "database": test_database,
        }
    
    def test_timeline_creation(self, timeline_system, sample_detection_event):
        """Test that timeline entries are created correctly"""
        # Extract components
        timeline_manager = timeline_system["timeline_manager"]
        database = timeline_system["database"]
        
        # Insert test event
        event_id = database.insert_event(sample_detection_event)
        
        # Create timeline entry
        timeline_manager.add_timeline_event(
            camera=sample_detection_event["camera"],
            source="event",
            source_id=event_id,
            start_time=sample_detection_event["start_time"],
            end_time=sample_detection_event["start_time"] + 10,
            data={
                "label": sample_detection_event["label"],
                "score": sample_detection_event["top_score"],
                "has_clip": sample_detection_event["has_clip"],
                "has_snapshot": sample_detection_event["has_snapshot"],
            }
        )
        
        # Get timeline entries
        timeline_entries = database.get_timeline_entries(
            camera=sample_detection_event["camera"],
            start_time=sample_detection_event["start_time"] - 60,
            end_time=sample_detection_event["start_time"] + 60,
        )
        
        # Check that timeline entry was created
        assert len(timeline_entries) > 0, "No timeline entries were created"
        
        # Check timeline entry properties
        entry = timeline_entries[0]
        assert entry["camera"] == sample_detection_event["camera"], "Incorrect camera name"
        assert entry["source"] == "event", "Incorrect source"
        assert entry["source_id"] == event_id, "Incorrect source ID"
        
        # Check timeline entry data
        data = json.loads(entry["data"])
        assert data["label"] == sample_detection_event["label"], "Incorrect label"
        assert data["score"] == sample_detection_event["top_score"], "Incorrect score"
    
    def test_timeline_query(self, timeline_system):
        """Test querying timeline entries"""
        # Extract components
        timeline_manager = timeline_system["timeline_manager"]
        database = timeline_system["database"]
        
        # Create test timeline entries
        now = time.time()
        
        # Create entries for different cameras
        for i in range(3):
            camera = f"camera_{i}"
            
            # Create entries at different times
            for j in range(5):
                start_time = now - (j * 60)  # 1 minute apart
                end_time = start_time + 30
                
                timeline_manager.add_timeline_event(
                    camera=camera,
                    source="recording",
                    source_id=f"rec_{i}_{j}",
                    start_time=start_time,
                    end_time=end_time,
                    data={
                        "type": "motion",
                        "score": 0.8,
                    }
                )
        
        # Query timeline for a specific camera
        entries = database.get_timeline_entries(
            camera="camera_0",
            start_time=now - 300,  # 5 minutes ago
            end_time=now,
        )
        
        # Check that entries were returned
        assert len(entries) == 5, f"Expected 5 entries, got {len(entries)}"
        
        # Query timeline for a specific time range
        entries = database.get_timeline_entries(
            camera="camera_1",
            start_time=now - 180,  # 3 minutes ago
            end_time=now - 60,  # 1 minute ago
        )
        
        # Check that entries were returned
        assert len(entries) == 2, f"Expected 2 entries, got {len(entries)}"
        
        # Query timeline for all cameras
        entries = database.get_timeline_entries(
            start_time=now - 60,  # 1 minute ago
            end_time=now,
        )
        
        # Check that entries were returned
        assert len(entries) == 3, f"Expected 3 entries, got {len(entries)}"
    
    def test_timeline_aggregation(self, timeline_system):
        """Test aggregating timeline entries"""
        # Extract components
        timeline_manager = timeline_system["timeline_manager"]
        database = timeline_system["database"]
        
        # Create test timeline entries
        now = time.time()
        camera = "test_camera"
        
        # Create overlapping entries
        timeline_manager.add_timeline_event(
            camera=camera,
            source="recording",
            source_id="rec_1",
            start_time=now - 60,
            end_time=now - 30,
            data={"type": "motion"}
        )
        
        timeline_manager.add_timeline_event(
            camera=camera,
            source="recording",
            source_id="rec_2",
            start_time=now - 40,
            end_time=now - 10,
            data={"type": "motion"}
        )
        
        # Aggregate timeline entries
        aggregated = timeline_manager.aggregate_timeline(
            camera=camera,
            start_time=now - 120,
            end_time=now,
            interval=30  # 30-second intervals
        )
        
        # Check aggregation
        assert len(aggregated) > 0, "No aggregated entries were returned"
        
        # Check that overlapping entries are counted correctly
        # The entries overlap from now-40 to now-30, so there should be
        # an interval with a count of 2
        has_overlap = False
        for entry in aggregated:
            if entry["count"] == 2:
                has_overlap = True
                break
        
        assert has_overlap, "Overlapping entries were not aggregated correctly"
    
    def test_timeline_cleanup(self, timeline_system):
        """Test cleaning up old timeline entries"""
        # Extract components
        timeline_manager = timeline_system["timeline_manager"]
        database = timeline_system["database"]
        
        # Create test timeline entries
        now = time.time()
        camera = "test_camera"
        
        # Create old entries (30 days old)
        old_time = now - (30 * 24 * 60 * 60)
        
        for i in range(5):
            timeline_manager.add_timeline_event(
                camera=camera,
                source="recording",
                source_id=f"old_rec_{i}",
                start_time=old_time - (i * 60),
                end_time=old_time - (i * 60) + 30,
                data={"type": "motion"}
            )
        
        # Create recent entries
        for i in range(5):
            timeline_manager.add_timeline_event(
                camera=camera,
                source="recording",
                source_id=f"new_rec_{i}",
                start_time=now - (i * 60),
                end_time=now - (i * 60) + 30,
                data={"type": "motion"}
            )
        
        # Count entries before cleanup
        all_entries = database.get_timeline_entries(
            camera=camera,
            start_time=0,
            end_time=now + 1,
        )
        count_before = len(all_entries)
        
        # Clean up old entries (older than 7 days)
        cleanup_time = now - (7 * 24 * 60 * 60)
        timeline_manager.cleanup_timeline(cleanup_time)
        
        # Count entries after cleanup
        all_entries = database.get_timeline_entries(
            camera=camera,
            start_time=0,
            end_time=now + 1,
        )
        count_after = len(all_entries)
        
        # Check that old entries were removed
        assert count_after == count_before - 5, "Old entries were not cleaned up"
        
        # Check that recent entries remain
        recent_entries = database.get_timeline_entries(
            camera=camera,
            start_time=now - 300,
            end_time=now,
        )
        assert len(recent_entries) == 5, "Recent entries were incorrectly removed"
