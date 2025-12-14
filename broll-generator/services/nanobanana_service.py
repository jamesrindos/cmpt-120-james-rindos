"""
Nanobanana Pro API Service
AI-powered image enhancement and cleanup
"""

import os
import httpx
import asyncio
import base64
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class EnhancedImage:
    """Represents an enhanced image from Nanobanana Pro"""
    original_poi_name: str
    lat: float
    lng: float
    image_data: bytes
    enhancement_applied: str
    style_preset: str = None


class NanobananService:
    """Service for image enhancement using Nanobanana Pro API"""

    BASE_URL = "https://api.nanobanana.pro/v1"

    # Style presets mapped to creative directions
    STYLE_PRESETS = {
        "cinematic": {
            "color_grade": "cinematic",
            "contrast": 1.2,
            "saturation": 0.9,
            "vignette": 0.3,
            "grain": 0.1
        },
        "warm": {
            "color_grade": "warm_sunset",
            "contrast": 1.1,
            "saturation": 1.1,
            "warmth": 0.3,
            "vignette": 0.2
        },
        "cool": {
            "color_grade": "cool_blue",
            "contrast": 1.15,
            "saturation": 0.85,
            "coolness": 0.25,
            "vignette": 0.25
        },
        "vibrant": {
            "color_grade": "vibrant",
            "contrast": 1.25,
            "saturation": 1.3,
            "clarity": 0.4,
            "vignette": 0.15
        },
        "moody": {
            "color_grade": "moody_dark",
            "contrast": 1.4,
            "saturation": 0.7,
            "shadows": -0.2,
            "vignette": 0.5
        },
        "clean": {
            "color_grade": "natural",
            "contrast": 1.05,
            "saturation": 1.0,
            "clarity": 0.3,
            "noise_reduction": 0.5
        },
        "vintage": {
            "color_grade": "vintage_film",
            "contrast": 1.1,
            "saturation": 0.8,
            "fade": 0.2,
            "grain": 0.3
        },
        "urban": {
            "color_grade": "urban_grit",
            "contrast": 1.3,
            "saturation": 0.9,
            "clarity": 0.5,
            "shadows": 0.1
        }
    }

    # Enhancement operations
    ENHANCEMENT_OPS = {
        "upscale": "Upscale image to 4K resolution",
        "denoise": "Remove noise and artifacts",
        "deblur": "Sharpen and remove motion blur",
        "dehaze": "Remove haze and improve clarity",
        "color_correct": "Auto color correction",
        "sky_enhance": "Enhance sky and atmosphere",
        "detail_enhance": "Enhance fine details",
        "lens_correct": "Fix lens distortion"
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("NANOBANANA_API_KEY")
        self.client = httpx.AsyncClient(timeout=60.0)

    def determine_style(self, creative_direction: str) -> str:
        """
        Determine the best style preset based on creative direction

        Args:
            creative_direction: User's creative direction text

        Returns:
            Style preset key
        """
        direction_lower = creative_direction.lower()

        style_keywords = {
            "cinematic": ["cinematic", "film", "movie", "dramatic"],
            "warm": ["warm", "golden", "sunset", "cozy", "autumn"],
            "cool": ["cool", "blue", "cold", "winter", "night"],
            "vibrant": ["vibrant", "colorful", "bright", "bold", "pop"],
            "moody": ["moody", "dark", "noir", "atmospheric", "shadows"],
            "clean": ["clean", "minimal", "modern", "crisp", "professional"],
            "vintage": ["vintage", "retro", "nostalgic", "old", "classic"],
            "urban": ["urban", "street", "gritty", "city", "industrial"]
        }

        for style, keywords in style_keywords.items():
            if any(keyword in direction_lower for keyword in keywords):
                return style

        return "cinematic"  # Default

    def determine_enhancements(self, creative_direction: str) -> List[str]:
        """
        Determine which enhancement operations to apply

        Args:
            creative_direction: User's creative direction text

        Returns:
            List of enhancement operation keys
        """
        # Always apply base enhancements for Street View images
        enhancements = ["upscale", "denoise", "lens_correct"]

        direction_lower = creative_direction.lower()

        if any(w in direction_lower for w in ["sharp", "detail", "crisp"]):
            enhancements.append("detail_enhance")

        if any(w in direction_lower for w in ["clear", "visibility", "haze"]):
            enhancements.append("dehaze")

        if any(w in direction_lower for w in ["sky", "outdoor", "landscape"]):
            enhancements.append("sky_enhance")

        return enhancements

    async def enhance_image(
        self,
        image_data: bytes,
        style_preset: str,
        enhancements: List[str]
    ) -> bytes:
        """
        Enhance a single image using Nanobanana Pro

        Args:
            image_data: Raw image bytes
            style_preset: Style preset to apply
            enhancements: List of enhancement operations

        Returns:
            Enhanced image bytes
        """
        # Encode image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')

        # Get style parameters
        style_params = self.STYLE_PRESETS.get(style_preset, self.STYLE_PRESETS["cinematic"])

        # Build request
        payload = {
            "image": image_b64,
            "style": style_params,
            "enhancements": enhancements,
            "output_format": "png",
            "output_quality": 95
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = await self.client.post(
            f"{self.BASE_URL}/enhance",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            result = response.json()
            # Decode the enhanced image
            return base64.b64decode(result["enhanced_image"])

        # If API fails, return original image
        return image_data

    async def batch_enhance(
        self,
        images: List[Any],
        creative_direction: str
    ) -> List[EnhancedImage]:
        """
        Enhance multiple images in batch

        Args:
            images: List of StreetViewImage objects
            creative_direction: User's creative direction

        Returns:
            List of EnhancedImage objects
        """
        # Determine style and enhancements
        style = self.determine_style(creative_direction)
        enhancements = self.determine_enhancements(creative_direction)

        enhanced_images = []

        # Process with concurrency limit
        semaphore = asyncio.Semaphore(2)  # Limit concurrent API calls

        async def process_image(img):
            async with semaphore:
                enhanced_data = await self.enhance_image(
                    img.image_data,
                    style,
                    enhancements
                )

                return EnhancedImage(
                    original_poi_name=img.poi_name,
                    lat=img.lat,
                    lng=img.lng,
                    image_data=enhanced_data,
                    enhancement_applied=", ".join(enhancements),
                    style_preset=style
                )

        tasks = [process_image(img) for img in images]
        results = await asyncio.gather(*tasks)

        return list(results)

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
