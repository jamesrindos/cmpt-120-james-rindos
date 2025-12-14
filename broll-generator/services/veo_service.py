"""
Google Veo 3.1 API Service
AI video generation from images
"""

import os
import httpx
import asyncio
import base64
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class GeneratedClip:
    """Represents a generated video clip"""
    name: str
    url: str
    thumbnail: str
    duration: float
    resolution: str
    poi_name: str
    motion_type: str
    style: str


class VeoService:
    """Service for generating video clips using Google Veo 3.1"""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    # Motion presets for B-roll
    MOTION_PRESETS = {
        "dolly_in": {
            "description": "Slow dolly push in towards subject",
            "camera_motion": "dolly_forward",
            "speed": "slow",
            "intensity": 0.3
        },
        "dolly_out": {
            "description": "Slow dolly pull back from subject",
            "camera_motion": "dolly_backward",
            "speed": "slow",
            "intensity": 0.3
        },
        "pan_left": {
            "description": "Smooth pan from right to left",
            "camera_motion": "pan_left",
            "speed": "medium",
            "intensity": 0.4
        },
        "pan_right": {
            "description": "Smooth pan from left to right",
            "camera_motion": "pan_right",
            "speed": "medium",
            "intensity": 0.4
        },
        "tilt_up": {
            "description": "Slow tilt upward revealing height",
            "camera_motion": "tilt_up",
            "speed": "slow",
            "intensity": 0.35
        },
        "tilt_down": {
            "description": "Slow tilt downward",
            "camera_motion": "tilt_down",
            "speed": "slow",
            "intensity": 0.35
        },
        "orbit_left": {
            "description": "Orbital movement around subject to the left",
            "camera_motion": "orbit_left",
            "speed": "medium",
            "intensity": 0.5
        },
        "orbit_right": {
            "description": "Orbital movement around subject to the right",
            "camera_motion": "orbit_right",
            "speed": "medium",
            "intensity": 0.5
        },
        "static_ambient": {
            "description": "Static shot with subtle ambient motion",
            "camera_motion": "static",
            "speed": "slow",
            "intensity": 0.15
        },
        "parallax": {
            "description": "Subtle parallax effect with depth",
            "camera_motion": "parallax",
            "speed": "very_slow",
            "intensity": 0.25
        },
        "tracking": {
            "description": "Tracking shot following motion",
            "camera_motion": "tracking",
            "speed": "medium",
            "intensity": 0.45
        },
        "crane_up": {
            "description": "Crane shot rising upward",
            "camera_motion": "crane_up",
            "speed": "slow",
            "intensity": 0.4
        }
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_VEO_API_KEY")
        self.client = httpx.AsyncClient(timeout=120.0)

    def determine_motion_types(self, creative_direction: str) -> List[str]:
        """
        Determine appropriate motion types based on creative direction

        Args:
            creative_direction: User's creative direction text

        Returns:
            List of motion preset keys
        """
        direction_lower = creative_direction.lower()
        motions = []

        motion_keywords = {
            "dolly_in": ["dolly", "push in", "approach", "closer"],
            "dolly_out": ["pull back", "reveal", "pull out"],
            "pan_left": ["pan", "sweep left"],
            "pan_right": ["pan", "sweep right"],
            "tilt_up": ["tilt up", "look up", "vertical", "height"],
            "tilt_down": ["tilt down", "look down"],
            "orbit_left": ["orbit", "around", "circular"],
            "orbit_right": ["orbit", "around", "circular"],
            "static_ambient": ["static", "still", "subtle", "minimal"],
            "parallax": ["parallax", "depth", "layered", "3d"],
            "tracking": ["tracking", "follow", "dynamic"],
            "crane_up": ["crane", "rising", "aerial"]
        }

        for motion, keywords in motion_keywords.items():
            if any(keyword in direction_lower for keyword in keywords):
                motions.append(motion)

        # Default cinematic motions if none specified
        if not motions:
            motions = ["dolly_in", "pan_left", "static_ambient", "parallax", "orbit_left"]

        return motions

    def build_prompt(
        self,
        poi_name: str,
        motion_type: str,
        creative_direction: str
    ) -> str:
        """
        Build a prompt for Veo video generation

        Args:
            poi_name: Name of the point of interest
            motion_type: Type of camera motion
            creative_direction: User's creative direction

        Returns:
            Formatted prompt string
        """
        motion_preset = self.MOTION_PRESETS.get(motion_type, self.MOTION_PRESETS["dolly_in"])

        prompt = f"""Generate a cinematic B-roll video clip of {poi_name}.

Camera Motion: {motion_preset['description']}
Movement Speed: {motion_preset['speed']}

Style Guidelines from Creative Direction:
{creative_direction}

Requirements:
- Smooth, professional camera movement
- Subtle ambient motion (people walking, leaves moving, light changes)
- Photorealistic quality
- Cinematic aspect ratio (16:9)
- Natural lighting enhancement
- No text overlays or graphics
- Duration: 4-6 seconds
"""
        return prompt

    async def generate_video(
        self,
        image_data: bytes,
        poi_name: str,
        motion_type: str,
        creative_direction: str,
        duration: float = 5.0
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a video clip from an image using Veo 3.1

        Args:
            image_data: Enhanced image bytes
            poi_name: Name of the point of interest
            motion_type: Type of camera motion to apply
            creative_direction: User's creative direction
            duration: Desired clip duration in seconds

        Returns:
            Dict with video URL and metadata, or None if failed
        """
        # Encode image
        image_b64 = base64.b64encode(image_data).decode('utf-8')

        # Build prompt
        prompt = self.build_prompt(poi_name, motion_type, creative_direction)

        # Get motion preset
        motion_preset = self.MOTION_PRESETS.get(motion_type, self.MOTION_PRESETS["dolly_in"])

        # Request payload for Veo 3.1
        payload = {
            "model": "veo-3.1",
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_b64
                            }
                        }
                    ]
                }
            ],
            "generation_config": {
                "video_length_seconds": duration,
                "fps": 24,
                "resolution": "1920x1080",
                "camera_motion": motion_preset["camera_motion"],
                "motion_intensity": motion_preset["intensity"]
            }
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = await self.client.post(
            f"{self.BASE_URL}/models/veo-3.1:generateVideo",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "video_url": result.get("video_url"),
                "thumbnail_url": result.get("thumbnail_url"),
                "duration": result.get("duration", duration),
                "resolution": "1920x1080"
            }

        return None

    async def generate_clips_batch(
        self,
        enhanced_images: List[Any],
        creative_direction: str
    ) -> List[GeneratedClip]:
        """
        Generate video clips from multiple enhanced images

        Args:
            enhanced_images: List of EnhancedImage objects
            creative_direction: User's creative direction

        Returns:
            List of GeneratedClip objects
        """
        clips = []

        # Determine motion types
        motion_types = self.determine_motion_types(creative_direction)

        # Process with concurrency limit
        semaphore = asyncio.Semaphore(2)  # Limit concurrent generations

        async def process_image(img, index):
            async with semaphore:
                # Cycle through motion types
                motion_type = motion_types[index % len(motion_types)]

                result = await self.generate_video(
                    image_data=img.image_data,
                    poi_name=img.original_poi_name,
                    motion_type=motion_type,
                    creative_direction=creative_direction
                )

                if result:
                    return GeneratedClip(
                        name=f"{img.original_poi_name} - {motion_type.replace('_', ' ').title()}",
                        url=result["video_url"],
                        thumbnail=result["thumbnail_url"],
                        duration=result["duration"],
                        resolution=result["resolution"],
                        poi_name=img.original_poi_name,
                        motion_type=motion_type,
                        style=img.style_preset
                    )
                return None

        tasks = [process_image(img, i) for i, img in enumerate(enhanced_images)]
        results = await asyncio.gather(*tasks)

        # Filter out None results
        clips = [clip for clip in results if clip is not None]

        return clips

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
