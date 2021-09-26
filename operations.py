import json
import os
import sys
import requests
import time
from database import db
from datetime import datetime
from docopt import docopt
from dotenv import load_dotenv

load_dotenv()


# ------------------------------------------ CONSTANTS ------------------------------------------ #

# API URLs
API_BASEURL_LILLE = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime"
API_BASEURL_LYON = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature"
API_BASEURL_PARIS = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel"
API_BASEURL_RENNES = "https://data.rennesmetropole.fr/api/records/1.0/search/" \
                     "?dataset=etat-des-stations-le-velo-star-en-temps-reel"
LYON_AVAILABLE_BICYCLES = "https://transport.data.gouv.fr/gbfs/lyon/station_status.json"


# --------------------------------------- STATION GETTERS --------------------------------------- #

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


def get_lyon_available_bikes():
    """
    Get available bikes per station for Lyon
    :return: Raw json from the official Transport Data API
    """
    url = LYON_AVAILABLE_BICYCLES

    response = requests.request("GET", url)
    response_json = json.loads(response.text.encode("utf8"))

    return response_json.get("data", {}).get("stations", [])


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



# ------------------------------------------- OPERATIONS -------------------------------------------- #

def find_station(city, station_name):
    pat = re.compile(station_name, re.I)

    if city == Lille:
        return(db.lille.find({"name": {"$regex" : pat}}))
    
    if city == Paris:
        return(db.paris.find({"name": {"$regex" : pat}}))

    if city == Lyon:
        return(db.lyon.find({"name": {"$regex" : pat}}))

    if city == Rennes:
        return(db.rennes.find({"name": {"$regex" : pat}}))


def delete_station(city, station_name):
    if city == "Lille":
        db.lille.delete_many({"name" : station_name})
    if city == "Paris":
        db.paris.delete_many({"name" : station_name})
    if city == "Lyon":
        db.lyon.delete_many({"name" : station_name})
    if city == "Rennes":
        db.rennes.delete_many({"name" : station_name})


def update_station(city, station_name):
    if city == "Lille":
        data = [{
            "name": s.get("fields", {}).get("nom").title(),
            "geometry": s.get("geometry"),
            "size": s.get("fields", {}).get("nbvelosdispo") + s.get("fields", {}).get("nbplacesdispo"),
            "tpe": s.get("fields", {}).get("type") == "AVEC TPE",
            "available": s.get("fields", {}).get("nbvelosdispo"),
            "date": datetime.utcnow()
        }
        for s in get_raw_stations_lille() if s.get("fields", {}).get("nom") == station_name ]

        db.lille.replace_one(
            {"name" : station_name},
            data[0]
        )

    if city == "Paris":
        data = [
            {
                "name": s.get("fields", {}).get("nom").title(),
                "geometry": s.get("geometry"),
                "size": s.get("fields", {}).get("nbvelosdispo") + s.get("fields", {}).get("nbplacesdispo"),
                "tpe": s.get("fields", {}).get("type") == "AVEC TPE",
                "available": s.get("fields", {}).get("nbvelosdispo"),
                "date": datetime.utcnow()
            }
            for s in get_raw_stations_paris() if s.get("fields", {}).get("nom") == station_name 
        ]

        db.paris.replace_one(
            {"name" : station_name},
            data[0]
        )

    if city == "Lyon":
        print("ok")
        data = [
            {
                "name": s.get("properties", {}).get("nom").title(),
                "geometry": s.get("geometry"),
                "size": s.get("properties", {}).get("nbbornettes"),
                "tpe": v.get("is_installed"),
                "available": v.get("num_bikes_available"),
                "date": datetime.utcnow()
            }
            for s in get_raw_stations_lyon() if s.get("properties", {}).get("nom").title() == station_name
            for v in get_available_bicycles() if int(v.get("station_id")) == s.get("properties", {}).get("idstation")
        ]

        db.lyon.replace_one(
            {"name" : station_name},
            data[0]
        )

    if city == "Rennes":
        data = [
            {
                "name": s.get("fields", {}).get("nom").title(),
                "geometry": s.get("geometry"),
                "size": s.get("fields", {}).get("nombreemplacementsactuels"),
                "tpe": False,  # No information in API response, False by default
                "available": s.get("fields", {}).get("nombrevelosdisponibles"),
                "date": datetime.utcnow()
            }
            for s in get_raw_stations_rennes() if s.get("fields", {}).get("nom") == station_name 
        ]

        db.rennes.replace_one(
            {"name" : station_name},
            data[0]
        )

