# -*- coding: utf-8 -*-
"""Tests for censusgeocode"""
# This file is part of censusgeocode.
# https://github.com/fitnr/censusgeocode

# Licensed under the General Public License (version 3)
# http://opensource.org/licenses/LGPL-3.0
# Copied and heavily modified from censusgeocode, licensed under GPL-3.0.
# https://github.com/fitnr/censusgeocode

import pytest
import warnings
from unittest.mock import patch, AsyncMock
import io

from async_censusgeocode import AsyncCensusGeocode, AddressResult, GeographyResult


@pytest.fixture
def acg():
    return AsyncCensusGeocode()


@pytest.mark.asyncio
async def test_returns_geo(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        # Set .json.return_value directly, not as an AsyncMock
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "input": {"foo": "bar"},
                "geographies": {
                    "Census Tracts": [
                        {
                            "BASENAME": "615",
                            "CENTLON": "-74.0",
                            "CENTLAT": "43.0",
                            "INTPTLON": "-74.0",
                            "INTPTLAT": "43.0",
                        }
                    ]
                },
            }
        }
        results = await acg.coordinates(-74, 43, returntype="geographies")
        assert isinstance(results, GeographyResult)
        assert results.input


@pytest.mark.asyncio
async def test_coords(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "geographies": {
                    "Counties": [
                        {
                            "BASENAME": "Saratoga",
                            "GEOID": "36091",
                            "CENTLON": "-74.0",
                            "CENTLAT": "43.0",
                            "INTPTLON": "-74.0",
                            "INTPTLAT": "43.0",
                        }
                    ],
                    "Census Tracts": [
                        {
                            "BASENAME": "615",
                            "CENTLON": "-74.0",
                            "CENTLAT": "43.0",
                            "INTPTLON": "-74.0",
                            "INTPTLAT": "43.0",
                        }
                    ],
                }
            }
        }
        results = await acg.coordinates(-74, 43)
        assert isinstance(results, GeographyResult)
        assert results.input


@pytest.mark.asyncio
async def test_url(acg):
    r = acg._geturl("coordinates", "geographies")
    assert r == "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"


@pytest.mark.asyncio
async def test_address_zipcode(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "geographies": {
                    "Counties": [
                        {
                            "BASENAME": "District of Columbia",
                            "CENTLON": "-77.0365",
                            "CENTLAT": "38.8977",
                            "INTPTLON": "-77.0365",
                            "INTPTLAT": "38.8977",
                        }
                    ]
                }
            }
        }
        results = await acg.address(
            "1600 Pennsylvania Avenue NW",
            city="Washington",
            state="DC",
            zipcode="20500",
        )
        assert isinstance(results, GeographyResult)
        assert results.input


@pytest.mark.asyncio
async def test_address_zip(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "geographies": {
                    "Counties": [
                        {
                            "BASENAME": "District of Columbia",
                            "CENTLON": "-77.0365",
                            "CENTLAT": "38.8977",
                            "INTPTLON": "-77.0365",
                            "INTPTLAT": "38.8977",
                        }
                    ]
                }
            }
        }
        results = await acg.address(
            "1600 Pennsylvania Avenue NW", city="Washington", state="DC", zip="20500"
        )
        assert isinstance(results, GeographyResult)
        assert results.input


@pytest.mark.asyncio
async def test_onelineaddress(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "geographies": {
                    "Counties": [
                        {
                            "BASENAME": "District of Columbia",
                            "CENTLON": "-77.0365",
                            "CENTLAT": "38.8977",
                            "INTPTLON": "-77.0365",
                            "INTPTLAT": "38.8977",
                        }
                    ],
                },
                "Metropolitan Divisions": [
                    {
                        "CENTLON": "-77.0",
                        "CENTLAT": "38.9",
                        "INTPTLON": "-77.0",
                        "INTPTLAT": "38.9",
                    }
                ],
                "Alaska Native Village Statistical Areas": [
                    {
                        "CENTLON": "-150.0",
                        "CENTLAT": "60.0",
                        "INTPTLON": "-150.0",
                        "INTPTLAT": "60.0",
                    }
                ],
            }
        }
        results = await acg.onelineaddress(
            "1600 Pennsylvania Avenue NW, Washington, DC, 20500", layers="all"
        )
        assert isinstance(results, GeographyResult)
        assert results["Counties"][0]["BASENAME"] == "District of Columbia"
        assert "Metropolitan Divisions" in results
        assert "Alaska Native Village Statistical Areas" in results


@pytest.mark.asyncio
async def test_address_return_type(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "addressMatches": [
                    {
                        "matchedAddress": "1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20502",
                        "addressComponents": {"streetName": "PENNSYLVANIA"},
                    }
                ]
            }
        }
        results = await acg.address(
            "1600 Pennsylvania Avenue NW",
            city="Washington",
            state="DC",
            zipcode="20500",
            returntype="locations",
        )
        assert (
            results[0]["matchedAddress"].upper()
            == "1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20502"
        )
        assert results[0]["addressComponents"]["streetName"] == "PENNSYLVANIA"


@pytest.mark.asyncio
async def test_benchmark_vintage(acg):
    with patch("async_censusgeocode.AsyncClient") as mock_client:
        bmark, vint = "Public_AR_Census2020", "Census2020_Current"
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.get = AsyncMock()
        mock_instance.get.return_value.json.return_value = {
            "result": {
                "input": {
                    "benchmark": {"benchmarkName": bmark},
                    "vintage": {"vintageName": vint},
                },
                "geographies": {
                    "Census Tracts": [
                        {
                            "GEOID": "11001006202",
                            "CENTLON": "-77.0365",
                            "CENTLAT": "38.8977",
                            "INTPTLON": "-77.0365",
                            "INTPTLAT": "38.8977",
                        }
                    ]
                },
            }
        }
        acg = AsyncCensusGeocode(benchmark=bmark, vintage=vint)
        result = await acg.address(
            "1600 Pennsylvania Avenue NW",
            city="Washington",
            state="DC",
            zipcode="20500",
            returntype="geographies",
        )
        assert isinstance(result, GeographyResult)
        assert result.input["benchmark"]["benchmarkName"] == bmark
        assert result.input["vintage"]["vintageName"] == vint
        assert result["Census Tracts"][0]["GEOID"] == "11001006202"


@pytest.mark.asyncio
async def test_addressbatch(acg):
    with (
        patch("builtins.open", create=True) as mock_open,
        patch("async_censusgeocode.AsyncClient") as mock_client,
    ):
        mock_open.side_effect = lambda *a, **kw: io.BytesIO(b"test csv")
        mock_instance = mock_client.return_value.__aenter__.return_value
        mock_instance.post = AsyncMock()
        # Use the same CSV columns for both batch calls
        mock_instance.post.return_value.text = (
            "id,address,match,tigerlineid,statefp,coordinate\n"
            '3,"3 GRAMERCY PARK W, NEW YORK, NY, 10003",Match,59653655,36,"-73.9857,40.7372"\n'
            "2,,,No Match,,,\n"
        )
        result = await acg.addressbatch(
            "tests/fixtures/batch.csv", returntype="locations"
        )
        assert isinstance(result, list)
        resultdict = {int(r["id"]): r for r in result if r["id"].isdigit()}
        assert resultdict[3]["address"] == "3 GRAMERCY PARK W, NEW YORK, NY, 10003"
        assert resultdict[2]["match"] is False

        # Use the same CSV columns for geographies
        mock_instance.post.return_value.text = (
            "id,address,match,matchtype,parsed,coordinate,tigerlineid,side,statefp,countyfp,tract,block\n"
            '3,,,,,"-73.9857,40.7372",59653655,,36,,,,\n'
            "2,,,,,,,,,,,,\n"
        )
        result = await acg.addressbatch(
            "tests/fixtures/batch.csv", returntype="geographies"
        )
        assert isinstance(result, list)
        resultdict = {int(r["id"]): r for r in result if r["id"].isdigit()}
        assert resultdict[3]["tigerlineid"] == "59653655"
        assert resultdict[3]["statefp"] == "36"
        assert resultdict[2]["match"] is False


@pytest.mark.asyncio
async def test_warning10k(acg):
    warnings.simplefilter("error")
    data = ({} for _ in range(10001))
    with pytest.raises(
        UserWarning,
        match="Sending more than 10,000 records, the upper limit for the Census Geocoder. Request will likely fail",
    ):
        result = await acg.addressbatch(data)
        assert result == []


@pytest.mark.asyncio
async def test_address_returns_addressresult():
    """Test that address() returns an AddressResult, not a coroutine."""
    expected = AddressResult(
        {
            "result": {
                "addressMatches": [
                    {"matchedAddress": "foo", "coordinates": {"x": 1, "y": 2}}
                ]
            }
        }
    )
    with patch.object(
        AsyncCensusGeocode, "_fetch", new_callable=AsyncMock
    ) as mock_fetch:
        mock_fetch.return_value = expected
        client = AsyncCensusGeocode()
        result = await client.address("123 Main St", city="Anytown", state="NY")
        assert isinstance(result, AddressResult)
        assert result[0]["matchedAddress"] == "foo"
