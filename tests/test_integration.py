# Adjust sys.path before any other imports to allow importing from src/
import sys
import os
from typing import List

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

try:
    from async_censusgeocode import AsyncCensusGeocode
except ImportError:
    # Try importing as a module from src if running from project root
    from src.async_censusgeocode import AsyncCensusGeocode
import pytest


@pytest.mark.asyncio
async def test_geocode_address_real():
    """Test geocoding a real address using the Census Geocoder API (integration)."""
    client = AsyncCensusGeocode()
    result = await client.address(
        street="1600 Pennsylvania Ave NW", city="Washington", state="DC", zip="20500"
    )
    assert isinstance(result, List)
    assert "coordinates" in result[0]
    assert "matchedAddress" in result[0]


@pytest.mark.asyncio
async def test_reverse_geocode_real():
    """Test reverse geocoding real coordinates using the Census Geocoder API (integration)."""
    client = AsyncCensusGeocode()
    # Coordinates for the White House
    result = await client.coordinates(x=-77.0365, y=38.8977)
    assert isinstance(result, dict)
    assert "2020 Census Blocks" in result.keys()
    assert "Census Tracts" in result.keys()
    assert "Counties" in result.keys()
    assert "States" in result.keys()
    assert "Combined Statistical Areas" in result.keys()
    assert "County Subdivisions" in result.keys()
    assert "119th Congressional Districts" in result.keys()
    assert "2020 Census Blocks" in result.keys()
