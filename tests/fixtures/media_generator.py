#!/usr/bin/env python3
"""
Media Generator for Arkos AI Testing

This script generates synthetic test videos and audio files for Arkos AI testing.
"""

import os
import sys
import argparse
import random
import math
import time
import wave
import struct
import numpy as np
import cv2
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional


class MediaGenerator:
    """Generate synthetic test media for Arkos AI testing."""

    def __init__(self, output_dir: Path, duration: int = 10, fps: int = 30, resolution: Tuple[int, int] = (1280, 720)):
        """Initialize the media generator.
        
        Args:
            output_dir: Directory to save generated media
            duration: Duration of generated videos in seconds
            fps: Frames per second for generated videos
            resolution: Resolution of generated videos (width, height)
        """
        self.output_dir = output_dir
        self.duration = duration
        self.fps = fps
        self.resolution = resolution
        
        # Create output directories
        self.video_dir = output_dir / "sample_videos"
        self.audio_dir = output_dir / "sample_audio"
        self.video_dir.mkdir(exist_ok=True, parents=True)
        self.audio_dir.mkdir(exist_ok=True, parents=True)
        
        # Set random seed for reproducibility
        random.seed(42)
        np.random.seed(42)

    def generate_all(self):
        """Generate all test media."""
        print("Generating test media...")
        
        # Generate videos
        self.generate_standard_video()
        self.generate_ptz_video()
        self.generate_audio_video()
        self.generate_multi_object_video()
        self.generate_license_plate_video()
        
        # Generate audio
        self.generate_dog_bark_audio()
        self.generate_glass_break_audio()
        self.generate_car_alarm_audio()
        
        print("Test media generation complete!")

    def generate_standard_video(self):
        """Generate a standard test video with a single moving person."""
        print("Generating standard test video...")
        
        # Create video writer
        output_path = self.video_dir / "standard.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
        
        # Generate frames with a moving person
        width, height = self.resolution
        total_frames = self.duration * self.fps
        
        # Person parameters
        person_width = 100
        person_height = 200
        person_x = width // 4
        person_y = height // 2
        person_speed_x = 3
        person_speed_y = 1
        
        for i in range(total_frames):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add background elements
            self._add_background(frame)
            
            # Update person position
            person_x += person_speed_x
            person_y += person_speed_y
            
            # Bounce off edges
            if person_x <= 0 or person_x + person_width >= width:
                person_speed_x *= -1
            if person_y <= 0 or person_y + person_height >= height:
                person_speed_y *= -1
            
            # Draw person
            self._draw_person(frame, person_x, person_y, person_width, person_height)
            
            # Add timestamp
            self._add_timestamp(frame, i / self.fps)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        print(f"Standard test video saved to {output_path}")

    def generate_ptz_video(self):
        """Generate a PTZ test video with simulated pan, tilt, and zoom movements."""
        print("Generating PTZ test video...")
        
        # Create video writer
        output_path = self.video_dir / "ptz.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
        
        # Generate frames with PTZ movements
        width, height = self.resolution
        total_frames = self.duration * self.fps
        
        # PTZ parameters
        pan_angle = 0
        tilt_angle = 0
        zoom_level = 1.0
        pan_speed = 1
        tilt_speed = 0.5
        zoom_speed = 0.02
        
        # Object parameters
        objects = [
            {"type": "person", "x": width // 4, "y": height // 2, "width": 100, "height": 200},
            {"type": "car", "x": width // 2, "y": height * 3 // 4, "width": 200, "height": 100},
            {"type": "dog", "x": width * 3 // 4, "y": height // 3, "width": 80, "height": 60},
        ]
        
        for i in range(total_frames):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add background elements
            self._add_background(frame)
            
            # Update PTZ parameters
            if i < total_frames // 3:
                # Pan phase
                pan_angle += pan_speed
            elif i < total_frames * 2 // 3:
                # Tilt phase
                tilt_angle += tilt_speed
            else:
                # Zoom phase
                zoom_level += zoom_speed
                if zoom_level > 2.0:
                    zoom_level = 2.0
            
            # Apply PTZ transformation
            M = self._get_ptz_transform(width, height, pan_angle, tilt_angle, zoom_level)
            frame = cv2.warpAffine(frame, M, (width, height))
            
            # Draw objects
            for obj in objects:
                if obj["type"] == "person":
                    self._draw_person(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                elif obj["type"] == "car":
                    self._draw_car(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                elif obj["type"] == "dog":
                    self._draw_dog(frame, obj["x"], obj["y"], obj["width"], obj["height"])
            
            # Add timestamp and PTZ info
            self._add_timestamp(frame, i / self.fps)
            cv2.putText(frame, f"Pan: {pan_angle:.1f}, Tilt: {tilt_angle:.1f}, Zoom: {zoom_level:.1f}",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        print(f"PTZ test video saved to {output_path}")

    def generate_audio_video(self):
        """Generate a test video with audio events."""
        print("Generating audio test video...")
        
        # Create video writer
        output_path = self.video_dir / "audio.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
        
        # Generate frames with a dog that barks
        width, height = self.resolution
        total_frames = self.duration * self.fps
        
        # Dog parameters
        dog_width = 80
        dog_height = 60
        dog_x = width // 2
        dog_y = height // 2
        dog_speed_x = 2
        dog_speed_y = 1
        
        # Barking parameters
        barking_frames = [int(self.fps * 2), int(self.fps * 5), int(self.fps * 8)]
        barking_duration = int(self.fps * 0.5)
        
        for i in range(total_frames):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add background elements
            self._add_background(frame)
            
            # Update dog position
            dog_x += dog_speed_x
            dog_y += dog_speed_y
            
            # Bounce off edges
            if dog_x <= 0 or dog_x + dog_width >= width:
                dog_speed_x *= -1
            if dog_y <= 0 or dog_y + dog_height >= height:
                dog_speed_y *= -1
            
            # Draw dog
            self._draw_dog(frame, dog_x, dog_y, dog_width, dog_height)
            
            # Add barking indicator
            is_barking = False
            for bark_frame in barking_frames:
                if i >= bark_frame and i < bark_frame + barking_duration:
                    is_barking = True
                    break
            
            if is_barking:
                cv2.putText(frame, "Barking!", (dog_x, dog_y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Add timestamp
            self._add_timestamp(frame, i / self.fps)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        print(f"Audio test video saved to {output_path}")

    def generate_multi_object_video(self):
        """Generate a test video with multiple moving objects."""
        print("Generating multi-object test video...")
        
        # Create video writer
        output_path = self.video_dir / "multi_object.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
        
        # Generate frames with multiple moving objects
        width, height = self.resolution
        total_frames = self.duration * self.fps
        
        # Create objects
        objects = []
        for i in range(5):
            obj_type = random.choice(["person", "car", "dog", "bicycle", "truck"])
            
            if obj_type == "person":
                obj_width = random.randint(80, 120)
                obj_height = random.randint(160, 240)
            elif obj_type == "car":
                obj_width = random.randint(180, 220)
                obj_height = random.randint(80, 120)
            elif obj_type == "dog":
                obj_width = random.randint(60, 100)
                obj_height = random.randint(40, 80)
            elif obj_type == "bicycle":
                obj_width = random.randint(100, 140)
                obj_height = random.randint(60, 100)
            elif obj_type == "truck":
                obj_width = random.randint(220, 280)
                obj_height = random.randint(100, 140)
            
            objects.append({
                "type": obj_type,
                "x": random.randint(0, width - obj_width),
                "y": random.randint(0, height - obj_height),
                "width": obj_width,
                "height": obj_height,
                "speed_x": random.randint(-3, 3),
                "speed_y": random.randint(-3, 3),
            })
        
        for i in range(total_frames):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add background elements
            self._add_background(frame)
            
            # Update and draw objects
            for obj in objects:
                # Update position
                obj["x"] += obj["speed_x"]
                obj["y"] += obj["speed_y"]
                
                # Bounce off edges
                if obj["x"] <= 0 or obj["x"] + obj["width"] >= width:
                    obj["speed_x"] *= -1
                if obj["y"] <= 0 or obj["y"] + obj["height"] >= height:
                    obj["speed_y"] *= -1
                
                # Draw object
                if obj["type"] == "person":
                    self._draw_person(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                elif obj["type"] == "car":
                    self._draw_car(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                elif obj["type"] == "dog":
                    self._draw_dog(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                elif obj["type"] == "bicycle":
                    self._draw_bicycle(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                elif obj["type"] == "truck":
                    self._draw_truck(frame, obj["x"], obj["y"], obj["width"], obj["height"])
                
                # Add label
                cv2.putText(frame, obj["type"], (obj["x"], obj["y"] - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add timestamp
            self._add_timestamp(frame, i / self.fps)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        print(f"Multi-object test video saved to {output_path}")

    def generate_license_plate_video(self):
        """Generate a test video with cars that have visible license plates."""
        print("Generating license plate test video...")
        
        # Create video writer
        output_path = self.video_dir / "license_plate.mp4"
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, self.fps, self.resolution)
        
        # Generate frames with cars that have license plates
        width, height = self.resolution
        total_frames = self.duration * self.fps
        
        # Create cars with license plates
        cars = []
        for i in range(3):
            car_width = random.randint(180, 220)
            car_height = random.randint(80, 120)
            
            # Generate random license plate
            plate = self._generate_license_plate()
            
            cars.append({
                "x": random.randint(0, width - car_width),
                "y": random.randint(0, height - car_height),
                "width": car_width,
                "height": car_height,
                "speed_x": random.randint(-3, 3),
                "speed_y": random.randint(-3, 3),
                "plate": plate,
            })
        
        for i in range(total_frames):
            # Create blank frame
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Add background elements
            self._add_background(frame)
            
            # Update and draw cars
            for car in cars:
                # Update position
                car["x"] += car["speed_x"]
                car["y"] += car["speed_y"]
                
                # Bounce off edges
                if car["x"] <= 0 or car["x"] + car["width"] >= width:
                    car["speed_x"] *= -1
                if car["y"] <= 0 or car["y"] + car["height"] >= height:
                    car["speed_y"] *= -1
                
                # Draw car
                self._draw_car(frame, car["x"], car["y"], car["width"], car["height"])
                
                # Draw license plate
                plate_width = car["width"] // 2
                plate_height = car["height"] // 5
                plate_x = car["x"] + (car["width"] - plate_width) // 2
                plate_y = car["y"] + car["height"] - plate_height - 5
                
                cv2.rectangle(frame, (plate_x, plate_y), (plate_x + plate_width, plate_y + plate_height), (255, 255, 255), -1)
                cv2.putText(frame, car["plate"], (plate_x + 5, plate_y + plate_height - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Add timestamp
            self._add_timestamp(frame, i / self.fps)
            
            # Write frame
            out.write(frame)
        
        # Release video writer
        out.release()
        print(f"License plate test video saved to {output_path}")

    def generate_dog_bark_audio(self):
        """Generate a dog bark audio sample."""
        print("Generating dog bark audio...")
        
        # Create audio file
        output_path = self.audio_dir / "dog_bark.wav"
        
        # Audio parameters
        sample_rate = 44100
        duration = 2.0
        num_samples = int(sample_rate * duration)
        
        # Generate dog bark waveform
        t = np.linspace(0, duration, num_samples, False)
        bark = np.zeros(num_samples)
        
        # Add bark components
        for i in range(3):
            start = int(sample_rate * (0.2 + i * 0.6))
            end = int(start + sample_rate * 0.3)
            
            if end > num_samples:
                end = num_samples
            
            bark_segment = np.sin(2 * np.pi * 300 * t[start:end]) * 0.3
            bark_segment += np.sin(2 * np.pi * 600 * t[start:end]) * 0.2
            bark_segment += np.sin(2 * np.pi * 1200 * t[start:end]) * 0.1
            bark_segment += np.random.normal(0, 0.1, end - start)
            
            # Apply envelope
            envelope = np.ones(end - start)
            attack = int((end - start) * 0.1)
            release = int((end - start) * 0.3)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-release:] = np.linspace(1, 0, release)
            
            bark_segment *= envelope
            bark[start:end] = bark_segment
        
        # Normalize
        bark = bark / np.max(np.abs(bark))
        
        # Convert to 16-bit PCM
        bark = (bark * 32767).astype(np.int16)
        
        # Write WAV file
        with wave.open(str(output_path), 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(bark.tobytes())
        
        print(f"Dog bark audio saved to {output_path}")

    def generate_glass_break_audio(self):
        """Generate a glass break audio sample."""
        print("Generating glass break audio...")
        
        # Create audio file
        output_path = self.audio_dir / "glass_break.wav"
        
        # Audio parameters
        sample_rate = 44100
        duration = 1.5
        num_samples = int(sample_rate * duration)
        
        # Generate glass break waveform
        t = np.linspace(0, duration, num_samples, False)
        glass_break = np.zeros(num_samples)
        
        # Add initial impact
        impact_start = int(sample_rate * 0.2)
        impact_duration = int(sample_rate * 0.05)
        impact_end = impact_start + impact_duration
        
        impact = np.random.normal(0, 1, impact_duration)
        impact *= np.linspace(1, 0, impact_duration)
        glass_break[impact_start:impact_end] = impact
        
        # Add glass shards
        for i in range(20):
            shard_start = impact_end + int(sample_rate * random.uniform(0, 0.8))
            shard_duration = int(sample_rate * random.uniform(0.02, 0.1))
            shard_end = shard_start + shard_duration
            
            if shard_end > num_samples:
                shard_end = num_samples
            
            shard = np.random.normal(0, 0.5, shard_end - shard_start)
            shard *= np.linspace(1, 0, shard_end - shard_start)
            
            if shard_start < num_samples:
                glass_break[shard_start:shard_end] += shard[:shard_end - shard_start]
        
        # Add high-frequency components
        glass_break += np.sin(2 * np.pi * 4000 * t) * 0.1 * np.exp(-5 * t)
        glass_break += np.sin(2 * np.pi * 6000 * t) * 0.05 * np.exp(-8 * t)
        
        # Normalize
        glass_break = glass_break / np.max(np.abs(glass_break))
        
        # Convert to 16-bit PCM
        glass_break = (glass_break * 32767).astype(np.int16)
        
        # Write WAV file
        with wave.open(str(output_path), 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(glass_break.tobytes())
        
        print(f"Glass break audio saved to {output_path}")

    def generate_car_alarm_audio(self):
        """Generate a car alarm audio sample."""
        print("Generating car alarm audio...")
        
        # Create audio file
        output_path = self.audio_dir / "car_alarm.wav"
        
        # Audio parameters
        sample_rate = 44100
        duration = 3.0
        num_samples = int(sample_rate * duration)
        
        # Generate car alarm waveform
        t = np.linspace(0, duration, num_samples, False)
        car_alarm = np.zeros(num_samples)
        
        # Add alarm beeps
        beep_freq = 800
        beep_duration = 0.2
        beep_interval = 0.4
        num_beeps = int(duration / beep_interval)
        
        for i in range(num_beeps):
            beep_start = int(sample_rate * i * beep_interval)
            beep_end = int(beep_start + sample_rate * beep_duration)
            
            if beep_end > num_samples:
                beep_end = num_samples
            
            beep = np.sin(2 * np.pi * beep_freq * t[beep_start:beep_end])
            
            # Alternate between two frequencies
            if i % 2 == 1:
                beep = np.sin(2 * np.pi * (beep_freq * 1.2) * t[beep_start:beep_end])
            
            # Apply envelope
            envelope = np.ones(beep_end - beep_start)
            attack = int((beep_end - beep_start) * 0.1)
            release = int((beep_end - beep_start) * 0.1)
            envelope[:attack] = np.linspace(0, 1, attack)
            envelope[-release:] = np.linspace(1, 0, release)
            
            beep *= envelope
            car_alarm[beep_start:beep_end] = beep
        
        # Normalize
        car_alarm = car_alarm / np.max(np.abs(car_alarm))
        
        # Convert to 16-bit PCM
        car_alarm = (car_alarm * 32767).astype(np.int16)
        
        # Write WAV file
        with wave.open(str(output_path), 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(car_alarm.tobytes())
        
        print(f"Car alarm audio saved to {output_path}")

    def _add_background(self, frame):
        """Add background elements to a frame."""
        height, width = frame.shape[:2]
        
        # Add sky
        cv2.rectangle(frame, (0, 0), (width, height // 3), (128, 128, 255), -1)
        
        # Add ground
        cv2.rectangle(frame, (0, height // 3), (width, height), (64, 128, 64), -1)
        
        # Add horizon line
        cv2.line(frame, (0, height // 3), (width, height // 3), (255, 255, 255), 2)
        
        # Add random buildings
        for i in range(5):
            building_x = width * i // 5
            building_width = width // 6
            building_height = random.randint(height // 6, height // 3)
            building_y = height // 3 - building_height
            
            cv2.rectangle(frame, (building_x, building_y), (building_x + building_width, height // 3), (128, 128, 128), -1)
            
            # Add windows
            for j in range(3):
                for k in range(4):
                    window_x = building_x + building_width // 8 + j * building_width // 4
                    window_y = building_y + building_height // 5 + k * building_height // 5
                    window_width = building_width // 8
                    window_height = building_height // 8
                    
                    cv2.rectangle(frame, (window_x, window_y), (window_x + window_width, window_y + window_height), (255, 255, 128), -1)

    def _draw_person(self, frame, x, y, width, height):
        """Draw a person on a frame."""
        # Draw body
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 0, 255), -1)
        
        # Draw head
        head_size = width // 2
        head_x = x + (width - head_size) // 2
        head_y = y
        cv2.circle(frame, (head_x + head_size // 2, head_y + head_size // 2), head_size // 2, (255, 200, 200), -1)
        
        # Draw arms
        arm_width = width // 3
        arm_height = height // 2
        cv2.rectangle(frame, (x - arm_width, y + height // 4), (x, y + height // 4 + arm_height), (0, 0, 255), -1)
        cv2.rectangle(frame, (x + width, y + height // 4), (x + width + arm_width, y + height // 4 + arm_height), (0, 0, 255), -1)
        
        # Draw legs
        leg_width = width // 3
        leg_height = height // 2
        cv2.rectangle(frame, (x + width // 4 - leg_width // 2, y + height), (x + width // 4 + leg_width // 2, y + height + leg_height), (0, 0, 255), -1)
        cv2.rectangle(frame, (x + width * 3 // 4 - leg_width // 2, y + height), (x + width * 3 // 4 + leg_width // 2, y + height + leg_height), (0, 0, 255), -1)

    def _draw_car(self, frame, x, y, width, height):
        """Draw a car on a frame."""
        # Draw body
        cv2.rectangle(frame, (x, y + height // 3), (x + width, y + height), (0, 0, 255), -1)
        
        # Draw roof
        roof_points = np.array([
            [x + width // 4, y + height // 3],
            [x + width * 3 // 4, y + height // 3],
            [x + width * 2 // 3, y],
            [x + width // 3, y]
        ])
        cv2.fillPoly(frame, [roof_points], (0, 0, 255))
        
        # Draw windows
        window_points = np.array([
            [x + width // 3, y + height // 6],
            [x + width * 2 // 3, y + height // 6],
            [x + width * 2 // 3, y + height // 3],
            [x + width // 3, y + height // 3]
        ])
        cv2.fillPoly(frame, [window_points], (128, 128, 255))
        
        # Draw wheels
        wheel_radius = height // 4
        cv2.circle(frame, (x + width // 4, y + height), wheel_radius, (0, 0, 0), -1)
        cv2.circle(frame, (x + width * 3 // 4, y + height), wheel_radius, (0, 0, 0), -1)
        
        # Draw wheel hubs
        cv2.circle(frame, (x + width // 4, y + height), wheel_radius // 2, (128, 128, 128), -1)
        cv2.circle(frame, (x + width * 3 // 4, y + height), wheel_radius // 2, (128, 128, 128), -1)

    def _draw_dog(self, frame, x, y, width, height):
        """Draw a dog on a frame."""
        # Draw body
        cv2.ellipse(frame, (x + width // 2, y + height // 2), (width // 2, height // 3), 0, 0, 360, (150, 75, 0), -1)
        
        # Draw head
        head_size = width // 3
        head_x = x + width - head_size // 2
        head_y = y
        cv2.circle(frame, (head_x, head_y + head_size // 2), head_size // 2, (150, 75, 0), -1)
        
        # Draw ears
        ear_width = head_size // 2
        ear_height = head_size // 2
        cv2.ellipse(frame, (head_x - ear_width // 2, head_y), (ear_width // 2, ear_height // 2), 0, 0, 360, (150, 75, 0), -1)
        cv2.ellipse(frame, (head_x + ear_width // 2, head_y), (ear_width // 2, ear_height // 2), 0, 0, 360, (150, 75, 0), -1)
        
        # Draw legs
        leg_width = width // 8
        leg_height = height // 2
        cv2.rectangle(frame, (x + width // 4 - leg_width // 2, y + height // 2), 
                     (x + width // 4 + leg_width // 2, y + height // 2 + leg_height), (150, 75, 0), -1)
        cv2.rectangle(frame, (x + width * 3 // 4 - leg_width // 2, y + height // 2), 
                     (x + width * 3 // 4 + leg_width // 2, y + height // 2 + leg_height), (150, 75, 0), -1)
        
        # Draw tail
        tail_width = width // 6
        tail_height = height // 3
        cv2.ellipse(frame, (x, y + height // 2), (tail_width, tail_height // 2), 0, 0, 360, (150, 75, 0), -1)

    def _draw_bicycle(self, frame, x, y, width, height):
        """Draw a bicycle on a frame."""
        # Draw frame
        cv2.line(frame, (x + width // 3, y + height * 2 // 3), (x + width * 2 // 3, y + height * 2 // 3), (0, 255, 0), 3)
        cv2.line(frame, (x + width // 3, y + height * 2 // 3), (x + width // 2, y + height // 3), (0, 255, 0), 3)
        cv2.line(frame, (x + width * 2 // 3, y + height * 2 // 3), (x + width // 2, y + height // 3), (0, 255, 0), 3)
        cv2.line(frame, (x + width // 2, y + height // 3), (x + width * 3 // 4, y + height // 3), (0, 255, 0), 3)
        
        # Draw wheels
        wheel_radius = height // 3
        cv2.circle(frame, (x + width // 3, y + height * 2 // 3), wheel_radius, (0, 0, 0), 2)
        cv2.circle(frame, (x + width * 2 // 3, y + height * 2 // 3), wheel_radius, (0, 0, 0), 2)
        
        # Draw spokes
        for i in range(8):
            angle = i * np.pi / 4
            x1 = int(x + width // 3 + wheel_radius * np.cos(angle))
            y1 = int(y + height * 2 // 3 + wheel_radius * np.sin(angle))
            cv2.line(frame, (x + width // 3, y + height * 2 // 3), (x1, y1), (128, 128, 128), 1)
            
            x2 = int(x + width * 2 // 3 + wheel_radius * np.cos(angle))
            y2 = int(y + height * 2 // 3 + wheel_radius * np.sin(angle))
            cv2.line(frame, (x + width * 2 // 3, y + height * 2 // 3), (x2, y2), (128, 128, 128), 1)
        
        # Draw handlebars
        cv2.line(frame, (x + width * 3 // 4, y + height // 3), (x + width * 3 // 4, y + height // 6), (0, 255, 0), 3)
        cv2.line(frame, (x + width * 3 // 4, y + height // 6), (x + width * 3 // 4 - width // 6, y + height // 6), (0, 255, 0), 3)
        
        # Draw seat
        cv2.ellipse(frame, (x + width // 2, y + height // 3), (width // 10, height // 10), 0, 0, 360, (0, 0, 0), -1)

    def _draw_truck(self, frame, x, y, width, height):
        """Draw a truck on a frame."""
        # Draw cab
        cab_width = width // 3
        cab_height = height * 2 // 3
        cv2.rectangle(frame, (x, y), (x + cab_width, y + cab_height), (255, 0, 0), -1)
        
        # Draw cargo area
        cargo_height = height * 2 // 3
        cv2.rectangle(frame, (x + cab_width, y), (x + width, y + cargo_height), (255, 0, 0), -1)
        
        # Draw windows
        window_width = cab_width * 2 // 3
        window_height = cab_height // 3
        window_x = x + (cab_width - window_width) // 2
        window_y = y + cab_height // 6
        cv2.rectangle(frame, (window_x, window_y), (window_x + window_width, window_y + window_height), (128, 128, 255), -1)
        
        # Draw wheels
        wheel_radius = height // 5
        wheel_y = y + height - wheel_radius
        
        # Front wheel
        cv2.circle(frame, (x + cab_width // 2, wheel_y), wheel_radius, (0, 0, 0), -1)
        cv2.circle(frame, (x + cab_width // 2, wheel_y), wheel_radius // 2, (128, 128, 128), -1)
        
        # Rear wheels
        cv2.circle(frame, (x + cab_width + (width - cab_width) // 4, wheel_y), wheel_radius, (0, 0, 0), -1)
        cv2.circle(frame, (x + cab_width + (width - cab_width) // 4, wheel_y), wheel_radius // 2, (128, 128, 128), -1)
        
        cv2.circle(frame, (x + cab_width + (width - cab_width) * 3 // 4, wheel_y), wheel_radius, (0, 0, 0), -1)
        cv2.circle(frame, (x + cab_width + (width - cab_width) * 3 // 4, wheel_y), wheel_radius // 2, (128, 128, 128), -1)

    def _add_timestamp(self, frame, time_seconds):
        """Add a timestamp to a frame."""
        timestamp = f"Time: {time_seconds:.2f}s"
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    def _get_ptz_transform(self, width, height, pan_angle, tilt_angle, zoom_level):
        """Get a transformation matrix for PTZ simulation."""
        # Create transformation matrix
        M = np.eye(2, 3, dtype=np.float32)
        
        # Apply pan (horizontal rotation)
        pan_rad = np.radians(pan_angle)
        M[0, 2] = -pan_rad * width / 10
        
        # Apply tilt (vertical rotation)
        tilt_rad = np.radians(tilt_angle)
        M[1, 2] = -tilt_rad * height / 10
        
        # Apply zoom
        M[0, 0] = zoom_level
        M[1, 1] = zoom_level
        M[0, 2] += (1 - zoom_level) * width / 2
        M[1, 2] += (1 - zoom_level) * height / 2
        
        return M

    def _generate_license_plate(self):
        """Generate a random license plate."""
        letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        numbers = "0123456789"
        
        # Generate plate in format: ABC-1234
        plate = ""
        for _ in range(3):
            plate += random.choice(letters)
        
        plate += "-"
        
        for _ in range(4):
            plate += random.choice(numbers)
        
        return plate


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate test media for Arkos AI testing")
    parser.add_argument("--output-dir", default="tests/fixtures", help="Output directory for generated media")
    parser.add_argument("--duration", type=int, default=10, help="Duration of generated videos in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second for generated videos")
    parser.add_argument("--resolution", default="1280x720", help="Resolution of generated videos (WxH)")
    args = parser.parse_args()
    
    # Parse resolution
    width, height = map(int, args.resolution.split("x"))
    
    # Create media generator
    output_dir = Path(args.output_dir)
    generator = MediaGenerator(output_dir, args.duration, args.fps, (width, height))
    
    # Generate all test media
    generator.generate_all()


if __name__ == "__main__":
    main()
