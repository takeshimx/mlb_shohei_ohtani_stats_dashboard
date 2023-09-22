from pymongo import MongoClient
import pandas as pd
import os
from dotenv import load_dotenv

# load the environment variables
load_dotenv(".env")
MONGO_URI = os.getenv("MONGO_URI")

# ----------- fetch data from MongoDB -----------
# Create a new client and connect to the server
client = MongoClient(MONGO_URI)

# Send a ping to confirm a successful connection
try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# target database and collection
db = client["user_db"]
collection = db["user"]


def insert_user(username, name, password):
    """Returns the user on a successful user creation, otherwise raises and error"""
    return collection.insert_one({"key": username, "name": name, "password": password})


def fetch_all_users():
    """Returns a dict of all users"""
    response = list(collection.find({}))
    return response


def create_df_from_mongo(db_name, collection_name, query=None):
    """Returns a dataframe by fetching from MongoDB"""
    # Create a new client and connect to the server
    client = MongoClient(MONGO_URI)

    # target database
    db = client[db_name]
    # Make a query to the specific DB and Collection
    cursor = db[collection_name].find(query)

    # Expand the cursor and construct the DataFrame
    df = pd.DataFrame(list(cursor))

    # Delete the _id
    del df["_id"]

    return df
