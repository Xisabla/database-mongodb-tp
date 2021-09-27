#!/usr/bin/env python3
"""Perform operations on station entries
Usage:
    operations.py find <city> <partial_name>
    operations.py delete <city> <station>
    operations.py update <city> <station>
    operations.py [-h | --help]
"""
import re
import sys
from database import db
from docopt import docopt
from worker import get_stations_lille, get_stations_lyon, get_stations_paris, get_stations_rennes


def find_station(city, station_name):
    """
    Find station by name (with some letters)
    :param city: City to find the station in
    :param station_name: Station (partial) name
    :return: The found station
    """
    pat = re.compile(station_name, re.I)

    if city == "Lille":
        return db.lille.find({"name": {"$regex": pat}})
    if city == "Paris":
        return db.paris.find({"name": {"$regex": pat}})
    if city == "Lyon":
        return db.lyon.find({"name": {"$regex": pat}})
    if city == "Rennes":
        return db.rennes.find({"name": {"$regex": pat}})


def delete_station(city, station_name):
    """
    Delete a station by its name
    :param city: City to delete the station in
    :param station_name: Name of the station
    """
    if city == "Lille":
        return db.lille.delete_many({"name": station_name})
    if city == "Paris":
        return db.paris.delete_many({"name": station_name})
    if city == "Lyon":
        return db.lyon.delete_many({"name": station_name})
    if city == "Rennes":
        return db.rennes.delete_many({"name": station_name})


def update_station(city, station_name):
    """
    Update a station last entry from the API
    :param city: City to update the station in
    :param station_name: Name of the station
    """
    # Retrieve data from API
    if city == "Lille":
        data = [s for s in get_stations_lille() if s["name"] == station_name]
    if city == "Lyon":
        data = [s for s in get_stations_lyon() if s["name"] == station_name]
    if city == "Paris":
        data = [s for s in get_stations_paris() if s["name"] == station_name]
    if city == "Rennes":
        data = [s for s in get_stations_rennes() if s["name"] == station_name]

    # Check for valid station
    if len(data) < 1:
        print("No station matching \"{}\" in city \"{}\"".format(station_name, city))
        sys.exit(1)

    # Update
    return db.lille.replace_one({"name": station_name}, data[0])


def main():
    args = docopt(__doc__)

    # Values from arguments
    cities = ["Lille", "Lyon", "Paris", "Rennes"]
    city = args["<city>"]

    # Check for existing city
    if city not in cities:
        print("City \"{}\" unavailable.\nPlease use one of: {}.".format(city, ", ".join(cities)))
        exit(1)

    # Find station
    if args["find"]:
        name = args["<partial_name>"]

        stations = set([station["name"].encode('utf-8').strip() for station in find_station(city, name)])

        if len(stations) > 0:
            print("Found {} station(s):".format(len(stations)))
            for station in stations:
                print(" - {}".format(station))
        else:
            print("No station was found")

        sys.exit(0)

    # Delete station
    if args["delete"]:
        name = args["<station>"]
        count = delete_station(city, name).deleted_count

        entry_txt = "entries" if count > 1 else "entry"

        print("{} {} deleted".format(count, entry_txt))

        sys.exit(0)

    # Update station
    if args["update"]:
        name = args["<station>"]
        count = update_station(city, name).modified_count

        entry_txt = "entries" if count > 1 else "entry"

        print("{} {} updated".format(count, entry_txt))

        sys.exit(0)


if __name__ == '__main__':
    main()
