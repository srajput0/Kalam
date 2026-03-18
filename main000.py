

import io
import os
import re
import sys
import string
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import core as helper
from core import *
from utils import progress_bar
from db import *
from config import *
from datetime import datetime, timedelta
from zoneinfo import *
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import *
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg
import speedtest
from single import *

LOG_CHANNEL = -1003510970149      # for media logs
LOG_GROUP_ID = -1003510970149     # for topic logs
#=======================================================
# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)
#=======================================================
def run_speedtest():
    test = speedtest.Speedtest()
    test.get_best_server()
    download_speed = test.download()
    upload_speed = test.upload()
    share_link = test.results.share()
    results = test.results.dict()
    return download_speed, upload_speed, share_link, results

@bot.on_message(filters.command("speed") & not_banned())
async def speedtest_handler(client, message):
    status_message = await message.reply_text("⇆ ʀᴜɴɴɪɴɢ sᴩᴇᴇᴅᴛᴇsᴛ...")
    loop = asyncio.get_event_loop()
    
    try:
        download_speed, upload_speed, share_link, results = await loop.run_in_executor(None, run_speedtest)
    except Exception as e:
        await status_message.edit(f"❌ ᴇʀʀᴏʀ: {e}")
        return

    download_mbps = download_speed / 8_000_000
    upload_mbps = upload_speed / 8_000_000
    
    output = f"""
sᴘᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛ:

<u>ᴄʟɪᴇɴᴛ:</u>
ɪsᴘ : {results['client']['isp']}
ᴄᴏᴜɴᴛʀʏ : {results['client']['country']}

<u>sᴇʀᴠᴇʀ:</u>
ɴᴀᴍᴇ : {results['server']['name']}
ᴄᴏᴜɴᴛʀʏ : {results['server']['country']}, {results['server']['cc']}
sᴘᴏɴsᴏʀ : {results['server']['sponsor']}
ʟᴀᴛᴇɴᴄʏ : {results['server']['latency']} ms
ᴘɪɴɢ : {results['ping']} ms

<u>sᴘᴇᴇᴅs:</u>
↳ ᴅᴏᴡɴʟᴏᴀᴅ : {download_mbps:.2f} MB/s
↳ ᴜᴘʟᴏᴀᴅ : {upload_mbps:.2f} MB/s
"""

    await bot.send_photo(chat_id=message.chat.id, photo=share_link, caption=output)
    await status_message.delete()

#====================================================================================
def get_user_vars(user_id):
    user_data = get_user_global_variables(user_id)
    # Extract values with default fallback
    thumb = user_data.get("thumb", "/d")
    thumb2 = user_data.get("thumb2", "/d")
    CR = user_data.get("CR", CREDIT)
    my_name = user_data.get("my_name", "/d")
    extension = user_data.get("extension", CREDITWITHLINK)
    pwtoken = user_data.get("pwtoken", None)
    cptoken = user_data.get("cptoken", None)
    cwtoken = user_data.get("cwtoken", 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg')
    topic = user_data.get("topic", "/d")
    watermark_text = user_data.get("watermark_text", "/d")
    mode = user_data.get("mode", "/master")
    font_style = user_data.get("font_style", "TTF (5).ttf")
    font_color = user_data.get("font_color", "00008B")
    return (
        thumb,
        thumb2,
        CR,
        my_name,
        extension,
        pwtoken,
        cptoken,
        cwtoken,
        topic,
        watermark_text,
        mode,
        font_style,
        font_color,
    )
user_stop_flags = {}
user_processing = {}
#================================================================================================================================
# Image URLs for the random image feature
image_urls = [
    "https://tinypic.host/images/2025/02/07/IMG_20250207_224444_975.jpg",
    "https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png",
    # Add more image URLs as needed
]
#=========================== Media topic ===================================
async def get_or_create_topic_id(channel_id, t_name, b_name):
    existing = topics_collection.find_one({"channel_id": channel_id, "topic": t_name})
    if existing:
        return existing["topic_id"]

    # Create forum topic
    try:
        forum_topic = await bot.create_forum_topic(channel_id, t_name)
        topic_id = forum_topic.id
        welcome = await bot.send_message(chat_id=channel_id,message_thread_id=topic_id,text=f"<blockquote><b>🧾Batch Name : {b_name}\n🧩Topic Name : {t_name}</b></blockquote>")
        try:
            await bot.pin_chat_message(channel_id, welcome.id)
            await bot.delete_messages(channel_id, welcome.id + 1)
        except Exception as e:
            await bot.send_message(chat_id=channel_id, message_thread_id=topic_id, text=f"Failed to pin message: {str(e)}")
        topics_collection.insert_one({"channel_id": channel_id, "topic": t_name, "topic_id": topic_id})
        return topic_id
    except Exception as e:
        print(f"Error creating topic: {e}")
        fallback_existing = topics_collection.find_one({"channel_id": channel_id, "topic": t_name})
        if fallback_existing:
            return fallback_existing["topic_id"]
        try:
            welcome = await bot.send_message(
                chat_id=channel_id,
                text=f"<blockquote>🧩Topic : {t_name}</blockquote>"
            )
            try:
                await welcome.pin()
            except Exception:
                await welcome.pin(both_sides=True)
            await bot.delete_messages(channel_id, welcome.id + 1)
            topics_collection.insert_one({
                "channel_id": channel_id,
                "topic": t_name,
                "topic_id": 0
            })
        except Exception as e2:
            await bot.send_message(chat_id=channel_id, text=f"Failed to pin message: {str(e2)}")
        return None

#================================================================================================================================
# 1️⃣ RESET specific channel's media topics
@bot.on_message(filters.command("rmt") & filters.private & filters.user(OWNER_ID) & not_banned())
async def reset_media_topic_command(client, message: Message):
    await message.reply("📢 Send the **Channel ID** (e.g., `-100xxxxxxxxxx`) to reset its saved media topics:")

    try:
        input_msg = await bot.listen(message.chat.id, filters=filters.user(message.from_user.id))
        await input_msg.delete()
        channel_id = str(input_msg.text.strip())  # Use string, don't cast to int

        result = topics_collection.delete_many({"channel_id": channel_id})
        await message.reply(
            f"✅ Media topic records for channel `{channel_id}` reset.\n"
            f"🗑️ Deleted `{result.deleted_count}` topic entries from database."
        )
    except Exception as e:
        await message.reply(f"❌ Failed to reset topics.\n**Error:** `{e}`")


# 2️⃣ SHOW saved topics from DB
@bot.on_message(filters.command("smt") & filters.private & filters.user(OWNER_ID) & not_banned())
async def show_saved_topics(client, message: Message):
    data = list(topics_collection.find())

    if not data:
        await message.reply("📂 No saved topics found in the database.")
        return

    # Format topic entries
    lines = ["📚 Saved Topics:\n"]
    for i, entry in enumerate(data, start=1):
        cid = entry.get("channel_id")
        topic = entry.get("topic")
        tid = entry.get("topic_id")
        lines.append(f"{i}. 🔹 Channel ID: {cid}\n   🧩 Topic: {topic}\n   🆔 Topic ID: {tid}\n")

    content = "\n".join(lines)

    # In-memory .txt file
    file = io.BytesIO(content.encode("utf-8"))
    file.name = "saved_topics.txt"

    await message.reply_document(document=file, caption="📄 Saved media topics from database.")


# 3️⃣ RESET ALL media topics
@bot.on_message(filters.command("ramt") & filters.private & filters.user(OWNER_ID) & not_banned())
async def reset_all_topics(client, message: Message):
    confirm = await message.reply("⚠️ Are you sure you want to delete all saved topics? Reply with `Yes` to confirm.")

    try:
        confirm_msg = await bot.listen(message.chat.id, filters=filters.user(message.from_user.id))
        await confirm_msg.delete()
        if confirm_msg.text.strip().lower() != "yes":
            return await message.reply("❌ Cancelled. Nothing was deleted.")

        result = topics_collection.delete_many({})
        await message.reply(
            f"✅ All topics reset successfully.\n🗑️ `{result.deleted_count}` topic entries deleted from database."
        )
    except Exception as e:
        await message.reply(f"❌ Failed to reset all topics.\n**Error:** `{e}`")


#================= Utility: Livegram log topic  =================
async def chat_topic(bot, user_id, user_first_name):
    existing = topics.find_one({"user_id": user_id})
    if existing:
        return existing["topic_id"]

    topic = await bot.create_forum_topic(LOG_GROUP_ID, user_first_name[:32])
    topics.insert_one({"user_id": user_id, "topic_id": topic.id})
    return topic.id

#=========== media log topics =========
async def get_or_create_topic(bot, m, LOG_CHANNEL):
    key = str(m.chat.id)
    doc = topics_col.find_one({"chat_id": key})

    if doc:
        return doc["topic_id"]

    topic_title = f"Logs-{key}"
    try:
        topic = await bot.create_forum_topic(LOG_CHANNEL, topic_title)
        topic_id = topic.id
        topics_col.insert_one({"chat_id": key, "topic_id": topic_id})
        return topic_id
    except Exception as e:
        print(f"Failed to create topic: {e}")
        return None

#============= reset topics ================
@bot.on_message(filters.command("reset") & filters.user(OWNER_ID) & not_banned())
async def reset_topic_command(bot, m):
    topics = list(topics_col.find())
    if not topics:
        await m.reply("❌ No saved topics found.")
        return

    msg = "**📑 Saved Topics:**\n\n"
    for i, t in enumerate(topics, start=1):
        msg += f"{i}. Chat ID: `{t['chat_id']}` | Topic ID: `{t['topic_id']}`\n"

    msg += (
        "\n**What would you like to do?**\n"
        "`reset <number>` – Reset a specific topic\n"
        "`reset all` – Reset all saved topics\n\n"
        "👉 _Example:_ `reset 2` or `reset all`"
    )

    prompt = await m.reply(msg)
    
    try:
        reply = await bot.listen(m.chat.id)
        await reply.delete()
        user_input = reply.text.strip().lower()

        if user_input == "reset all":
            count = topics_col.delete_many({}).deleted_count
            await m.reply(f"✅ All topics reset. ({count} entries removed)")
        elif user_input.startswith("reset"):
            try:
                index = int(user_input.split()[1]) - 1
                if 0 <= index < len(topics):
                    chat_id = topics[index]["chat_id"]
                    topics_col.delete_one({"chat_id": chat_id})
                    await m.reply(f"✅ Topic for Chat ID `{chat_id}` has been reset.")
                else:
                    await m.reply("❌ Invalid topic number.")
            except:
                await m.reply("❌ Invalid format. Use `reset <number>` or `reset all`.")
        else:
            await m.reply("❌ Unknown input. Use `reset <number>` or `reset all`.")
    except Exception as e:
        await m.reply(f"⚠️ Error: {str(e)}")
#================================================================================================================================
#======== 1. get_expiry to calculate expiry datetime based on duration string ============
def get_expiry(duration: str):
    now = datetime.utcnow()
    if duration.endswith("m") and duration[:-1].isdigit():
        return now + timedelta(minutes=int(duration[:-1]))
    elif duration.endswith("h") and duration[:-1].isdigit():
        return now + timedelta(hours=int(duration[:-1]))
    elif duration.endswith("d") and duration[:-1].isdigit():
        return now + timedelta(days=int(duration[:-1]))
    elif duration.endswith("w") and duration[:-1].isdigit():
        return now + timedelta(weeks=int(duration[:-1]))
    elif duration == "1mo":
        return now + timedelta(days=30)
    elif duration == "1y":
        return now + timedelta(days=365)
    else:
        raise ValueError("Invalid duration format")

#======== 2. get_start_time to calculate plan start time from expiry ============
def get_start_time(expires: datetime, duration: str) -> datetime:
    # Calculate start time by reversing expiry calculation
    if duration.endswith("m") and duration[:-1].isdigit():
        return expires - timedelta(minutes=int(duration[:-1]))
    elif duration.endswith("h") and duration[:-1].isdigit():
        return expires - timedelta(hours=int(duration[:-1]))
    elif duration.endswith("d") and duration[:-1].isdigit():
        return expires - timedelta(days=int(duration[:-1]))
    elif duration.endswith("w") and duration[:-1].isdigit():
        return expires - timedelta(weeks=int(duration[:-1]))
    elif duration == "1mo":
        return expires - timedelta(days=30)
    elif duration == "1y":
        return expires - timedelta(days=365)
    else:
        raise ValueError("Invalid duration format")

#======== 3. utc_to_ist_ampm to convert UTC to IST in readable format ============
def utc_to_ist_ampm(utc_dt):
    ist = utc_dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("Asia/Kolkata"))
    return ist.strftime("%Y-%m-%d %I:%M:%S %p")
    
#======== 4. is_authorized to check if user is premium and auto-remove expired users ============
def is_authorized(user_id):
    user = users_collection.find_one({"_id": user_id})
    if user and user.get("expires_at"):
        if datetime.utcnow() < user["expires_at"]:
            return True
        else:
            users_collection.delete_one({"_id": user_id})
    return user_id == OWNER_ID

#======== 5. add for adding a user to premium ============
@bot.on_message(filters.command("add") & filters.user(OWNER_ID) & not_banned())
async def add_user(_, m: Message):
    if len(m.command) < 3:
        return await m.reply("⚠️ Usage: /add [user_id] [1m/1h/1d/1w/1mo/1y]")
    try:
        uid = int(m.command[1])
        duration = m.command[2]
        expires = get_expiry(duration)
        start_time = get_start_time(expires, duration)
        start_str = utc_to_ist_ampm(start_time)
        expires_str = utc_to_ist_ampm(expires)

        users_collection.update_one(
            {"_id": uid},
            {"$set": {"expires_at": expires, "duration": duration}},
            upsert=True
        )

        try:
            user_obj = await bot.get_users(uid)
            name = user_obj.first_name or "User"
        except:
            name = "User"

        def get_progress_caption():
            now = datetime.utcnow()
            remaining = expires - now
            remaining_seconds = max(0, remaining.total_seconds())
            total_duration = (expires - start_time).total_seconds()
            percent = int((remaining_seconds / total_duration) * 100) if total_duration > 0 else 0
            bar_blocks = int(percent / 10)
            progress = "🟩" * bar_blocks + "⬜" * (10 - bar_blocks)
            caption = (
                f"👤 **Name :** {name}\n"
                f"🆔 **User ID :** `{uid}`\n"
                f"🕒 **Duration :** `{duration}`\n"
                f"📆 **Start Time :** `{start_str}`\n"
                f"⏰ **Expires At :** `{expires_str}`\n"
                f"⏳ **Remaining :** `{str(remaining).split('.')[0] if remaining_seconds > 0 else 'Expired'}`\n"
                f"📶 **Progress :** {percent}%\n`{progress}`"
            )
            return caption, remaining_seconds

        initial_caption, _ = get_progress_caption()
        owner_msg = await m.reply(f"✅ Premium access granted to `{uid}`.\n\n{initial_caption}")

        try:
            user_msg = await bot.send_message(uid, f"🎉 **Congratulations!** 🎉\n\n{initial_caption}")
        except Exception as e:
            print(f"Couldn't notify user: {e}")
            user_msg = None

        # ⏳ Auto-update until expiry
        async def auto_update_msg():
            while True:
                await asyncio.sleep(600)
                try:
                    new_caption, remaining = get_progress_caption()
                    if remaining <= 0:
                        final_caption = (
                            f"{new_caption}"
                        )
                        await owner_msg.edit_text(f"⚠️ Premium for `{uid}` has expired.\n\n{final_caption}")
                        print("Owner message expired — final update done.")
                        break
                    await owner_msg.edit_text(f"✅ Premium access granted to `{uid}`.\n\n{new_caption}")
                except Exception as e:
                    print("[Owner auto-update stopped]", e)
                    break

        async def auto_update_user():
            if not user_msg:
                return
            while True:
                await asyncio.sleep(600)
                try:
                    new_caption, remaining = get_progress_caption()
                    if remaining <= 0:
                        final_caption = (
                            f"❌ **Premium Expired!** ❌\n\n"
                            f"{new_caption}"
                        )
                        await user_msg.edit_text(f"{final_caption}")
                        print("User message expired — final update done.")
                        break
                    await user_msg.edit_text(f"🎉 **Congratulations!** 🎉\n\n{new_caption}")
                except Exception as e:
                    print("[User auto-update stopped]", e)
                    break

        asyncio.create_task(auto_update_msg())
        asyncio.create_task(auto_update_user())

    except Exception as e:
        print(f"[add_user error] {e}")
        await m.reply("❌ Invalid ID or duration.")

#======== 6. rem for removing a user from premium ============
@bot.on_message(filters.command("rem") & filters.user(OWNER_ID) & not_banned())
async def remove_user(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("⚠️ Usage: /rem [user_id]")
    try:
        uid = int(m.command[1])
        user = users_collection.find_one({"_id": uid})
        if not user:
            return await m.reply("❌ User not found.\n🤔 Are you sure this user has premium access?")
        result = users_collection.delete_one({"_id": uid})
        if result.deleted_count:
            try:
                user_info = await bot.get_users(uid)
                name = user_info.first_name
            except:
                name = "User"
            try:
                await bot.send_message(uid,
                    f"⚠️ **Your premium plan has been removed.**\n\n"
                    f"🙏 Thank you {name} for using our service.\n"
                )
            except:
                pass
            await m.reply(
                f"✅ **Premium Removed Successfully**\n\n"
                f"👤 **User:** `{uid}` ({name})\n\n"
                f"🗑️ Removed from authorized users."
            )
        else:
            await m.reply("❌ User not found.\n🤔 Are you sure this user has premium access?")
    except:
        await m.reply("⚠️ Usage: /rem [user_id]")

#======== 7. users for listing all premium users ============
async def generate_users_text(users):
    text = "👑 **Premium Users List** 👑\n\n"
    now = datetime.utcnow()
    active_found = False

    for i, user in enumerate(users, start=1):
        uid = user["_id"]
        duration = user.get("duration", "?")
        expires = user.get("expires_at")

        try:
            user_info = await bot.get_users(uid)
            name = user_info.first_name or "User"
        except:
            name = "User"

        try:
            start_time = get_start_time(expires, duration)
            total = (expires - start_time).total_seconds()
            remain = max(0, (expires - now).total_seconds())
            percent = int((remain / total) * 100) if total > 0 else 0
            bar = "🟩" * (percent // 10) + "⬜" * (10 - percent // 10)
            start_str = utc_to_ist_ampm(start_time)
            remaining_str = str(timedelta(seconds=int(remain))) if remain > 0 else "Expired"
        except:
            start_str, bar, percent, remaining_str = "N/A", "⬜" * 10, 0, "N/A"
            remain = 0

        expires_str = utc_to_ist_ampm(expires) if expires else "N/A"

        if remain > 0:
            active_found = True

        text += (
            f"{i}. 👤 Name :  {name}**\n"
            f"    🆔 User ID : `{uid}`\n"
            f"    🕒 Duration : `{duration}`\n"
            f"    📅 Start : `{start_str}`\n"
            f"    ⏰ Expires : `{expires_str}`\n"
            f"    ⌛ Remaining : `{remaining_str}`\n"
            f"    📶 Progress : {percent}%\n    `{bar}`\n\n"
        )
    return text, active_found

@bot.on_message(filters.command("users") & filters.user(OWNER_ID) & not_banned())
async def show_users(_, m: Message):
    users = list(users_collection.find())
    if not users:
        return await m.reply("🚫 No authorized users found.")

    text, active_found = await generate_users_text(users)
    sent = await m.reply(text)

    async def auto_update():
        while True:
            await asyncio.sleep(600)
            try:
                users = list(users_collection.find())
                text, active_found = await generate_users_text(users)
                if active_found:
                    await sent.edit_text(text)
                else:
                    await sent.delete()
                    await bot.send_message(
                        OWNER_ID,
                        "🚨 All premium users have expired. The /users status message was deleted."
                    )
                    print("🛑 All users expired. Auto-update stopped, message deleted, owner notified.")
                    break
            except Exception as e:
                print("Auto-update error:", e)
                break

    asyncio.create_task(auto_update())

#======== 8. clear for removing all premium users except owner ============
@bot.on_message(filters.command("clear") & filters.user(OWNER_ID) & not_banned())
async def clear_all_users(_, m: Message):
    users = list(users_collection.find({"_id": {"$ne": OWNER_ID}}))
    if not users:
        return await m.reply("ℹ️ No premium users found to clear.")
    confirm_msg = await m.reply(
        f"⚠️ Are you sure you want to remove **{len(users)}** premium users?\n\n"
        "Reply with `Yes` to confirm."
    )
    try:
        reply = await bot.listen(m.chat.id, timeout=30)
        if reply.text.strip().upper() != "YES":
            return await m.reply("❌ Cancelled.")
    except:
        return await m.reply("⏰ Timed out. Cancelled.")
    removed_text = "🧹 **Removed Premium Users:**\n\n"
    for i, u in enumerate(users, start=1):
        uid = u["_id"]
        duration = u.get("duration", "?")
        expires = u.get("expires_at")
        try:
            user_obj = await bot.get_users(uid)
            name = user_obj.first_name or "User"
        except:
            name = "User"
        try:
            start_time = get_start_time(expires, duration)
            start_str = utc_to_ist_ampm(start_time)
        except:
            start_str = "N/A"
        users_collection.delete_one({"_id": uid})
        try:
            await bot.send_message(
                uid,
                f"⚠️ **Your Premium Plan Has Been Removed** ⚠️\n\n"
                f"👤 **Name :** {name}\n"
                f"🕒 **Plan Duration :** `{duration}`\n"
                f"📆 **Activated On :** `{start_str}`\n\n"
                "🙏 Thank you for using our premium service."
            )
        except:
            pass
        removed_text += (
            f"{i}. 👤 Name :  {name}**\n"
            f"   🆔 User ID : `{uid}`\n"
            f"   🕒 Duration : `{duration}`\n"
            f"   📅 Start : `{start_str}`\n\n"
        )
    await m.reply(f"✅ Successfully removed **{len(users)}** users.\n\n{removed_text}")

#======== 9. myplan for checking current user's premium status ============
@bot.on_message(filters.command("myplan") & not_banned())
async def check_premium(_, m: Message):
    user_id = m.from_user.id
    user = users_collection.find_one({"_id": user_id})
    try:
        user_obj = await bot.get_users(user_id)
        name = user_obj.first_name or "User"
    except:
        name = "User"

    if user_id == OWNER_ID:
        return await m.reply(
            f"👑 **Hello {name} (Owner)**\n\n"
            "🎖 You have **Full Lifetime Premium Access !**\n"
        )

    if not user:
        return await m.reply(
            f"🚫 **Sorry {name}, you're not a premium user.**\n\n"
            f"📩 Please contact the {CREDITWITHLINK} or request access.\n\n"
            "🔐 Premium access gives you powerful features to supercharge your experience!"
        )

    async def get_plan_text():
        now = datetime.utcnow()
        expires = user.get("expires_at")
        duration_str = user.get("duration", "1m")
        try:
            started_at = get_start_time(expires, duration_str)
        except:
            started_at = expires - timedelta(minutes=1)
        total_duration = (expires - started_at).total_seconds()
        remaining = expires - now
        remaining_seconds = max(0, remaining.total_seconds())
        percent = int((remaining_seconds / total_duration) * 100) if total_duration > 0 else 0
        bar_blocks = int(percent / 10)
        progress = "🟩" * bar_blocks + "⬜" * (10 - bar_blocks)
        start_str = utc_to_ist_ampm(started_at)
        expires_str = utc_to_ist_ampm(expires)
        caption = (
            f"🎖 **Premium Plan Of {name}** 🎖\n\n"
            f"🆔 **User ID :** `{user_id}`\n"
            f"🕒 **Duration :** `{duration_str}`\n"
            f"✅ **Started At :** `{start_str}`\n"
            f"⏰ **Expires At :** `{expires_str}`\n"
            f"⏳ **Remaining :** `{str(remaining).split('.')[0] if remaining_seconds > 0 else 'Expired'}`\n\n"
            f"📶 **Progress :** {percent}%\n`{progress}`"
        )
        return caption, remaining_seconds

    text, remaining_seconds = await get_plan_text()
    sent = await m.reply(text)

    async def auto_update():
        while True:
            await asyncio.sleep(600)  # 10 minutes
            try:
                text, remaining_seconds = await get_plan_text()
                if remaining_seconds > 0:
                    await sent.edit_text(text)
                else:
                    await sent.delete()
                    break
            except Exception as e:
                print("Auto-update stopped for /myplan:", e)
                break
    asyncio.create_task(auto_update())
    
#======== 10. auto_remove_expired runs in background and clears expired users ============
async def auto_remove_expired():
    while True:
        now = datetime.utcnow()
        expired_users = list(users_collection.find({"expires_at": {"$lte": now}}))
        for user in expired_users:
            uid = user["_id"]
            duration = user.get("duration", "unknown")
            expires = user.get("expires_at")
            try:
                start_time = get_start_time(expires, duration)
                start_str = utc_to_ist_ampm(start_time)
            except:
                start_str = "N/A"
            expires_str = utc_to_ist_ampm(expires)
            try:
                user_obj = await bot.get_users(uid)
                name = user_obj.first_name or "User"
            except:
                name = "User"
            users_collection.delete_one({"_id": uid})
            try:
                await bot.send_message(
                    uid,
                    f"⚠️ **Your Premium Plan Has Expired** ⚠️\n\n"
                    f"👤 **Name :** {name}\n"
                    f"🆔 **User ID :** `{uid}`\n"
                    f"🕒 **Duration :** `{duration}`\n"
                    f"📆 **Started On :** `{start_str}`\n"
                    f"⌛ **Expired At :** `{expires_str}`\n\n"
                    "🙏 Thank you for using our premium service."
                )
            except:
                pass
            try:
                await bot.send_message(
                    OWNER_ID,
                    f"⚠️ **A Premium Plan Just Expired** ⚠️\n\n"
                    f"👤 **Name :** {name}\n"
                    f"🆔 **User ID :** `{uid}`\n"
                    f"🕒 **Duration :** `{duration}`\n"
                    f"📆 **Start Time :** `{start_str}`\n"
                    f"⌛ **Expired At :** `{expires_str}`\n\n"
                    "🗑️ User has been removed from the premium database."
                )
            except:
                pass
        await asyncio.sleep(600)
#======================== Ad based token system =============================
Param = {}
async def create_ttl_index():
    await users_collection.create_index("expires_at", expireAfterSeconds=0)

async def generate_random_param(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def get_shortened_url(deep_link):
    api_url = f"https://{WEBSITE_URL}/api?api={AD_API}&url={deep_link}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as response:
            if response.status == 200:
                data = await response.json()
                if data.get("status") == "success":
                    return data.get("shortenedUrl")
    return None
    
@bot.on_message(filters.command("token"))
async def smart_handler(client, message):
    user_id = message.chat.id
    if is_authorized(user_id):
        return await message.reply("✅ Your session is already active or you're a premium user.")

    return await message.reply(
        "⛔️ <b><u>Feature Not Available</u></b>\n\n"
        "<blockquote>"
        "The <b>/token</b> feature is only available in our free-tier bots to let users experience premium features temporarily.\n\n"
        "Since you're already using a premium bot, this feature is currently <b>disabled</b>."
        "</blockquote>\n\n"
        "💎 <b><u>Want full access?</u></b>\n"
        "<blockquote>"
        f"💬 Contact <b>{CREDITWITHLINK}</b> to get a personal premium plan with:\n"
        "✅ Unlimited access\n"
        "✅ Fast download/upload\n"
        "✅ Custom thumbnails, fonts, watermarks\n"
        "</blockquote>",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📞 Contact", url=f"{CONTACTLINK}"),
             InlineKeyboardButton("🛠️ Help", url=f"{HELPLINK}")],
        ])
    )

    param = await generate_random_param()
    Param[user_id] = param

    deep_link = f"https://t.me/{client.me.username}?start={param}"
    shortened_url = await get_shortened_url(deep_link)

    if not shortened_url:
        return await message.reply("❌ Failed to generate the token link. Try again.")

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Verify Token", url=shortened_url)]
    ])
    await message.reply(
        "Click below to verify your free access token:\n\n"
        "> 🕒 Valid for 3 hours\n> 🆓 Unlocks all features temporarily",
        reply_markup=button
    )
#======================= redeem codes ====================
def generate_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
@bot.on_message(filters.command("codes") & filters.user(OWNER_ID))
async def generate_codes_cmd(bot, message: Message):
    if len(message.command) < 2 or not message.command[1].isdigit():
        return await message.reply("⚠️ Usage: /codes [number_of_codes]")

    count = int(message.command[1])
    if count < 1 or count > 100:
        return await message.reply("⚠️ Please generate between 1 and 100 codes at a time.")

    codes = []
    for _ in range(count):
        code = generate_code()
        redeem_codes.insert_one({
            "code": code,
            "created_at": datetime.utcnow()
        })
        codes.append(code)

    formatted_codes = "\n".join(f"`/redeem {c}`" for c in codes)
    await message.reply(f"✅ Generated {count} redeem codes:\n\n{formatted_codes}")


@bot.on_message(filters.command("redeem") & filters.private)
async def redeem_code_cmd(bot, message: Message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: /redeem [code]")

    code = message.command[1].upper()

    # Check if code exists
    doc = redeem_codes.find_one({"code": code})
    if not doc:
        return await message.reply("❌ Invalid or already used code.")

    # Check if user already has access
    user = users_collection.find_one({"_id": user_id})
    if user and user.get("expires_at") and user["expires_at"] > datetime.utcnow():
        return await message.reply("✅ You already have active access.")

    # Grant 3-hour access
    expires_at = datetime.utcnow() + timedelta(hours=3)
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {
            "expires_at": expires_at,
            "duration": "3h"
        }},
        upsert=True
    )

    # Delete the code to make it one-time use
    redeem_codes.delete_one({"code": code})

    await message.reply(
        f"🎉 Redeem successful! You now have free access until {expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )

#================================================================================================================================
# /ban: Ban a user (reply or by ID)
@bot.on_message(filters.command("ban") & filters.user(OWNER_ID) & not_banned())
async def ban_user(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Use `/ban user_id`")
    try:
        user_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Invalid user ID.")
    # Prevent banning OWNER_ID
    if user_id == OWNER_ID:
        return await message.reply("🙅 You can't ban yourself, boss.")
    banned.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    await message.reply(f"✅ Banned user `{user_id}`")
    # Notify banned user
    try:
        await client.send_message(
            user_id,
            "<i><b>You have been banned🚫 by the OWNER.\n\nYou can no longer use this bot.</b></i>"
        )
    except Exception:
        pass  # User has blocked the bot or can't be messaged

# /unban: Unban user by ID
@bot.on_message(filters.command("unban") & filters.user(OWNER_ID) & not_banned())
async def unban_user(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Usage: /unban <user_id>")
    try:
        user_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Invalid user ID.")
    result = banned.delete_one({"user_id": user_id})
    
    if result.deleted_count:
        await message.reply(f"<i><b>✅ Unbanned user `{user_id}`</b></i>")
    else:
        await message.reply("<i><b>ℹ️ User was not banned.</b></i>")
    try:
        await client.send_message(
            user_id,
            "<i><b>✅ You have been unbanned by the OWNER.</b></i>"
        )
    except Exception:
        pass  # User has blocked the bot or can't be messaged
        
#===============================================================================================================================
def add_user(user_id):
    if not collection.find_one({"_id": user_id}):
        collection.insert_one({"_id": user_id})

def remove_user(user_id):
    collection.delete_one({"_id": user_id})
    
def get_all_users():
    return [doc["_id"] for doc in collection.find()]
    
# Global store to keep track of broadcast requests
broadcast_requests = {}

@bot.on_message(filters.command("broadcast") & filters.user(OWNER_ID) & not_banned())
async def broadcast_handler(bot, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message to broadcast it.")

    # Save the message ID and user ID
    broadcast_requests[message.from_user.id] = {
        "chat_id": message.chat.id,
        "message_id": message.reply_to_message.id
    }

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_broadcast"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast")
        ]
    ])

    await message.reply_text(
        "Are you sure you want to broadcast this message?",
        reply_markup=buttons
    )


@bot.on_callback_query(filters.regex("^(confirm_broadcast|cancel_broadcast)$"))
async def handle_broadcast_decision(bot, query: CallbackQuery):
    user_id = query.from_user.id
    action = query.data

    if user_id not in broadcast_requests:
        return await query.answer("No broadcast request found.", show_alert=True)

    data = broadcast_requests.pop(user_id)
    chat_id = data["chat_id"]
    message_id = data["message_id"]

    if action == "cancel_broadcast":
        await query.message.edit_text("❌ Broadcast canceled.")
        return

    await query.message.edit_text("📣 Broadcasting...")

    # Start broadcasting
    sent = 0
    failed = 0
    total = 0
    failed_users = []

    users = get_all_users()

    for uid in users:
        total += 1
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=chat_id,
                message_id=message_id
            )
            sent += 1
        except Exception as e:
            print(f"Failed to send to {uid}: {e}")
            failed += 1
            failed_users.append(uid)

    # Report
    report_text = (
        f"<blockquote>📢 <b>Broadcast Complete</b></blockquote>\n\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed to Send: {failed}\n"
        f"📊 Total Users: {total}"
    )
    await bot.send_message(chat_id, report_text)

#================= Reactiom & add users in database ======================
from random import choice
emojis = [
    "😢", "🌚", "😱", "😁", "👻", "❤️", "👍", "👎",
    "🔥", "🥰", "👏", "🤔", "🤯", "🤬", "🎉", "🤩",
    "🤮", "💩", "🙏", "👌", "🕊️", "🤡", "🥱", "🥴",
    "😍", "🐬", "❤️‍🔥", "🌭", "💯", "🤣", "⚡", "🍌",
    "🏆", "💔", "😐", "🤨", "🍓", "🍾", "💋", "🖕",
    "😈", "😴", "😭", "🤓", "🧑‍💻", "👀", "🎃", "🙈",
    "😇", "😨", "🤝", "✍️", "🤗", "🫡", "🎅", "🎄",
    "☃️", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄",
    "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀",
    "😡"
]
efcts = [5107584321108051014, 5159385139981059251, 5104841245755180586, 5046509860389126442]
async def react_msg(msg):
    for attempt in range(5):
        try:
            emoji = choice(emojis)
            await msg.react(emoji, big=True)
            break
        except Exception as e:
            await asyncio.sleep(0.3)
            continue
@bot.on_message(filters.private & filters.text, group=-1)
async def auto_react(bot, message):
    if message.edit_date or not message.from_user:
        return
    add_user(message.from_user.id)
    await asyncio.sleep(0.5)
    await react_msg(message)

    if message.chat.id == LOG_GROUP_ID and message.from_user.id == OWNER_ID:
        return  # ⛔ Skip OWNER_ID's message in LOG_GROUP to avoid loop
        
    user = message.from_user
    if banned.find_one({"user_id": user.id}):
        # Stylish message with appeal button
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Appeal to OWNER", callback_data=f"appeal_{user.id}")]
        ])
        return await message.reply(
            "<i><b>❌Access Denied!\n\n🚫You are banned by the OWNER.</b></i>",
            reply_markup=buttons
        )

    if "://" in message.text:
        await handle_link_text(bot, message)
        return
        
    topic_id = await chat_topic(bot, user.id, user.first_name)

    tag = f"👤 [{user.first_name}](tg://user?id={user.id})"

    # Inline buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Ban User", callback_data=f"ban_{user.id}"),
         InlineKeyboardButton("ℹ️ User Info", callback_data=f"info_{user.id}")]
    ])

    try:
        if message.text or message.caption:
            content = message.text or message.caption
            await bot.send_message(LOG_GROUP_ID, f"{tag}:\n{content}", reply_markup=buttons, message_thread_id=topic_id)
        elif message.photo:
            await bot.send_photo(LOG_GROUP_ID, message.photo.file_id, caption=tag, reply_markup=buttons, message_thread_id=topic_id)
        elif message.video:
            await bot.send_video(LOG_GROUP_ID, message.video.file_id, caption=tag, reply_markup=buttons, message_thread_id=topic_id)
        elif message.document:
            await bot.send_document(LOG_GROUP_ID, message.document.file_id, caption=tag, reply_markup=buttons, message_thread_id=topic_id)
        elif message.audio:
            await bot.send_audio(LOG_GROUP_ID, message.audio.file_id, caption=tag, reply_markup=buttons, message_thread_id=topic_id)
        elif message.voice:
            await bot.send_voice(LOG_GROUP_ID, message.voice.file_id, caption=tag, reply_markup=buttons, message_thread_id=topic_id)
        elif message.animation:
            await bot.send_animation(LOG_GROUP_ID, message.animation.file_id, caption=tag, reply_markup=buttons, message_thread_id=topic_id)
        else:
            await bot.send_message(LOG_GROUP_ID, f"{tag}:\nUnsupported message type.", reply_markup=buttons, message_thread_id=topic_id)
    except Exception as e:
        print("Logging Error:", e)
    
    
@bot.on_callback_query(filters.regex(r"^appeal_(\d+)"))
async def handle_appeal_request(client: Client, callback: CallbackQuery):
    user_id = int(callback.data.split("_")[1])
    user = await client.get_users(user_id)
    await callback.answer("Appeal sent to the OWNER.", show_alert=True)

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
        ]
    ])

    await client.send_message(
        OWNER_ID,
        f"<i><b>📩Unban Appeal Received!\n\n👤 User: [{user.first_name}](tg://user?id={user.id})\n🆔 ID: `{user.id}`</b></i>",
        reply_markup=buttons
    )

@bot.on_callback_query(filters.regex(r"^(approve|reject)_(\d+)"))
async def process_appeal(client: Client, callback: CallbackQuery):
    action, user_id = callback.data.split("_")
    user_id = int(user_id)

    user = await client.get_users(user_id)

    if action == "approve":
        banned.delete_one({"user_id": user_id})
        await client.send_message(user_id, "<b>✅ You have been <i>unbanned</i>. You may now use the bot.</b>")
        await callback.message.edit_text(f"<i><b>✅ User [{user.first_name}](tg://user?id={user.id}) has been unbanned.</b></i>")
    else:
        await client.send_message(user_id, "<b>❌ Your appeal was <i>rejected</i> by the OWNER. You remain banned.</b>")
        await callback.message.edit_text(f"<i><b>❌ OWNER rejected the appeal of [{user.first_name}](tg://user?id={user.id}).</b></i>")

    await callback.answer()

#===============================================================================================================================
# OWNER_ID replies in group topic -> message user
@bot.on_message(filters.chat(LOG_GROUP_ID) & filters.reply & filters.user(OWNER_ID))
async def OWNER_ID_reply(client: Client, message: Message):
    try:
        replied_msg = message.reply_to_message
        thread_id = replied_msg.message_thread_id
        if not thread_id:
            return await message.reply("❌ No thread ID found in the replied message.")

        topic = topics.find_one({"topic_id": thread_id})
        if not topic:
            return await message.reply("❌ Couldn't find user for this topic.")

        user_id = topic["user_id"]

        if message.text:
            await client.send_message(user_id, message.text)
        elif message.photo:
            await client.send_photo(user_id, message.photo.file_id, caption=message.caption)
        elif message.video:
            await client.send_video(user_id, message.video.file_id, caption=message.caption)
        elif message.document:
            await client.send_document(user_id, message.document.file_id, caption=message.caption)
        elif message.audio:
            await client.send_audio(user_id, message.audio.file_id, caption=message.caption)
        elif message.voice:
            await client.send_voice(user_id, message.voice.file_id, caption=message.caption)
        elif message.animation:
            await client.send_animation(user_id, message.animation.file_id, caption=message.caption)
        else:
            await message.reply("⚠️ Unsupported reply type.")

        #await message.reply("✅ Message sent to user.")

    except UserIsBlocked:
        await message.reply("🚫 User has blocked the bot.")
    except Exception as e:
        await message.reply(f"❌ Failed: {e}")

# /users: list topic users
@bot.on_message(filters.command("topics") & filters.user(OWNER_ID) & not_banned())
async def list_topics(client: Client, message: Message):
    data = list(topics.find())
    
    if not data:
        await message.reply("📂 No topics found in the database.")
        return

    lines = ["👥 Registered Topics:\n"]
    for i, doc in enumerate(data, start=1):
        uid = doc.get("user_id")
        tid = doc.get("topic_id")
        lines.append(f"{i}. User ID: {uid} | Topic ID: {tid}")

    content = "\n".join(lines)

    file = io.BytesIO(content.encode("utf-8"))
    file.name = "user_topics.txt"

    await message.reply_document(document=file, caption="📄 Registered user topics")

@bot.on_message(filters.command("rut") & filters.user(OWNER_ID) & not_banned())
async def reset_user_topic(client: Client, message: Message):
    await message.reply("🆔 Send the User ID to reset their topic data:")

    try:
        user_msg = await bot.listen(message.chat.id, filters=filters.user(message.from_user.id))
        user_id = int(user_msg.text.strip())
        await user_msg.delete()  # delete input

        result = topics.delete_many({"user_id": user_id})

        await message.reply(
            f"✅ Reset complete for user `{user_id}`.\n"
            f"🗑️ {result.deleted_count} topic records deleted."
        )
    except Exception as e:
        await message.reply(f"❌ Failed to reset topic.\n**Error:** `{e}`")


# Step 1: Ask for confirmation
@bot.on_message(filters.command("ract") & filters.user(OWNER_ID) & not_banned())
async def confirm_reset(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, reset", callback_data="confirm_reset_topics")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_reset_topics")]
    ])
    await message.reply("⚠️ Are you sure you want to reset all saved topics?", reply_markup=buttons)

# Step 2: Handle confirmation or cancellation
@bot.on_callback_query(filters.regex("^(confirm|cancel)_reset_topics$") & filters.user(OWNER_ID))
async def handle_reset_callback(client: Client, callback_query):
    action = callback_query.data

    if action == "confirm_reset_topics":
        deleted = topics.delete_many({})
        await callback_query.message.edit_text(
            f"✅ Reset successful.\n\n🧹 {deleted.deleted_count} entries removed."
        )
    else:
        await callback_query.message.edit_text("❎ Reset canceled.")

# /ban: Ban a user (reply or by ID)
@bot.on_message(filters.command("ban") & filters.user(OWNER_ID) & not_banned())
async def ban_user(client: Client, message: Message):
    args = message.text.split()
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
    elif len(args) > 1:
        try:
            user_id = int(args[1])
        except ValueError:
            return await message.reply("❌ Invalid user ID.")
    else:
        return await message.reply("Reply to a user or use `/ban user_id`")

    # Prevent banning OWNER_ID
    if user_id == OWNER_ID:
        return await message.reply("🙅 You can't ban yourself, boss.")

    banned.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    await message.reply(f"✅ Banned user `{user_id}`")
    # Notify banned user
    try:
        await client.send_message(
            user_id,
            "<i><b>You have been banned by the OWNER.*\n\nYou can no longer use this bot.</b></i>"
        )
    except Exception:
        pass  # User has blocked the bot or can't be messaged

# /unban: Unban user by ID
@bot.on_message(filters.command("unban") & filters.user(OWNER_ID) & not_banned())
async def unban_user(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("Usage: /unban <user_id>")
    
    try:
        user_id = int(args[1])
    except ValueError:
        return await message.reply("❌ Invalid user ID.")
    
    result = banned.delete_one({"user_id": user_id})
    
    if result.deleted_count:
        await message.reply(f"✅ Unbanned user `{user_id}`")
    else:
        await message.reply("ℹ️ User was not banned.")
    try:
        await client.send_message(
            user_id,
            "<i><b>✅ You have been unbanned by the OWNER_ID.</b></i>"
        )
    except Exception:
        pass  # User has blocked the bot or can't be messaged

@bot.on_callback_query(filters.regex(r"^ban_(\d+)$"))
async def ban_user_callback(client, callback):
    if callback.from_user.id != OWNER_ID:
        return await callback.answer("❌ Only the OWNER can ban users.", show_alert=True)

    user_id = int(callback.matches[0].group(1))
    if user_id == OWNER_ID:
        return await callback.answer("🙅 You can't ban yourself, boss.", show_alert=True)

    banned.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)
    await callback.answer("✅ User banned.")

    try:
        await client.send_message(
            user_id,
            "<i><b>You have been banned by the OWNER.\nAccess to the bot has been revoked.</b></i>"
        )
    except:
        pass

    await callback.message.reply(f"🚫 Banned user `{user_id}`")

@bot.on_callback_query(filters.regex(r"^info_(\d+)$"))
async def user_info_callback(client, callback):
    if callback.from_user.id != OWNER_ID:
        return await callback.answer("❌ Only the OWNER can see user info.", show_alert=True)

    user_id = callback.matches[0].group(1)
    await callback.message.reply(f"👤 User ID: `{user_id}`")
    await callback.answer()


# /bannedusers: Show all banned user IDs
@bot.on_message(filters.command("banned") & filters.user(OWNER_ID) & not_banned())
async def show_banned_users(client: Client, message: Message):
    users = list(banned.find({}))
    if not users:
        return await message.reply("✅ No users are currently banned.")
    
    msg = "**🚫 Banned Users:**\n"
    for u in users:
        msg += f"- `{u['user_id']}`\n"
    
    await message.reply(msg)

#========================== Accept logs ===================================
def is_accept_log_enabled():
    doc = logs.find_one({"_id": "config"}) or {}
    return doc.get("acceptlog", False)

@bot.on_message(filters.command("aml") & filters.user(OWNER_ID) & not_banned())
async def acceptlog_cmd(client, message: Message):
    if len(message.command) != 2 or message.command[1] not in ["0", "1"]:
        return await message.reply("⚠️ Usage:\n`/aml 0` - Disable logs\n`/aml 1` - Enable logs")

    val = bool(int(message.command[1]))
    logs.update_one({"_id": "config"}, {"$set": {"acceptlog": val}}, upsert=True)

    status = "✅ Enabled" if val else "❌ Disabled"
    await message.reply(f"🔧 Accept Log is now: {status}")
#=================================================================================================================================
async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

EMOJIS = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
emoji_counter = 0  # Initialize a global counter

def get_next_emoji():
    global emoji_counter
    emoji = EMOJIS[emoji_counter]
    emoji_counter = (emoji_counter + 1) % len(EMOJIS)
    return emoji
    
#================================================================================================================================
failed_links = []  # List to store failed links
fail_cap =f"**➜ This file Contain Failed Downloads while Downloding \n You Can Retry them one more time **"

#================================================================================================================================
class Data:
    START = (
        "<blockquote>𝕎𝕖𝕝𝕔𝕠𝕞𝕖! **{0}**\n**{1}**</blockquote>\n\n"
    )

# Set timezone to Asia/Kolkata
india_tz = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(india_tz)
hour = current_time.hour

# Define time-block based greeting
if 4 <= hour < 6:
  wish = "Wakey wakey! 🌄 A beautiful dawn to you!"
elif 6 <= hour < 9:
  wish = "Top of the morning! ☀️ Hope your day starts well!"
elif 9 <= hour < 12:
  wish = "Good morning 🌞 Shine bright today!"
elif 12 <= hour < 14:
  wish = "It's noon time 🌞 Stay energized!"
elif 14 <= hour < 17:
  wish = "Good afternoon 🍃 Stay focused and fresh!"
elif 17 <= hour < 19:
  wish = "Good early evening 🌇 How’s your day going?"
elif 19 <= hour < 22:
  wish = "Good evening 🌆 Time to relax a bit!"
elif 22 <= hour or hour < 4:
  wish = "Good night 🌙 Sweet dreams and cozy vibes!"
else:
  wish = "Hello 👋 Have a great time!"

# Define the start command handler
@bot.on_message(filters.command("start") & not_banned())
async def start(client: Client, msg: Message):
    user_id = msg.from_user.id
    allowed, other_bot = await is_user_allowed(user_id, client)
    if not allowed:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Switch to this bot", callback_data="switch_bot")]
        ])
        return await msg.reply_text(
            f"❌ You are already registered in another bot: @{other_bot}\n"
            f"Do you want to switch to this bot?",
            reply_markup=keyboard
        )
    user = await bot.get_me()
    mention = user.mention
    
    wait_msg = await msg.reply(
        "**🔄 Initializing your dashboard...**"
    )
    welcome_image_path = await send_welcome_message(client, msg)
    
    await wait_msg.delete()
    
    start_message = await client.send_photo(
        chat_id=msg.chat.id,
        photo=welcome_image_path,
        message_effect_id=random.choice(efcts),
        caption=Data.START.format(msg.from_user.mention, wish)
    )
    if len(msg.command) > 1:
        param = msg.command[1]
        if user_id in Param and Param[user_id] == param:
            expires = datetime.utcnow() + timedelta(hours=3)
            users_collection.update_one(
                {"_id": user_id},
                {"$set": {
                    "expires_at": expires,
                    "duration": "3h"
                }},
                upsert=True
            )
            del Param[user_id]
            return await msg.reply("✅ You have been verified successfully! Enjoy your session for 3 hours.")
        else:
            return await msg.reply("❌ Invalid or expired token. Please use /token to generate a new one.")

    await asyncio.sleep(1)
    await start_message.edit_text(
        f"╭━━━━━━━━━━━━━━━━━━━━➣\n"
        f"┣⪼ 👋 Welcome {msg.from_user.first_name}!\n"
        f"┣⪼ 🚀 Starting DRM Bot...\n"
        f"╰━━━━━━━━━━━━━━━━━━━━➣\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        "╭━━━━ INITIALIZING ━━━━➣\n"
        "┣⪼ 🔄 System Status:\n"
        "┃  ├─⪼ 📡 Connecting to servers...\n"
        "┃  ╰─⪼ ⚙️ Loading modules...\n"
        "┣⪼ 📊 Progress:\n"
        "┃   ╰─⪼ ▰▱▱▱▱▱▱▱▱▱ 10%\n"
        "╰━━━━━━━━━━━━━━━━━━━━➣\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        "╭━━━━━━ LOADING ━━━━━━➣\n"
        "┣⪼ 🔄 System Status:\n"
        "┃  ├─⪼ ✅ Servers connected\n"
        "┃  ├─⪼ 📦 Loading features...\n"
        "┃  ╰─⪼ 🔍 Checking systems...\n"
        "┣⪼ 📊 Progress:\n"
        "┃   ╰─⪼ ▰▰▰▰▱▱▱▱▱▱ 40%\n"
        "╰━━━━━━━━━━━━━━━━━━━━➣\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        "╭━━━━━━ PREPARING ━━━━━━➣\n"
        "┣⪼ 🔄 System Status:\n"
        "┃  ├─⪼ ✅ Features loaded\n"
        "┃  ├─⪼ 🔐 Checking security...\n"
        "┃  ╰─⪼ 📡 Syncing data...\n"
        "┣⪼ 📊 Progress:\n"
        "┃   ╰─⪼ ▰▰▰▰▰▰▰▱▱▱ 70%\n"
        "╰━━━━━━━━━━━━━━━━━━━━━➣\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        "╭━━━━━ FINALIZING ━━━━━➣\n"
        "┣⪼ 🔄 System Status:\n"
        "┃  ├─⪼ ✅ Security verified\n"
        "┃  ├─⪼ ✅ Data synced\n"
        "┃  ╰─⪼ 🔍 Checking access...\n"
        "┣⪼ 📊 Progress:\n"
        "┃   ╰─⪼ ▰▰▰▰▰▰▰▰▰▱ 90%\n"
        "╰━━━━━━━━━━━━━━━━━━━━➣\n\n"
    )

    # Start command
    await asyncio.sleep(1)   
    # Check if user ID is already saved in the database
    if not is_authorized(user_id):
        await start_message.edit_text(
            Data.START.format(msg.from_user.mention, wish) +
            f"💡 <b><u>You're currently on the Free Plan 🆓</u></b>\n\n"
            f"<blockquote>"
            f"I'm here to simplify your workflow! Just send a <b>.txt</b> file containing video links 📄, "
            f"and I’ll upload them directly to Telegram for you — fast, clean, and hassle-free 🚀\n\n"
            f"✨ Lightning-fast downloads\n"
            f"✨ Instant uploads to chat or channel\n"
            f"✨ Use your own custom thumbnails, fonts, and watermarks"
            f"</blockquote>\n\n"
            f"🔐 <b><u>Premium Access Required</u></b>\n"
            f"<blockquote>"
            f"💬 To unlock full features and unlimited usage, please contact:\n\n"
            f"<b>{CREDITWITHLINK}</b> 🎫"
            f"</blockquote>\n\n"
            f"▶️ <b>To get started, press /id</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Features", callback_data="show_features")],
                [InlineKeyboardButton("✨ Commands", callback_data="show_commands"),
                InlineKeyboardButton("🗄️ Settings", callback_data="settings")],
                [InlineKeyboardButton("💳 Premium", callback_data="show_plans")],
                [InlineKeyboardButton(text="📞 Contact", url=f"{CONTACTLINK}"),
                InlineKeyboardButton(text="🛠️ Help", url=f"{HELPLINK}")],
          ]),
        )

    else:
        await asyncio.sleep(1)
        await start_message.edit_text(
            Data.START.format(msg.from_user.mention, wish) +
            f"🎉 <b><u>Welcome, Premium Member!</u></b>\n\n"
            f"<blockquote>"
            f"You're now enjoying the full power of the bot 🚀\n\n"
            f"✔️ Unlimited high-speed downloads\n"
            f"✔️ Instant Telegram uploads\n"
            f"✔️ Custom thumbnails, fonts, and watermark options\n"
            f"✔️ Priority access and faster processing"
            f"</blockquote>\n\n"
            f"🧰 <b>Explore your tools below:</b>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Features", callback_data="show_features")],
                [InlineKeyboardButton("✨ Commands", callback_data="show_commands"),
                InlineKeyboardButton("🗄️ Settings", callback_data="settings")],
                [InlineKeyboardButton("💳 Premium", callback_data="show_plans")],
                [InlineKeyboardButton(text="📞 Contact", url=f"{CONTACTLINK}"),
                InlineKeyboardButton(text="🛠️ Help", url=f"{HELPLINK}")],
          ]),
        )
        
#================================================================================================================================
@bot.on_callback_query(filters.regex("back_to_main"))
async def back_to_main(client, callback_query):
    await callback_query.message.edit_text(
        Data.START.format(callback_query.from_user.mention, wish) +
        f"**You are currently using the {CREDIT}.**\n",
        reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Features", callback_data="show_features")],
                [InlineKeyboardButton("✨ Commands", callback_data="show_commands"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
                [InlineKeyboardButton("💳 Premium", callback_data="show_plans")],
                [InlineKeyboardButton(text="📞 Contact", url=f"{CONTACTLINK}"),
                InlineKeyboardButton(text="🛠️ Help", url=f"{HELPLINK}")],
          ]),
        disable_web_page_preview=True
    )
    await callback_query.answer()

#================================================================================================================================  
# Handle the commands button press
@bot.on_callback_query(filters.regex("show_commands"))
async def show_features(client, callback_query):
    text = "<blockquote>✨ **Available Commands:**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆔 Chat ID", callback_data="id"), InlineKeyboardButton("ℹ️ Info", callback_data="info")],
        [InlineKeyboardButton("📺 YouTube", callback_data="youtube")],
        [InlineKeyboardButton("✍️ Text 2 .txt", callback_data="t2t"), InlineKeyboardButton("📝 Edit .txt", callback_data="e2t")],
        [InlineKeyboardButton("📱 Log Media Group", callback_data="log_media_group"), InlineKeyboardButton("☎️ Log Info Group", callback_data="log_information_group")],
        [InlineKeyboardButton("📇 Cookies", callback_data="cookies")],
        [InlineKeyboardButton("📑 Title Clean", callback_data="tittle"), InlineKeyboardButton("🔓 Helper Dec", callback_data="helper")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle the feature button press
@bot.on_callback_query(filters.regex("show_features"))
async def feature_button(client, callback_query):
  caption = (
      "<b>⋅ ─  ✨Bot Features✨  ─ ⋅</b>\n"
      "<blockquote>⛲ Unleash the Power of Premium Features!</blockquote>\n\n"
      "<b>🔧 Tech-Engineered for Performance</b>\n"
      "<blockquote>Crafted using Python + Pyrogram | Deployed on Render/Koyeb | 99.9% Uptime | API-Optimized ⚙️</blockquote>\n\n"
      "<b>💎 Premium Features You’ll Love: </b>\n"
      "<blockquote>➤ 🔁 Custom Caption\n"
      "➤ 🔄 Auto Topic Wise Uploader\n" 
      "➤ 👮 Admin-Only Command Access\n"
      "➤ 🧹 Clear All settings in a Tap\n"
      "➤ 🎯 Ultra-fast Video Uploader\n"
      "➤ ⏱️ Auto-delete Processed Message After Processing\n"
      "➤ 🖼 Supports Media Types: Images | Videos | PDFs</blockquote>\n\n"
      "<b>🛡️ Secure | Fast | Fully Customizable"
      "🔥 Ideal for Channels, Groups & Media Management</b>\n\n"
      "<b>📲 Try it now —</b> and see the difference premium automation makes.\n"
  )
  keyboard = InlineKeyboardMarkup(
    [
      [InlineKeyboardButton("📌 Auto Pin Batch Name", callback_data="pin_command")],
      [InlineKeyboardButton("📇 Index Range", callback_data="index_command"), InlineKeyboardButton("📂 2GB+ File", callback_data="2gb_command")],
      [InlineKeyboardButton("🔄 Restart Command", callback_data="restart_command")],
      [InlineKeyboardButton("🖋️ File Name", callback_data="file_name_command"), InlineKeyboardButton("✍️ Caption", callback_data="caption_command")],
      [InlineKeyboardButton(" 🏷️ Auto Topic Wise Uploader", callback_data="title_command")],
      [InlineKeyboardButton("🤖 Txt Operation", callback_data="editor_command"), InlineKeyboardButton("🎥 YouTube to .TXT", callback_data="y2t_command")],
      [InlineKeyboardButton("💧 Thumbnail Watermark", callback_data="thumb_watermark_command")],
      [InlineKeyboardButton("📇 Channel ID", callback_data="channel_id_command"), InlineKeyboardButton("🚦 Other Feature", callback_data="other_command")],      
      [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]

    ]
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
    reply_markup=keyboard)
  await callback_query.answer()
    
#================================================================================================================================
# Handle the settings button press
@bot.on_callback_query(filters.regex("settings"))
async def show_features(client, callback_query):
    text = "<blockquote>✨ **My Premium BOT Settings:**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Caption", callback_data="mode")],
        [InlineKeyboardButton("📸 Vid Thumb", callback_data="vthumb"), InlineKeyboardButton("🖼️ Pdf Thumb", callback_data="pthumb")],
        [InlineKeyboardButton("💧 Pdf Watermark", callback_data="pwatermark")],
        [InlineKeyboardButton("✍️ Credit", callback_data="credit"), InlineKeyboardButton("👮‍♂️ Extension", callback_data="extension")],
        [InlineKeyboardButton("🎨 Font Color", callback_data="font_color"), InlineKeyboardButton("🅰️ Font Style", callback_data="font_style")],
        [InlineKeyboardButton("🏷️ Auto Topic Wise Uploader", callback_data="topic")],
        [InlineKeyboardButton("🔏 Token", callback_data="token"), InlineKeyboardButton("🖋️ File Name", callback_data="myname")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle the settings button press
@bot.on_callback_query(filters.regex("cookies"))
async def cookies(client, callback_query):
    text = "<blockquote>✨ **Update YouTube & Instagram Cookies:**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔻 YouTube", callback_data="ytcookie"),
        InlineKeyboardButton("🔺 Instagram", callback_data="igcookie")],
        [InlineKeyboardButton("🔙 Back", callback_data="show_commands")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle the settings button press
@bot.on_callback_query(filters.regex("token"))
async def token(client, callback_query):
    text = "<blockquote>✨ **Update Your Same Batch Token**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Careerwill", callback_data="cwloginsave")],
        [InlineKeyboardButton("Classplus", callback_data="cploginsave"), InlineKeyboardButton("Physics Wallah", callback_data="pwloginsave")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)
    
#================================================================================================================================
# Handle Premium Plans button press
@bot.on_callback_query(filters.regex("show_plans"))
async def show_plans(client, callback_query):
    text = (
        "<blockquote>**Here are the pricing details for SAINI DRM Bot:**</blockquote>\n\n"
        "🗓️ **Subscription Duration & Price:**\n"
        "<blockquote>1 Day ➠ ₹150 💰\n"
        "10 Days ➠ ₹450 💵\n"
        "30 Days ➠ ₹1000 💴</blockquote>\n\n"
        "📑 **Supported Apps and Links:**\n"
        "<blockquote>• 📚 Appx Zip+Encrypted Url\n"
        "• 🎓 Classplus DRM+ NDRM\n"
        "• 🧑‍🏫 PhysicsWallah DRM\n"
        "• 📚 CareerWill + PDF\n"
        "• 🎓 Khan GS\n"
        "• 🎓 Study Iq DRM\n"
        "• 🚀 APPX + APPX Enc PDF\n"
        "• 🎓 Vimeo Protection\n"
        "• 🎓 Brightcove Protection\n"
        "• 🎓 Visionias Protection\n"
        "• 🎓 Zoom Video\n"
        "• 🎓 Utkarsh Protection(Video + PDF)\n"
        "• 🎓 All Non DRM+AES Encrypted URLs\n"
        "• 🎓 MPD URLs if the key is known (e.g., Mpd_url?key=key XX:XX)</blockquote>\n\n"
        "🚀 Unlock premium features and save with our flexible plans! 🚀\n\n"
        f"<blockquote>Register Your Bots Now : {CREDITWITHLINK}</blockquote>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)
    
#=============================================================================================================================
@bot.on_message(filters.command(["upgrade"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(
        f"<blockquote>╭━━━━━━━━━━ DRM BOT ━━━━━━━━━━➣\n"
        f"┣⪼ 📱 Available Services:\n"
        f"┃\n"
        f"┣⪼ 🔒 LEVEL 1 PREMIUM(1500₹) 🔒\n"
        f"┃  ├─⪼ 📚 Appx Encrypted PDF (All)\n"
        f"┃  ├─⪼ 📩 Appx Zip+Encrypted URLs\n"
        f"┃  ├─⪼ 🎓 Study IQ\n"
        f"┃  ├─⪼ ❓ IFRAME MediaDelivary\n"
        f"┃  ├─⪼ 📺 ClassPlus DRM\n"
        f"┃  ├─⪼ 🎓 Terabox\n"
        f"┃  ├─⪼ 🆕 Vimeo All Type\n"
        f"┃  ├─⪼ 🎥 Youtube \n"
        f"┃  ├─⪼ 🧠 Abhinay Math\n"
        f"┃  ├─⪼ 📚 Ojha IAS\n"
        f"┃  ├─⪼ 🎥 Spayee/Graphy Video\n"
        f"┃  ├─⪼ 📚 Spayee/Graphy Pdf(Type: .pdfPSWD=)\n"
        f"┃  ╰─⪼ 🎥 Pallycon DRM\n"
        f"┣⪼ 💰 Monthly: ₹1500/-\n"
        f"┃\n"
        f"┣⪼ 🔒 LEVEL 2 PREMIUM(2500₹) 🔒\n"
        f"┃  ├─⪼ 🎯 TP Stream:\n"
        f"┃  │  ├─⪼ 🏛 Forum IAS\n"
        f"┃  │  ╰─⪼ 🔍 Insight IAS\n"
        f"┃  │\n"
        f"┃  ╰─⪼ 🎯 VdoCrypt:\n"
        f"┃     ├─⪼ 📈 Next IAS\n"
        f"┃     ├─⪼ 📚 Kalam Academy\n"
        f"┃     ├─⪼ 📺 Utkarsh \n"
        f"┃     ╰─⪼ ⭐️ MadeEasy\n"
        f"┣⪼ 💰 Monthly: ₹2500/-\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━➣</blockquote>",
        reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="📞 Contact", url=f"{CONTACTLINK}"),
                InlineKeyboardButton(text="🛠️ Help", url=f"{HELPLINK}")],
           ]),
    )  
    
#=============================================================================================================================
# 📌 Auto Pin Batch Name
@bot.on_callback_query(filters.regex("pin_command"))
async def pin_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨📌 Auto Pin✨  ─ ⋅</b>"
      "<blockquote>📍Batch Name Pinning System\n"
      "🛠️ Automated Pinning at Its Best!</blockquote>\n\n"
      "<b>🔹 Batch Name Auto-Pinning:</b>\n"
      "<blockquote>The system intelligently pins the batch name to the top of the bot/group/channel, starting from the first link.</blockquote>\n\n"
      "<b>🔹 Seamless Integration:</b>\n"
      "<blockquote>Once the first link is detected, the batch name is pinned automatically — no manual work required!</blockquote>\n\n"
      "<b>🔹 Perfect for Courses, Projects, and Events:</b>\n"
      "<blockquote>Ensure every participant sees the most crucial details right at the top.</blockquote>\n\n"
      "<b>🌐 Enhance Your Group Experience</b>\n"
      "<blockquote>✅ Time-Saving\n"
      "✅ Efficient Organization\n"
      "✅ Ideal for Large Groups & Channels</blockquote>\n"     
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://tinypic.host/images/2025/06/14/IMG_20250614_193326.jpg", caption=caption),
      reply_markup=keyboard)

#=============================================================================================================================
# 🔄 Restart Command
@bot.on_callback_query(filters.regex("restart_command"))
async def restart_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨🔄 Restart Command✨  ─ ⋅</b>\n"
      "<blockquote>🧠 Intelligent Session Recovery\n"
      "⚖️ Pick Up Right Where You Left Off</blockquote>\n\n"
      "<b>🔹 Smart Bot Recovery:</b>\n"
      "<blockquote>If the bot stops or restarts, simply use the /restart command to resume operations without losing progress.</blockquote>\n\n"
      "<b>🔹 No Rework Needed:</b>\n"
      "<blockquote>No need to start from scratch — the bot remembers your last state and continues seamlessly.</blockquote>\n\n"
      "<b>💡 Ideal for:</b>\n"
      "<blockquote>✔️ Long Batch Processes\n"
      "✔️ Interrupted Downloads\n"
      "✔️ Server Restarts or Crashes</blockquote>\n\n"
      "<b>🚀 Reliable | Resumable | Hassle-Free</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://tinypic.host/images/2025/06/14/IMG_20250614_193750.jpg", caption=caption),
      reply_markup=keyboard)
    
#=============================================================================================================================
# 📂 2GB+ File Supported
@bot.on_callback_query(filters.regex("2gb_command"))
async def pin_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨📂 2GB+ File Supported✨  ─ ⋅</b>\n"
      "<blockquote>🛠️ No Limits, Just Performance\n"
      "⚡ Handle Bigger Files with Ease</blockquote>\n\n"
      "<b>🔹 Large File Compatibility:</b>\n"
      "<blockquote>Supports files over 2GB — no compression, no quality loss.</blockquote>\n\n"
      "<b>🔹 Auto-Split Technology:</b>\n"
      "<blockquote>Files are automatically divided into parts, ensuring smooth delivery without Telegram upload limits.</blockquote>\n\n"
      "<b>🔧 Built for bulk uploads, course packs, and more.</b>\n"
      "<blockquote>✅ Seamless Chunking\n"
      "✅ Zero Manual Effort\n"
      "✅ Fully Automated in the Background</blockquote>\n\n"
      "<b>🔐 Smart | Scalable | Stable</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://tinypic.host/images/2025/06/15/IMG_20250615_181140.jpg", caption=caption),
      reply_markup=keyboard)
    
#=============================================================================================================================
# Txt Operation 
@bot.on_callback_query(filters.regex("editor_command"))
async def editor_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨🤖 TXT Operation✨  ─ ⋅</b>\n"
      "<blockquote>📁 All-in-One Text Utility Engine\n"
      "🧠 From URLs to Clean .txt Files in Seconds</blockquote>\n\n"
      "<b> 🎥 YouTube URL → .txt:</b>\n"
      "<blockquote>Automatically extract and convert YouTube links into organized .txt format.</blockquote>\n\n"
      "<b> 🧹 Clean-up Tools:</b>\n"
      "<blockquote>Remove extra parentheses and unwanted clutter — text becomes clean and ready to use.</blockquote>\n\n"
      "<b> 📝 Text to .txt File:</b>\n"
      "<blockquote>Paste any raw text and instantly export it into a downloadable .txt document.</blockquote>\n\n"
      "<b>🔹 🔤 Alphabetical Sorting:</b>\n"
      "<blockquote>Neatly sort text entries A–Z — ideal for organized lists, indexes, and naming.</blockquote>\n\n"
      "<b> 🧾 Bot working Logs:</b>\n"
      "<blockquote>Track task history, executions, and actions — transparent logs for every process.</blockquote>\n\n"
      "<b> 🍪 Cookies Updates:</b>\n"
      "<blockquote>Easily update your YouTube & Instagram cookies for uninterrupted access and smooth parsing.</blockquote>\n\n"
      "<b>📂 Lightweight | Fast | Zero Manual Work</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
      reply_markup=keyboard)
    
#=============================================================================================================================
# ✍️ Caption
@bot.on_callback_query(filters.regex("caption_command"))
async def caption_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨🎮  Caption Modes✨  ─ ⋅</b>\n"
      "<blockquote>🚂 Dual Caption Engines\n"
      "🧠 Choose Your Caption Style with Power & Flexibility</blockquote>\n\n"
      "<b>🔹 Master Mode:</b>\n"
      "<blockquote>Simple, clean, and structured captions — perfect for organized content delivery.</blockquote>\n\n"
      "<b>🔹 Megatron Mode:</b>\n"
      "<blockquote>Dynamic, detailed, and feature-rich captions — ideal for advanced users and power-packed posts.</blockquote>\n\n"
      "<b>⚙️ Switch Easily via Settings Panel:</b>\n"
      "<blockquote>Access the in-bot Settings Panel to toggle between modes instantly — no coding, no commands needed.</blockquote>\n\n"
      "<b>🚀 2 Modes. 1 Bot. Infinite Possibilities.</b>\n"
      "<blockquote>✅ Adaptive Styling\n"
      "✅ Creator-Friendly\n"
      "✅ Enhanced Viewer Experience</blockquote>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
      reply_markup=keyboard)

#=============================================================================================================================
# ✍️ File name
@bot.on_callback_query(filters.regex("file_name_command"))
async def custom_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨🖋️ Custom Filename✨  ─ ⋅</b>\n"
      "<blockquote>📛 Tailored Naming, Perfected\n"
      "🔧 Rename with Precision Before the Extension</blockquote>\n\n"
      "<b>🔹 Custom Name Support:</b>\n"
      "<blockquote>Easily add a custom title or tag before the file extension — for example:\n"
      "Lecture_01.pdf → Lecture_01_admin.pdf</blockquote>\n\n"
      "<b>🔹 Smart & Clean Naming Logic:</b>\n"
      "<blockquote>Maintains original extension, adds branding, batch names, or personal labels effortlessly.</blockquote>\n\n"
      "<b>🛠️ Perfect for:</b>\n"
      "<blockquote>✔️ Content Creators\n"
      "✔️ Course Uploads\n"
      "✔️ Media Sorting</blockquote>\n\n"
      "<b>✨ Professional File Naming | Instant Output | Fully Automated</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://tinypic.host/images/2025/06/14/IMG_20250614_195129.jpg", caption=caption),
      reply_markup=keyboard)
    
#=============================================================================================================================
# 💧 Custom Thumbnail Watermark
@bot.on_callback_query(filters.regex("thumb_watermark_command"))
async def watermark_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨💧 Thumbnail & Watermark✨  ─ ⋅</b>\n"
      "<blockquote>🔏 Pro-Grade Media Customization\n"
      "🎯 Automated Visual Branding for Your Files</blockquote>\n\n"
      "<b>🔹 📸 Video & PDF Thumbnail Support:</b>\n"
      "<blockquote>Easily set custom thumbnails for both video and PDF files — clean, professional presentation every time.</blockquote>\n\n"
      "<b>🔹 💦 PDF Watermark Support:</b>\n"
      "<blockquote>Add your custom watermark to PDF files for branding, protection, or authenticity.</blockquote>\n\n"
      "<b>🎛️ Configure via Settings Panel:</b>\n"
      "<blockquote>Enable or customize thumbnails and watermarks directly in the Bot Settings Panel — no code, no confusion.</blockquote>\n\n"
      "✅ Brand Your Files\n"
      "✅ Enhance Viewer Trust\n"
      "✅ Streamlined Aesthetic Delivery\n\n"
      "<b>📂 Smart | Branded | Effortless</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
      reply_markup=keyboard)
      
#=============================================================================================================================
# Index Range
@bot.on_callback_query(filters.regex("index_command"))
async def index_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨🔢 Index Range✨  ─ ⋅</b>\n"
      "<blockquote>Smart Download Controller\n"
      "Targeted Downloading, Simplified</blockquote>\n\n"
      "<b>📩 Download by Index Range:</b>\n"
      "<blockquote>Specify a custom range using - (e.g. 1-10) to download only selected items — perfect for skipping unwanted files.</blockquote>\n\n"
      "<b>🔹 Single Link Sharing:</b>\n"
      "<blockquote>Need to share only the first downloadable link? We've got you covered. Just trigger it — no clutter, just clarity.</blockquote>\n\n"
      "<b>⚙️ Advanced Control | Lightweight Execution | Instant Results</b>\n"
      "<blockquote>✅ Useful for Series, Courses, or Leeching Specific Episodes\n"
      "✅ Works with Both Direct & Button-Based Links\n"
      "✅ Clean Interface for Smooth User Experience</blockquote>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://tinypic.host/images/2025/06/14/IMG_20250614_193309.jpg", caption=caption),
      reply_markup=keyboard)
    
#=============================================================================================================================
# 🏷️ Custom Title Feature
@bot.on_callback_query(filters.regex("title_command"))
async def title_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨📚 Topic Wise Upload✨  ─ ⋅</b>\n"
      "<blockquote>🛡️ Organized Media Delivery\n"
      "🎯 Auto-Categorized Uploads by Topic</blockquote>\n\n"
      "<b>🔹 Smart Topic Detection:</b>\n"
      "<blockquote>The bot automatically uploads videos and documents under the right topic/thread in your Telegram group — keeping everything structured and searchable.</blockquote>\n\n"
      "<b>🔹 Custom Topic Setup:</b>\n"
      "<blockquote>Use the intuitive Settings Panel to assign topics for uploads — no clutter, no confusion.</blockquote>\n\n"
      "<b>🧩 Perfect for:</b>\n"
      "<blockquote>✔️ Course Modules\n"
      "✔️ Series Uploads\n"
      "✔️ Multi-topic Groups</blockquote>\n\n"
      "<b>🛠️ Auto-Threaded | Neat | Professional</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://tinypic.host/images/2025/06/14/IMG_20250614_193248.jpg", caption=caption),
      reply_markup=keyboard)

#=============================================================================================================================
# ✍️ YouTube 
@bot.on_callback_query(filters.regex("y2t_command"))
async def y2t_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
      "<b>⋅ ─  ✨📄 YouTube to .TXT File✨  ─ ⋅</b>\n"
      "<blockquote>📱Smart Extraction Engine\n"
      "🔍 Convert Playlists or Searches into Clean .txt in One Tap</blockquote>\n\n"
      "<b>🔹 Auto Extract from YouTube Playlists</b>\n"
      "<blockquote>Generate a full .txt list of video titles, URLs, or IDs directly from a YouTube playlist.</blockquote>\n\n"
      "<b>🔹 Search & Extract:</b>\n"
      "<blockquote>Search YouTube via keywords and instantly convert the results into a structured .txt format.</blockquote>\n\n"
      "<b>🎛️ How to Use:</b>\n"
      "<blockquote>Just tap the YouTube Button in the command menu — no manual copying, no hassle.</blockquote>\n\n"
      "✅ Supports Long Playlists\n"
      "✅ Clean Formatting\n"
      "✅ Fast & Accurate\n\n"
      "<b>📂 Efficient | Creator-Friendly | Plug & Play</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
      reply_markup=keyboard)
    
#=============================================================================================================================
# 🏷️ Channel ID
@bot.on_callback_query(filters.regex("channel_id_command"))
async def channel_id_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
    "<b>⋅ ─  ✨📡 Channel ID Delivery✨  ─ ⋅</b>\n"
    "<blockquote>🚚 Direct Media Delivery\n"
    "🚀 Auto-Share to Groups & Channels with Precision</blockquote>\n\n"
    "<b>🔹 Smart Media Routing:</b>\n"
    "<blockquote>Bot can directly forward or upload media to a specified Channel or Group using just the Channel ID or Group ID.</blockquote>\n\n"
    "<b>🔹 No Manual Forwarding Needed:</b>\n"
    "<blockquote>Once configured, every media file is instantly shared to the desired destination — fast, accurate, automated.</blockquote>\n\n"
    "<b>🔧 How to Use:</b>\n"
    "<blockquote>Set your Channel or Group ID in the bot’s Settings Panel, and the rest is handled seamlessly.</blockquote>\n\n"
    "<blockquote>✅ Ideal for Content Creators, Leech Bots & Forward Channels\n"
    "✅ Supports All Media Types\n"
    "✅ Background Delivery – No Spam in Main Chat</blockquote>\n\n"
    "<b>📂 Effortless | Targeted | Real-Time Distribution</b>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
      reply_markup=keyboard)

#===========================================================================================================================
# Other feature 
@bot.on_callback_query(filters.regex("other_command"))
async def feature(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]])
  caption = (
    "<b>⋅ ─  ✨⚙️ Other Features✨  ─ ⋅</b>\n"
    "<blockquote>🧠 Intelligent Backend, Seamless Frontend</blockquote>\n\n"
    "<b>🔒 Powerful Controls | User-Aware Automation | MongoDB Backbone</b>\n\n"
    "<b> 🛑 /stop Command – Contextual Processing:</b>\n"
    "<blockquote>Works only during .txt extraction. Once completed or interrupted:\n"
    "– Bot automatically saves session to MongoDB\n"
    "– Sends a Failed Link Report for retry or review</blockquote>\n\n"
    "<b> 📢 Broadcast System:</b>\n"
    "<blockquote>Broadcast any type of message across all users or channels:\n"
    "– 📝 Text\n"
    "– 📄 Documents\n"
    "– 🎥 Videos\n"
    "– 🖼️ Media\n"
    "— Mass communication simplified.</blockquote>\n\n"
    "<b> 🚫 Ban / ✅ Unban System:</b>\n"
    "<blockquote>Automatically ban or unban users based on usage patterns, spam detection, or behavior logic.\n"
    "— Built-in protection, no manual monitoring needed.</blockquote>\n\n"
    "<b> 🕒 Real-Time User Authentication:</b>\n"
    "<blockquote>Every user is verified live at runtime — ensuring only authorized access to premium features.</blockquote>\n\n"
    "<b>🧠 MongoDB-Powered Core:</b>\n"
    "<blockquote>Every operation — session saving, user tracking, file indexing, and analytics — is securely stored and served via MongoDB</blockquote>\n"
  )
  await callback_query.message.edit_media(
    InputMediaPhoto(media="https://envs.sh/GVI.jpg", caption=caption),
      reply_markup=keyboard)

#==============================================================================================================================
# Handle the Video Thumbnail button press
@bot.on_callback_query(filters.regex("vthumb"))
async def handle_vthumb(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit(f"Send the Video Thumb URL (e.g., https://envs.sh/GV0.jpg) for default thumbnail /d \n\n<blockquote><i>Simple send Your Name for watermark on Thumbnail\nYou can direct upload thumb\nFor document format send : No</i></blockquote>", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        # Handle uploaded photo
        if input_msg.photo:
            thumb = await input_msg.download()  # Download the uploaded photo
            update_user_global_variables(user_id, {"thumb": thumb})
            await editable.edit(f"✅ Thumbnail set successfully as an uploaded photo for user {user_id} !", reply_markup=keyboard)

        # Handle URL
        elif input_msg.text.startswith("http://") or input_msg.text.startswith("https://"):
            thumb = input_msg.text
            update_user_global_variables(user_id, {"thumb": thumb})
            await editable.edit(f"✅ Thumbnail set successfully from the URL for user {user_id} !", reply_markup=keyboard)

        # Handle `/d` for default thumbnail
        elif input_msg.text.lower() == "/d":
            thumb = "/d"  # Set the thumbnail to `/d`
            update_user_global_variables(user_id, {"thumb": thumb})
            await editable.edit(f"✅ Thumbnail set to default for user {user_id} !", reply_markup=keyboard)

        # Handle `No` to disable the thumbnail
        elif input_msg.text == "No":
            thumb = "No"  # Set the thumbnail to `No`
            update_user_global_variables(user_id, {"thumb": thumb})
            await editable.edit(f"✅ Thumbnail disabled for user {user_id} !", reply_markup=keyboard)

        else:
            thumb = input_msg.text
            update_user_global_variables(user_id, {"thumb": thumb})
            await editable.edit(f"✅ Thumbnail set as a overlay text for user {user_id} !", reply_markup=keyboard)
        
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set thumbnail:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("pthumb"))
async def handle_pthumb(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit(f"Send the Pdf Thumb URL (e.g., https://envs.sh/GVI.jpg) for default thumbnail /d \n\n<blockquote><i>You can direct upload thumb</i></blockquote>", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        # Handle uploaded photo
        if input_msg.photo:
            thumb2 = await input_msg.download()  # Download the uploaded photo
            update_user_global_variables(user_id, {"thumb2": thumb2})
            await editable.edit(f"✅ Thumbnail set successfully as an uploaded photo for user {user_id} !", reply_markup=keyboard)

        # Handle URL
        elif input_msg.text.startswith("http://") or input_msg.text.startswith("https://"):
            thumb2 = input_msg.text
            update_user_global_variables(user_id, {"thumb2": thumb2})
            await editable.edit(f"✅ Thumbnail set successfully from the URL for user {user_id} !", reply_markup=keyboard)

        # Handle `/d` for default thumbnail
        elif input_msg.text.lower() == "/d":
            thumb2 = "/d"  # Set the thumbnail disabled to `/d`
            update_user_global_variables(user_id, {"thumb2": thumb2})
            await editable.edit(f"✅ Default Thumbnail Set for user {user_id} !", reply_markup=keyboard)

        # Invalid input
        else:
            await editable.edit("**❌ Invalid input. Please upload a photo, send a URL, `/d`, or `No`.**", reply_markup=keyboard)
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set thumbnail:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("credit"))
async def handle_credit(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit("**Send the Credit Name, for default Send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            CR = f"{CREDIT}"
            update_user_global_variables(user_id, {"CR": CR})
            await editable.edit(f"✅ Credit set successfully as default for user {user_id} !", reply_markup=keyboard)
        else:
            CR = input_msg.text
            update_user_global_variables(user_id, {"CR": CR})
            await editable.edit(f"✅ Credit set successfully for user {user_id} !", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Credit:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("extension"))
async def handle_extension(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit("**Send the extension Name for Megatron Caption, for default Send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            extension = f"{CREDIT}"
            update_user_global_variables(user_id, {"extension": extension})
            await editable.edit(f"✅ Extension set successfully as default for user {user_id} !", reply_markup=keyboard)
        else:
            extension = input_msg.text
            update_user_global_variables(user_id, {"extension": extension})
            await editable.edit(f"✅ Extension set successfully for user {user_id} !", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Extension:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("myname"))
async def handle_myname(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit("**Send the End File Name, else Send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            myname = '/d'
            update_user_global_variables(user_id, {"my_name": myname})
            await editable.edit(f"✅ End File Name disabled successfully for user {user_id} !", reply_markup=keyboard)
        else:
            myname = input_msg.text
            update_user_global_variables(user_id, {"my_name": myname})
            await editable.edit(f"✅ End File Name set successfully for user {user_id} !", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set End file name:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
        
#==============================================================================================================================
@bot.on_callback_query(filters.regex("^pwloginsave$"))
async def handle_pwloginsave(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit("**Send Physics Wallah Same Batch Token for processing PW .txt file else send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    pwtoken = input_msg.text
    update_user_global_variables(user_id, {"pwtoken": pwtoken})
    await editable.edit(f"✅ Classplus Token update successfully for user {user_id} !", reply_markup=keyboard)
    await input_msg.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("^cploginsave$"))
async def handle_cploginsave(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit(
        "**Send Classplus Token for processing CP `.txt` file or send /d for auto token**", 
        reply_markup=keyboard
    )
    input_msg = await bot.listen(editable.chat.id)
    cptoken_input = input_msg.text.strip()
    if cptoken_input == "/d":
        try:
            cptoken = requests.get("https://teamjncnew1.vercel.app/api/token").text.strip()
            await editable.edit("✅ Token auto-fetched successfully from API.", reply_markup=keyboard)
        except Exception as e:
            await editable.edit(f"❌ Failed to fetch token: {e}", reply_markup=keyboard)
            await input_msg.delete()
            return
    else:
        cptoken = cptoken_input
    update_user_global_variables(user_id, {"cptoken": cptoken})
    await editable.edit(f"✅ Classplus Token updated successfully for user {user_id} !", reply_markup=keyboard)
    await input_msg.delete()
    
#==============================================================================================================================
@bot.on_callback_query(filters.regex("^cwloginsave$"))
async def handle_cwloginsave(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit("**Send  Careerwill Token for processing CW .txt file else send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text == "/d":
            cwtoken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
            update_user_global_variables(user_id, {"cwtoken": cwtoken})
            await editable.edit(f"✅ Carrerwill Token update successfully for user {user_id}!", reply_markup=keyboard)
        else:
            cwtoken = input_msg.text
            update_user_global_variables(user_id, {"cwtoken": cwtoken})
            await editable.edit(f"✅ Carrerwill Token update successfully for user {user_id} !", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to update Careerwill Token:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
        
#==============================================================================================================================
@bot.on_callback_query(filters.regex("topic"))
async def handle_topic(client, callback_query):
    user_id = callback_query.from_user.id
    user_data = get_user_global_variables(user_id)
    current_topic = user_data.get("topic", "default")  # default fallback

    # Add ✅ tick mark to selected option
    on_label = "✅ 🔛 On" if current_topic == "yes" else "🔛 On"
    off_label = "✅ 📴 Off" if current_topic == "default" else "📴 Off"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(on_label, callback_data="toopic_yes"), InlineKeyboardButton(off_label, callback_data="toopic_default")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]
    ])
    await callback_query.message.edit(
        "**🔹Choose your Topic Preference:**\n\n<blockquote><i>Title fetched from (title) this bracket</i></blockquote>",
        reply_markup=keyboard
    )

@bot.on_callback_query(filters.regex("^toopic_"))
async def set_topic_preference(client, callback_query):
    user_id = callback_query.from_user.id
    selected = callback_query.data.split("_")[1]

    try:
        if selected == "yes":
            update_user_global_variables(user_id, {"topic": "yes"})
            await callback_query.answer("✅ Topic-wise upload enabled!", show_alert=True)
        elif selected == "default":
            update_user_global_variables(user_id, {"topic": "default"})
            await callback_query.answer("✅ Default title mode selected!", show_alert=True)

        # Refresh the menu with the updated tick
        await handle_topic(client, callback_query)

    except Exception as e:
        await callback_query.message.edit(
            f"<b>❌ Failed to set Topic:</b>\n<blockquote>{str(e)}</blockquote>"
    )
#==============================================================================================================================
@bot.on_callback_query(filters.regex("pwatermark"))
async def handle_pwatermark(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]])
    editable = await callback_query.message.edit("**Send pdf 💦 watermark text else send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            watermark_text = '/d'
            update_user_global_variables(user_id, {"watermark_text": watermark_text})
            await editable.edit(f"✅ Pdf Watermark disabled successfully for user {user_id} !", reply_markup=keyboard)
        else:
            watermark_text = input_msg.text
            update_user_global_variables(user_id, {"watermark_text": watermark_text})
            await editable.edit(f"✅ Pdf Watermark enabled successfully for user {user_id} !", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Pdf Watermark:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("mode"))
async def handle_mode(client, callback_query):
    user_id = callback_query.from_user.id
    user_data = get_user_global_variables(user_id)
    current_mode = user_data.get("mode", "/master")  # Default fallback

    # Add ✅ to the selected mode
    master_label = "✅ 🤖 Master" if current_mode == "/master" else "🤖 Master"
    megatron_label = "✅ ⚙️ Megatron" if current_mode == "/megatron" else "⚙️ Megatron"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(master_label, callback_data="set_master"), InlineKeyboardButton(megatron_label, callback_data="set_megatron")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="settings")]
    ])
    await callback_query.message.edit(
        "**Choose Caption Mode:**",
        reply_markup=keyboard
    )

@bot.on_callback_query(filters.regex("^set_"))
async def set_mode_callback(client, callback_query):
    user_id = callback_query.from_user.id
    mode = "/master" if "master" in callback_query.data else "/megatron"

    update_user_global_variables(user_id, {"mode": mode})
    await callback_query.answer(f"✅ Mode set to {mode}!", show_alert=True)

    # Refresh menu to show updated tick mark
    await handle_mode(client, callback_query)
#================================================================================================================================
@bot.on_callback_query(filters.regex("font_color"))
async def choose_font_color(client, callback_query):
    user_id = callback_query.from_user.id
    user_data = get_user_global_variables(user_id)
    selected_color = user_data.get("font_color", "00008B")

    def color_btn(name, hex_code, emoji):
        tick = "✅ " if selected_color.upper() == hex_code else ""
        return InlineKeyboardButton(f"{tick}{emoji} {name}", callback_data=f"color_{hex_code}")

    keyboard = InlineKeyboardMarkup([
        [color_btn("White", "FFFFFF", "⚪"), color_btn("Black", "000000", "⚫"), color_btn("Blue", "0000FF", "🔵")],
        [color_btn("Green", "008000", "🟢"), color_btn("Yellow", "FFFF00", "🟡"), color_btn("Red", "FF0000", "🟥")],
        [color_btn("Purple", "800080", "🟣"), color_btn("Orange", "FF7F00", "🟠"), color_btn("Gray", "808080", "🩶")],
        [color_btn("Pink", "FFC0CB", "🌸"), color_btn("Brown", "A52A2A", "🤎"), color_btn("Cyan", "00FFFF", "💧")],
        [color_btn("Magenta", "FF00FF", "🟪"), color_btn("Lime", "00FF00", "🟩"), color_btn("Navy", "000080", "🔷")],
        [color_btn("Teal", "008080", "🌊"), color_btn("Maroon", "800000", "🟥"), color_btn("Olive", "808000", "🫒")],
        [color_btn("Sky Blue", "87CEEB", "☁️"), color_btn("Gold", "FFD700", "🌟"), color_btn("Indigo", "4B0082", "🔹")],
        [color_btn("Beige", "F5F5DC", "🤍"), color_btn("Turquoise", "40E0D0", "💠"), color_btn("Lavender", "E6E6FA", "🪻")],
        [color_btn("Mint", "98FF98", "🌿"), color_btn("Peach", "FFDAB9", "🍑"), color_btn("Salmon", "FA8072", "🍣")],
        [color_btn("Coral", "FF7F50", "🪸"), color_btn("Crimson", "DC143C", "🩸"), color_btn("Periwinkle", "CCCCFF", "📘")],
        [color_btn("Sea Green", "2E8B57", "🌱"), color_btn("Rose", "FF007F", "🌹"), color_btn("Ivory", "FFFFF0", "🤍")],
        [color_btn("Khaki", "F0E68C", "🌾"), color_btn("Slate Blue", "6A5ACD", "🔷"), color_btn("Chartreuse", "7FFF00", "🍏")],
        [InlineKeyboardButton("🔙 Back", callback_data="settings")]
    ])


    await callback_query.message.edit(
        "🎨 **Choose your preferred font color:**\n\n_This color will be used in your thumbnails._",
        reply_markup=keyboard
    )

@bot.on_callback_query(filters.regex(r"color_"))
async def set_font_color(client, callback_query):
    user_id = callback_query.from_user.id
    color_code = callback_query.data.split("_")[1]
    update_user_global_variables(user_id, {"font_color": color_code})
    await choose_font_color(client, callback_query)  # re-render with tick
    
#================================================================================================================================
@bot.on_callback_query(filters.regex("font_style"))
async def choose_font_style(client, callback_query):
    user_id = callback_query.from_user.id
    user_data = get_user_global_variables(user_id)
    selected_style = user_data.get("font_style", "TTF (5).ttf")

    font_dir = "Fonts"
    fonts = [f for f in os.listdir(font_dir) if f.endswith(('.ttf', '.otf'))]
    if not fonts:
        return await callback_query.answer("❌ No fonts found in Fonts folder.")

    buttons = []
    for i in range(0, len(fonts), 4):
        row = []
        for font in fonts[i:i+4]:
            name = os.path.splitext(font)[0][:20]
            tick = "✅ " if font == selected_style else ""
            row.append(InlineKeyboardButton(f"{tick}{name}", callback_data=f"fontset_{font}"))
        buttons.append(row)

    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="settings")])
    await callback_query.message.edit(
        "🅰️ **Choose your preferred font style:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
@bot.on_callback_query(filters.regex(r"^fontset_(.+)$"))
async def preview_font_style(client, callback_query):
    user_id = callback_query.from_user.id
    font_file = callback_query.data.split("_", 1)[1]

    demo_text = "Selected Font"
    preview_path = await helper.create_text_thumbnail(
        text=demo_text,
        user_id=user_id,
        filename=f"preview_{user_id}.png",
        override_font=font_file  # You should update the function to accept this param
    )

    # Edit the same message with preview image and caption
    await callback_query.message.edit_media(
        media=InputMediaPhoto(
            media=preview_path,
            caption=(
                f"<b>🅰️ Font Preview</b>\n"
                f"<code>{font_file}</code>\n\n"
                "This is how your text will appear with this font.\n\n"
                "✅ <i>If you like it, tap confirm below.</i>"
            )
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_font_{font_file}")],
            [InlineKeyboardButton("🔙 Back", callback_data="font_style")]
        ])
    )
@bot.on_callback_query(filters.regex(r"^confirm_font_(.+)$"))
async def confirm_font_style(client, callback_query):
    user_id = callback_query.from_user.id
    font_file = callback_query.data.split("_", 2)[2]
    update_user_global_variables(user_id, {"font_style": font_file})
    await choose_font_style(client, callback_query)  # Refresh font list with new ✅
    
#================================================================================================================================
@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    text = f"<blockquote><b>The ID of this chat id is:</b></blockquote>\n`{chat_id}`"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 Send to OWNER", callback_data=f"send_id:{chat_id}")]
    ])
    if str(chat_id).startswith("-100"):
        await message.reply_text(text)
    else:
        await message.reply_text(text, reply_markup=keyboard)

#========================= Callback: Send to OWNER_ID ==========================
@bot.on_callback_query(filters.regex(r"send_id:(\d+)"))
async def handle_send_to_OWNER_ID(bot, query):
    user_id = int(query.matches[0].group(1))

    await bot.send_message(
        OWNER_ID,
        f"📬 <b>USER_ID</b> : 👤 <code>{user_id}</code>\n"
        f"⚙️ <b>COMMAND</b> : <code>/add {user_id}</code>"
    )

    await query.answer("✅ Sent to OWNER!", show_alert=True)


#=========================================================================================================================
@bot.on_callback_query(filters.regex("id"))
async def id_command(client, callback_query):
    chat_id = callback_query.message.chat.id
    await callback_query.message.reply_text(f"<blockquote><b>The ID of this chat id is:</b></blockquote>\n`{chat_id}`")

#====================================================================================================================================
@bot.on_callback_query(filters.regex("info"))
async def info_command(client, callback_query):
    
    user = callback_query.from_user
    name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    username = f"@{user.username}" if user.username else "No Username"
    
    text = (
        f"╭────────────────╮\n"
        f"│✨ **Your Telegram Info**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{name}`\n"
        f"├🔹**User ID :** {username}\n"
        f"├🔹**TG ID :** `{user.id}`\n"
        f"├🔹**Profile :** {user.mention}\n"
        f"╰────────────────╯"
    )
    
    await callback_query.message.reply_text(        
        text=text,
        disable_web_page_preview=True
    )

#================================================================================================================================
# Command "/helper" to decrypt the input text file
@bot.on_callback_query(filters.regex("helper"))
async def helper_command(client, callback_query):
    try:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="show_commands")]])
        # Prompt the user to send a text file
        editable = await callback_query.message.edit("**Send me the `helper://` encrypted .txt file to decrypt.**", reply_markup=keyboard)
        input_message = await client.listen(callback_query.message.chat.id)  # Corrected reference
        input_file = await input_message.download()  # Download the file

        # Decrypt the file
        decrypted_file = decrypt_file_txt(input_file)
        await editable.edit(f"**File decrypted successfully: {decrypted_file}**", reply_markup=keyboard)

        # Send the decrypted file back to the user
        await client.send_document(
            chat_id=callback_query.message.chat.id,
            document=decrypted_file,
            caption="Here is your decrypted file."
        )

    except Exception as e:
        await editable.edit(f"<b>Failed Reason:</b>\n<blockquote>{str(e)}</blockquote>",reply_markup=keyboard)

#================================================================================================================================
@bot.on_callback_query(filters.regex("^ytcookie$"))
async def handle_ytcookies(client, callback_query):

    keyboard=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cookies")]])
    editable = await callback_query.message.edit("Please upload YouTube cookies file (.txt format).", reply_markup=keyboard)

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(editable.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await editable.edit("**❌ Invalid file type. Please upload a .txt file.**", reply_markup=keyboard)
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await editable.edit(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await editable.edit(f"<b>Fail Reason:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)


#===================================================================================================================================
@bot.on_callback_query(filters.regex("^igcookie$"))
async def handle_igcookies(client, callback_query):
    keyboard=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="cookies")]])
    editable = await callback_query.message.edit("Please upload Instagram cookies file (.txt format).", reply_markup=keyboard)

    try:
        input_message: Message = await client.listen(editable.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await editable.edit("**❌ Invalid file type. Please upload a .txt file.**", reply_markup=keyboard)
            return
        cookies_path = await input_message.download(file_name=INSTAGRAM_COOKIES_PATH)
        with open(cookies_path, 'r') as file:
            cookies_data = file.read()  # Read the cookies data
        with open(INSTAGRAM_COOKIES_PATH, 'w') as file:
            file.write(cookies_data)  # Overwrite the old cookies with new data
        await editable.edit(
            f"✅ Cookies updated successfully.\n📂 Saved at: `{INSTAGRAM_COOKIES_PATH}`"
        )
    except Exception as e:
        await editable.edit(f"<b>Fail Reason:</b>\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)    

#===================================================================================================================================
@bot.on_callback_query(filters.regex("t2t"))
async def handle_text(client, callback_query):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="show_commands")]])
    editable = await callback_query.message.edit(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>", reply_markup=keyboard)
    input_message: Message = await bot.listen(editable.chat.id)
    if not input_message.text:
        await editable.edit("**Send valid text data**", reply_markup=keyboard)
        return

    text_data = input_message.text.strip()
    await input_message.delete()  # Corrected here
    
    await editable.edit("**🔄 Send file name or send /d for filename**", reply_markup=keyboard)
    inputn: Message = await bot.listen(editable.chat.id)
    raw_textn = inputn.text
    await inputn.delete()  # Corrected here

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await client.send_document(chat_id=callback_query.message.chat.id, document=txt_file, caption=f"<blockquote>`{custom_file_name}.txt`</blockquote>\nYou can now download your content! 📥")
    os.remove(txt_file)

# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

#===================================================================================================================================
@bot.on_callback_query(filters.regex("e2t"))
async def handle_txt(client, callback_query):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="show_commands")]])
    editable = await callback_query.message.edit(f"<blockquote>Welcome to the .txt File Editor!\nSend your `.txt` file containing subjects, links, and topics.</blockquote>", reply_markup=keyboard)
    input_message: Message = await bot.listen(editable.chat.id)
    if not input_message.document:
        await editable.edit("**Upload a valid `.txt` file.**", reply_markup=keyboard)
        return
    file_name = input_message.document.file_name
    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file_name)
    uploaded_file = await input_message.download(uploaded_file_path)

    await input_message.delete(True)

    try:
        with open(uploaded_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
    except Exception as e:
        await editable.edit(f"**Failed Reason:**<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
        return

    # Parse the content into subjects with links and topics
    subjects = {}
    current_subject = None
    for line in content:
        line = line.strip()
        if line and ":" in line:
            # Split the line by the first ":" to separate title and URL
            title, url = line.split(":", 1)
            title, url = title.strip(), url.strip()

            # Add the title and URL to the dictionary
            if title in subjects:
                subjects[title]["links"].append(url)
            else:
                subjects[title] = {"links": [url], "topics": []}

            # Set the current subject
            current_subject = title
        elif line.startswith("-") and current_subject:
            # Add topics under the current subject
            subjects[current_subject]["topics"].append(line.strip("- ").strip())

    # Sort the subjects alphabetically and topics within each subject
    sorted_subjects = sorted(subjects.items())
    for title, data in sorted_subjects:
        data["topics"].sort()

    # Save the edited file to the defined path with the file name
    try:
        final_file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(final_file_path, 'w', encoding='utf-8') as f:
            for title, data in sorted_subjects:
                # Write title and its links
                for link in data["links"]:
                    f.write(f"{title}:{link}\n")
                # Write topics under the title
                for topic in data["topics"]:
                    f.write(f"- {topic}\n")
    except Exception as e:
        await callback_query.message.edit(f"**Failed Reason:**\n</blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
        return

    # Send the sorted and edited file back to the user
    try:
        await client.send_document(
            chat_id=callback_query.message.chat.id,
            document=final_file_path,
            caption="**Your edited .txt file with subjects, links, and topics sorted alphabetically!**"
        )
    except Exception as e:
        await editable.edit(f"**Failed Reason:\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        # Clean up the temporary file
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)  


#===================================================================================================================================
@bot.on_callback_query(filters.regex("tittle"))
async def handle_title(client, callback_query):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="show_commands")]])
    editable = await callback_query.message.edit("**Send Your .txt file with links for ✂️ Remove extra parentheses**\n", reply_markup=keyboard)
    input: Message = await bot.listen(editable.chat.id)
    txt_file = await input.download()
    await input.delete(True)

    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    cleaned_lines = [line.replace('(', '').replace(')', '').replace('_', ' ') for line in lines]
      
    cleaned_txt_file = os.path.splitext(txt_file)[0] + '_cleaned.txt'
    with open(cleaned_txt_file, 'w') as f:
        f.write(''.join(cleaned_lines))
      
    await client.send_document(chat_id=callback_query.message.chat.id, document=cleaned_txt_file,caption="Here is your cleaned txt file.")
    os.remove(cleaned_txt_file)

#===================================================================================================================================
@bot.on_callback_query(filters.regex("youtube"))
async def handle_youtube(client, callback_query):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="show_commands")]])
    editable = await callback_query.message.edit(f"<blockquote>Send YouTube Website/Playlist link for convert in .txt file</blockquote>", reply_markup=keyboard)
    input_message: Message = await bot.listen(editable.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)

    # Fetch the YouTube information using yt-dlp with cookies
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': 'youtube_cookies.txt'  # Specify the cookies file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await editable.edit(f"**Failed Reason:**\n<blockquote>{str(e)}</blockquote>", reply_markup=keyboard)
            return

    # Extract the YouTube links
    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry['url']
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result['url']
        videos.append(f"{video_title}: {url}")

    # Create and save the .txt file with the custom name
    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)  # Ensure the directory exists
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    # Send the generated text file to the user with a pretty caption
    await client.send_document(
        chat_id=callback_query.message.chat.id,
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<pre><code>{title}.txt</code></pre>\n'
    )

    # Remove the temporary text file after sending
    os.remove(txt_file)

#===========================================================================================================================
@bot.on_message(filters.command(["logs"]) & not_banned())
async def send_logs(client: Client, m: Message):  # Correct parameter name
    if m.chat.id != OWNER_ID:  # Use `m` instead of `message`
        return await m.reply_text("You are not authorized to use this command.")
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

#===================================== User Cancel Cmd ========================
@bot.on_message(filters.command("cancel") & not_banned())
async def stop_handler(bot, m: Message):
    user_id = m.from_user.id

    # Premium check
    if not is_authorized(user_id):
        return await bot.send_message(
            m.chat.id,
            f"<blockquote>__**Oopss! You are not a Premium member**__\n"
            f"__**Please /upgrade Your Plan**__\n"
            f"__**Send me your user id for authorization**__\n"
            f"__**Your User id**__ - `{user_id}`</blockquote>\n\n"
        )

    # Forcefully clear the processing flag
    user_processing[user_id] = False
    user_stop_flags[user_id] = True  # Still set this to ensure graceful stopping

    # Failed links send (optional)
    if failed_links:
        error_file_send = await m.reply_text("📤 Sending your Failed Downloads List Before Cancelling...")
        with open("failed_downloads.txt", "w") as f:
            for link in failed_links:
                f.write(link + "\n")
        await m.reply_document(document="failed_downloads.txt", caption=fail_cap)
        await error_file_send.delete()
        os.remove('failed_downloads.txt')
        failed_links.clear()

    # ✅ Final confirmation message
    await m.reply_text(
        "> ⚠️ **Stop Command Received Successfully**\n\n"
        "> ✅ Your request has been registered. The current file will complete as usual.\n"
        "> ⏳ After that, all further processing will be gracefully stopped.\n\n"
        "> 🔒 <i>You won't lose your progress — your session is safe.</i>"
        "> ⚠️ <i>If you still face issues, try using</i> /restart <i>to refresh the session.</i>"
    )
#================================== Owner Stop cmd ==========================
@bot.on_message(filters.command("stop") & filters.user(OWNER_ID) & not_banned())
async def cancel_bot(bot, m: Message):
    await m.reply_text(
        "<b>♻️ Restart Command Received</b>\n\n"
        "<blockquote>"
        "✅ The bot is refreshing its systems to deliver optimal performance.\n"
        "⏳ Please wait a few moments while services restart smoothly.\n"
        "🚀 Everything will be back shortly!\n"
        "</blockquote>\n"
        "👋 <i>See you soon...</i>"
    )
    os.execl(sys.executable, sys.executable, *sys.argv)
#============================= CHeck all saved Sessions (owner ) =============================
@bot.on_message(filters.command("sessions") & filters.user(OWNER_ID) & not_banned())
async def list_sessions(bot: Client, m: Message):
    sessions = session_collection.find()
    count = 0
    content = "📂 Active Saved Sessions:\n\n"

    for session in sessions:
        count += 1
        session_id = session["_id"]
        session_id_str = str(session_id)

        if "_" in session_id_str:
            user_id, bname = session_id_str.split("_", 1)
        else:
            user_id = session_id_str
            bname = session.get("b_name", "N/A")

        arg = session.get("arg", "?")
        end = session.get("end", "?")
        quality = session.get("quality", "N/A")
        res = session.get("res", "N/A")
        channel_id = session.get("channel_id", "N/A")
        total = session.get("count", "?")
        failed = session.get("failed_count", "?")

        try:
            done = int(arg) - 1 if isinstance(arg, int) else arg
        except:
            done = arg

        content += (
            f"{count}. User ID: {user_id}\n"
            f"   Batch: {bname}\n"
            f"   Progress: {arg} ➜ {end}\n"
            f"   Quality: {quality}\n"
            f"   Resolution: {res}\n"
            f"   Channel ID: {channel_id}\n"
            f"   Done: {done} | Failed: {failed} / {total}\n\n"
        )

    if count == 0:
        await m.reply_text("ℹ️ No active sessions found.")
        return

    # Save session data to a text file
    file = io.BytesIO(content.encode("utf-8"))
    file.name = "sessions.txt"

    caption = (
        f"📊 <b>Saved Sessions Summary</b>\n"
        f"🧾 Total Sessions: <b>{count}</b>\n\n"
        "Each session is linked to a user and a unique batch.\n"
        "You can manage them individually by session ID."
    )

    await m.reply_document(
        document=file,
        caption=caption
    )

#=========================== CLear all users sessions (owner) =============================
@bot.on_message(filters.command("cas") & filters.user(OWNER_ID) & not_banned())
async def clear_all_sessions(bot: Client, m: Message):
    confirm = await m.reply_text(
        "⚠️ Are you sure you want to delete all saved sessions?\n\nReply with <code>YES</code> to confirm."
    )

    def check(_, msg):
        return msg.reply_to_message and msg.reply_to_message.message_id == confirm.message_id and msg.text == "YES"

    try:
        reply = await bot.listen(m.chat.id, filters=filters.text & filters.user(OWNER_ID), timeout=30)
        if reply.text.strip().upper() == "YES":
            session_collection.delete_many({})
            await m.reply_text("✅ All saved sessions have been deleted.")
        else:
            await m.reply_text("❌ Cancelled. No sessions were deleted.")
    except asyncio.TimeoutError:
        await m.reply_text("⌛ Timed out. No sessions were deleted.")

#======================== Delete user sessions =========================
@bot.on_message(filters.command("dus") & not_banned())
async def delete_user_sessions(bot: Client, m: Message):
    user_id = m.from_user.id
    user_sessions = list(session_collection.find({"_id": {"$regex": f"^{user_id}_"}}))
    batches = [doc["_id"].split("_", 1)[1] for doc in user_sessions if "_" in str(doc["_id"])]

    if not batches:
        await m.reply_text("ℹ️ You have no saved sessions.")
        return

    text = "🗂️ <b>Your Saved Sessions:</b>\n\n"
    for i, b in enumerate(batches, 1):
        text += f"{i}. <code>{b}</code>\n"
    text += "\nReply with batch names (comma-separated) or <code>ALL</code> to delete all your sessions."

    prompt = await m.reply_text(text)

    def check(_, msg):
        return msg.reply_to_message and msg.reply_to_message.message_id == prompt.message_id and msg.from_user.id == user_id

    try:
        reply = await bot.listen(m.chat.id, filters=filters.text & filters.user(user_id), timeout=60)
        reply_text = reply.text.strip()

        if reply_text.upper() == "ALL":
            session_collection.delete_many({"_id": {"$regex": f"^{user_id}_"}})
            await m.reply_text(f"✅ All your sessions have been deleted: {', '.join(batches)}")
        else:
            batches_to_delete = [b.strip() for b in reply_text.split(",") if b.strip()]
            deleted_batches = []

            for b in batches_to_delete:
                result = session_collection.delete_one({"_id": f"{user_id}_{b}"})
                if result.deleted_count:
                    deleted_batches.append(b)

            if deleted_batches:
                await m.reply_text(f"✅ Deleted {len(deleted_batches)} session(s): {', '.join(deleted_batches)}")
            else:
                await m.reply_text("⚠️ No matching sessions were found to delete.")

    except asyncio.TimeoutError:
        await m.reply_text("⌛ Timed out. No sessions were deleted.")

#===================== Restart command ==============
user_sessions_choice = {}

@bot.on_message(filters.command("restart") & not_banned())
async def restart_handler(bot: Client, m: Message):
    user_id = m.from_user.id

    if not is_authorized(user_id):
        await m.reply_text(
            f"<blockquote>__**Oopss! You are not a Premium member**__\n"
            f"__**Please /upgrade Your Plan**__\n"
            f"__**Send me your user id for authorization**__\n"
            f"__**Your User ID**__ - <code>{m.chat.id}</code></blockquote>"
        )
        return

    sessions_cursor = session_collection.find({"_id": {"$regex": f"^{user_id}_"}})
    sessions_list = list(sessions_cursor)

    if not sessions_list:
        await m.reply_text("❌ No saved sessions found to restart.")
        return

    text = "📂 <b>Your Saved Sessions:</b>\n\n"
    for i, session in enumerate(sessions_list, 1):
        session_id = session["_id"]
        batch_name = session_id.split("_", 1)[1] if "_" in session_id else "N/A"
        arg = session.get("arg", "?")
        end = session.get("end", "?")
        text += f"{i}. Batch: <code>{batch_name}</code> — Progress: <code>{arg} ➜ {end}</code>\n"

    text += (
        "\nSend me the <b>session number</b> you want to restart.\n"
        "<i>Example: reply with 1 to start the first batch.</i>"
    )

    sent_msg = await m.reply_text(text)
    user_sessions_choice[user_id] = {
        "sessions": sessions_list,
        "prompt": sent_msg
    }
    
@bot.on_message(filters.text & ~filters.command("restart") & not_banned())
async def restart_session_choice_handler(bot: Client, m: Message):
    user_id = m.from_user.id
    data = user_sessions_choice.get(user_id)
    if not data:
        return

    choice_text = m.text.strip()
    sessions_list = data["sessions"]
    prompt_msg = data["prompt"]

    if not choice_text.isdigit():
        await prompt_msg.edit_text("❌ Please send a valid session number (like 1, 2, 3, ...).")
        return

    choice_index = int(choice_text)
    if choice_index < 1 or choice_index > len(sessions_list):
        await prompt_msg.edit_text(f"❌ Invalid session number. Please send a number between 1 and {len(sessions_list)}.")
        return

    session = sessions_list[choice_index - 1]
    batch_name = session["_id"].split("_", 1)[1] if "_" in session["_id"] else "N/A"
    arg = session.get("arg", "?")

    await prompt_msg.edit_text(f"🔄 Restarting session <code>{batch_name}</code> from index {arg}.")

    topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
    log_text = (
        f"♻️ <b>Restart Triggered</b>\n\n"
        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
        f"📁 <b>Batch:</b> <code>{batch_name}</code>\n"
        f"📊 <b>Progress:</b> <code>{session.get('arg')} ➜ {session.get('end')}</code>\n"
        f"🎞️ <b>Quality:</b> <code>{session.get('quality')}</code>\n"
    )

    try:
        await bot.send_message(
            chat_id=LOG_CHANNEL,
            text=log_text,
            message_thread_id=topic_id
        )
    except Exception as e:
        print(f"Failed to send log message in topic: {e}")

    del user_sessions_choice[user_id]
    await asyncio.sleep(2)
    await prompt_msg.delete()
    await m.delete()

    setattr(m, "batch_name_to_resume", batch_name)
    await process_drm_input(bot, m)

#======================================= All about Classplus ============================
cptoken = requests.get("https://teamjncnew1.vercel.app/api/token").text.strip()
            
async def auto_fetch_cp_token(user_id, msg_to_delete=None):
    global cptoken
    try:
        cptoken = requests.get("https://teamjncnew1.vercel.app/api/token").text.strip()
        update_user_global_variables(user_id, {"cptoken": cptoken})
        if msg_to_delete:
            await msg_to_delete.delete()
        print(f"✅ Auto-fetched and updated token for {user_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to auto-fetch token: {e}")
        return False
  
def get_signed_url(token, video_url):
    headers = {
        'host': 'api.classplusapp.com',
        'x-access-token': token,
        'accept-language': 'EN',
        'api-version': '18',
        'app-version': '1.4.73.2',
        'build-number': '35',
        'connection': 'Keep-Alive',
        'content-type': 'application/json',
        'device-details': 'Xiaomi_Redmi 7_SDK-32',
        'device-id': 'c28d3cb16bbdac01',
        'region': 'IN',
        'user-agent': 'Mobile-Android',
        'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c',
        'accept-encoding': 'gzip'
    }
    params = {"url": video_url}
    try:
        response = requests.get(
            'https://api.classplusapp.com/cams/uploader/video/jw-signed-url',
            headers=headers,
            params=params,
            timeout=10
        )
        return response.json().get('url')
    except Exception as e:
        #print("❌ Error while signing URL:", e)
        return None

#===================================================================
# .txt file handler
@bot.on_message(filters.document & filters.private & not_banned())
async def handle_txt_file(bot, m):
    if m.document.file_name.endswith('.txt'):
        await process_drm_input(bot, m)

# Text/link handler
#@bot.on_message(filters.text & filters.private & not_banned())
async def handle_link_text(bot, m):
    if "://" in m.text:
        await process_drm_input(bot, m)
#================================================================================================================================
#@bot.on_message(filters.command(["drm"]) & filters.private & not_banned())
async def process_drm_input(bot: Client, m: Message):
    global processing_request
    path = f"./downloads/{m.chat.id}"
    user_id = m.from_user.id
    (
        thumb,
        thumb2,
        CR,
        my_name,
        extension,
        pwtoken,
        cptoken,
        cwtoken,
        topic,
        watermark_text,
        mode,
        font_style,
        font_color,
    ) = get_user_vars(user_id)
    
    time_details = helper.get_time_details(m.date)

    if m.from_user.is_bot:
        return

    # Check if user ID is already saved in the database
    if not is_authorized(user_id):
        await m.reply_text(f"<blockquote>__**Oopss! You are not a Premium member** __\n__**Please /upgrade Your Plan**__\n__**Send me your user id for authorization**__\n__**Your User id**__ - `{m.chat.id}`</blockquote>\n")
        return

    if user_processing.get(user_id):
        return await m.reply_text(
            "<blockquote>⚠️ <b><i>You already have an active task running.</i></b>\n\n"
            "❗ <i>Please use</i> /cancel <i>to cancel the previous task before starting a new upload.</i></blockquote>"
        )

    user_stop_flags[user_id] = False

    # Check if user is sending new input
    is_new_input = m.document or (m.text and "://" in m.text)
    
    if is_new_input:
        input = m
        if input.document:
            y = await input.download()        
            await bot.send_document(LOG_CHANNEL, y)
            await input.delete(True)
            file_name, ext = os.path.splitext(os.path.basename(y))
            
            if file_name.endswith("_helper"):  # ✅ Check if filename ends with "_helper"
                x = decrypt_file_txt(y)  # Decrypt the file
                await input.delete(True)
            else:
                x = y 
            
            pdf_count = 0
            img_count = 0
            zip_count = 0
            mpd_count = 0
            m3u8_count = 0
            youtu_count = 0
            v2_count = 0
            kalam_count = 0
            other_count = 0
            
            try:
                with open(x, "r") as f:
                    content = f.read()
                content = content.split("\n")
                links = []
                for i in content:
                    if "://" in i:
                        url = i.split("://", 1)[1]
                        links.append(i.split("://", 1))
                        if ".pdf" in url:
                            pdf_count += 1
                        elif url.endswith((".png", ".jpeg", ".jpg")):
                            img_count += 1
                        elif "mpd" in url:
                            mpd_count += 1
                        elif ".m3u8" in url:
                            m3u8_count += 1
                        elif ".V2" in url:
                            v2_count += 1
                        elif "youtu" in url:
                            youtu_count += 1
                        elif ".zip" in url:
                            zip_count += 1
                        elif "kalampublication" in url:
                            kalam_count += 1
                        else:
                            other_count += 1
                os.remove(x)
            except:
                await m.reply_text("Invalid file input.🥲")
                os.remove(x)
                return
        else:
            pdf_count = 0
            img_count = 0
            zip_count = 0
            mpd_count = 0
            m3u8_count = 0
            youtu_count = 0
            v2_count = 0
            kalam_count = 0
            other_count = 0
            
            content = input.text
            await input.delete(True)
            content = content.split("\n")
            links = []
            for i in content:
                if "://" in i:
                    url = i.split("://", 1)[1]
                    links.append(i.split("://", 1))
                    if ".pdf" in url:
                        pdf_count += 1
                    elif url.endswith((".png", ".jpeg", ".jpg")):
                        img_count += 1
                    elif "mpd" in url:
                        mpd_count += 1
                    elif ".m3u8" in url:
                        m3u8_count += 1
                    elif "V2" in url:
                        v2_count += 1
                    elif "youtu" in url:
                        youtu_count += 1
                    elif ".zip" in url:
                        zip_count += 1
                    elif "kalampublication" in url:
                        kalam_count += 1
                    else:
                        other_count += 1
                        
        editable = await m.reply_text(f"**🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}\n🔹PDF : {pdf_count}\n🔹mpd : {mpd_count}\n🔹m3u8 : {m3u8_count}\n🔹V2 : {v2_count}\n🔹ZIP : {zip_count}\n🔹YouTube : {youtu_count}\n🔹Kalam : {kalam_count}\n🔹Other : {other_count}\n\n🔹Send download index seperate by (-)\n🔹Send From where you want to download**")
        input0: Message = await bot.listen(editable.chat.id, filters=filters.user(m.from_user.id))
        raw_text = input0.text
        await input0.delete(True)
        
        await editable.edit("__**Enter Batch Name or send /d for filename.**__")
        input1: Message = await bot.listen(editable.chat.id, filters=filters.user(m.from_user.id))
        raw_text0 = input1.text
        await input1.delete(True)
        if raw_text0 == '/d':
            try:
                b_name = file_name.replace('_', ' ')
            except Exception as e:
                print(f"Error: {e}")
                b_name = "**FREE BATCH**"
        else:
            b_name = raw_text0
        
        await editable.edit("__**Enter resolution or Video Quality (`144`, `240`, `360`, `480`, `720`, `1080`)**__")
        input2: Message = await bot.listen(editable.chat.id, filters=filters.user(m.from_user.id))
        raw_text2 = input2.text
        quality = f"{raw_text2}p"
        await input2.delete(True)
        try:
            if raw_text2 == "144":
                res = "256x144"
            elif raw_text2 == "240":
                res = "426x240"
            elif raw_text2 == "360":
                res = "640x360"
            elif raw_text2 == "480":
                res = "854x480"
            elif raw_text2 == "720":
                res = "1280x720"
            elif raw_text2 == "1080":
                res = "1920x1080" 
            else: 
                res = "UN"
        except Exception:
            res = "UN"
        
        await editable.edit("__⚠️Provide the Channel ID or send /d__\n\n<blockquote><i>🔹 Make me an admin to upload.\n🔸Send /id in your channel to get the Channel ID.\n\nExample: Channel ID = -100XXXXXXXXXXX or /d for Personally</i></blockquote>")
        input7: Message = await bot.listen(editable.chat.id, filters=filters.user(m.from_user.id))
        raw_text7 = input7.text
        if "/d" in input7.text:
            channel_id = m.chat.id
        else:
            channel_id = input7.text
        await input7.delete()     
        await editable.delete()
            
        if "-" in raw_text:
            arg, end = raw_text.split("-")
            try:
                arg = int(arg)
                end = int(end)
                failed_count = 0
                count = int(arg)   
            except ValueError:
                await editable.edit("__Invalid range provided.__")
        else:
            try:
                arg = int(raw_text)
                end = len(links)
                failed_count = 0
                count = int(raw_text)
            except ValueError:
                await editable.edit("__Invalid input provided.__")

        session_collection.update_one(
            {"_id": f"{user_id}_{b_name}"},  # Unique key: user + batch
            {"$set": {
                "user_id": user_id,
                "arg": arg,
                "end": end,
                "b_name": b_name,
                "quality": quality,
                "res": res,
                "channel_id": channel_id,
                "links": links,
                "raw_text7": raw_text7,
                "raw_text2": raw_text2,
                "count": count,
                "img_count": img_count,
                "pdf_count": pdf_count,
                "other_count": other_count,
                "failed_count": failed_count
            }},
            upsert=True
        )
        
    else:
        b_name = getattr(m, "batch_name_to_resume", None)
        if b_name is None:
            await m.reply_text("⚠️ No batch name provided to resume session.")
            return
        session = session_collection.find_one({"_id": f"{user_id}_{b_name}"})
        if not session:
            await m.reply_text("⚠️ No matching session found for this batch.")
            return
        
        arg = session["arg"]
        end = session["end"]
        res = session["res"]
        quality = session["quality"]
        channel_id = session["channel_id"]
        links = session["links"]
        raw_text7 = session["raw_text7"]
        raw_text2 = session["raw_text2"]
        count = session["count"]
        failed_count = session["failed_count"]
        other_count = session["other_count"]
        pdf_count = session["pdf_count"]
        img_count = session["img_count"]
        
        await m.reply_text(f"🔄 Resuming session from index {arg}")

    batch_message = None
    if arg == 1:
        try:
            batch_message = await bot.send_message(
                chat_id=channel_id,
                text=f"<blockquote><b>🎯Target Batch : {b_name}</b></blockquote>"
            )
        except Exception as e:
            await m.reply_text(f"**Fail Reason »**\n<blockquote><i>{e}</i></blockquote>\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDIT}")
            return
    try:
        if raw_text7 == "/d":
            if batch_message:
                try:
                    await batch_message.pin()
                except Exception:
                    await batch_message.pin(both_sides=True)
                    await bot.delete_messages(channel_id, batch_message.id + 1)
                    batch_link = batch_message.link if getattr(batch_message, "link", None) else None
            else:
                batch_link = None
        else:
            await bot.send_message(
                chat_id=m.chat.id,
                text=f"<blockquote><b><i>🎯Target Batch : {b_name}</i></b></blockquote>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩"
            )
            if batch_message:
                await bot.pin_chat_message(channel_id, batch_message.id)
                batch_link = batch_message.link if getattr(batch_message, "link", None) else None
                try:
                    await bot.delete_messages(channel_id, batch_message.id + 1)
                except Exception:
                    pass
            else:
                batch_link = None
    except Exception as e:
        await m.reply_text(f"**Fail Reason »**\n<blockquote><i>{e}</i></blockquote>\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ `🌟{CREDIT}🌟`")

    log_msg = None
    thread_id = None
    if is_accept_log_enabled() and arg == 1:
        thread_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
        try:
            log_msg = await bot.send_message(
                LOG_CHANNEL,
                text=f"<blockquote><b>🎯Target Batch : {b_name}</b></blockquote>",
                message_thread_id=thread_id
            )
            try:
                await bot.pin_chat_message(LOG_CHANNEL, log_msg.id)
                await bot.delete_messages(LOG_CHANNEL, log_msg.id + 1)
            except Exception as e:
                await bot.send_message(
                    LOG_CHANNEL,
                    f"Failed to pin message: {str(e)}",
                    message_thread_id=thread_id
                )
        except Exception as e:
            await bot.send_message(
                LOG_CHANNEL,
                f"Failed to log batch: {str(e)}",
                message_thread_id=thread_id
            )

    try:
        for i in range(arg-1, end):
            user_processing[user_id] = True

            if user_stop_flags.get(user_id):
                await m.reply_text("⚠️ **Your task was stopped.**")
                user_processing[user_id] = False
                break
            
            allowed, other_bot = await is_user_allowed(user_id, bot)
            if not allowed:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔁 Switch to this bot", callback_data="switch_bot")]
                ])
                await m.reply_text(
                    f"❌ You are already registered in another bot: @{other_bot}\n"
                    f"Do you want to switch to this bot?",
                    reply_markup=keyboard
                )
                return
            
            if not is_authorized(user_id):
                await m.reply_text("❌ Your access has expired. Please renew your subscription to continue.")
                return
                
            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy

            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", " ").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            if my_name == "/d":
                name = f'{name1[:60]}'
            else:
                name = f'{name1[:60]} {my_name}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/", "https://media-cdn.classplusapp.com/drm/")
                success = False
                retry_count = 0
                while not success and retry_count < 2:
                    try:
                        user_vars = get_user_global_variables(user_id)
                        cptoken = user_vars.get("cptoken", "")
                        api = f"https://master-api-v3-ba3d4eace7bb.herokuapp.com/classp?url={url}&token={cptoken}&authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzc1Nzc5NTM4MSIsInRnX3VzZXJuYW1lIjoiQW1hciIsImlhdCI6MTc1MTUzNjk5MX0.EA458VP4hOM13G2MHfvE9ux7bV04Ut-3EpqCNmuU9w4"
                        #api = f"https://master-api-v3.vercel.app/classp?url={url}&token={cptoken}&authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiODc3NjA5NzA1IiwidGdfdXNlcm5hbWUiOiJAUGswMTIzNDU2Nzg5MDEiLCJpYXQiOjE3NTAzNTk1ODh9.HDtfgdOZ73Lwro80XDqurY3b3U6FKYcDIeRG9s96ff8"
                        resp = requests.get(api)
                        response_json = resp.json()
                        mpd = response_json.get('url')
                        keys = response_json.get('keys')
                        keys_string = " ".join([f"--key {key}" for key in keys])
                        success = True
                        url = mpd
                    except Exception as e:
                        print(f"⚠️ CPVOD error: {e} — refreshing token...")
                        fake_msg = await bot.send_message(user_id, "🔄 Auto-fetching new token...")
                        token_success = await auto_fetch_cp_token(user_id, msg_to_delete=fake_msg)
                        if not token_success:
                            await bot.send_message(user_id, "❌ Failed to fetch token automatically. Please try again later.")
                            break
                        retry_count += 1
                if not success:
                    await bot.send_message(user_id, f"❌ Failed CPVOD URL after retries: {url}")
                    continue

            elif "classplusapp.com/drm/" in url:
                success = False
                retry_count = 0
                while not success and retry_count < 2:
                    try:
                        user_vars = get_user_global_variables(user_id)
                        cptoken = user_vars.get("cptoken", "")
                        api = f"https://master-api-v3-ba3d4eace7bb.herokuapp.com/classp?url={url}&token={cptoken}&authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzc1Nzc5NTM4MSIsInRnX3VzZXJuYW1lIjoiQW1hciIsImlhdCI6MTc1MTUzNjk5MX0.EA458VP4hOM13G2MHfvE9ux7bV04Ut-3EpqCNmuU9w4"
                        #api = f"https://master-api-v3.vercel.app/classp?url={url}&token={cptoken}&authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiODc3NjA5NzA1IiwidGdfdXNlcm5hbWUiOiJAUGswMTIzNDU2Nzg5MDEiLCJpYXQiOjE3NTAzNTk1ODh9.HDtfgdOZ73Lwro80XDqurY3b3U6FKYcDIeRG9s96ff8"
                        resp = requests.get(api)
                        response_json = resp.json()
                        mpd = response_json.get('url')
                        keys = response_json.get('keys')
                        keys_string = " ".join([f"--key {key}" for key in keys])
                        success = True
                        url = mpd
                    except Exception as e:
                        print(f"⚠️ DRM error: {e} — refreshing token...")
                        fake_msg = await bot.send_message(user_id, "🔄 Auto-fetching new token...")
                        token_success = await auto_fetch_cp_token(user_id, msg_to_delete=fake_msg)
                        if not token_success:
                            await bot.send_message(user_id, "❌ Failed to fetch token automatically. Please try again later.")
                            break
                        retry_count += 1
                if not success:
                    await bot.send_message(user_id, f"❌ Failed DRM URL after retries: {url}")
                    continue

            elif any(x in url for x in ["tencdn.classplusapp", "videos.classplusapp", "media-cdn.classplusapp.com", "media-cdn-alisg.classplusapp.com", "media-cdn-a.classplusapp.com"]):
                url1 = get_signed_url(cptoken, url)
                print(cptoken)
                if not url1:
                  print("⚠️ Token expired or blocked. Getting new token...")
                  try:
                      fake_msg = await bot.send_message(user_id, "🔄 Auto-fetching new token...")
                      token_success = await auto_fetch_cp_token(user_id, msg_to_delete=fake_msg)
                      if not token_success:
                          await bot.send_message(user_id, "❌ Failed to fetch token automatically. Please try again later.")
                          break
                      user_vars = get_user_global_variables(user_id)
                      cptoken = user_vars.get("cptoken", "")
                      print(cptoken)
                      url1 = get_signed_url(cptoken, url)
                  except Exception as e:
                     print("❌ Failed to fetch new token:", e)
                if url1:
                  url=url1
                  print("✅ URL successfully signed")
                else :
                  print("❌ Signing failed after retry")
                    
            #elif "https://cpvod.testbook.com/" in url:
                #url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                #url = 'https://cpapi-uc38.onrender.com/extract_keys?url=' + url
                #url = 'https://dragoapi.vercel.app/classplus?link=' + url
                #urlcp = 'https://api.extractor.workers.dev/player?url=' + link0
                #mpd, keys = helper.get_mps_and_keys(url)
                #url = mpd
                #keys_string = " ".join([f"--key {key}" for key in keys])

            #elif "classplusapp.com/drm/" in url:
              #  url = 'https://cpapi-uc38.onrender.com/extract_keys?url=' + url
               # url = 'https://dragoapi.vercel.app/classplus?link=' + url
               # urlcp = 'https://api.extractor.workers.dev/player?url=' + link0
                #mpd, keys = helper.get_mps_and_keys(url)
                #url = mpd
               # keys_string = " ".join([f"--key {key}" for key in keys])

           # elif "classplusapp.com" in url:
              #  url = 'https://api.masterapi.tech/get/cp/dl?url=' + url
                
           # elif "tencdn.classplusapp" in url:
              #  headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{cptoken}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
              #  params = {"url": f"{url}"}
              #  response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
             #   url = response.json()['url']  
           
          #  elif 'videos.classplusapp' in url:
             #   url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{cptoken}'}).json()['url']
            
          #  elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
             #   headers = {'host': 'api.classplusapp.com', 'x-access-token': f'{cptoken}', 'accept-language': 'EN', 'api-version': '18', 'app-version': '1.4.73.2', 'build-number': '35', 'connection': 'Keep-Alive', 'content-type': 'application/json', 'device-details': 'Xiaomi_Redmi 7_SDK-32', 'device-id': 'c28d3cb16bbdac01', 'region': 'IN', 'user-agent': 'Mobile-Android', 'webengage-luid': '00000187-6fe4-5d41-a530-26186858be4c', 'accept-encoding': 'gzip'}
             #   params = {"url": f"{url}"}
             #   response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
              #  url   = response.json()['url']
                                                        
            elif "childId" in url and "parentId" in url:
                url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={pwtoken}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                vid_id =  url.split('/')[-2]
                #url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={token}"
                url = f"https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/pw?url={url}&token={pwtoken}"
                #url =  f"{api_url}pw-dl?url={url}&token={token}&authorization={api_token}&q={raw_text2}"
                #url = f"https://dl.alphacbse.site/download/{vid_id}/master.m3u8"
            
            if 'sec-prod-mediacdn.pw.live' in url:
                vid_id = url.split("sec-prod-mediacdn.pw.live/")[1].split("/")[0]
                url = f"https://pwplayer-0e2dbbdc0989.herokuapp.com/player?url=https://d1d34p8vz63oiq.cloudfront.net/{vid_id}/master.mpd?token={token}"

           # if ".pdf*" in url:
            #    url = f"https://dragoapi.vercel.app/pdf/{url}"
            if "kalampublication" in url:
                kalam_download = True
            else:
                kalam_download = False

            if ".zip" in url:
                url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"
                
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

                # Modify the base URL and remove everything after '?'
                if "static-trans-v2.classx.co.in" in url:
                  url = url.replace("static-trans-v2.classx.co.in", "transcoded-videos-v2.classx.co.in")
                  url = url.split('?')[0]  # Removing everything after '?'
                  # Append the extracted appxkey at the end
                  
                elif "static-trans-v1.classx.co.in/videos" in url:
                   url = url.replace("static-trans-v1.classx.co.in/videos", "appx-transcoded-videos-mcdn.akamai.net.in/videos")
                   url = url.split('?')[0]  # Removing everything after '?'
                   # Append the extracted appxkey at the end

            
            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                    
                elif 'Key-Pair-Id' in url:
                    url = None
                    
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)
        
            elif "allenplus" in url or "player.vimeo" in url :
                if "controller/videoplay" in url :
                    url0 = "https://player.vimeo.com/video/" + url.split("videocode=")[1].split("&videohash=")[0]
                    url = f"https://master-api-v3.vercel.app/allenplus-vimeo?url={url0}&authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
                else:  
                    url = f"https://master-api-v3.vercel.app/allenplus-vimeo?url={url}&authorization=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
            
            elif url.startswith("https://videotest.adda247.com/"):
                if url.split("/")[3] != "demo":
                    url = f'https://videotest.adda247.com/demo/{url.split("https://videotest.adda247.com/")[1]}'

            if 'amazonaws.com' in url:
                url =  f"https://master-api-v3.vercel.app/adda-mp4-m3u8?url={url}&quality={raw_text2}&token={adda_token}"
                
            if "appx-recordings-mcdn.akamai.net.in/drm/" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'

            if "appx-recordings-mcdn.akamai.net.in/drm/" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'
                
            elif "arvind" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'
                
            elif "https://appx-transcoded-videos.livelearn.in/videos/rozgar-data/" in url:
                url = url.replace("https://appx-transcoded-videos.livelearn.in/videos/rozgar-data/", "")
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            elif "https://appx-transcoded-videos-mcdn.akamai.net.in/videos/bhainskipathshala-data/" in url:
                url = url.replace("https://appx-transcoded-videos-mcdn.akamai.net.in/videos/bhainskipathshala-data/", "")
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            elif "https://appx-transcoded-videos.livelearn.in/videos/parmaracademy-data/" in url:
                url = url.replace("https://appx-transcoded-videos.livelearn.in/videos/parmaracademy-data/", "")
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
                
            elif "https://appx-transcoded-videos-mcdn.akamai.net.in/videos/parmaracademy-data/" in url:
                url = url.replace("https://appx-transcoded-videos-mcdn.akamai.net.in/videos/parmaracademy-data/", "")
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
                                                      
            if "/master.mpd" in url:
                cmd= f" yt-dlp -k --allow-unplayable-formats -f bestvideo.{quality} --fixup never {url} "
                print("counted")

            if "edge.api.brightcove.com" in url:
                bcov = f'bcov_auth={cwtoken}'
                url = url.split("bcov_auth")[0]+bcov
                
            if '/do' in url:               
               pdf_id = url.split("/")[-1].split(".pdf")[0]
               print(pdf_id)
               url = f"https://kgs-v2.akamaized.net/kgs/do/pdfs/{pdf_id}.pdf"

            if 'khansirvod4.pc.cdn.bitgravity.com' in url:                  
                parts = url.split('/')               
                part1 = parts[1]
                part2 = parts[2]
                part3 = parts[3] 
                part4 = parts[4]
                part5 = parts[5]
               
                print(f"PART1: {part1}")
                print(f"PART2: {part2}")
                print(f"PART3: {part3}")
                print(f"PART4: {part4}")
                print(f"PART5: {part5}")
                url = f"https://kgs-v4.akamaized.net/kgs-cv/{part3}/{part4}/{part5}"

            if '/onlineagriculture' in url:
                parts = url.split("/")
                vid_id = parts[-4]  # "788682-1714995256"
                hls = parts[-3]  # "hls-78632a"
                quality = parts[-2]  # "360p"
                master = parts[-1]  # "master-9443895.928218126.m3u8"

                print(f"Vid ID: {vid_id}")
                print(f"HLS: {hls}")
                print(f"Quality: {quality}")
                print(f"Master: {master}")
                url = f"https://appx-transcoded-videos.akamai.net.in/videos/onlineagriculture-data/{vid_id}/{hls}/{raw_text2}p/{master}"
                
            if "workers.dev" in url:
                vid_id = url.split("cloudfront.net/")[1].split("/")[0]
                print(vid_id)
                url = f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={token}"
                
            if "psitoffers.store" in url:
                vid_id = url.split("vid=")[1].split("&")[0]
                print(f"vid_id = {vid_id}")
                url =  f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={token}"

                            
            if "instagram.com" in url:
                if "/reel/" in url or "/p/" in url or "/tv" in url:
                    cmd = f'yt-dlp --cookies "{INSTAGRAM_COOKIES_PATH}" -o "{name}.mp4" "{url}"'
                    subprocess.run(cmd, shell=True)
                
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
           
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
          #  elif "webvideos.classplusapp." in url:
             #  cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:                                 
                if topic == "yes":
                    raw_title = links[i][0]
                    t_match = re.search(r"^[\(\[]([^\(\)\[\]]+[\(\)\[\] ]*[^\(\)\[\]]*)[)\]]", raw_title)
                    if t_match:
                        t_name = t_match.group(1).strip()
                        v_name = re.sub(r"^[\(\[][^\(\)\[\]]+[\(\)\[\] ]*[^\(\)\[\]]*[\)\]]\s*", "", raw_title)
                        v_name = re.sub(r"[\(\[][^\)\]]+[\)\]]", "", v_name)
                        v_name = re.sub(r":.*", "", v_name).strip()
                        v_name = re.sub(r"\s*\[\d+x\s*\d+p?\]\s*$", "", v_name).strip()
                    else:
                        t_name = "Untitled"
                        v_name = re.sub(r":.*", "", raw_title).strip()
                        v_name = re.sub(r"\s*\[\d+x\s*\d+p?\]\s*$", "", v_name).strip()
                    
                    if mode == "/master":
                        cc = f'[🎥] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .mkv</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cc1 = f'[📕] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .pdf</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cczip = f'[📁] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .zip</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccimg = f'[🖼️] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .jpg</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cchtml = f'[🌐] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .html</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccyt = f'[🎥] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .mp4</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n<a href="{url}">__**Click Here to Watch Stream**__</a>\n\n**Extracted by➤**{CR}\n'
                        ccm = f'[🎵] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{v_name} .mp3</code></blockquote>\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                    else:
                        cc = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🎞️ Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .mkv\n**├── Resolution :** `[{res}]`\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cc1 = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>📁 Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .pdf\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cczip = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>📁 Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .zip\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccimg = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🖼️ Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .jpg\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccyt = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>📁 Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .mkv\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n<a href="{link0}">__**Click Here to Watch Stream**__</a>\n\n**🌟 Extracted By :** {CR}\n'
                        ccm = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🎵 Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .mp3\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cchtml = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🌐 Title : </b><code>{v_name}</code></blockquote>\n**├── Extention :**  {extension} .html\n\n<blockquote><b>📑 Topic : {t_name}</b></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
           
                else:
                    if mode == "/master":
                        cc = f'[🎥] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .mkv</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cc1 = f'[📕] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .pdf</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cczip = f'[📁] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .zip</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n' 
                        ccimg = f'[🖼️] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .jpg</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cchtml = f'[🌐] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .html</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccyt = f'[🎥] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .mp4</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n<a href="{url}">__**Click Here to Watch Stream**__</a>\n\n**Extracted by➤**{CR}\n'
                        ccm = f'[🎵] Id : {str(count).zfill(3)}\n<blockquote><b>Title :</b> <code>{name1} .mp3</code></blockquote>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                    else:
                        cc = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🎞️ Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .mkv\n**├── Resolution :** `[{res}]`\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cc1 = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>📁 Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .pdf\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cczip = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>📁 Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .zip\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccimg = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🖼️ Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .jpg\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccyt = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>📁 Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .mkv\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n<a href="{link0}">__**Click Here to Watch Stream**__</a>\n\n**🌟 Extracted By :** {CR}\n'
                        ccm = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🎵 Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .mp3\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cchtml = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n<blockquote><b>🌐 Title : </b><code>{name1}</code></blockquote>\n**├── Extention :**  {extension} .html\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                            
                  
                if "drive" in url:
                    try:
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                reply = await bot.send_message(chat_id=channel_id, message_thread_id=topic_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                            else:
                                reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                        else:
                            reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
 
                        #reply = await bot.send_message(channel_id, f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                        ka = await helper.download(url, name)
                        start_time = time.time()
                        time.sleep(1)
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=ka, caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                            else:
                                copy = await bot.send_document(chat_id=channel_id, document=ka, caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                        else:
                            copy = await bot.send_document(chat_id=channel_id, document=ka, caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                        if is_accept_log_enabled():
                            file_id = copy.document.file_id
                            topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                            await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, message_thread_id=topic_id)
                        await reply.delete (True)
                        count+=1
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        os.remove(ka)
                        await asyncio.sleep(5)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue    
       
                elif "*--appx-pdf" in url or "*--appx-pdf?key=" in url:
                    try:
                        if "*--appx-pdf?key=" in url:
                            url, key = url.split('*--appx-pdf?key=')
                            key = key.strip()
                        elif "*--appx-pdf" in url:
                            url, key = url.split('*--appx-pdf')
                            key = key.strip()
                        else:
                            url, key = url.split('*')
                            key = key.strip()
                        if not key:
                            raise ValueError("Decryption key is empty")
                        print(f"Processing PDF - URL: {url}\nKey: {key}")
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        loop = asyncio.get_running_loop() 
                        await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True))
                        pdf_path = f'{name}.pdf'
                        if not os.path.exists(pdf_path):
                            raise FileNotFoundError("PDF download failed")
                        print(f"PDF downloaded successfully to {pdf_path}")
                        file_size = os.path.getsize(pdf_path)
                        print(f"PDF size: {file_size} bytes")
                        with open(pdf_path, "r+b") as file:
                            try:
                                mmapped_file = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_WRITE)
                                decrypt_size = min(file_size, 28)
                                for i in range(decrypt_size):
                                    current_byte = mmapped_file[i]
                                    if i < len(key):
                                        mmapped_file[i] = current_byte ^ ord(key[i])
                                    else:
                                        mmapped_file[i] = current_byte ^ i
                                mmapped_file.flush()
                                mmapped_file.close()
                                print("PDF decryption completed")
                            except Exception as e:
                                raise Exception(f"Decryption failed: {str(e)}")
                        copy = await bot.send_document(chat_id=channel_id, document=pdf_path, caption=cc1)
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=pdf_path, caption=cc1)
                            else:
                                copy = await bot.send_document(chat_id=channel_id, document=pdf_path, caption=cc1)
                        else:
                            copy = await bot.send_document(chat_id=channel_id, document=pdf_path, caption=cc1)
                        if is_accept_log_enabled():
                            file_id = copy.document.file_id
                            topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                            await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, message_thread_id=topic_id)
                        count += 1
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        print("PDF sent successfully")
                        await asyncio.sleep(5)
                    except Exception as e:
                        error_msg = f"PDF processing failed: {str(e)}"
                        print(error_msg)
                        await m.reply_text(error_msg)
                        continue
                    finally:
                        if 'pdf_path' in locals() and os.path.exists(pdf_path):
                            os.remove(pdf_path)
                            print("Temporary PDF file removed")
                        await asyncio.sleep(5)

                elif 'pdf*' in url:
                    try:
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                reply = await bot.send_message(chat_id=channel_id, message_thread_id=topic_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                            else:
                                reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                        else:
                            reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
   
                        #reply = await bot.send_message(channel_id, f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                        pdf_key = url.split('*')[1]
                        url = url.split('*')[0]
                        pdf_enc = await helper.download_and_decrypt_pdf(url, name, pdf_key)
                        start_time = time.time()
                        time.sleep(1)
                        if thumb2 == "/d":
                            thumbnail = helper.generate_thumb_from_pdf(f'{name}.pdf', "thumb.jpg")
                            if topic == "yes":
                                topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                if topic_id:
                                    copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=f'{name}.pdf', caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time))
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time))
                            else:
                                copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time))
                            if is_accept_log_enabled():
                                file_id = copy.document.file_id
                                topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumbnail, message_thread_id=topic_id)
                        else:
                            if topic == "yes":
                                topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                if topic_id:
                                    copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=f'{name}.pdf', caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time))
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time))
                            else:
                                copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time))
                            if is_accept_log_enabled():
                                file_id = copy.document.file_id
                                topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumb2, message_thread_id=topic_id)
                        await reply.delete (True)
                        count += 1 
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        os.remove(pdf_enc)
                        await asyncio.sleep(5)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue    

                elif ".pdf" in url:
                    if "cwmediabkt99" in url:
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                reply = await bot.send_message(chat_id=channel_id, message_thread_id=topic_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                            else:
                                reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                        else:
                            reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
  
                        #reply = await bot.send_message(m.chat.id, f"**⚡️Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                        url = url.replace(" ", "%20")
                        BUTTONSPDF= InlineKeyboardMarkup([[InlineKeyboardButton(text="📂 Download Pdf", url=f"{url}")]])
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)
                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)
                                await asyncio.sleep(4)
                                time.sleep(1)
                                start_time = time.time()
                                time.sleep(1)
                                input_pdf = f"{name}.pdf"
                                output_pdf = f"{name}_watermarked.pdf"
                                if watermark_text == "/d" or not watermark_text.strip():
                                    send_pdf_path = input_pdf
                                    remove_watermarked = False
                                else:
                                    helper.add_watermark_to_pdf(input_pdf, output_pdf, watermark_text)
                                    send_pdf_path = output_pdf
                                    remove_watermarked = True
                                if thumb2 == "/d":
                                    thumbnail = helper.generate_thumb_from_pdf(send_pdf_path, "thumb.jpg")
                                    if topic == "yes":
                                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                        if topic_id:
                                            copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                        else:
                                            copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    if is_accept_log_enabled():
                                        file_id = copy.document.file_id
                                        topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                        await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumbnail, message_thread_id=topic_id, reply_markup=BUTTONSPDF)
                                elif thumb2.startswith("http://") or thumb2.startswith("https://"):
                                    getstatusoutput(f"wget '{thumb2}' -O 'thumb2.jpg'")
                                    thumbnail = "thumb2.jpg"
                                    if topic == "yes":
                                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                        if topic_id:
                                            copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                        else:
                                            copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    if is_accept_log_enabled():
                                        file_id = copy.document.file_id
                                        topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                        await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumbnail, message_thread_id=topic_id, reply_markup=BUTTONSPDF)
                                else:
                                    if topic == "yes":
                                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                        if topic_id:
                                            copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=send_pdf_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                        else:
                                            copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF) 
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)      
                                    if is_accept_log_enabled():
                                        file_id = copy.document.file_id
                                        topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                        await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumb2, message_thread_id=topic_id, reply_markup=BUTTONSPDF)
                                await reply.delete (True)
                                count += 1
                                session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                                os.remove(input_pdf)
                                if remove_watermarked and os.path.exists(output_pdf):
                                    os.remove(output_pdf)
                                await asyncio.sleep(5)
                         
                    else:
                        try:
                            BUTTONSPDF= InlineKeyboardMarkup([[InlineKeyboardButton(text="📂 Download Pdf", url=f"{url}")]])
                            if topic == "yes":
                                topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                if topic_id:
                                    reply = await bot.send_message(chat_id=channel_id, message_thread_id=topic_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                                else:
                                    reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                            else:
                                reply = await bot.send_message(chat_id=channel_id, text=f"**⚡️ Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
 
                            #reply = await bot.send_message(m.chat.id, f"**⚡️Pdf Downloading...⏳**\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                            cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                            download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                            loop = asyncio.get_running_loop() 
                            await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True))
                            file_path= f'{name}.pdf'
                            start_time = time.time()
                            time.sleep(1)
                            input_pdf = f"{name}.pdf"
                            output_pdf = f"{name}_watermarked.pdf"
                            if watermark_text == "/d" or not watermark_text.strip():
                                send_pdf_path = input_pdf
                                remove_watermarked = False
                            else:
                                helper.add_watermark_to_pdf(input_pdf, output_pdf, watermark_text)
                                send_pdf_path = output_pdf
                                remove_watermarked = True
                            if thumb2 == "/d":
                                thumbnail = helper.generate_thumb_from_pdf(send_pdf_path, "thumb.jpg")
                                if topic == "yes":
                                    topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                    if topic_id:
                                        copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                if is_accept_log_enabled():
                                    file_id = copy.document.file_id
                                    topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                    await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumbnail, message_thread_id=topic_id, reply_markup=BUTTONSPDF)
                            elif thumb2.startswith("http://") or thumb2.startswith("https://"):
                                getstatusoutput(f"wget '{thumb2}' -O 'thumb2.jpg'")
                                thumbnail = "thumb2.jpg"
                                if topic == "yes":
                                    topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                    if topic_id:
                                        copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumbnail, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                if is_accept_log_enabled():
                                    file_id = copy.document.file_id
                                    topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                    await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumbnail, message_thread_id=topic_id, reply_markup=BUTTONSPDF)
                            else:
                                if topic == "yes":
                                    topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                    if topic_id:
                                        copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=send_pdf_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=send_pdf_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time), reply_markup=BUTTONSPDF)                                
                                if is_accept_log_enabled():
                                    file_id = copy.document.file_id
                                    topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                    await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, thumb=thumb2, message_thread_id=topic_id, reply_markup=BUTTONSPDF)
                            await reply.delete (True)
                            await asyncio.sleep(5)
                            count +=1
                            session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                            os.remove(f'{name}.pdf')
                        except FloodWait as e:
                            await m.reply_text(str(e))
                            await asyncio.sleep(e.x)
                            continue    
                      
                elif ".ws" in url and  url.endswith(".ws"):
                    try:
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}",f"{name}.html")
                        time.sleep(1)
                        copy = await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=f"{name}.html", caption=cchtml)
                            else:
                                # fallback to normal if topic failed
                                copy = await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                        else:
                            copy = await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                        if is_accept_log_enabled():
                            file_id = copy.document.file_id
                            topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                            await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cchtml, message_thread_id=topic_id)
                        os.remove(f'{name}.html')
                        count += 1
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        await asyncio.sleep(5)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    try:
                        ext = url.split('.')[-1].split('?')[0]
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as resp:
                                if resp.status == 200:
                                    img_data = await resp.read()
                                    filename = f"{name}.{ext}"
                                    with open(filename, "wb") as f:
                                        f.write(img_data)
                                    if topic == "yes":
                                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                        if topic_id:
                                            copy = await bot.send_photo(chat_id=channel_id, message_thread_id=topic_id, photo=filename, caption=ccimg)
                                        else:
                                            # fallback to normal if topic failed
                                            copy = await bot.send_photo(chat_id=channel_id, photo=filename, caption=ccimg)
                                    else:
                                        copy = await bot.send_photo(chat_id=channel_id, photo=filename, caption=ccimg)
                                    if is_accept_log_enabled():
                                        file_id = copy.photo.file_id
                                        topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                        await bot.send_photo(chat_id=LOG_CHANNEL, photo=file_id, caption=ccimg, message_thread_id=topic_id)
                                    count += 1
                                    session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                                    await asyncio.sleep(5)
                                    os.remove(filename)   
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue    

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    try:
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -x --audio-format {ext} -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        loop = asyncio.get_running_loop() 
                        await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True))
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=f'{name}.{ext}', caption=ccm)
                            else:
                                # fallback to normal if topic failed
                                copy = await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=ccm)
                        else:
                            copy = await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=ccm)
                        if is_accept_log_enabled():
                            file_id = copy.document.file_id
                            topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                            await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=ccm, message_thread_id=topic_id)
                        count += 1
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        await asyncio.sleep(5)
                        os.remove(f'{name}.{ext}')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue    
           
                elif kalam_download:
                    try:
                        kalam_headers = {
                            "Host": "testing-news.kalampublication.in",
                            "mobilenumber": "aDhYejdQcVIyd0IxazlEZg\u003d\u003d",
                            "range": "bytes=0-",
                            "referer": "https://testing-news.kalampublication.in",
                            "user-agent": "okhttp/4.12.0"
                        }
                        index_remaining_links = end - count
                        index_progress = (count/end) * 100
                        emoji = get_next_emoji()
                        Show1 = f"__**Video Downloading (Kalam)**__\n\u003cblockquote\u003e\u003ci\u003e\u003cb\u003e{str(count).zfill(3)}) {name1}\u003c/i\u003e\u003c/b\u003e\u003c/blockquote\u003e"
                        Show = f"\u003cblockquote\u003e🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%\u003c/blockquote\u003e\n┃\n" \
                                   f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                                   f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                                   f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                                   f"\u003cblockquote\u003e**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**\u003c/blockquote\u003e\n┃\n" \
                                   f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                                   f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » \u003ca href='{batch_link}'\u003e{b_name}\u003c/a\u003e\n" \
                                   f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                                   f"\u003cblockquote\u003e📚𝐓𝐢𝐭𝐥𝐞 » `{name}`\u003c/blockquote\u003e\n┃\n" \
                                   f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                                   f'┣━🔗𝐋𝐢𝐧𝐤 » \u003ca href="{link0}"\u003e**Original Link**\u003c/a\u003e\n┃\n' \
                                   f'╰━━🖇️𝐔𝐫𝐥 » \u003ca href="{url}"\u003e**Api Link**\u003c/a\u003e\n' \
                                   f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                                   f"🛑**Send** /cancel **to stop process**\n┃\n" \
                                   f"\u003cblockquote\u003e✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDITWITHLINK}\u003c/blockquote\u003e"
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                emoji_msg = await bot.send_message(channel_id, emoji, message_thread_id=topic_id)
                                prog1 = await bot.send_message(channel_id, Show1, message_thread_id=topic_id, disable_web_page_preview=True)
                            else:
                                emoji_msg = await bot.send_message(channel_id, emoji)
                                prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                        else:
                            emoji_msg = await bot.send_message(channel_id, emoji)
                            prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                        prog = await bot.send_message(m.chat.id, Show, disable_web_page_preview=True)

                        # Download using aiohttp with kalam headers
                        async with aiohttp.ClientSession(headers=kalam_headers) as session:
                            async with session.get(url) as resp:
                                if resp.status == 200 or resp.status == 206:
                                    video_data = await resp.read()
                                    filename = f"{name}.mp4"
                                    with open(filename, "wb") as f:
                                        f.write(video_data)
                                else:
                                    raise Exception(f"Kalam download failed with status {resp.status}")

                        await prog.delete(True)
                        await prog1.delete(True)
                        await emoji_msg.delete(True)
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                        else:
                            topic_id = None
                        if is_accept_log_enabled():
                            log_topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                            await helper.log_send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, LOG_CHANNEL, log_topic_id, topic_id)
                        else:
                            await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, topic_id)
                        count += 1
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        await asyncio.sleep(5)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue

                elif "youtu" in url:
                    try:
                        yt_thumb = helper.get_yt_thumb(url)
                        BUTTONSYT = InlineKeyboardMarkup([[InlineKeyboardButton(text="🟢 Watch Video 🟢", url=f"{url}")]])
                        if topic == "yes":
                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                            if topic_id:
                                copy = await bot.send_photo(chat_id=channel_id, message_thread_id=topic_id, photo=yt_thumb, caption=ccyt, reply_markup=BUTTONSYT)
                            else:
                                # fallback to normal if topic failed
                                copy = await bot.send_photo(chat_id=channel_id, photo=yt_thumb, caption=ccyt, reply_markup=BUTTONSYT)
                        else:
                            copy = await bot.send_photo(chat_id=channel_id, photo=yt_thumb, caption=ccyt, reply_markup=BUTTONSYT)
                        if is_accept_log_enabled():
                            file_id = copy.photo.file_id
                            topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                            await bot.send_photo(chat_id=LOG_CHANNEL, photo=file_id, caption=ccyt, message_thread_id=topic_id, reply_markup=BUTTONSYT)
                        count += 1
                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                        await asyncio.sleep(5)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        await asyncio.sleep(e.x)
                        continue

                elif ".p1" in url:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                    if "encrypted" in url:
                        # Handle encrypted P1 URLs differently if needed
                        async with aiohttp.ClientSession(headers=headers) as session:
                            async with session.get(url) as response:
                                if response.status == 200:
                                    p1_data = await response.read()
                                    with open(f"{name}.p1", 'wb') as f:
                                        f.write(p1_data)
                                    if topic == "yes":
                                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                        if topic_id:
                                            copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=f'{name}.p1', caption=cc1)
                                        else:
                                            copy = await bot.send_document(chat_id=channel_id, document=f'{name}.p1', caption=cc1)
                                    else:
                                        copy = await bot.send_document(chat_id=channel_id, document=f'{name}.p1', caption=cc1)
                                    if is_accept_log_enabled():
                                        file_id = copy.document.file_id
                                        topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                        await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, message_thread_id=topic_id)
                                    count += 1
                                    session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                                    await asyncio.sleep(5)
                                    os.remove(f'{name}.p1')
                                else:
                                    await m.reply_text(f"Failed to download P1. Status code: {response.status}")
                    else:
                        cmd = f'yt-dlp -o "{name}.p1" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        loop = asyncio.get_running_loop() 
                        await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True))
                        
                        if os.path.exists(f'{name}.p1'):
                            new_name = f'{name}.p1'
                            os.rename(f'{name}.p1', new_name)
                            if topic == "yes":
                                topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                if topic_id:
                                    copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=new_name, caption=cc1)
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=new_name, caption=cc1)
                            else:
                                copy = await bot.send_document(chat_id=channel_id, document=new_name, caption=cc1)
                            if is_accept_log_enabled():
                                file_id = copy.document.file_id
                                topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, message_thread_id=topic_id)
                            count += 1
                            session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                            await asyncio.sleep(5)
                            os.remove(new_name)
                        else:
                            async with aiohttp.ClientSession(headers=headers) as session:
                                async with session.get(url) as response:
                                    if response.status == 200:
                                        p1_data = await response.read()
                                        with open(f"{name}.p1", 'wb') as f:
                                            f.write(p1_data)
                                        if topic == "yes":
                                            topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                                            if topic_id:
                                                copy = await bot.send_document(chat_id=channel_id, message_thread_id=topic_id, document=f'{name}.p1', caption=cc1)
                                            else:
                                                copy = await bot.send_document(chat_id=channel_id, document=f'{name}.p1', caption=cc1)
                                        else:
                                            copy = await bot.send_document(chat_id=channel_id, document=f'{name}.p1', caption=cc1)
                                        if is_accept_log_enabled():
                                            file_id = copy.document.file_id
                                            topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                                            await bot.send_document(chat_id=LOG_CHANNEL, document=file_id, caption=cc1, message_thread_id=topic_id)
                                        count += 1
                                        session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                                        os.remove(f'{name}.p1')
                                        await asyncio.sleep(5)
                                    else:
                                        await m.reply_text(f"Failed to download P1. Status code: {response.status}")
                    await asyncio.sleep(e.x)
                    continue

                elif 'encrypted.m' in url:    
                    index_remaining_links = end - count
                    index_progress = (count/end) * 100
                    emoji = get_next_emoji()
                    #emoji_msg = await bot.send_message(channel_id, emoji)
                    Show1 = f"__**Video Downloading**__\n<blockquote><i><b>{str(count).zfill(3)}) {name1}</i></b></blockquote>" 
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n" \
                               f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                               f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**</blockquote>\n┃\n" \
                               f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                               f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » <a href='{batch_link}'>{b_name}</a>\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » `{name}`</blockquote>\n┃\n" \
                               f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                               f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                               f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"🛑**Send** /cancel **to stop process**\n┃\n" \
                               f"<blockquote>✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDITWITHLINK}</blockquote>"
                    if topic == "yes":
                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                        if topic_id:
                            emoji_msg = await bot.send_message(channel_id, emoji, message_thread_id=topic_id)
                            prog1 = await bot.send_message(channel_id, Show1, message_thread_id=topic_id, disable_web_page_preview=True)
                        else:
                            emoji_msg = await bot.send_message(channel_id, emoji)
                            prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    else:
                        emoji_msg = await bot.send_message(channel_id, emoji)
                        prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
 
                    #prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    prog = await bot.send_message(m.chat.id, Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await prog1.delete(True)  
                    await emoji_msg.delete(True)
                    if topic == "yes":
                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                    else:
                        topic_id = None
                    if is_accept_log_enabled():
                        log_topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                        await helper.log_send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, LOG_CHANNEL, log_topic_id, topic_id)
                    else:
                        await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, topic_id)
                    #await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1  
                    session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                    await asyncio.sleep(5)  
                    continue  

                elif 'drmcdni' in url or 'drm/wv' in url:
                    index_remaining_links = end - count
                    index_progress = (count/end) * 100
                    emoji = get_next_emoji()
                    #emoji_msg = await bot.send_message(channel_id, emoji)
                    Show1 = f"__**Video Downloading**__\n<blockquote><i><b>{str(count).zfill(3)}) {name1}</i></b></blockquote>"    
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n" \
                               f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                               f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**</blockquote>\n┃\n" \
                               f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                               f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » <a href='{batch_link}'>{b_name}</a>\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » `{name}`</blockquote>\n┃\n" \
                               f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                               f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                               f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"🛑**Send** /cancel **to stop process**\n┃\n" \
                               f"<blockquote>✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDITWITHLINK}</blockquote>"
                    if topic == "yes":
                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                        if topic_id:
                            emoji_msg = await bot.send_message(channel_id, emoji, message_thread_id=topic_id)
                            prog1 = await bot.send_message(channel_id, Show1, message_thread_id=topic_id, disable_web_page_preview=True)
                        else:
                            emoji_msg = await bot.send_message(channel_id, emoji)
                            prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    else:
                        emoji_msg = await bot.send_message(channel_id, emoji)
                        prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
 
                    #prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    prog = await bot.send_message(m.chat.id, Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await prog1.delete(True)
                    await emoji_msg.delete(True)
                    if topic == "yes":
                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                    else:
                        topic_id = None
                    if is_accept_log_enabled():
                        log_topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                        await helper.log_send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, LOG_CHANNEL, log_topic_id, topic_id)
                    else:
                        await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, topic_id)
                    #await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1
                    session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                    await asyncio.sleep(5)
                    continue
     
                else:
                    index_remaining_links = end - count
                    index_progress = (count/end) * 100
                    emoji = get_next_emoji()
                    #emoji_msg = await bot.send_message(channel_id, emoji)
                    Show1 = f"__**Video Downloading**__\n<blockquote><i><b>{str(count).zfill(3)}) {name1}</i></b></blockquote>"
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n" \
                               f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                               f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**</blockquote>\n┃\n" \
                               f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                               f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » <a href='{batch_link}'>{b_name}</a>\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » `{name}`</blockquote>\n┃\n" \
                               f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                               f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                               f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"🛑**Send** /cancel **to stop process**\n┃\n" \
                               f"<blockquote>✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ {CREDITWITHLINK}</blockquote>"
                    if topic == "yes":
                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                        if topic_id:
                            emoji_msg = await bot.send_message(channel_id, emoji, message_thread_id=topic_id)
                            prog1 = await bot.send_message(channel_id, Show1, message_thread_id=topic_id, disable_web_page_preview=True)
                        else:
                            emoji_msg = await bot.send_message(channel_id, emoji)
                            prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    else:
                        emoji_msg = await bot.send_message(channel_id, emoji)
                        prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
 
                    #prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await prog1.delete(True)
                    await emoji_msg.delete(True)
                    if topic == "yes":
                        topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                    else:
                        topic_id = None
                    if is_accept_log_enabled():
                        log_topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                        await helper.log_send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, LOG_CHANNEL, log_topic_id, topic_id)
                    else:
                        await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id, topic_id)
                    #await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1
                    session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count}})
                    await asyncio.sleep(5)
                
            except Exception as e:
                if topic == "yes":
                    topic_id = await get_or_create_topic_id(channel_id, t_name, b_name)
                    if topic_id:
                        await bot.send_message(chat_id=channel_id, message_thread_id=topic_id, text=f'⚠️**Downloading Failed**⚠️\n**Name =>>** `{str(count).zfill(3)} {name1}`\n**Url =>>**\n<blockquote expandable>{link0}</blockquote>\n\n<i><b>Failed Reason:</b></i>\n<blockquote>{str(e)}</blockquote>', disable_web_page_preview=True)
                    else:
                        await bot.send_message(chat_id=channel_id, text=f'⚠️**Downloading Failed**⚠️\n**Name =>>** `{str(count).zfill(3)} {name1}`\n**Url =>>**\n<blockquote expandable>{link0}</blockquote>\n\n<i><b>Failed Reason:</b></i>\n<blockquote>{str(e)}</blockquote>', disable_web_page_preview=True)
                else:
                    await bot.send_message(channel_id, f'⚠️**Downloading Failed**⚠️\n**Name =>>** `{str(count).zfill(3)} {name1}`\n**Url =>>**\n<blockquote expandable>{link0}</blockquote>\n\n<i><b>Failed Reason:</b></i>\n<blockquote>{str(e)}</blockquote>', disable_web_page_preview=True)

                if is_accept_log_enabled():
                    topic_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                    await bot.send_message(chat_id=LOG_CHANNEL, text=f'⚠️**Downloading Failed**⚠️\n**Name =>>** `{str(count).zfill(3)} {name1}`\n**Url =>>**\n<blockquote expandable>{link0}</blockquote>\n\n<i><b>Failed Reason:</b></i>\n<blockquote>{str(e)}</blockquote>', message_thread_id=topic_id, disable_web_page_preview=True)
                failed_links.append(f"{name1} : {link0}")
                count += 1
                failed_count += 1
                session_collection.update_one({"_id": f"{user_id}_{b_name}"}, {"$set": {"arg": count, "count": count, "failed_count": failed_count}})
                await asyncio.sleep(5)
                continue

    except Exception as e:
        await m.reply_text(e)
        await asyncio.sleep(5)

    if failed_links:
        error_file_send = await m.reply_text("**📤 Sending you Failed Downloads List **")
        with open("failed_downloads.txt", "w") as f:
           for link in failed_links:
               f.write(link + "\n")
        #After writing to the file, send it
        await m.reply_document(document="failed_downloads.txt", caption=fail_cap)
        await error_file_send.delete()
        failed_links.clear()
        os.remove(f'failed_downloads.txt')

    if raw_text7 == "/d":
        success_count = end - failed_count
        if mode == "/master":
            await bot.send_message(channel_id, f"-┈━═.•°✅ Completed ✅°•.═━┈-\n<blockquote>🎯Batch Name : {b_name}</blockquote>\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n")
            if is_accept_log_enabled():
                thread_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                await bot.send_message(LOG_CHANNEL, f"-┈━═.•°✅ Completed ✅°•.═━┈-\n<blockquote>🎯Batch Name : {b_name}</blockquote>\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n", message_thread_id=thread_id)
        else:
            await bot.send_message(channel_id, f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
            await bot.send_message(channel_id, f"⋅ ─ list index ({arg}-{end}) out of range ─ ⋅\n<blockquote>✨ **BATCH** » {b_name}✨</blockquote>\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
            if is_accept_log_enabled():
                thread_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                await bot.send_message(LOG_CHANNEL, f"⋅ ─ list index ({arg}-{end}) out of range ─ ⋅\n<blockquote>✨ **BATCH** » {b_name}✨</blockquote>\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅", message_thread_id=thread_id)
        
    else:
        success_count = end - failed_count
        if mode == "/master":   
            await bot.send_message(channel_id, f"-┈━═.•°✅ Completed ✅°•.═━┈-\n<blockquote>🎯Batch Name : <a href='{batch_link}'>{b_name}</a></blockquote>\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n")
            if is_accept_log_enabled():
                thread_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                await bot.send_message(LOG_CHANNEL, f"-┈━═.•°✅ Completed ✅°•.═━┈-\n<blockquote>🎯Batch Name : <a href='{batch_link}'>{b_name}</a></blockquote>\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n", message_thread_id=thread_id)
        else:
            await bot.send_message(channel_id, f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
            await bot.send_message(channel_id, f"⋅ ─ list index ({arg}-{end}) out of range ─ ⋅\n<blockquote>✨ **BATCH** » <a href='{batch_link}'>{b_name}</a>✨</blockquote>\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
            if is_accept_log_enabled():
                thread_id = await get_or_create_topic(bot, m, LOG_CHANNEL)
                await bot.send_message(LOG_CHANNEL, f"⋅ ─ list index ({arg}-{end}) out of range ─ ⋅\n<blockquote>✨ **BATCH** » <a href='{batch_link}'>{b_name}</a>✨</blockquote>\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅", message_thread_id=thread_id)
            
        await bot.send_message(m.chat.id, f"<blockquote><b>✅ Your Task is completed, please check your Set Channel📱</b></blockquote>")
        
    user_processing[user_id] = False
    
    if not user_stop_flags.get(user_id, False):
        session_collection.delete_one({"_id": f"{user_id}_{b_name}"})
        await bot.send_message(
            m.chat.id,
            f"<blockquote>🗑️ <b><i>Session</i></b> <code>{b_name}</code> <b><i>has been permanently deleted</i></b> for user <code>{user_id}</code>.</blockquote>\n\n"
            f"<i>▶️ Use fresh commands to start a new session anytime.</i>"
        )
    else:
        await bot.send_message(
            m.chat.id,
            f"<blockquote>⚠️ <b><i>Session</i></b> <code>{b_name}</code> <b><i>has been preserved due to a manual stop request.</i></b></blockquote>\n\n"
            f"<i>🔄 You can resume it anytime using the</i> /restart <i>command.</i>"
        )
        user_stop_flags[user_id] = False

#========================== Switch bot ==========================
@bot.on_callback_query(filters.regex("switch_bot"))
async def switch_callback(client, callback_query):
    user_id = callback_query.from_user.id
    global BOT_INFO

    if BOT_INFO is None:
        me = await client.get_me()
        BOT_INFO = {
            "id": me.id,
            "username": me.username
        }
    users_col.delete_one({"user_id": user_id})
    users_col.insert_one({
        "user_id": user_id,
        "bot_id": BOT_INFO["id"],
        "bot_username": BOT_INFO["username"],
        "joined_at": datetime.utcnow()
    })
    await callback_query.message.edit("✅ You have successfully switched to this bot!")
    
# ================= Notify All Users on Startup ====================
async def notify_all_users_on_startup():
    await asyncio.sleep(25)
    users = get_all_users()
    notified = 0
    msg = (
        "🚀 <b><u>Bot is Live & Operational!</u></b>\n\n"
        "<blockquote expandable>"
        "✨ <i>Welcome back! All systems are running smoothly.</i>\n\n"
        "🔁 <b>/restart</b> — <i>Resume your previous upload session</i>\n"
        "🛑 <b>/cancel</b> — <i>Abort any ongoing task instantly</i>\n"
        "💎 <b>Premium Perks</b> — <i>Lightning-fast access & exclusive features</i>\n\n"
        "🤖 <i>We appreciate having you with us.</i>\n"
        "</blockquote>\n"
    )
    for uid in users:
        try:
            await bot.send_message(uid, msg)
            notified += 1
            await asyncio.sleep(0.2)
        except:
            continue
    print(f"✅ Notified {notified} users that bot is live.")

# ================= Setup Bot Commands ====================
async def setup_bot_commands():
    await asyncio.sleep(25)
    owner_cmds = [
        BotCommand("start", "📡 Check if bot is online & ready"),
        BotCommand("cancel", "⛔ Force-stop your current process"),
        BotCommand("id", "🆔 Get your Telegram User/Chat ID"),
        BotCommand("add", "🎫 Grant Premium Access"),
        BotCommand("rem", "❌ Remove Premium Access"),
        BotCommand("clear", "🧹 Wipe All Premium Users"),
        BotCommand("users", "👥 List of Active Premium Users"),
        BotCommand("myplan", "📃 Your Premium Plan Details"),
        BotCommand("ban", "🚫 Block a user from access"),
        BotCommand("unban", "♻️ Unblock a previously banned user"),
        BotCommand("banned", "📛 List All Banned Users"),
        BotCommand("codes", "🎟️ Generate Redeemable Codes"),
        BotCommand("topics", "🗂️ View All Log Topics"),
        BotCommand("rut", "🔁 Reset Chat Log for User"),
        BotCommand("ract", "🔃 Reset All Log Threads"),
        BotCommand("aml", "🟢 Authorize Logging Access"),
        BotCommand("reset", "🧾 Reset Media Log Records"),
        BotCommand("speed", "🚀 Test File Speed (Upload/Download)"),
        BotCommand("rmt", "🧹 Reset Channel Media Logs"),
        BotCommand("smt", "📂 Show Saved Media Logs"),
        BotCommand("ramt", "💣 Delete All Media Logs"),
        BotCommand("dus", "🗑️ Delete Your Upload Sessions"),
        BotCommand("cas", "💥 Wipe Every User's Session"),
        BotCommand("sessions", "📊 View All Saved Sessions"),
        BotCommand("restart", "🔄 Resume Previous Upload Session"),
        BotCommand("stop", "🔁 Restart the bot completely"),
        BotCommand("broadcast", "📢 Send Message to All Users"),
    ]
    user_cmds = [
        BotCommand("start", "📡 Check if bot is online & ready"),
        BotCommand("cancel", "⛔ Stop your current running task"),
        BotCommand("id", "🆔 View Your Telegram User ID"),
        BotCommand("myplan", "📃 View Your Premium Plan Info"),
        BotCommand("speed", "⚡ Measure Upload/Download Speed"),
        BotCommand("upgrade", "🔼 Upgrade to Premium Membership"),
        BotCommand("dus", "🗑️ Clear Your Upload Session Data"),
        BotCommand("redeem", "🎟️ Redeem a Premium Code"),
        BotCommand("token", "⛔ Reserved for Premium Bots Only"),
        BotCommand("restart", "🔄 Resume Last Saved Upload"),
    ]
    await bot.set_bot_commands(user_cmds, scope=BotCommandScopeDefault())
    await bot.set_bot_commands(owner_cmds, scope=BotCommandScopeChat(chat_id=OWNER_ID))
    print("✅ Bot commands set successfully.")

# ================= Final Bot Runner ====================
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(auto_remove_expired())             # 🔁 Auto expire checker
    loop.create_task(setup_bot_commands())              # ✅ Command setter
    loop.create_task(notify_all_users_on_startup())     # 📢 Startup notifier
    print("🚀 Bot is launching...")
    bot.run()
