"""
Integration tests for database operations
"""

import pytest
import time
import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

from arkos.db import Database


@pytest.mark.integration
class TestDatabaseOperations:
    """Integration tests for database operations"""
    
    @pytest.fixture
    def test_db(self, temp_dir):
        """Fixture to create a test database"""
        db_path = temp_dir / "test_db.sqlite"
        db = Database(str(db_path))
        db.migrate()
        return db
    
    def test_event_operations(self, test_db):
        """Test event database operations"""
        # Create test event
        event = {
            "camera": "test_camera",
            "label": "person",
            "sub_label": None,
            "top_score": 0.95,
            "false_positive": False,
            "start_time": time.time(),
            "end_time": None,
            "current_zones": ["yard"],
            "entered_zones": ["yard"],
            "has_clip": True,
            "has_snapshot": True,
            "thumbnail": "/path/to/thumbnail.jpg",
            "region": [0.2, 0.3, 0.4, 0.5],
            "box": [240, 360, 480, 600],
            "area": 288000,
            "ratio": 0.8,
            "stationary": False,
            "motionless_count": 0,
            "position_changes": 5,
        }
        
        # Insert event
        event_id = test_db.insert_event(event)
        
        # Check that event was inserted
        assert event_id is not None, "Event ID should not be None"
        
        # Get event
        retrieved_event = test_db.get_event(event_id)
        
        # Check event properties
        assert retrieved_event["id"] == event_id, "Event ID mismatch"
        assert retrieved_event["camera"] == event["camera"], "Camera mismatch"
        assert retrieved_event["label"] == event["label"], "Label mismatch"
        assert retrieved_event["top_score"] == event["top_score"], "Score mismatch"
        
        # Update event
        update_data = {
            "end_time": time.time(),
            "has_clip": True,
            "has_snapshot": True,
        }
        test_db.update_event(event_id, update_data)
        
        # Get updated event
        updated_event = test_db.get_event(event_id)
        
        # Check updated properties
        assert updated_event["end_time"] == update_data["end_time"], "End time not updated"
        assert updated_event["has_clip"] == update_data["has_clip"], "has_clip not updated"
        assert updated_event["has_snapshot"] == update_data["has_snapshot"], "has_snapshot not updated"
        
        # Delete event
        test_db.delete_event(event_id)
        
        # Check that event was deleted
        deleted_event = test_db.get_event(event_id)
        assert deleted_event is None, "Event was not deleted"
    
    def test_recording_operations(self, test_db):
        """Test recording database operations"""
        # Create test recording
        recording = {
            "camera": "test_camera",
            "path": "/recordings/test_camera/2023-01-01/12-00-00.mp4",
            "start_time": time.time() - 3600,  # 1 hour ago
            "end_time": time.time() - 3540,  # 59 minutes ago
            "duration": 60,
            "motion": True,
            "objects": True,
        }
        
        # Insert recording
        recording_id = test_db.insert_recording(recording)
        
        # Check that recording was inserted
        assert recording_id is not None, "Recording ID should not be None"
        
        # Get recordings
        recordings = test_db.get_recordings(
            camera=recording["camera"],
            start_time=recording["start_time"] - 60,
            end_time=recording["end_time"] + 60,
        )
        
        # Check that recording was retrieved
        assert len(recordings) == 1, "Expected 1 recording"
        assert recordings[0]["id"] == recording_id, "Recording ID mismatch"
        assert recordings[0]["camera"] == recording["camera"], "Camera mismatch"
        assert recordings[0]["path"] == recording["path"], "Path mismatch"
        
        # Delete recording
        test_db.delete_recording(recording_id)
        
        # Check that recording was deleted
        deleted_recordings = test_db.get_recordings(
            camera=recording["camera"],
            start_time=recording["start_time"] - 60,
            end_time=recording["end_time"] + 60,
        )
        assert len(deleted_recordings) == 0, "Recording was not deleted"
    
    def test_timeline_operations(self, test_db):
        """Test timeline database operations"""
        # Create test timeline entry
        timeline_entry = {
            "camera": "test_camera",
            "source": "event",
            "source_id": "test_event_001",
            "start_time": time.time() - 3600,  # 1 hour ago
            "end_time": time.time() - 3540,  # 59 minutes ago
            "data": json.dumps({
                "label": "person",
                "score": 0.95,
                "has_clip": True,
            }),
        }
        
        # Insert timeline entry
        entry_id = test_db.insert_timeline_entry(timeline_entry)
        
        # Check that entry was inserted
        assert entry_id is not None, "Timeline entry ID should not be None"
        
        # Get timeline entries
        entries = test_db.get_timeline_entries(
            camera=timeline_entry["camera"],
            start_time=timeline_entry["start_time"] - 60,
            end_time=timeline_entry["end_time"] + 60,
        )
        
        # Check that entry was retrieved
        assert len(entries) == 1, "Expected 1 timeline entry"
        assert entries[0]["id"] == entry_id, "Timeline entry ID mismatch"
        assert entries[0]["camera"] == timeline_entry["camera"], "Camera mismatch"
        assert entries[0]["source"] == timeline_entry["source"], "Source mismatch"
        assert entries[0]["source_id"] == timeline_entry["source_id"], "Source ID mismatch"
        
        # Delete timeline entry
        test_db.delete_timeline_entry(entry_id)
        
        # Check that entry was deleted
        deleted_entries = test_db.get_timeline_entries(
            camera=timeline_entry["camera"],
            start_time=timeline_entry["start_time"] - 60,
            end_time=timeline_entry["end_time"] + 60,
        )
        assert len(deleted_entries) == 0, "Timeline entry was not deleted"
    
    def test_query_performance(self, test_db):
        """Test database query performance"""
        # Insert many events
        now = time.time()
        event_ids = []
        
        for i in range(100):
            event = {
                "camera": "test_camera",
                "label": "person",
                "sub_label": None,
                "top_score": 0.95,
                "false_positive": False,
                "start_time": now - (i * 60),  # 1 minute apart
                "end_time": now - (i * 60) + 30,
                "current_zones": ["yard"],
                "entered_zones": ["yard"],
                "has_clip": True,
                "has_snapshot": True,
                "thumbnail": f"/path/to/thumbnail_{i}.jpg",
                "region": [0.2, 0.3, 0.4, 0.5],
                "box": [240, 360, 480, 600],
                "area": 288000,
                "ratio": 0.8,
                "stationary": False,
                "motionless_count": 0,
                "position_changes": 5,
            }
            
            event_id = test_db.insert_event(event)
            event_ids.append(event_id)
        
        # Measure query time for different time ranges
        start_time = time.time()
        events = test_db.get_events(
            camera="test_camera",
            start_time=now - 3600,  # 1 hour ago
            end_time=now,
            limit=100,
        )
        query_time = time.time() - start_time
        
        # Check query results
        assert len(events) == 60, f"Expected 60 events, got {len(events)}"
        
        # Check query performance
        assert query_time < 0.1, f"Query took too long: {query_time:.3f} seconds"
        
        # Test query with filters
        start_time = time.time()
        events = test_db.get_events(
            camera="test_camera",
            labels=["person"],
            has_clip=True,
            has_snapshot=True,
            limit=50,
        )
        query_time = time.time() - start_time
        
        # Check query results
        assert len(events) == 50, f"Expected 50 events, got {len(events)}"
        
        # Check query performance
        assert query_time < 0.1, f"Filtered query took too long: {query_time:.3f} seconds"
    
    def test_concurrent_operations(self, test_db):
        """Test concurrent database operations"""
        import threading
        
        # Create test data
        now = time.time()
        
        # Function to insert events
        def insert_events(db, prefix, count):
            for i in range(count):
                event = {
                    "camera": f"{prefix}_camera",
                    "label": "person",
                    "sub_label": None,
                    "top_score": 0.95,
                    "false_positive": False,
                    "start_time": now - (i * 60),
                    "end_time": now - (i * 60) + 30,
                    "current_zones": ["yard"],
                    "entered_zones": ["yard"],
                    "has_clip": True,
                    "has_snapshot": True,
                    "thumbnail": f"/path/to/{prefix}_thumbnail_{i}.jpg",
                    "region": [0.2, 0.3, 0.4, 0.5],
                    "box": [240, 360, 480, 600],
                    "area": 288000,
                    "ratio": 0.8,
                    "stationary": False,
                    "motionless_count": 0,
                    "position_changes": 5,
                }
                
                db.insert_event(event)
        
        # Create threads for concurrent operations
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=insert_events,
                args=(test_db, f"thread_{i}", 20)
            )
            threads.append(thread)
        
        # Start threads
        for thread in threads:
            thread.start()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
        
        # Check that all events were inserted
        events = test_db.get_events(limit=1000)
        assert len(events) == 100, f"Expected 100 events, got {len(events)}"
        
        # Check that events from different threads are present
        cameras = set(event["camera"] for event in events)
        assert len(cameras) == 5, f"Expected 5 cameras, got {len(cameras)}"
        for i in range(5):
            assert f"thread_{i}_camera" in cameras, f"Missing camera thread_{i}_camera"
    
    def test_database_migration(self, temp_dir):
        """Test database migration"""
        # Create database file
        db_path = temp_dir / "migration_test.sqlite"
        
        # Create database with initial schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create a simple initial schema
        cursor.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY,
            camera TEXT NOT NULL,
            label TEXT NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL
        )
        """)
        conn.commit()
        conn.close()
        
        # Create database object and run migrations
        db = Database(str(db_path))
        db.migrate()
        
        # Check that migrations were applied
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check for new columns added by migrations
        cursor.execute("PRAGMA table_info(events)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check for columns that should be added by migrations
        assert "top_score" in column_names, "Migration did not add top_score column"
        assert "has_clip" in column_names, "Migration did not add has_clip column"
        assert "has_snapshot" in column_names, "Migration did not add has_snapshot column"
        
        # Check for new tables added by migrations
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # Check for tables that should be added by migrations
        assert "recordings" in table_names, "Migration did not add recordings table"
        assert "timeline" in table_names, "Migration did not add timeline table"
        
        conn.close()
