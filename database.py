import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient, GEO2D
from pymongo.errors import PyMongoError

load_dotenv()

# Database url
ATLAS_URL = os.getenv("ATLAS_URL")

try:
    client = MongoClient(ATLAS_URL)
except PyMongoError as e:
    sys.exit("Failed worker initialization: " + str(e))

# TODO: Change for production (main branch)
db = client.gautier

db.lille.create_index([("geometry", GEO2D)])
db.lyon.create_index([('geometry', GEO2D)])
db.paris.create_index([('geometry', GEO2D)])
db.rennes.create_index([('geometry', GEO2D)])
