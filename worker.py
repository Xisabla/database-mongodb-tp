import json
import os
import requests
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

load_dotenv()

# ------------------------------------------ CONSTANTS ------------------------------------------ #

# API URLs
API_BASEURL_LILLE = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime"

# Database url
ATLAS_URL = os.getenv("ATLAS_URL")

# Worker configuration
REFRESH_DELAY = int(os.getenv("WORKER_REFRESH_DELAY"))

# ----------------------------------- DATABASE INITIALIZATION ----------------------------------- #

try:
    client = MongoClient(ATLAS_URL)
except (ConnectionFailure, ConfigurationError) as e:
    sys.exit("Failed worker initialization: " + str(e))

db = client.gautier


# --------------------------------------- STATION GETTERS --------------------------------------- #


def get_stations_lille():
    """
    Get raw stations entries for Lille, format and select fields
    :return: Entries for lille stations with fields "name", "geometry", "size", "tpe", "available" and "date"
    """
    return [
        {
            "name": s.get("fields", {}).get("nom").title(),
            "geometry": s.get("fields", {}).get("localisation"),
            "size": s.get("fields", {}).get("nbvelosdispo") + s.get("fields", {}).get("nbplacesdispo"),
            "tpe": s.get("fields", {}).get("type") == "AVEC TPE",
            "available": s.get("fields", {}).get("nbvelosdispo"),
            "date": datetime.utcnow()
        }
        for s in get_raw_stations_lille()
    ]


def get_raw_stations_lille():
    """
    Get stations information for Lille
    :return: Raw json from the Lille OpenData API
    """
    url = API_BASEURL_LILLE + \
        "&q=" \
        "&rows=300" \
        "&lang=fr" \
        "&timezone=Europe%2FParis"

    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode("utf8"))

    return response_json.get("records", [])


# ------------------------------------------- WORKER -------------------------------------------- #


def worker(verbose=True):
    """
    Run worker to insert new entries
    :type verbose: bool
    :param verbose: If set on true, will show debug information
    """
    while True:
        lille = get_stations_lille()

        if verbose:
            print(
                "{}: Got {} entries for Lille, {} entries for Lyon, {} entries for Paris, {} entries for Rennes".format(
                    datetime.now(), len(lille), 0, 0, 0))

        db.lille.insert_many(lille, ordered=False)

        if verbose:
            print("{}: Saved entries to database".format(datetime.now()))

        time.sleep(REFRESH_DELAY)


if __name__ == '__main__':
    worker()
