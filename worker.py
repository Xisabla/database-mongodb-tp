import json
import os
import requests
import time
from database import db
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------ CONSTANTS ------------------------------------------ #

# API URLs
API_BASEURL_LILLE = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime"
API_BASEURL_LYON = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature"
API_BASEURL_PARIS = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel"
API_BASEURL_RENNES = "https://data.rennesmetropole.fr/api/records/1.0/search/" \
                     "?dataset=etat-des-stations-le-velo-star-en-temps-reel"

# Worker configuration
REFRESH_DELAY = int(os.getenv("WORKER_REFRESH_DELAY"))

# --------------------------------------- STATION GETTERS --------------------------------------- #


def get_stations_lille():
    """
    Get Lille station entries formatted
    :return: Entries for Lille stations with fields "name", "geometry", "size", "tpe", "available" and "date"
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


def get_stations_lyon():
    """
    Get Lyon station entries formatted
    :return: Entries for Lyon stations with fields "name", "geometry", "size", "tpe", "available" and "date"
    """
    return [
        {
            "name": s.get("properties", {}).get("nom").title(),
            "geometry": s.get("geometry", {}).get("coordinates"),
            "size": s.get("properties", {}).get("nbbornettes"),
            "tpe": False,  # No information in API response, False by default
            "available": -1,  # No information in API response, -1 by default
            "date": datetime.utcnow()
        }
        for s in get_raw_stations_lyon()
    ]


def get_stations_paris():
    """
    Get Paris station entries formatted
    :return: Entries for Paris stations with fields "name", "geometry", "size", "tpe", "available" and "date"
    """
    return [
        {
            "name": s.get("fields", {}).get("name").title(),
            "geometry": s.get("fields", {}).get("coordonnees_geo"),
            "size": s.get("fields", {}).get("capacity"),
            "tpe": s.get("fields", {}).get("is_installed") == "OUI",
            "available": s.get("fields", {}).get("numbikesavailable"),
            "date": datetime.utcnow()
        }
        for s in get_raw_stations_paris()
    ]


def get_stations_rennes():
    """
    Get Rennes station entries formatted
    :return: Entries for Rennes stations with fields "name", "geometry", "size", "tpe", "available" and "date"
    """
    return [
        {
            "name": s.get("fields", {}).get("nom").title(),
            "geometry": s.get("fields", {}).get("coordonnees"),
            "size": s.get("fields", {}).get("nombreemplacementsactuels"),
            "tpe": False,  # No information in API response, False by default
            "available": s.get("fields", {}).get("nombrevelosdisponibles"),
            "date": datetime.utcnow()
        }
        for s in get_raw_stations_rennes()
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


def get_raw_stations_lyon():
    """
    Get stations information for Lyon
    :return: Raw json from the GrandLyon download API
    """
    url = API_BASEURL_LYON + \
          "&typename=pvo_patrimoine_voirie.pvostationvelov" \
          "&outputFormat=application/json;%20subtype=geojson" \
          "&SRSNAME=EPSG:4171"

    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode("utf8"))

    return response_json.get("features", [])


def get_raw_stations_paris():
    """
    Get stations information for Paris
    :return: Raw json from the Paris OpenData API
    """
    url = API_BASEURL_PARIS + \
          "&q=" \
          "&lang=fr" \
          "&rows=3000" \
          "&timezone=Europe%2FParis"

    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode("utf8"))

    return response_json.get("records", [])


def get_raw_stations_rennes():
    """
    Get stations information for Rennes
    :return: Raw json from the Rennes OpenData API
    """
    url = API_BASEURL_RENNES + \
          "&q=" \
          "&lang=fr" \
          "&rows=3000" \
          "&timezone=Europe%2FParis"

    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode("utf8"))

    return response_json.get("records", [])


# ------------------------------------------- WORKER -------------------------------------------- #


def worker(refresh_delay=600, save=True, verbose=True):
    """
    Run worker to insert new entries
    :type refresh_delay: int
    :param refresh_delay: Delay between 2 worker's run
    :type save: bool
    :param save: If set on true, will save entries to the database
    :type verbose: bool
    :param verbose: If set on true, will show debug information
    """
    if verbose:
        print("Worker running, refresh rate: {} seconds".format(refresh_delay))

    while True:
        [lille, lyon, paris, rennes] = [get_stations_lille(), get_stations_lyon(), get_stations_paris(),
                                        get_stations_rennes()]

        if verbose:
            print(
                "{}: Got {} entries for Lille, {} entries for Lyon, {} entries for Paris, {} entries for Rennes".format(
                    datetime.now(), len(lille), len(lyon), len(paris), len(rennes)))

        if save:
            db.lille.insert_many(lille, ordered=False)
            db.lyon.insert_many(lyon, ordered=False)
            db.paris.insert_many(paris, ordered=False)
            db.rennes.insert_many(rennes, ordered=False)

            if verbose:
                print("{}: Saved entries to database".format(datetime.now()))

        time.sleep(refresh_delay)


if __name__ == '__main__':
    try:
        worker(refresh_delay=REFRESH_DELAY)
    except KeyboardInterrupt:
        pass