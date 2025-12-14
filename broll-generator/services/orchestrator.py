"""
B-Roll Generation Orchestrator
Coordinates the full pipeline from location to video clips
"""

import asyncio
from typing import List, Dict, Any

from .places_service import PlacesService, PointOfInterest
from .streetview_service import StreetViewService, StreetViewImage
from .nanobanana_service import NanobananService, EnhancedImage
from .veo_service import VeoService, GeneratedClip


class BRollOrchestrator:
    """
    Orchestrates the complete B-roll generation pipeline:
    1. POI Discovery (Google Places)
    2. Image Capture (Street View)
    3. Image Enhancement (Nanobanana Pro)
    4. Video Generation (Veo 3.1)
    """

    def __init__(
        self,
        places_service: PlacesService,
        streetview_service: StreetViewService,
        nanobanana_service: NanobananService,
        veo_service: VeoService
    ):
        self.places = places_service
        self.streetview = streetview_service
        self.nanobanana = nanobanana_service
        self.veo = veo_service

    async def discover_pois(
        self,
        location: str,
        creative_direction: str,
        num_pois: int = 5
    ) -> List[PointOfInterest]:
        """
        Step 1: Discover points of interest based on location and creative direction

        Args:
            location: City, town, or neighborhood
            creative_direction: User's creative direction
            num_pois: Number of POIs to discover

        Returns:
            List of PointOfInterest objects
        """
        return await self.places.discover_pois(
            location=location,
            creative_direction=creative_direction,
            num_results=num_pois
        )

    async def capture_streetview_images(
        self,
        pois: List[PointOfInterest]
    ) -> List[StreetViewImage]:
        """
        Step 2: Capture Street View images for each POI

        Args:
            pois: List of discovered points of interest

        Returns:
            List of StreetViewImage objects
        """
        all_images = []

        for poi in pois:
            images = await self.streetview.capture_poi_images(
                poi_name=poi.name,
                lat=poi.lat,
                lng=poi.lng,
                creative_direction=""  # Will be passed in full pipeline
            )
            all_images.extend(images)

        return all_images

    async def enhance_images(
        self,
        images: List[StreetViewImage],
        creative_direction: str
    ) -> List[EnhancedImage]:
        """
        Step 3: Enhance images using Nanobanana Pro

        Args:
            images: List of captured Street View images
            creative_direction: User's creative direction for styling

        Returns:
            List of EnhancedImage objects
        """
        return await self.nanobanana.batch_enhance(
            images=images,
            creative_direction=creative_direction
        )

    async def generate_videos(
        self,
        enhanced_images: List[EnhancedImage],
        creative_direction: str
    ) -> List[Dict[str, Any]]:
        """
        Step 4: Generate video clips from enhanced images

        Args:
            enhanced_images: List of enhanced images
            creative_direction: User's creative direction

        Returns:
            List of clip dictionaries for frontend
        """
        clips = await self.veo.generate_clips_batch(
            enhanced_images=enhanced_images,
            creative_direction=creative_direction
        )

        # Convert to frontend-friendly format
        return [
            {
                "name": clip.name,
                "url": clip.url,
                "thumbnail": clip.thumbnail,
                "duration": clip.duration,
                "resolution": clip.resolution,
                "poi": clip.poi_name,
                "motion": clip.motion_type,
                "style": clip.style
            }
            for clip in clips
        ]

    async def run_full_pipeline(
        self,
        location: str,
        creative_direction: str,
        num_clips: int = 5,
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Run the complete B-roll generation pipeline

        Args:
            location: Target location
            creative_direction: Creative direction text
            num_clips: Number of clips to generate
            progress_callback: Optional callback for progress updates

        Returns:
            List of generated clip dictionaries
        """
        if progress_callback:
            await progress_callback(10, "Discovering points of interest...")

        # Step 1: Discover POIs
        pois = await self.discover_pois(location, creative_direction, num_clips)

        if not pois:
            raise ValueError(f"No points of interest found in {location}")

        if progress_callback:
            await progress_callback(25, f"Found {len(pois)} locations. Capturing imagery...")

        # Step 2: Capture Street View images
        images = await self.streetview.capture_all_pois(pois, creative_direction)

        if not images:
            raise ValueError("No Street View imagery available for these locations")

        if progress_callback:
            await progress_callback(45, f"Captured {len(images)} images. Enhancing...")

        # Step 3: Enhance images
        enhanced = await self.enhance_images(images, creative_direction)

        if progress_callback:
            await progress_callback(65, "Generating video clips with Veo 3.1...")

        # Step 4: Generate videos
        clips = await self.generate_videos(enhanced, creative_direction)

        if progress_callback:
            await progress_callback(100, f"Generated {len(clips)} B-roll clips!")

        return clips

    async def cleanup(self):
        """Clean up resources"""
        await asyncio.gather(
            self.places.close(),
            self.streetview.close(),
            self.nanobanana.close(),
            self.veo.close()
        )
