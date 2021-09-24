from database import db
from pymongo import DESCENDING

if __name__ == '__main__':
    lat = 50.63404011481544
    lon = 3.048599988675121
    max_found = 5

    found = [e for e in db.lille.find({"geometry": {"$near": [lat, lon]}}).limit(max_found).sort("date", DESCENDING)]
    print(len(found))
    for e in found:
        print ("- {}".format(e["name"]))
