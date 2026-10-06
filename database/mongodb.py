from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Select Database
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
datasets_collection = db["datasets"]
reports_collection = db["reports"]
activities_collection = db["activities"]