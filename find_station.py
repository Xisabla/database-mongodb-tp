#/usr/bin/env python3

from database import db
from docopt import docopt
from pymongo import ASCENDING, DESCENDING


def find_geo_stations(lat, lon, target, limit):
    return [station for station in db[target].aggregate([
        {"$geoNear": {
            "near": [lat, lon],
            "distanceField": "distance",
            "spherical": True
        }},
        {"$sort": {"distance": ASCENDING, "date": DESCENDING}},
        {"$limit": limit},
    ])]


def main():
    args = docopt(__doc__)

    targets = ["lille", "lyon", "paris", "rennes"]

    # Defaults
    limit = 5
    target = None

    if args["--limit"]:
        limit = int(args["--limit"])
    if args["--target"]:
        target = args["--target"]

    lon = float(args["<longitude>"])
    lat = float(args["<latitude>"])

    if target:
        if target.lower() not in targets:
            print("Target \"{}\" unavailable.\nPlease use one of: {}.".format(target, ", ".join(targets)))
            exit(1)

        # Search for stations in specific collection
        for station in find_geo_stations(lat, lon, target.lower(), limit):
            print("- {}: {}".format(station["name"].encode('utf-8').strip(), station["distance"]))
    else:
        # Search in all collections
        for target in targets:
            print("{}:".format(target.title()))
            for station in find_geo_stations(lat, lon, target.lower(), limit):
                print("- {}: {}".format(station["name"].encode('utf-8').strip(), station["distance"]))


if __name__ == '__main__':
    main()

    # lat = 50.625880
    # lon = 3.041086
    # max_found = 5
