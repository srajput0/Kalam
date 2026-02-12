import os
import re
import sys
import m3u8
import json
from datetime import datetime
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
from core import decrypt_file_txt
from utils import progress_bar
from vars import OWNER, AUTH_USERS, LOG_CHANNEL
from vars import API_ID, API_HASH, BOT_TOKEN
from vars import save_user_id, get_all_user_ids, remove_user_id
from vars import cookies_file_path, INSTAGRAM_COOKIES_PATH
from vars import adda_token, token_cp, api_token, api_url
from vars import photozip, photocp, photoyt, photologo
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

#================================================================================================================================
# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

#==============================================================================================================================
# Global variable 
thumb = "/d"
thumb2 = "/d"
CR = "𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎"
my_name = "/d"
extension = "[𝄟⃝‌🐬🇳‌ɪᴋʜɪʟ𝄟⃝🐬](https://t.me/+MdZ2996M2G43MWFl)"
token = None
topic = "/d"
watermark_text = '\n'
mode = "/master"

#================================================================================================================================
def get_time_details(message_time):
    """
    Helper function to calculate message time, current time, time difference, and format them in IST.
    """
    try:
        # Current UTC time
        current_time = datetime.utcnow()

        # Set the timezone to Asia/Kolkata
        kolkata_tz = pytz.timezone('Asia/Kolkata')

        # Convert UTC times to Kolkata time
        message_time_ist = message_time.astimezone(kolkata_tz)
        current_time_ist = current_time.astimezone(kolkata_tz)

        # Calculate the time difference
        time_difference = current_time_ist - message_time_ist

        # Format the times and time difference
        msg_time_formatted = message_time_ist.strftime("%H:%M:%S (IST)")
        cur_time_formatted = current_time_ist.strftime("%H:%M:%S (IST)")
        date_formatted = message_time_ist.strftime("%d-%m-%Y (IST)")
        message_time_formatted = message_time_ist.strftime("%Y-%m-%d %H:%M:%S (IST)")
        current_time_formatted = current_time_ist.strftime("%Y-%m-%d %H:%M:%S (IST)")
        time_difference_formatted = str(time_difference)

        return {
            "msg_time": msg_time_formatted,
            "cur_time": cur_time_formatted,
            "msg_date": date_formatted,
            "message_time": message_time_formatted,
            "current_time": current_time_formatted,
            "time_difference": time_difference_formatted,
            "day": message_time_ist.strftime('%A')
        }
    except Exception as e:
        return {"error": str(e)}


#================================================================================================================================
# Image URLs for the random image feature
image_urls = [
    "https://tinypic.host/images/2025/02/07/IMG_20250207_224444_975.jpg",
    "https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png",
    # Add more image URLs as needed
]
    
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
@bot.on_message(filters.command("start"))
async def start(client: Client, msg: Message):
    user_id = msg.chat.id
    user_list = get_all_user_ids()
    # Check if user ID is already saved in the database
    if user_id not in user_list:
        save_user_id(user_id)  # Save user ID to the database
    user = await bot.get_me()
    mention = user.mention
    random_image = random.choice(image_urls)

    start_message = await client.send_photo(
         chat_id=msg.chat.id,
         photo=random_image,
         caption=Data.START.format(msg.from_user.mention, wish)
    )
    await asyncio.sleep(1)
    await start_message.edit_text(
        "╭━━━━━━━━━━━━━━━━━━━━➣\n"
        "┣⪼ 👋 Welcome {0}!\n"
        "┣⪼ 🚀 Starting DRM Bot...\n"
        "╰━━━━━━━━━━━━━━━━━━━━\n\n"
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
        "╰━━━━━━━━━━━━━━━━━━━━➣\n\n"
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
    if msg.from_user.id in AUTH_USERS:                
        await start_message.edit_text(
            Data.START.format(msg.from_user.mention, wish) +
            "<blockquote>Great! You are a premium member! </blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Commands", callback_data="show_commands"),
                InlineKeyboardButton("✨ Features", callback_data="show_features")],
                [InlineKeyboardButton("🗄️ Settings", callback_data="settings"),
                InlineKeyboardButton("💳 Premium", callback_data="show_plans")],
                [InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot"),
                InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl")],
           ]),
        )
    else:
        await asyncio.sleep(2)
        await start_message.edit_text(
            Data.START.format(msg.from_user.mention, wish) +
            "**You are currently using the free version. 🆓**\n\n"
            "I'm here to make your life easier by downloading videos from your **.txt** file 📄 and uploading them directly to Telegram!\n\n"
            "Want to get started? Press /id\n\n<blockquote>💬 Contact [𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎](https://t.me/saini_contact_bot) to Get The Subscription 🎫 and unlock the full potential of your new bot! 🔓</blockquote>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✨ Commands", callback_data="show_commands"),
                InlineKeyboardButton("✨ Features", callback_data="show_features")],
                [InlineKeyboardButton("🗄️ Settings", callback_data="settings"),
                InlineKeyboardButton("💳 Premium", callback_data="show_plans")],
                [InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot"),
                InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl")],
          ]),
    )
    
#================================================================================================================================
@bot.on_callback_query(filters.regex("back_to_main"))
async def back_to_main(client, callback_query):
    await callback_query.message.edit_text(
        Data.START.format(callback_query.from_user.mention, wish) +
        "<blockquote>You are currently using the 𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎. </blockquote>\n",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Commands", callback_data="show_commands"),
            InlineKeyboardButton("✨ Features", callback_data="show_features")],
            [InlineKeyboardButton("🗄️ Settings", callback_data="settings"),
            InlineKeyboardButton("💳 Premium", callback_data="show_plans")],
            [InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot"),
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl")],
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
        [InlineKeyboardButton("Chat ID", callback_data="id"),
        InlineKeyboardButton("Info", callback_data="info")],
        [InlineKeyboardButton("YouTube", callback_data="youtube"),
        InlineKeyboardButton("Text 2 .txt", callback_data="t2t")],
        [InlineKeyboardButton("Edit .txt", callback_data="e2t"),
        InlineKeyboardButton("Title Clean", callback_data="title")],
        [InlineKeyboardButton("Cookies", callback_data="cookies"),
         InlineKeyboardButton("Helper Dec", callback_data="helper")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle the feature button press
@bot.on_callback_query(filters.regex("show_features"))
async def show_features(client, callback_query):
    text = "<blockquote>✨ **My Premium BOT Features:**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📌 Auto Pin", callback_data="feature_1"),
        InlineKeyboardButton("📂 2GB+ File", callback_data="feature_2")],
        [InlineKeyboardButton("🤖 Txt Operation", callback_data="feature_3"),
        InlineKeyboardButton("Name&Caption", callback_data="feature_4")],
        [InlineKeyboardButton("Thumb&Wtrmark", callback_data="feature_5"),
        InlineKeyboardButton("Index Range", callback_data="feature_6")],
        [InlineKeyboardButton("Channel ID", callback_data="feature_7"),
        InlineKeyboardButton("🚦 Other", callback_data="feature_8")],
        [InlineKeyboardButton("🔙 Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle the settings button press
@bot.on_callback_query(filters.regex("settings"))
async def show_features(client, callback_query):
    text = "<blockquote>✨ **My Premium BOT Settings:**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Vid Thumb", callback_data="vthumb"),
        InlineKeyboardButton("Pdf Thumb", callback_data="pthumb")],
        [InlineKeyboardButton("Credit", callback_data="credit"),
        InlineKeyboardButton("Extension", callback_data="extension")],
        [InlineKeyboardButton("File Name", callback_data="myname"),
        InlineKeyboardButton("Token", callback_data="token")],
        [InlineKeyboardButton("Topic", callback_data="topic"),
        InlineKeyboardButton("Pdf 💦", callback_data="pwatermark")],
        [InlineKeyboardButton("Mode", callback_data="mode"),
        InlineKeyboardButton("🔙 Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle the settings button press
@bot.on_callback_query(filters.regex("cookies"))
async def show_features(client, callback_query):
    text = "<blockquote>✨ **Update YouTube & Instagram Cookies:**</blockquote>"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("YouTube", callback_data="ytcookies"),
        InlineKeyboardButton("Instagram", callback_data="igcookies")],
        [InlineKeyboardButton("🔙 Back", callback_data="show_commands")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#================================================================================================================================
# Handle Premium Plans button press
@bot.on_callback_query(filters.regex("show_plans"))
async def show_plans(client, callback_query):
    text = (
        "<blockquote>**Here are the pricing details for SAINI DRM Bot:**</blockquote>\n\n"
        "🗓️ **Subscription Duration & Price:**\n"
        "<blockquote>1 Day ➠ ₹XX 💰\n"
        "10 Days ➠ ₹XXX 💵\n"
        "30 Days ➠ ₹XXX 💴</blockquote>\n\n"
        "📑 **Supported Apps and Links:**\n\n"
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
        "<blockquote>Register Your Bots Now : [𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎](https://t.me/saini_contact_bot)</blockquote>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 1
@bot.on_callback_query(filters.regex("feature_1"))
async def feature(client, callback_query):
    text = "<blockquote>**📌 Auto Pin Batch Name**</blockquote>\n\nAutomatically Pins the Batch Name"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 2
@bot.on_callback_query(filters.regex("feature_2"))
async def feature(client, callback_query):
    text = "<blockquote>**📂 2GB+ File Supported:**</blockquote>\n\nSupports large files over 2GB, automatically splitting into parts."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 3
@bot.on_callback_query(filters.regex("feature_3"))
async def feature(client, callback_query):
    text = (
        "<blockquote>**🤖 Txt Operation:**</blockquote>\n\n"
        "Convert YouTube URL to .txt\n\n"
        "Remove extra parentheses\n\n"
        "Text to .txt\n\n"
        "Edit txt in alphabetically\n\n"
        "Bot working logs\n\n"
        "Remove extra parentheses\n\n"
        "Update Yt & IG cookies\n\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 4
@bot.on_callback_query(filters.regex("feature_4"))
async def feature(client, callback_query):
    text = (
        "<blockquote>Example for 🖋️ Custom Name Before File Extension :</blockquote>\n"
        "Support for Custom Name before the File Extension.\n\n"
        "<blockquote>Caption</blockquote>\n"
        "Support Master and Megatron Caption\n\n"
        "<blockquote>Use the Setting Pannel in Bots.</blockquote>\n\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 5
@bot.on_callback_query(filters.regex("feature_5"))
async def feature(client, callback_query):
    text = (
        "<blockquote>Video & Pdf Thumbnail Support\n💦 Pdf Watermark also Support</blockquote>\n\n"
        "Use the Setting Pannel in Bots.\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 6
@bot.on_callback_query(filters.regex("feature_6"))
async def feature(client, callback_query):
    text = (
        "<blockquote>Index Range</blockquote>\n\n"
        "Download Index seperate by (-)\n"
        "You can also share 1st downloadable link"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 7
@bot.on_callback_query(filters.regex("feature_7"))
async def feature(client, callback_query):
    text = (
        "<blockquote>Channel ID</blockquote>\n\n"
        "Bot direct send document and video in Channel\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#=============================================================================================================================
# Feature 8
@bot.on_callback_query(filters.regex("feature_8"))
async def feature(client, callback_query):
    text = (
        "<blockquote>Other features</blockquote>\n\n"
        "After txt complete extract or given command /stop : Bot send failed list of link\n\n"
        "Broadcasting any text & media\n"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Features", callback_data="show_features")]
    ])
    await callback_query.message.edit(text, reply_markup=keyboard)

#==============================================================================================================================
# Handle the Video Thumbnail button press
@bot.on_callback_query(filters.regex("vthumb"))
async def handle_vthumb(client, callback_query):
    global thumb  # Access global thumbnail variable
    # Simulate the /vthumb command logic
    editable = await callback_query.message.reply_text(f"Send the Video Thumb URL (e.g., https://envs.sh/GV0.jpg) for default thumbnail /d \n\n<blockquote><i>You can direct upload thumb\nFor document format send : No</i></blockquote>", disable_web_page_preview=True)
    input_msg = await bot.listen(editable.chat.id)

    try:
        # Handle uploaded photo
        if input_msg.photo:
            thumb = await input_msg.download()  # Download the uploaded photo
            await editable.reply("✅ Thumbnail set successfully as an uploaded photo!")

        # Handle URL
        elif input_msg.text.startswith("http://") or input_msg.text.startswith("https://"):
            getstatusoutput(f"wget '{input_msg.text}' -O 'thumb.jpg'")
            thumb = "thumb.jpg"
            await editable.reply("✅ Thumbnail set successfully from the URL!")

        # Handle `/d` for default thumbnail
        elif input_msg.text.lower() == "/d":
            thumb = "/d"  # Set the thumbnail to `/d`
            await editable.reply("✅ Thumbnail set to default (`/d`)!")

        # Handle `No` to disable the thumbnail
        elif input_msg.text == "No":
            thumb = "No"  # Set the thumbnail to `No`
            await editable.reply("✅ Thumbnail disabled (`No`)!")

        # Invalid input
        else:
            await editable.reply("❌ Invalid input. Please upload a photo, send a URL, `/d`, or `No`.")
    except Exception as e:
        await editable.reply(f"❌ Failed to set thumbnail. Error: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("pthumb"))
async def handle_pthumb(client, callback_query):
    global thumb2  # Access global thumbnail variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send the PDF Thumb URL (e.g., https://envs.sh/GVI.jpg) for default Send /d",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)

    try:
        # Handle uploaded photo
        if input_msg.photo:
            thumb2 = await input_msg.download()  # Download the uploaded photo
            await editable.reply("✅ Thumbnail set successfully as an uploaded photo!")

        # Handle URL
        elif input_msg.text.startswith("http://") or input_msg.text.startswith("https://"):
            getstatusoutput(f"wget '{input_msg.text}' -O 'thumb2.jpg'")
            thumb2 = "thumb2.jpg"
            await editable.reply("✅ Thumbnail set successfully from the URL!")

        # Handle `/d` for default thumbnail
        elif input_msg.text.lower() == "/d":
            thumb2 = "/d"  # Set the thumbnail disabled to `/d`
            await editable.reply("✅ Thumbnail disabled !")

        # Invalid input
        else:
            await editable.reply("❌ Invalid input. Please upload a photo, send a URL, `/d`, or `No`.")
    except Exception as e:
        await editable.reply(f"❌ Failed to set thumbnail. Error: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("credit"))
async def handle_credit(client, callback_query):
    global CR  # Access global thumbnail variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send the Credit Name, for default Send /d",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            CR = '[𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)'
            await editable.reply("✅ Credit set successfully as default!")
        else:
            CR = input_msg.text
            await editable.reply("✅ Credit set successfully !")
            
    except Exception as e:
        await editable.reply(f"❌ Failed to set Credit. Error: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("extension"))
async def handle_extension(client, callback_query):
    global extension  # Access global thumbnail variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send the extension Name for Megatron Caption, for default Send /d",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            extension = '[𝄟⃝‌🐬🇳‌ɪᴋʜɪʟ𝄟⃝🐬](https://t.me/+MdZ2996M2G43MWFl)'
            await editable.reply("✅ Extension set successfully as default!")
        else:
            extension = input_msg.text
            await editable.reply("✅ Extension set successfully !")
            
    except Exception as e:
        await editable.reply(f"❌ Failed to set Extension.\nError: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("myname"))
async def handle_myname(client, callback_query):
    global my_name  # Access global thumbnail variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send the End File Name, else Send /d",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            await editable.reply("✅ End File Name disabled successfully!")
        else:
            my_name = input_msg.text
            await editable.reply("✅ End File Name set successfully !")
            
    except Exception as e:
        await editable.reply(f"❌ Failed to set End file name.\nError: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()
        
#==============================================================================================================================
@bot.on_callback_query(filters.regex("token"))
async def handle_token(client, callback_query):
    global token  # Access global token variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send PW token for processing PW .txt file",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    token = input_msg.text
    await editable.reply("✅ Token update successfully !")
    await input_msg.delete()
    await editable.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("topic"))
async def handle_topic(client, callback_query):
    global topic  # Access global topic variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "__🔹If you want to add topic feature : Send `yes`, for default Send /d__\n\n<blockquote><i>Title fetched from (title) this bracket</i></blockquote>",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "yes":
            topic = 'yes'
            await editable.reply("✅ Topic enabled successfully!")
        else:
            topic = input_msg.text
            await editable.reply("✅ Topic disabled successfully !")
            
    except Exception as e:
        await editable.reply(f"❌ Failed to set Topic.\nError: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()

#==============================================================================================================================
@bot.on_callback_query(filters.regex("pwatermark"))
async def handle_pwatermark(client, callback_query):
    global watermark_text  # Access global topic variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send pdf 💦 watermark text else send /d",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            watermark_text = '\n'
            await editable.reply("✅ Pdf Watermark disabled successfully!")
        else:
            watermark_text = input_msg.text + '\n'
            await editable.reply("✅ Pdf Watermark enabled successfully !")
            
    except Exception as e:
        await editable.reply(f"❌ Failed to set Pdf Watermark.\nError: {str(e)}")
    finally:
        await input_msg.delete()
        await editable.delete()


#==============================================================================================================================
@bot.on_callback_query(filters.regex("mode"))
async def handle_mode(client, callback_query):
    global mode  # Access global mode variable
    # Prompt the user for a thumbnail input
    editable = await callback_query.message.reply_text(
        "Send /master for Master Caption\nSend /megatron for Megatron Caption",
        disable_web_page_preview=True
    )
    input_msg = await bot.listen(editable.chat.id)
    mode = input_msg.text
    await editable.reply("✅ Caption mode update successfully !")
    await input_msg.delete()
    await editable.delete()

        
#================================================================================================================================
@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")
    
#=========================================================================================================================
@bot.on_callback_query(filters.regex("id"))
async def id_command(client, callback_query):
    chat_id = callback_query.message.chat.id
    await callback_query.message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")

#====================================================================================================================================
@bot.on_callback_query(filters.regex("info"))
async def info_command(client, callback_query):
    
    user = callback_query.from_user
    name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    username = f"@{user.username}" if user.username else "No Username"
    
    text = (
        f"╭────────────────╮\n"
        f"│✨ **__Your Telegram Info__**✨ \n"
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
        # Prompt the user to send a text file
        await callback_query.message.reply_text("**Send me the `helper://` encrypted .txt file to decrypt.**")
        input_message = await client.listen(callback_query.message.chat.id)  # Corrected reference
        input_file = await input_message.download()  # Download the file

        # Decrypt the file
        decrypted_file = decrypt_file_txt(input_file)
        await callback_query.message.reply_text(f"**File decrypted successfully: {decrypted_file}**")

        # Send the decrypted file back to the user
        await client.send_document(
            chat_id=callback_query.message.chat.id,
            document=decrypted_file,
            caption="Here is your decrypted file."
        )

    except Exception as e:
        await callback_query.message.reply_text(f"An error occurred: {str(e)}")
#================================================================================================================================
@bot.on_message(filters.command("addauth") & filters.private)
async def add_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        new_user_id = int(message.command[1])
        if new_user_id in AUTH_USERS:
            await message.reply_text("User ID is already authorized.")
        else:
            AUTH_USERS.append(new_user_id)
            # Update the environment variable (if needed)
            os.environ['AUTH_USERS'] = ','.join(map(str, AUTH_USERS))
            await message.reply_text(f"User ID {new_user_id} added to authorized users.")
            await bot.send_message(chat_id=new_user_id, text=
                f" 🎉 Welcome to Non-DRM Bot! 🎉\n\n"
                f"• Use Command : /help to get started 🌟\n\n"
                f"You can have access to download all Non-DRM+AES Encrypted URLs 🔐 including\n\n"
                f"<blockquote>• 📚 Appx Zip+Encrypted Url\n"
                f"• 🎓 Classplus DRM+ NDRM\n"
                f"• 🧑‍🏫 PhysicsWallah DRM\n"
                f"• 📚 CareerWill + PDF\n"
                f"• 🎓 Khan GS\n"
                f"• 🎓 Study Iq DRM\n"
                f"• 🚀 APPX + APPX Enc PDF\n"
                f"• 🎓 Vimeo Protection\n"
                f"• 🎓 Brightcove Protection\n"
                f"• 🎓 Visionias Protection\n"
                f"• 🎓 Zoom Video\n"
                f"• 🎓 Utkarsh Protection(Video + PDF)\n"
                f"• 🎓 All Non DRM+AES Encrypted URLs\n"
                f"• 🎓 MPD URLs if the key is known (e.g., Mpd_url?key=key XX:XX)</blockquote>\n\n"
                f"You are now authorized user.\n\n"
                f"Enjoy premium features!", disable_web_page_preview=True, reply_markup=keyboard 
            )
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")

#================================================================================================================================
@bot.on_message(filters.command("users") & filters.private)
async def list_auth_users(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")

    try:
        # Fetch authorized users from AUTH_USERS
        auth_user_list = '\n'.join(map(str, AUTH_USERS))  # AUTH_USERS is an in-memory list

        # Fetch all users from persistent storage (get_all_user_ids)
        total_user_list = '\n'.join(map(str, get_all_user_ids()))  # Assuming this fetches all users from storage

        # Send the lists to the chat
        await message.reply_text(f"👥 **Authorized Users:**\n{auth_user_list}")
        await message.reply_text(f"🌍 **Total Users:**\n{total_user_list}")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
        
#================================================================================================================================
@bot.on_message(filters.command("broadcast") & filters.private)
async def broadcast_message(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")

    await message.reply_text("Please provide the content to broadcast (text, photo, video, or document).")

    try:
        input_message: Message = await client.listen(message.chat.id)

        if input_message.text:
            broadcast_content = input_message.text
            broadcast_type = "text"
        elif input_message.photo:
            broadcast_content = input_message.photo.file_id
            broadcast_type = "photo"
        elif input_message.video:
            broadcast_content = input_message.video.file_id
            broadcast_type = "video"
        elif input_message.document:
            broadcast_content = input_message.document.file_id
            broadcast_type = "document"
        else:
            return await message.reply_text("Invalid content type. Please provide text, photo, video, or document.")

        user_ids = get_all_user_ids()  # Get all user IDs from MongoDB
        success_count = 0
        failure_count = 0

        # Send the broadcast message to each user
        for user_id in user_ids:
            try:
                if broadcast_type == "text":
                    await client.send_message(chat_id=user_id, text=broadcast_content)
                elif broadcast_type == "photo":
                    await client.send_photo(chat_id=user_id, photo=broadcast_content)
                elif broadcast_type == "video":
                    await client.send_video(chat_id=user_id, video=broadcast_content)
                elif broadcast_type == "document":
                    await client.send_document(chat_id=user_id, document=broadcast_content)
                success_count += 1
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")
                failure_count += 1

        await message.reply_text(f"Broadcast message has been sent to {success_count} users successfully. Failed to send to {failure_count} users.")

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

#================================================================================================================================
@bot.on_message(filters.command("rmauth") & filters.private)
async def remove_auth_user(client: Client, message: Message):
    if message.chat.id != OWNER:
        return await message.reply_text("You are not authorized to use this command.")
    
    try:
        user_id_to_remove = int(message.command[1])
        if user_id_to_remove not in AUTH_USERS:
            await message.reply_text("User ID is not in the authorized users list.")
        else:
            AUTH_USERS.remove(user_id_to_remove)
            # Update the environment variable (if needed)
            os.environ['AUTH_USERS'] = ','.join(map(str, AUTH_USERS))
            await message.reply_text(f"User ID {user_id_to_remove} removed from authorized users.")
            await bot.send_message(chat_id=user_id_to_remove, text=f"Your are removed from authorisation. Now you are free user")
    except (IndexError, ValueError):
        await message.reply_text("Please provide a valid user ID.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

#================================================================================================================================
@bot.on_callback_query(filters.regex("ytcookies"))
async def handle_cookies(client, callback_query):
    editable = await callback_query.message.reply_text(
        "Please upload the cookies file (.txt format).",
        disable_web_page_preview=True
    )

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(editable.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await callback_query.message.reply_text("Invalid file type. Please upload a .txt file.")
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await callback_query.message.reply_text(f"⚠️ An error occurred: {str(e)}")


#===================================================================================================================================
@bot.on_callback_query(filters.regex("igcookies"))
async def handle_cookies(client, callback_query):
    editable = await callback_query.message.reply_text(
        "📂 Please upload the Instagram cookies file in .txt format. 📄",
        quote=True
    )
    try:
        input_message: Message = await client.listen(editable.chat.id)
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await callback_query.message.reply_text("❌ Invalid file type. Please upload a .txt file.")
            return
        cookies_path = await input_message.download(file_name=INSTAGRAM_COOKIES_PATH)
        with open(cookies_path, 'r') as file:
            cookies_data = file.read()  # Read the cookies data
        with open(INSTAGRAM_COOKIES_PATH, 'w') as file:
            file.write(cookies_data)  # Overwrite the old cookies with new data
        await input_message.reply_text(
            f"✅ Cookies updated successfully.\n📂 Saved at: `{INSTAGRAM_COOKIES_PATH}`"
        )
    except Exception as e:
        await callback_query.message.reply_text(f"⚠️ An error occurred: {str(e)}")    

#===================================================================================================================================
@bot.on_callback_query(filters.regex("t2t"))
async def handle_text(client, callback_query):
    editable = await callback_query.message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(editable.chat.id)
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()  # Corrected here
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(editable.chat.id)
    raw_textn = inputn.text
    await inputn.delete()  # Corrected here
    await editable.delete()

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
    editable = await callback_query.message.reply_text(f"<blockquote>Welcome to the .txt File Editor!\nSend your `.txt` file containing subjects, links, and topics.</blockquote>")
    input_message: Message = await bot.listen(editable.chat.id)
    if not input_message.document:
        await callback_query.message.reply_text("**🚨Upload a valid `.txt` file.**")
        return
    file_name = input_message.document.file_name
    uploaded_file_path = os.path.join(UPLOAD_FOLDER, file_name)
    uploaded_file = await input_message.download(uploaded_file_path)

    await input_message.delete(True)
    await editable.delete(True)

    try:
        with open(uploaded_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
    except Exception as e:
        await callback_query.message.reply_text(f"🚨 **Error**: Unable to read the file.\n\nDetails: {e}")
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
        await callback_query.message.reply_text(f"🚨 **Error**: Unable to write the edited file.\n\nDetails: {e}")
        return

    # Send the sorted and edited file back to the user
    try:
        await client.send_document(
            chat_id=callback_query.message.chat.id,
            document=final_file_path,
            caption="**Your edited .txt file with subjects, links, and topics sorted alphabetically!**"
        )
    except Exception as e:
        await callback_query.message.reply_text(f"🚨 **Error**: Unable to send the file.\n\nDetails: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)  


#===================================================================================================================================
@bot.on_callback_query(filters.regex("title"))
async def handle_title(client, callback_query):
    editable = await callback_query.message.reply_text("**Send Your .txt file with links for ✂️ Remove extra parentheses**\n")
    input: Message = await bot.listen(editable.chat.id)
    txt_file = await input.download()
    await input.delete(True)
    await editable.delete()
      
    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    cleaned_lines = [line.replace('(', '').replace(')', '').replace('_', ' ') for line in lines]
      
    cleaned_txt_file = os.path.splitext(txt_file)[0] + '_cleaned.txt'
    with open(cleaned_txt_file, 'w') as f:
        f.write(''.join(cleaned_lines))
      
    await client.send_document(chat_id=callback_query.message.chat.id, document=cleaned_txt_file,caption="Here is your cleaned txt file.")
    os.remove(cleaned_txt_file)

def process_links(links):
    processed_links = []
    
    for link in links.splitlines():
        if "m3u8" in link:
            processed_links.append(link)
        elif "mpd" in link:
            # Remove everything after and including '*'
            processed_links.append(re.sub(r'\*.*', '', link))
    
    return "\n".join(processed_links)

#===================================================================================================================================
@bot.on_callback_query(filters.regex("youtube"))
async def handle_youtube(client, callback_query):
    editable = await callback_query.message.reply_text(
        f"<blockquote>Send YouTube Website/Playlist link for convert in .txt file</blockquote>"
    )
    input_message: Message = await bot.listen(editable.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete(True)
    await editable.delete(True)

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
            await callback_query.message.reply_text(
                f"<pre><code>🚨 Error occurred {str(e)}</code></pre>"
            )
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
    
#===================================================================================================================================


#===========================================================================================================================
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):  # Correct parameter name
    if m.chat.id != OWNER:  # Use `m` instead of `message`
        return await m.reply_text("You are not authorized to use this command.")
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

#================================================================================================================================
@bot.on_message(filters.command(["stop"]) )
async def restart_handler(_, m):
    if m.chat.id not in AUTH_USERS:
        print(f"User ID not in AUTH_USERS", m.chat.id)
        await bot.send_message(
            m.chat.id, 
            f"<blockquote>__**Oopss! You are not a Premium member**__\n"
            f"__**PLEASE UPGRADE YOUR PLAN**__\n"
            f"__**Send me your user id for authorization**__\n"
            f"__**Your User id** __- `{m.chat.id}`</blockquote>\n\n"
        )
    else:
        if failed_links:
            error_file_send = await m.reply_text("**📤 Sending your Failed Downloads List Before Stoping   **")
            with open("failed_downloads.txt", "w") as f:
               for link in failed_links:
                 f.write(link + "\n")
        # After writing to the file, send it
            await m.reply_document(document="failed_downloads.txt", caption=fail_cap)
            await error_file_send.delete()
            os.remove(f'failed_downloads.txt')
            failed_links.clear()
            processing_request = False  # Reset the processing flag
            await m.reply_text("🚦**STOPPED**🚦", True)
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            processing_request = False  # Reset the processing flag
            await m.reply_text("🚦**STOPPED**🚦", True)
            os.execl(sys.executable, sys.executable, *sys.argv)

#================================================================================================================================
@bot.on_message(filters.command(["drm"]) & filters.private)
async def txt_handler(bot: Client, m: Message):
    global thumb  # Access the global video thumbnail set by /vthumb
    global thumb2  # Access the global pdf thumbnail set by /pthumb
    global CR # Access the global credit set by /credit
    global my_name
    global extension
    global watermark_text
    global mode
    global token # specially for pw
    time_details = get_time_details(m.date)

    if m.from_user.is_bot:
        return
    editable = await m.reply_text(f"__Hii, I am non-drm Downloader Bot__\n<blockquote><i>Send Me Your txt file or text which enclude Name with url...\nE.g: Name: Link</i></blockquote>")
    input: Message = await bot.listen(editable.chat.id, filters=filters.user(m.from_user.id))
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

        path = f"./downloads/{m.chat.id}"
        pdf_count = 0
        img_count = 0
        zip_count = 0
        mpd_count = 0
        m3u8_count = 0
        youtu_count = 0
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
                    elif "youtu" in url:
                        youtu_count += 1
                    elif ".zip" in url:
                        zip_count += 1
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
                elif "youtu" in url:
                    youtu_count += 1
                elif ".zip" in url:
                    zip_count += 1
                else:
                    other_count += 1

    await editable.edit(f"**🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}\n🔹PDF : {pdf_count}\n🔹mpd : {mpd_count}\n🔹m3u8 : {m3u8_count}\n🔹ZIP : {zip_count}\n🔹YouTube : {youtu_count}\n🔹Other : {other_count}\n\n🔹Send download index seperate by (-)\n🔹Send From where you want to download**")
    if m.chat.id not in AUTH_USERS:
            print(f"User ID not in AUTH_USERS", m.chat.id)
            await bot.send_message(m.chat.id, f"<blockquote>__**Oopss! You are not a Premium member** __\n__**PLEASE UPGRADE YOUR PLAN**__\n__**Send me your user id for authorization**__\n__**Your User id**__ - `{m.chat.id}`</blockquote>\n")
            return
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
    try:
        batch_message = await bot.send_message(chat_id=channel_id, text=f"<blockquote><b>🎯Target Batch : {b_name}</b></blockquote>")
    except Exception as e:
        await m.reply_text(f"**Fail Reason »**\n<blockquote><i>{e}</i></blockquote>\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ `🌟『𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎』🌟`")
        return

    try:
        if raw_text7 == "/d":
            batch_link = None            
        else:
            await bot.send_message(chat_id=m.chat.id, text=f"<blockquote><b><i>🎯Target Batch : {b_name}</i></b></blockquote>\n\n🔄 Your Task is under processing, please check your Set Channel📱. Once your task is complete, I will inform you 📩")
            await bot.pin_chat_message(channel_id, batch_message.id)
            batch_link = batch_message.link
            message_id = batch_message.id 
            pinning_message_id = message_id + 1
            await bot.delete_messages(channel_id, pinning_message_id)
    except Exception as e:
        await m.reply_text(f"**Fail Reason »**\n<blockquote><i>{e}</i></blockquote>\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ `🌟『𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎』🌟`")

    if "-" in raw_text:
        arg, end = raw_text.split("-")
        try:
            arg = int(arg)
            end = int(end)
            failed_count = 0
            counti = 0
            count = int(arg)   
        except ValueError:
            await editable.edit("__Invalid range provided.__")
    else:
        try:
            arg = int(raw_text)
            end = len(links)
            failed_count = 0
            counti = 0
            count = int(raw_text)
        except ValueError:
            await editable.edit("__Invalid input provided.__")

    try:
        for i in range(arg-1, end):
            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy

            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
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
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "tencdn.classplusapp" in url:
                headers = {'Host': 'api.classplusapp.com', 'x-access-token': f'{token_cp}', 'user-agent': 'Mobile-Android', 'app-version': '1.4.37.1', 'api-version': '18', 'device-id': '5d0d17ac8b3c9f51', 'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30', 'accept-encoding': 'gzip'}
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{token_cp}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = { 'x-access-token': f'{token_cp}',"X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url   = response.json()['url']
                                                        
            elif "childId" in url and "parentId" in url:
                url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                           
            elif "d1d34p8vz63oiq" in url or "sec1.pw.live" in url:
                vid_id =  url.split('/')[-2]
                #url = f"https://pwplayer-38c1ae95b681.herokuapp.com/pw?url={url}&token={raw_text4}"
                url = f"https://anonymouspwplayer-b99f57957198.herokuapp.com/pw?url={url}?token={raw_text4}"
                #url =  f"{api_url}pw-dl?url={url}&token={raw_text4}&authorization={api_token}&q={raw_text2}"
                #url = f"https://dl.alphacbse.site/download/{vid_id}/master.m3u8"
            
            if 'sec-prod-mediacdn.pw.live' in url:
                vid_id = url.split("sec-prod-mediacdn.pw.live/")[1].split("/")[0]
                url = f"https://pwplayer-0e2dbbdc0989.herokuapp.com/player?url=https://d1d34p8vz63oiq.cloudfront.net/{vid_id}/master.mpd?token={raw_text4}"

           # if ".pdf*" in url:
            #    url = f"https://dragoapi.vercel.app/pdf/{url}"
            if ".zip" in url:
                url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"
                
            elif 'encrypted.m' in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

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
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
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
                if "/reel/" in url or "/p/" in url or "/tv/" in url:
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
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:                                 
                if topic == "yes":
                    # Check the format of the link to extract video name and topic name accordingly
                    if links[i][0].startswith("("):
                        # Extract the topic name for format: (TOPIC) Video Name:URL
                        t_name = re.search(r"\((.*?)\)", links[i][0]).group(1).strip().upper()
                        v_name = re.search(r"\)\s*(.*?):", links[i][0]).group(1).strip()
                    else:
                        # Extract the topic name for format: Video Name (TOPIC):URL
                        t_name = re.search(r"\((.*?)\)", links[i][0]).group(1).strip().upper()
                        v_name = links[i][0].split("(", 1)[0].strip()

                    if mode == "/master":
                        cc = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{v_name} [{res}p] .mkv`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cc1 = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[📕]Pdf Id : {str(count).zfill(3)}\n**File Title :** `{v_name} .pdf`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cczip = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[📁]Zip Id : {str(count).zfill(3)}\n**Zip Title :** `{v_name} .zip`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n' 
                        ccimg = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[🖼️]Img Id : {str(count).zfill(3)}\n**Img Title :** `{v_name} .jpg`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cchtml = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[🌐]Html Id : {str(count).zfill(3)}\n**Html Title :** `{v_name} .html`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccyt = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{v_name} .mp4`\n<a href="{url}">__**Click Here to Watch Stream**__</a>\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccm = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n[🎵]Mp3 Id : {str(count).zfill(3)}\n**Mp3 Title :** `{v_name} .mp3`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n' 
                    else:
                        cc = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🎞️ Title :** `{v_name}`\n**├── Extention :**  {extension} .mkv\n**├── Resolution :** `[{res}]`\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cc1 = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**📁 Title :** `{v_name}`\n**├── Extention :**  {extension} .pdf\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cczip = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**📁 Title :** `{v_name}`\n**├── Extention :**  {extension} .zip\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccimg = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🖼️ Title :** `{v_name}`\n**├── Extention :**  {extension} .jpg\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccyt = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**📁 Title :** `{v_name}`\n**├── Extention :**  {extension} .mkv\n\n<a href="{link0}">__Click Here to Watch Stream**__</a>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccm = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🎵 Title :** `{v_name}`\n**├── Extention :**  {extension} .mp3\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cchtml = f'⋅ ─  ✨`{t_name}`✨  ─ ⋅\n\n**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🌐 Title :** `{v_name}`\n**├── Extention :**  {extension} .mp4\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
           
                else:
                    if mode == "/master":
                        cc = f'[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{name1} [{res}p] .mkv`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cc1 = f'[📕]Pdf Id : {str(count).zfill(3)}\n**File Title :** `{name1} .pdf`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cczip = f'[📁]Zip Id : {str(count).zfill(3)}\n**Zip Title :** `{name1} .zip`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n' 
                        ccimg = f'[🖼️]Img Id : {str(count).zfill(3)}\n**Img Title :** `{name1} .jpg`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        cchtml = f'[🌐]Html Id : {str(count).zfill(3)}\n**Html Title :** `{name1} .html`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccyt = f'[🎥]Vid Id : {str(count).zfill(3)}\n**Video Title :** `{name1} .mp4`\n<a href="{url}">__**Click Here to Watch Stream**__</a>\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                        ccm = f'[🎵]Mp3 Id : {str(count).zfill(3)}\n**Mp3 Title :** `{name1} .mp3`\n<blockquote><b>Batch Name : {b_name}</b></blockquote>\n\n**Extracted by➤**{CR}\n'
                    else:
                        cc = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🎞️ Title :** `{name1}`\n**├── Extention :**  {extension} .mkv\n**├── Resolution :** `[{res}]`\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cc1 = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {extension} .pdf\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cczip = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {extension} .zip\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccimg = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🖼️ Title :** `{name1}`\n**├── Extention :**  {extension} .jpg\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccyt = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {extension} .mkv\n\n<a href="{link0}">__**Click Here to Watch Stream**__</a>\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        ccm = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🎵 Title :** `{name1}`\n**├── Extention :**  {extension} .mp3\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                        cchtml = f'**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n**🌐 Title :** `{name1}`\n**├── Extention :**  {extension} .html\n\n<blockquote><b>📚 Course : {b_name}</b></blockquote>\n\n**🌟 Extracted By :** {CR}\n'
                            
                  
                if "drive" in url:
                    reply = await bot.send_message(channel_id, f"__**⚡️ Pdf Downloading...⏳**__\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                    ka = await helper.download(url, name)
                    start_time = time.time()
                    time.sleep(1)
                    copy = await bot.send_document(chat_id=channel_id,document=ka, caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                    await reply.delete (True)
                    count+=1
                    counti+=1
                    os.remove(ka)
                    time.sleep(1)
                    continue

                elif "*--appx-pdf" in url or "*--appx-pdf?key=" in url:
                    try:
                        # Extract key and clean URL
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
                        
                        # Download PDF
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                
                        pdf_path = f'{name}.pdf'
                
                        if not os.path.exists(pdf_path):
                            raise FileNotFoundError("PDF download failed")

                        print(f"PDF downloaded successfully to {pdf_path}")
                        file_size = os.path.getsize(pdf_path)
                        print(f"PDF size: {file_size} bytes")
                            
                        # Decrypt PDF
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

                        # Send file
                        await bot.send_document(chat_id=channel_id, document=pdf_path, caption=cc1)
                        count += 1
                        print("PDF sent successfully")
                        
                    except Exception as e:
                        error_msg = f"PDF processing failed: {str(e)}"
                        print(error_msg)
                        await m.reply_text(error_msg)
                        continue
                    finally:
                        # Cleanup
                        if 'pdf_path' in locals() and os.path.exists(pdf_path):
                            os.remove(pdf_path)
                            print("Temporary PDF file removed")
                        time.sleep(5)

                elif 'pdf*' in url:
                    reply = await bot.send_message(channel_id, f"__**⚡️ Pdf Downloading...⏳**__\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                    pdf_key = url.split('*')[1]
                    url = url.split('*')[0]
                    pdf_enc = await helper.download_and_decrypt_pdf(url, name, pdf_key)
                    start_time = time.time()
                    time.sleep(1)
                    if thumb2 == "/d":           
                        copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                    else:
                        copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time))
                        os.remove(thumb2)                
                    await reply.delete (True)
                    count += 1 
                    counti+=1
                    os.remove(pdf_enc)
                    time.sleep(1)
                    continue
                  
              #  elif ".pdf*" in url:
                   # try:
                  #      url_part, key_part = url.split("*")
                      #  url = f"https://dragoapi.vercel.app/pdf/{url_part}*{key_part}"
                     #   cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                      #  download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                      #  os.system(download_cmd)
                     #   copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1)
                      #  count += 1
                        #counti+=1
                     #   os.remove(f'{name}.pdf')
                  #  except FloodWait as e:
                     #   await m.reply_text(str(e))
                     #   time.sleep(e.x)
                      #  continue 


                elif ".pdf" in url:
                    reply = await bot.send_message(channel_id, f"__**⚡️ Pdf Downloading...⏳**__\n<blockquote>{str(count).zfill(3)}) {name}</blockquote>")
                    if "cwmediabkt99" in url:
                        await asyncio.sleep(4)
                        url = url.replace(" ", "%20")
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)
                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)
                                await asyncio.sleep(4)
                                time.sleep(1)
                                start_time = time.time()
                                time.sleep(1)
                                if thumb2 == "/d":           
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                                else:
                                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.pdf', caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time))
                                    os.remove(thumb2)                
                                await reply.delete (True)
                                count += 1
                                counti+=1
                                os.remove(f'{name}.pdf')

                    else:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        file_path= f'{name}.pdf'
                        new_file_path = await helper.watermark_pdf(file_path, watermark_text)
                        time.sleep(1)
                        start_time = time.time()
                        time.sleep(1)
                        if thumb2 == "/d":           
                            copy = await bot.send_document(chat_id=channel_id, document=new_file_path, caption=cc1, progress=progress_bar, progress_args=(reply, start_time))
                        else:
                            copy = await bot.send_document(chat_id=channel_id, document=new_file_path, caption=cc1, thumb=thumb2, progress=progress_bar, progress_args=(reply, start_time))
                            os.remove(thumb2)                
                        await reply.delete (True)
                        count +=1
                        counti+=1
                        os.remove(new_file_path)
                        os.remove(f'{name}.pdf')
                        time.sleep(1)
                        continue 
                      
                elif ".ws" in url and  url.endswith(".ws"):
                    await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}",f"{name}.html")
                    time.sleep(1)
                    await bot.send_document(chat_id=channel_id, document=f"{name}.html", caption=cchtml)
                    os.remove(f'{name}.html')
                    count += 1
                    counti+=1
                    time.sleep(5)
                    continue
                            
                elif ".zip" in url:
                    BUTTONSZIP= InlineKeyboardMarkup([[InlineKeyboardButton(text="🎥 ZIP STREAM IN PLAYER", url=f"{url}")]])
                    await bot.send_photo(chat_id=channel_id, photo=photozip, caption=cczip, reply_markup=BUTTONSZIP)
                    count +=1
                    counti+=1
                    time.sleep(1)    
                    continue

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    ext = url.split('.')[-1]
                    cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_photo(chat_id=channel_id, photo=f'{name}.{ext}', caption=ccimg)
                    count += 1
                    counti+=1
                    os.remove(f'{name}.{ext}')
                    time.sleep(e.x)
                    continue

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    ext = url.split('.')[-1]
                    cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_document(chat_id=channel_id, document=f'{name}.{ext}', caption=ccm)
                    count += 1
                    counti+=1
                    os.remove(f'{name}.{ext}')
                    time.sleep(e.x)
                    continue
                    
                #elif "youtu" in url:
                     # await bot.send_photo(chat_id=channel_id, photo=photoyt, caption=ccyt)
                      #count +=1
                      #counti+=1    
                       #time.sleep(1)    
                      #continue

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
                                    message = await bot.send_document(chat_id=channel_id, document=f'{name}.p1', caption=cc1)
                                    count += 1
                                    os.remove(f'{name}.p1')
                                else:
                                    await m.reply_text(f"Failed to download P1. Status code: {response.status}")
                    else:
                        cmd = f'yt-dlp -o "{name}.p1" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        
                        if os.path.exists(f'{name}.p1'):
                            new_name = f'{name}.p1'
                            os.rename(f'{name}.p1', new_name)
                            message = await bot.send_document(chat_id=channel_id, document=new_name, caption=cc1)
                            count += 1
                            os.remove(new_name)
                        else:
                            async with aiohttp.ClientSession(headers=headers) as session:
                                async with session.get(url) as response:
                                    if response.status == 200:
                                        p1_data = await response.read()
                                        with open(f"{name}.p1", 'wb') as f:
                                            f.write(p1_data)
                                        message = await bot.send_document(chat_id=channel_id, document=f'{name}.p1', caption=cc1)
                                        count += 1
                                        os.remove(f'{name}.p1')
                                    else:
                                        await m.reply_text(f"Failed to download P1. Status code: {response.status}")
                    time.sleep(e.x)
                    continue

                elif 'encrypted.m' in url:    
                               #f"<blockquote>🚀𝐓𝐱𝐭 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {txt_progress:.2f}%</blockquote>\n" \
                               #f"┣🔗𝐓𝐱𝐭 𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {total_remaining_links}\n" \
                               #f"┣━🔗𝐓𝐨𝐭𝐚𝐥 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐞𝐝 𝐋𝐢𝐧𝐤𝐬 » {counti}\n" \
                              # f"╰━━🖇️𝐓𝐱𝐭 𝐏𝐚𝐫𝐭 𝐃𝐨𝐧𝐞 » {txt_part_done_progress:.2f}%\n" \
                               #f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               #f"<blockquote>📅𝐏𝐫𝐨𝐠 𝐃𝐚𝐭𝐞 & 𝐓𝐢𝐦𝐞</blockquote>\n" \
                              # f"┣🕰️𝐒𝐭𝐚𝐫𝐭 𝐃𝐚𝐭𝐞: {time_details['msg_date']}\n" \
                              # f"┣━📅𝐒𝐭𝐚𝐫𝐭 𝐃𝐚𝐲: {time_details['day']}\n" \
                              # f"╰━━⏰𝐒𝐭𝐚𝐫𝐭 𝐓𝐢𝐦𝐞: {time_details['msg_time']}\n" \
                             #  f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                    index_remaining_links = end - count
                    total_remaining_links = len(links) - count
                    index_progress = (count/end) * 100
                    txt_progress =(count/len(links)) * 100
                    txt_part_done_progress = (counti/len(links)) * 100
                    emoji = get_next_emoji()
                    #emoji_message = await show_random_emojis(message)
                    emoji_msg = await bot.send_message(channel_id, emoji)
                    #Show = f"✈️ 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ✈️\n\n┠ 📈 Total Links = {len(links)}\n┠ 💥 Currently On = {str(count).zfill(3)}\n\n**📩 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📩**\n\n**🧚🏻‍♂️ Title** : {name}\n├── **Extention** : {MR}\n├── **Resolution** : {raw_text2}\n├── **Url** : `Kya karega URL dekh 👻👻`\n├── **Thumbnail** : `{input6.text}`\n├── **Bot Made By** : saini👑" 
                    Show1 = f"__**Video Downloading**__\n<blockquote><i><b>{str(count).zfill(3)}) {name1}</i></b></blockquote>" 
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n" \
                               f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                               f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**</blockquote>\n┃\n" \
                               f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                               f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » <a href='{batch_link}'>{b_name}</a>\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » `{name}`</blockquote>\n┃\n" \
                               f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                               f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                               f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"🛑**Send** /stop **to stop process**\n┃\n" \
                               f"<blockquote>✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)</blockquote>"
                    prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    prog = await bot.send_message(m.chat.id, Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)  
                    filename = res_file  
                    await prog.delete(True)  
                    await prog1.delete(True)  
                    #await emoji_message.delete()
                    await emoji_msg.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)  
                    count += 1  
                    counti += 1
                    await asyncio.sleep(1)  
                    continue  

                elif 'drmcdni' in url or 'drm/wv' in url:
                    index_remaining_links = end - count
                    total_remaining_links = len(links) - count
                    index_progress = (count/end) * 100
                    txt_progress =(count/len(links)) * 100
                    txt_part_done_progress = (counti/len(links)) * 100
                    emoji = get_next_emoji()
                    emoji_msg = await bot.send_message(channel_id, emoji)
                    #emoji_message = await show_random_emojis(message)
                    #Show = f"𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 ✈️\n\n┠ 📈 Total Links = {len(links)}\n┠ 💥 Currently On = {str(count).zfill(3)}\n\n**📩 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 📩**\n\n**🧚🏻‍♂️ Title** : {name}\n├── **Extention** : {MR}\n├── **Resolution** : {raw_text2}\n├── **Url** : `Kya karega URL dekh  👻👻`\n├── **Thumbnail** : `{input6.text}`\n├── **Bot Made By** : saini 👑"
                    Show1 = f"__**Video Downloading**__\n<blockquote><i><b>{str(count).zfill(3)}) {name1}</i></b></blockquote>"    
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n" \
                               f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                               f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**</blockquote>\n┃\n" \
                               f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                               f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » <a href='{batch_link}'>{b_name}</a>\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » `{name}`</blockquote>\n┃\n" \
                               f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                               f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                               f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"🛑**Send** /stop **to stop process**\n┃\n" \
                               f"<blockquote>✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)</blockquote>"
                    prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    prog = await bot.send_message(m.chat.id, Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await prog.delete(True)
                    await prog1.delete(True)
                    #await emoji_message.delete()
                    await emoji_msg.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1
                    counti += 1
                    await asyncio.sleep(1)
                    continue
     
                else:
                    index_remaining_links = end - count
                    total_remaining_links = len(links) - count
                    index_progress = (count/end) * 100
                    txt_progress =(count/len(links)) * 100
                    txt_part_done_progress = (counti/len(links)) * 100
                    emoji = get_next_emoji()
                    emoji_msg = await bot.send_message(channel_id, emoji)
                    #emoji_message = await show_random_emojis(message)
                    #Show = f"<blockquote>🚀𝐈𝐧𝐝𝐞𝐱 𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n┣🔗𝐈𝐧𝐝𝐞𝐱 𝐑𝐚𝐧𝐠𝐞 » {count}/{end} : {len(links)}\n┃\n" \
                    Show1 = f"__**Video Downloading**__\n<blockquote><i><b>{str(count).zfill(3)}) {name1}</i></b></blockquote>"
                    Show = f"<blockquote>🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {index_progress:.2f}%</blockquote>\n┃\n" \
                               f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{end} : {len(links)}\n┃\n" \
                               f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 » {index_remaining_links}\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>**⚡Dᴏᴡɴʟᴏᴀᴅ Sᴛᴀʀᴛᴇᴅ...⏳**</blockquote>\n┃\n" \
                               f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                               f"╰━📚𝐂𝐨𝐮𝐫𝐬𝐞 » <a href='{batch_link}'>{b_name}</a>\n" \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"<blockquote>📚𝐓𝐢𝐭𝐥𝐞 » `{name}`</blockquote>\n┃\n" \
                               f"┣🍁𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {quality}\n┃\n" \
                               f'┣━🔗𝐋𝐢𝐧𝐤 » <a href="{link0}">**Original Link**</a>\n┃\n' \
                               f'╰━━🖇️𝐔𝐫𝐥 » <a href="{url}">**Api Link**</a>\n' \
                               f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                               f"🛑**Send** /stop **to stop process**\n┃\n" \
                               f"<blockquote>✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)</blockquote>"
                    prog1 = await bot.send_message(channel_id, Show1, disable_web_page_preview=True)
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await prog1.delete(True)
                    await emoji_msg.delete(True)
                    #await emoji_message.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog, channel_id)
                    count += 1
                    counti += 1
                    time.sleep(1)
                
            except Exception as e:
                await bot.send_message(channel_id, f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}\n\n<blockquote><i><b>Failed Reason: {str(e)}</b></i></blockquote>', disable_web_page_preview=True)
                failed_links.append(f"{name1} : {link0}")
                count += 1
                counti += 1
                failed_count += 1
                time.sleep(2)
                continue

    except Exception as e:
        await m.reply_text(e)
        time.sleep(2)

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
        else:
            await bot.send_message(channel_id, f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
            await bot.send_message(channel_id, f"⋅ ─ list index ({arg}-{end}) out of range ─ ⋅\n\n✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
        
    else:
        success_count = end - failed_count
        if mode == "/master":   
            await bot.send_message(channel_id, f"-┈━═.•°✅ Completed ✅°•.═━┈-\n<blockquote>🎯Batch Name : <a href='{batch_link}'>{b_name}</a></blockquote>\n<blockquote>🔗 Total URLs: {len(links)} \n┃   ┠🔴 Total Failed URLs: {failed_count}\n┃   ┠🟢 Total Successful URLs: {success_count}\n┃   ┃   ┠🎥 Total Video URLs: {other_count}\n┃   ┃   ┠📄 Total PDF URLs: {pdf_count}\n┃   ┃   ┠📸 Total IMAGE URLs: {img_count}</blockquote>\n")
        else:
            await bot.send_message(channel_id, f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
            await bot.send_message(channel_id, f"⋅ ─ list index ({arg}-{end}) out of range ─ ⋅\n\n✨ **BATCH** » <a href='{batch_link}'>{b_name}</a>✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
            
        await bot.send_message(m.chat.id, f"<blockquote>✅ Your Task is completed, please check your Set Channel📱</blockquote>")
        




#================================================================================================================================



#================================================================================================================================
bot.run()
if __name__ == "__main__":
    asyncio.run(main())
