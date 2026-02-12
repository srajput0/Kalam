from pymongo import MongoClient
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Multiple owner IDs
OWNER_IDS = [7621154046, 5680454765, 7517045929]

# MongoDB connection
client = MongoClient("mongodb+srv://teamjnc:TeamJNC123@cluster0.wx59fkk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["telegram_bots"]
users_col = db["registered_users"]

# Global bot info, to be filled on first use
BOT_INFO = None

# ✅ AUTO INIT BOT_INFO ONLY WHEN NEEDED
async def is_user_allowed(user_id: int, bot=None):
    global BOT_INFO

    # 🔁 Lazy-load BOT_INFO only when needed
    if BOT_INFO is None:
        if bot is None:
            raise ValueError("BOT_INFO is not initialized and bot instance not provided.")
        me = await bot.get_me()
        BOT_INFO = {
            "id": me.id,
            "username": me.username
        }

    # ✅ Allow owners on all bots
    if user_id in OWNER_IDS:
        return True, None

    user = users_col.find_one({"user_id": user_id})
    if user:
        if user["bot_id"] == BOT_INFO["id"]:
            return True, None
        else:
            return False, user["bot_username"]
    else:
        users_col.insert_one({
            "user_id": user_id,
            "bot_id": BOT_INFO["id"],
            "bot_username": BOT_INFO["username"],
            "joined_at": datetime.utcnow()
        })
        return True, None
