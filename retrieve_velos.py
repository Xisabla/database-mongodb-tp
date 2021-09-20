import requests
from pymongo import MongoClient
import time

atlas = MongoClient('mongodb+srv://tp:tp@cluster0.h2uze.mongodb.net/?retryWrites=true&w=majority')

db = atlas.willax

def get_vlille():
    url = "https://opendata.lillemetropole.fr/api/records/1.0/search/?dataset=vlille-realtime&q=&rows=3000&facet=libelle&facet=nom&facet=commune&facet=etat&facet=type&facet=etatconnexion"
    r = requests.get(url).json()
    return r["records"]

def get_velib():
    url = "https://opendata.paris.fr/api/records/1.0/search/?dataset=velib-disponibilite-en-temps-reel&q=&rows=3000&facet=name&facet=is_installed&facet=is_renting&facet=is_returning&facet=nom_arrondissement_communes&refine.is_installed=OUI"
    r = requests.get(url).json()
    return r["records"]

def get_velo_lyon():
    url = "https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&VERSION=2.0.0&request=GetFeature&typename=pvo_patrimoine_voirie.pvostationvelov&outputFormat=application/json;%20subtype=geojson&SRSNAME=EPSG:4171&startIndex=0&count=3000"
    r = requests.get(url).json()
    return r["features"]

def get_velo_rennes():
    url = "https://data.rennesmetropole.fr/api/records/1.0/search/?dataset=etat-des-stations-le-velo-star-en-temps-reel&q=&rows=3000&facet=nom&facet=etat&facet=nombreemplacementsactuels&facet=nombreemplacementsdisponibles&facet=nombrevelosdisponibles"
    r = requests.get(url).json()
    return r["records"]

def get_velib_stations():
    data = [
        {
            'name': s["fields"]["name"],
            'geometry': s["fields"]["coordonnees_geo"],
            'size': s["fields"]["capacity"],
            'tpe': s["fields"]["is_installed"] == "OUI",
            'available': s["fields"]["numbikesavailable"],
            'date' : time.strftime("%a %d %b %Y %H:%M:%S", time.localtime())
        }
        for s in get_velib()
    ]
    return data


def get_lyon_stations():
    data = [
        {
            'name': s["properties"]["nom"],
            'geometry': s["geometry"]["coordinates"],
            'size': s["properties"]["nbbornettes"],
            'date': time.strftime("%a %d %b %Y %H:%M:%S", time.localtime())
        }
        for s in get_velo_lyon()
    ]
    return data


def get_rennes_stations():
    data = [
        {
            'name': s["fields"]["nom"],
            'geometry': s["fields"]["coordonnees"],
            'size': s["fields"]["nombreemplacementsactuels"],
            'available': s["fields"]["nombrevelosdisponibles"],
            'date': time.strftime("%a %d %b %Y %H:%M:%S", time.localtime())
        }
        for s in get_velo_rennes()
    ]
    return data

while True:
    print('UPDATING')
    velo_paris = get_velib_stations()
    velo_lyon = get_lyon_stations()
    velo_rennes = get_rennes_stations()
    db.paris.insert_many(velo_paris, ordered=False)
    db.lyon.insert_many(velo_lyon, ordered=False)
    db.rennes.insert_many(velo_rennes, ordered=False)
    time.sleep(600)

