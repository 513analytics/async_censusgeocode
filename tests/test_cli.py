import sys
import io
import csv
import pytest
from unittest.mock import patch, AsyncMock

import importlib


@pytest.mark.asyncio
async def test_cli_address(monkeypatch):
    sys_argv = ["src.cli.py", "1600 Pennsylvania Avenue NW, Washington, DC, 20500"]
    fake_result = [{"coordinates": {"x": -77.0365, "y": 38.8977}}]
    with (
        patch.object(sys, "argv", sys_argv),
        patch(
            "async_censusgeocode.AsyncCensusGeocode.onelineaddress",
            new_callable=AsyncMock,
        ) as mock_onelineaddress,
        patch("builtins.print") as mock_print,
    ):
        mock_onelineaddress.return_value = fake_result
        main_mod = importlib.import_module("src.cli")
        main_mod.main()


@pytest.mark.asyncio
async def test_cli_csv(monkeypatch, tmp_path):
    csv_path = tmp_path / "batch.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([1, "1600 Pennsylvania Avenue NW", "Washington", "DC", "20500"])
    fake_result = [
        {
            "id": "1",
            "address": "1600 Pennsylvania Avenue NW",
            "match": True,
            "matchtype": "Exact",
            "parsed": "",
            "tigerlineid": "123",
            "side": "L",
            "lat": 38.8977,
            "lon": -77.0365,
        }
    ]
    sys_argv = ["src.cli.py", "--csv", str(csv_path)]
    with (
        patch.object(sys, "argv", sys_argv),
        patch(
            "async_censusgeocode.AsyncCensusGeocode.addressbatch",
            new_callable=AsyncMock,
        ) as mock_addressbatch,
    ):
        mock_addressbatch.return_value = fake_result
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            main_mod = importlib.import_module("src.cli")
            main_mod.main()
        output = buf.getvalue()
