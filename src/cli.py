# Copyright (C) 2015-7 Neil Freeman

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copied from censusgeocode, licensed under GPL-3.0.
# https://github.com/fitnr/censusgeocode

"""Command-line interface for censusgeocode"""

import sys
import argparse
import asyncio
import csv
import io

from .async_censusgeocode import DEFAULT_BENCHMARK, DEFAULT_VINTAGE, AsyncCensusGeocode


async def main():
    """Command-line interface for async-censusgeocode"""
    parser = argparse.ArgumentParser(
        "async-censusgeocode",
        description="Command-line interface for the Census Geocoding API",
    )

    parser.add_argument("-v", "--version", action="version", version="%(prog)s v0.1.0")
    parser.add_argument("address", type=str, nargs="?", default=None)
    parser.add_argument(
        "--csv",
        type=str,
        help=(
            "comma-delimited file of addresses. No header. Must have the following columns: id, street address, city, state, zip. "
            "The id must be a unique. Read from stdin with -"
        ),
    )
    parser.add_argument(
        "--rettype",
        choices=["locations", "geographies"],
        default="locations",
        help=(
            "Query type. Geographies will return state, county, tract, and block code in addition to TIGER/Line info and "
            "latitude and longitude. For use with --csv"
        ),
    )
    parser.add_argument(
        "--benchmark",
        default=DEFAULT_BENCHMARK,
        help="Version of the locator to query. See Census documentation for options.",
    )
    parser.add_argument(
        "--vintage",
        default=DEFAULT_VINTAGE,
        help="Geography version query. See Census documentation for options.",
    )
    parser.add_argument(
        "--timeout",
        metavar="SECONDS",
        type=int,
        default=12,
        help="Request timeout [default: 12]",
    )

    args = parser.parse_args()
    acg = AsyncCensusGeocode(benchmark=args.benchmark, vintage=args.vintage)

    if args.address:
        result = await acg.onelineaddress(
            args.address, returntype=args.rettype, timeout=args.timeout
        )

        try:
            print(
                "{},{}".format(
                    result[0]["coordinates"]["x"], result[0]["coordinates"]["y"]
                )
            )

        except IndexError:
            print("Address not found: {}".format(args.address), file=sys.stderr)
            sys.exit(1)

    elif args.csv:
        if args.csv == "-":
            # No streaming here - consume the entirety of stdin.
            infile = io.StringIO()
            csv.writer(infile).writerows(csv.reader(sys.stdin))
            infile.seek(0)

        else:
            infile = args.csv

        result = await acg.addressbatch(
            infile, returntype=args.rettype, timeout=args.timeout
        )

        fieldnames = acg.batchfields[args.rettype] + ["lat", "lon"]
        fieldnames.pop(fieldnames.index("coordinate"))
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result)

    else:
        print("Address or csv file required", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
