"""
Google Street View API Service
Captures street-level imagery from points of interest
"""

import os
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import base64
import io


@dataclass
class StreetViewImage:
    """Represents a captured Street View image"""
    poi_name: str
    lat: float
    lng: float
    heading: float
    pitch: float
    fov: float
    image_data: bytes
    image_url: str = None


class StreetViewService:
    """Service for capturing Street View imagery"""

    BASE_URL = "https://maps.googleapis.com/maps/api/streetview"
    METADATA_URL = "https://maps.googleapis.com/maps/api/streetview/metadata"

    # Camera angles for cinematic variety
    CAMERA_PRESETS = {
        "establishing": {"pitch": 10, "fov": 90},
        "eye_level": {"pitch": 0, "fov": 75},
        "low_angle": {"pitch": -15, "fov": 80},
        "high_angle": {"pitch": 25, "fov": 85},
        "wide": {"pitch": 5, "fov": 110},
        "tight": {"pitch": 0, "fov": 50},
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_STREETVIEW_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def check_availability(self, lat: float, lng: float) -> bool:
        """
        Check if Street View imagery is available at a location

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            True if imagery is available
        """
        params = {
            "location": f"{lat},{lng}",
            "key": self.api_key
        }

        response = await self.client.get(self.METADATA_URL, params=params)
        data = response.json()

        return data.get("status") == "OK"

    def determine_shot_types(self, creative_direction: str) -> List[str]:
        """
        Determine appropriate shot types based on creative direction

        Args:
            creative_direction: User's creative direction text

        Returns:
            List of shot type keys from CAMERA_PRESETS
        """
        direction_lower = creative_direction.lower()
        shots = []

        # Keywords to shot type mapping
        if any(w in direction_lower for w in ["wide", "establishing", "overview"]):
            shots.append("wide")
            shots.append("establishing")

        if any(w in direction_lower for w in ["intimate", "close", "detail", "tight"]):
            shots.append("tight")

        if any(w in direction_lower for w in ["dramatic", "cinematic", "low angle"]):
            shots.append("low_angle")

        if any(w in direction_lower for w in ["aerial", "overview", "high angle"]):
            shots.append("high_angle")

        # Default shots if none matched
        if not shots:
            shots = ["establishing", "eye_level", "wide"]

        return shots[:3]  # Limit to 3 shot types per POI

    async def capture_image(
        self,
        lat: float,
        lng: float,
        heading: float,
        pitch: float = 0,
        fov: float = 90,
        size: str = "1280x720"
    ) -> Optional[bytes]:
        """
        Capture a single Street View image

        Args:
            lat: Latitude
            lng: Longitude
            heading: Camera heading (0-360)
            pitch: Camera pitch (-90 to 90)
            fov: Field of view (10-120)
            size: Image size (width x height)

        Returns:
            Image bytes or None if failed
        """
        params = {
            "location": f"{lat},{lng}",
            "size": size,
            "heading": heading,
            "pitch": pitch,
            "fov": fov,
            "key": self.api_key
        }

        response = await self.client.get(self.BASE_URL, params=params)

        if response.status_code == 200:
            return response.content

        return None

    async def capture_poi_images(
        self,
        poi_name: str,
        lat: float,
        lng: float,
        creative_direction: str
    ) -> List[StreetViewImage]:
        """
        Capture multiple Street View images for a POI with varied angles

        Args:
            poi_name: Name of the point of interest
            lat: Latitude
            lng: Longitude
            creative_direction: User's creative direction

        Returns:
            List of StreetViewImage objects
        """
        images = []

        # Check availability first
        if not await self.check_availability(lat, lng):
            return images

        # Get appropriate shot types
        shot_types = self.determine_shot_types(creative_direction)

        # Calculate varied headings (front and sides of location)
        base_headings = [0, 90, 180, 270]

        for i, shot_type in enumerate(shot_types):
            preset = self.CAMERA_PRESETS[shot_type]
            heading = base_headings[i % len(base_headings)]

            image_data = await self.capture_image(
                lat=lat,
                lng=lng,
                heading=heading,
                pitch=preset["pitch"],
                fov=preset["fov"],
                size="1920x1080"  # Full HD for video generation
            )

            if image_data:
                # Generate URL for reference
                image_url = (
                    f"{self.BASE_URL}?"
                    f"location={lat},{lng}&"
                    f"size=1920x1080&"
                    f"heading={heading}&"
                    f"pitch={preset['pitch']}&"
                    f"fov={preset['fov']}&"
                    f"key={self.api_key}"
                )

                images.append(StreetViewImage(
                    poi_name=poi_name,
                    lat=lat,
                    lng=lng,
                    heading=heading,
                    pitch=preset["pitch"],
                    fov=preset["fov"],
                    image_data=image_data,
                    image_url=image_url
                ))

        return images

    async def capture_all_pois(
        self,
        pois: List[Any],
        creative_direction: str
    ) -> List[StreetViewImage]:
        """
        Capture Street View images for multiple POIs

        Args:
            pois: List of PointOfInterest objects
            creative_direction: User's creative direction

        Returns:
            List of all captured StreetViewImage objects
        """
        all_images = []

        # Process POIs with concurrency limit
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests

        async def process_poi(poi):
            async with semaphore:
                return await self.capture_poi_images(
                    poi_name=poi.name,
                    lat=poi.lat,
                    lng=poi.lng,
                    creative_direction=creative_direction
                )

        tasks = [process_poi(poi) for poi in pois]
        results = await asyncio.gather(*tasks)

        for images in results:
            all_images.extend(images)

        return all_images

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
