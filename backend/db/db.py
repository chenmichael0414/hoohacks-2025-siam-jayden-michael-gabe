from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Connect to MongoDB using the MONGO_URI from .env
client = MongoClient(os.getenv("MONGO_URI"))

# Choose a database and collection
db = client["hoohacks_notes"]
notes_collection = db["notes"]

# You can now use notes_collection.insert_one(), find(), etc.
