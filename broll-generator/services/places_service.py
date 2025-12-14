"""
Google Places API Service
Discovers points of interest based on location and creative direction
"""

import os
import httpx
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class PointOfInterest:
    """Represents a point of interest with location data"""
    place_id: str
    name: str
    lat: float
    lng: float
    address: str
    types: List[str]
    rating: float = 0.0
    photo_reference: str = None


class PlacesService:
    """Service for discovering points of interest using Google Places API"""

    BASE_URL = "https://maps.googleapis.com/maps/api/place"

    # Mapping creative direction keywords to Google Places types
    POI_TYPE_MAPPING = {
        "cafe": ["cafe", "coffee_shop", "bakery"],
        "restaurant": ["restaurant", "food"],
        "bar": ["bar", "night_club"],
        "art": ["art_gallery", "museum", "street_art"],
        "architecture": ["landmark", "church", "city_hall", "library"],
        "nature": ["park", "garden", "natural_feature"],
        "shopping": ["shopping_mall", "store", "market"],
        "culture": ["museum", "cultural_center", "temple", "church"],
        "nightlife": ["night_club", "bar", "casino"],
        "historic": ["historical_landmark", "monument", "memorial"],
        "modern": ["shopping_mall", "stadium", "office"],
        "street": ["neighborhood", "locality", "sublocality"],
        "urban": ["transit_station", "bus_station", "subway_station"],
        "food": ["restaurant", "food", "meal_takeaway", "street_vendor"],
        "market": ["market", "grocery", "supermarket"],
    }

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def geocode_location(self, location: str) -> Dict[str, float]:
        """
        Convert a location string to coordinates

        Args:
            location: City, town, or address string

        Returns:
            Dict with lat and lng keys
        """
        url = f"{self.BASE_URL}/textsearch/json"
        params = {
            "query": location,
            "key": self.api_key
        }

        response = await self.client.get(url, params=params)
        data = response.json()

        if data.get("status") == "OK" and data.get("results"):
            loc = data["results"][0]["geometry"]["location"]
            return {"lat": loc["lat"], "lng": loc["lng"]}

        raise ValueError(f"Could not geocode location: {location}")

    def parse_creative_direction(self, creative_direction: str) -> List[str]:
        """
        Parse creative direction text to extract relevant POI types

        Args:
            creative_direction: User's creative direction text

        Returns:
            List of Google Places types to search for
        """
        direction_lower = creative_direction.lower()
        types = set()

        for keyword, poi_types in self.POI_TYPE_MAPPING.items():
            if keyword in direction_lower:
                types.update(poi_types)

        # Default types if none matched
        if not types:
            types = {"point_of_interest", "establishment", "tourist_attraction"}

        return list(types)

    async def search_nearby(
        self,
        lat: float,
        lng: float,
        poi_types: List[str],
        radius: int = 2000,
        max_results: int = 10
    ) -> List[PointOfInterest]:
        """
        Search for nearby places matching the given types

        Args:
            lat: Latitude
            lng: Longitude
            poi_types: List of place types to search
            radius: Search radius in meters
            max_results: Maximum number of results

        Returns:
            List of PointOfInterest objects
        """
        all_places = []

        for poi_type in poi_types[:3]:  # Limit to 3 types to avoid too many API calls
            url = f"{self.BASE_URL}/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "type": poi_type,
                "key": self.api_key
            }

            response = await self.client.get(url, params=params)
            data = response.json()

            if data.get("status") == "OK":
                for place in data.get("results", [])[:5]:
                    poi = PointOfInterest(
                        place_id=place["place_id"],
                        name=place["name"],
                        lat=place["geometry"]["location"]["lat"],
                        lng=place["geometry"]["location"]["lng"],
                        address=place.get("vicinity", ""),
                        types=place.get("types", []),
                        rating=place.get("rating", 0.0),
                        photo_reference=place.get("photos", [{}])[0].get("photo_reference")
                    )
                    all_places.append(poi)

        # Deduplicate by place_id and sort by rating
        seen = set()
        unique_places = []
        for place in sorted(all_places, key=lambda x: x.rating, reverse=True):
            if place.place_id not in seen:
                seen.add(place.place_id)
                unique_places.append(place)

        return unique_places[:max_results]

    async def discover_pois(
        self,
        location: str,
        creative_direction: str,
        num_results: int = 5
    ) -> List[PointOfInterest]:
        """
        Main method to discover POIs based on location and creative direction

        Args:
            location: Location string (city, town, neighborhood)
            creative_direction: User's creative direction text
            num_results: Number of POIs to return

        Returns:
            List of PointOfInterest objects
        """
        # Get coordinates
        coords = await self.geocode_location(location)

        # Parse creative direction to get POI types
        poi_types = self.parse_creative_direction(creative_direction)

        # Search for places
        pois = await self.search_nearby(
            coords["lat"],
            coords["lng"],
            poi_types,
            radius=3000,
            max_results=num_results * 2  # Get extra to filter
        )

        return pois[:num_results]

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
