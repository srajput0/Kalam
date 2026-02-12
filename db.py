#🇳‌🇮‌🇰‌🇭‌🇮‌🇱‌
# Add moong db database
import os
from config import *
from pymongo import MongoClient
from datetime import datetime, timedelta
from pyrogram import Client, filters

#=================≠==================
# Initialize MongoDB client
client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]

users_collection = db["premium"]
collection = db["users"]
logs = db["settings"]
topics_col = db['log_topics']
banned = db["banned"]
user_database = db["data"]
topics = db["topics"]
topics_collection = db["media_topics"]
session_collection = db["sessions"]
redeem_codes = db["redeem_codes"]

#=================≠==================
def is_authorized(user_id):
    return users_collection.find_one({"_id": user_id}) or user_id == OWNER_ID

#==============================================
# Banned user checking 
def not_banned():
    async def func(_, __, message):
        user = message.from_user
        if not user:
            return False
        return banned.find_one({"user_id": user.id}) is None
    return filters.create(func)

#=================≠==================
def get_user_global_variables(user_id):
    """
    Retrieves global variables for a specific user.
    """
    try:
        user_data = user_database.find_one({"user_id": user_id})
        if not user_data:
            # Default global variables
            default_variables = {
                "thumb": "Team JNC",
                "thumb2": "/d",
                "CR": CREDIT,
                "my_name": "/d",
                "extension": CREDITWITHLINK,
                "pwtoken": None,
                "cptoken": None,
                "cwtoken": 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg',
                "topic": "/d",
                "watermark_text": '/d',
                "mode": "/master",
                "font_style": 'TTF (5).ttf',
                "font_color": "00008B",
            }
            user_database.insert_one({"user_id": user_id, **default_variables})
            return default_variables
        return user_data
    except Exception as e:
        print(f"Error fetching global variables for user {user_id}: {e}")
        return {}

#===============
def update_user_global_variables(user_id, updates):
    """
    Updates global variables for a specific user.
    """
    try:
        user_database.update_one({"user_id": user_id}, {"$set": updates}, upsert=True)
        print(f"Updated global variables for user {user_id}: {updates}")
    except Exception as e:
        print(f"Error updating global variables for user {user_id}: {e}")
