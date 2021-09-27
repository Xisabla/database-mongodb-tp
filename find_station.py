#!/usr/bin/env python3
"""Find close stations

Usage:
    find_station.py <latitude> <longitude> [-h | --help] [--target=<town>] [--limit=<n>]

Options:
    -h --help       Show this screen
    --target=<town> Find stations in a specific town ("Lille", "Lyon", "Paris", "Rennes")
    --limit=<n>     Number of stations to show [default=5]
"""
from database import db
from docopt import docopt
from pymongo import ASCENDING, DESCENDING


def find_geo_stations(lat, lon, target, limit):
    # type: (long, long, str, int) -> object
    """
    Find stations close to a geographical point
    :param lat: Geographic latitude of the point
    :param lon: Geographic longitude of the point
    :param target: Target city (Lille, Lyon, Paris, Rennes)
    :param limit: Maximum stations to show
    :return: The list of close stations
    """
    return [station for station in db[target].aggregate([
        {"$geoNear": {
            "near": [lat, lon],
            "distanceField": "distance",
            "spherical": True
        }},
        {"$sort": {"distance": ASCENDING, "date": DESCENDING}},
        {"$limit": limit},
    ])]


def show_station_data(station):
    """
    Show relevant information about the station (name, available bikes, tpe)
    :param station: Station to show information from
    """
    name = station["name"].encode('utf-8').strip()
    available = station["available"]
    tpe = "Yes" if station["tpe"] else "No"

    if available < 0:
        available_text = "<no valid data for available bikes>"
    else:
        available_text = "{} bike(s) available".format(available)

    print("- {}: {}, TPE: {}".format(
        name,
        available_text,
        tpe))


def main():
    args = docopt(__doc__)

    targets = ["lille", "lyon", "paris", "rennes"]

    # Defaults
    limit = 5
    target = None

    # Values from arguments
    if args["--limit"]:
        limit = int(args["--limit"])
    if args["--target"]:
        target = args["--target"]

    lon = float(args["<longitude>"])
    lat = float(args["<latitude>"])

    # Find and show
    if target:
        if target.lower() not in targets:
            print("Target \"{}\" unavailable.\nPlease use one of: {}.".format(target, ", ".join(targets)))
            exit(1)

        # Search for stations in specific collection
        for station in find_geo_stations(lat, lon, target.lower(), limit):
            show_station_data(station)
    else:
        # Search in all collections
        for target in targets:
            print("{}:".format(target.title()))
            for station in find_geo_stations(lat, lon, target.lower(), limit):
                show_station_data(station)


if __name__ == '__main__':
    main()
