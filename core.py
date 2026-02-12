import os
import re
import fitz
import io
from io import BytesIO
from datetime import datetime, timedelta
import time
import random
import mmap
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import requests
import tgcrypto
import subprocess
from subprocess import getstatusoutput
import concurrent.futures
from math import ceil
from PIL import Image, ImageDraw, ImageFont
from utils import progress_bar
from pyrogram import Client, filters
from pyrogram.types import Message
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from pathlib import Path  
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from db import get_user_global_variables
#==========================================================================
async def send_welcome_message(jnc: Client, message: Message):
    user_id = message.from_user.id
    user_photo_path = f"./DOWNLOADS/user_photos/{user_id}.jpg"
    final_path = f"./DOWNLOADS/user_welcome_images/{user_id}_welcome.png"
    base_dir = "Fonts"
    welcome_bg_path = os.path.join(base_dir, "background.png")
    fallback_photo = os.path.join(base_dir, "no-profile.jpg")
    font_path = os.path.join(base_dir, "TTF (5).ttf")
    os.makedirs(os.path.dirname(user_photo_path), exist_ok=True)
    os.makedirs(os.path.dirname(final_path), exist_ok=True)
    welcome_image = Image.open(welcome_bg_path).convert("RGBA")
    try:
        user_profile = await jnc.get_users(user_id)
        if user_profile.photo:
            big_file_id = user_profile.photo.big_file_id
            await jnc.download_media(big_file_id, file_name=user_photo_path)
            user_photo = Image.open(user_photo_path).convert("RGBA")
        else:
            raise Exception("No profile photo available")
    except Exception as e:
        print(f"[x] Profile fetch failed: {e}")
        user_photo = Image.open(fallback_photo).convert("RGBA")
    circle_size = (680, 680)
    user_photo = user_photo.resize(circle_size)
    mask = Image.new("L", circle_size, 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, circle_size[0], circle_size[1]), fill=255)
    user_photo.putalpha(mask)
    circle_pos = ((welcome_image.width - user_photo.width) // 2 - 773,
                  (welcome_image.height - user_photo.height) // 2)
    welcome_image.paste(user_photo, circle_pos, user_photo)
    draw = ImageDraw.Draw(welcome_image)
    font_small = ImageFont.truetype(font_path, 70)
    font_big = ImageFont.truetype(font_path, 130)
    draw.text((270, user_photo.height + 460), f"ID : {user_id}", font=font_small, fill="white")
    welcome_msg = "Welcome to team JNC\n  Advanced Uploader"
    draw.multiline_text((950, 450), welcome_msg, font=font_big, fill="white", spacing=25)
    welcome_image.save(final_path, format="PNG", quality=170)
    return final_path

#===========================================================================
def generate_thumb_from_pdf(pdf_path, output_path="thumb.jpg"):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        pix.save(output_path)
        if os.path.exists(output_path):
            return output_path
        else:
            print("Thumbnail file was not saved.")
            return None
    except Exception as e:
        print(f"generate_thumb_from_pdf error: {e}")
        return None

#================================================================================
def get_yt_thumb(url):
    # Try to extract the video ID from common YouTube URL formats
    patterns = [
        r'youtu\.be/([0-9A-Za-z_-]{11})',
        r'v=([0-9A-Za-z_-]{11})',
        r'embed/([0-9A-Za-z_-]{11})',
        r'\/([0-9A-Za-z_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return None

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
# Same AES Key aur IV jo encryption ke liye use kiya tha
KEY = b'^#^#&@*HDU@&@*()'   
IV = b'^@%#&*NSHUE&$*#)'   

# Decryption function
def dec_url(enc_url):
    enc_url = enc_url.replace("helper://", "")  # "helper://" prefix hatao
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    decrypted = unpad(cipher.decrypt(b64decode(enc_url)), AES.block_size)
    return decrypted.decode('utf-8')

# Function to split name & Encrypted URL properly
def split_name_enc_url(line):
    match = re.search(r"(helper://\S+)", line)  # Find `helper://` ke baad ka encrypted URL
    if match:
        name = line[:match.start()].strip().rstrip(":")  # Encrypted URL se pehle ka text
        enc_url = match.group(1).strip()  # Sirf Encrypted URL
        return name, enc_url
    return line.strip(), None  # Agar encrypted URL nahi mila, to pura line name maan lo

# Function to decrypt file URLs
def decrypt_file_txt(input_file):
    output_file = "decrypted_" + input_file  # Output file ka naam

    # Ensure the directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
        for line in f:
            name, enc_url = split_name_enc_url(line)  # Sahi tarike se name aur encrypted URL split karo
            if enc_url:
                dec = dec_url(enc_url)  # Decrypt URL
                out.write(f"{name}: {dec}\n")  # Ek hi `:` likho
            else:
                out.write(line.strip() + "\n")  # Agar encrypted URL nahi mila to line jaisa hai waisa likho

    return output_file   # Decrypted file ka naam return karega

#================================================================================================================================
def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)

#================================================================================================================================
#def get_mps_and_keys(api_url):
    #response = requests.get(api_url)
    #response_json = response.json()
    #mpd = response_json.get('MPD')
    #keys = response_json.get('KEYS')
    #return mpd, keys

#def get_mps_and_keys(api_url, retries=5, delay=1):
    #for attempt in range(1, retries + 1):
        #try:
           # response = requests.get(api_url, timeout=10)
           # response.raise_for_status()  # Raise HTTPError for bad status
           # response_json = response.json()
           # mpd = response_json.get('mpd')
           # keys = response_json.get('keys')
           # if mpd is None or keys is None:
          #      raise ValueError("MPD or KEYS missing in response")
         #   return mpd, keys
        #except (requests.RequestException, ValueError) as e:
            #if attempt == retries:
             #   raise 
            #time.sleep(delay) 

def get_mps_and_keys(url, retries=3, delay=1):
    first_api = f"https://key-one-gamma.vercel.app/api?url={url}"
    second_api = f"https://cpapi-uc38.onrender.com/extract_keys?url={url}"
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(first_api, timeout=10)
            response.raise_for_status()
            data = response.json()
            mpd = data.get("MPD")
            keys = data.get("KEYS")
            if not mpd or not keys:
                raise ValueError("MPD or KEYS missing in first API response")
            return mpd, keys
        except (requests.RequestException, ValueError) as e:
            print(f"[First API] Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(second_api, timeout=10)
            response.raise_for_status()
            data = response.json()
            mpd = data.get("mpd")
            keys = data.get("keys")
            if not mpd or not keys:
                raise ValueError("mpd or keys missing in second API response")
            return mpd, keys
        except (requests.RequestException, ValueError) as e:
            print(f"[Second API] Attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(delay)
    raise Exception("Failed to fetch MPD and keys from both APIs.")
            
#================================================================================================================================
def exec(cmd):
        process = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.stdout.decode()
        print(output)
        return output
        #err = process.stdout.decode()
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        print("Waiting for tasks to complete")
        fut = executor.map(exec,cmds)
async def aio(url,name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(k, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return k

#================================================================================================================================
async def download(url,name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(ka, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return ka

async def pdf_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name   
   

def parse_vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = []
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",2)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    new_info.append((i[0], i[2]))
            except:
                pass
    return new_info


def vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = dict()
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",3)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    
                    # temp.update(f'{i[2]}')
                    # new_info.append((i[2], i[0]))
                    #  mp4,mkv etc ==== f"({i[1]})" 
                    
                    new_info.update({f'{i[2]}':f'{i[0]}'})

            except:
                pass
    return new_info

#================================================================================================================================
async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        download_cmd = f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{output_path}/file.%(ext)s" --allow-unplayable-format --no-check-certificate --external-downloader aria2c "{mpd_url}"'
        print(f"Running command: {download_cmd}")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True))

        avDir = list(output_path.iterdir())
        print(f"Downloaded files: {avDir}")
        print("Decrypting")

        video_decrypted = False
        audio_decrypted = False

        for data in avDir:
            if data.suffix == ".mp4" and not video_decrypted:
                decrypt_video_cmd = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/video.mp4"'
                print(f"Running command: {decrypt_video_cmd}")
                await loop.run_in_executor(None, lambda: subprocess.run(decrypt_video_cmd, shell=True))
                if (output_path / "video.mp4").exists():
                    video_decrypted = True
                data.unlink()

            elif data.suffix == ".m4a" and not audio_decrypted:
                decrypt_audio_cmd = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/audio.m4a"'
                print(f"Running command: {decrypt_audio_cmd}")
                await loop.run_in_executor(None, lambda: subprocess.run(decrypt_audio_cmd, shell=True))
                if (output_path / "audio.m4a").exists():
                    audio_decrypted = True
                data.unlink()

        if not video_decrypted or not audio_decrypted:
            raise FileNotFoundError("Decryption failed: video or audio file not found.")

        merge_cmd = f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" -c copy "{output_path}/{output_name}.mp4"'
        print(f"Running command: {merge_cmd}")
        await loop.run_in_executor(None, lambda: subprocess.run(merge_cmd, shell=True))

        if (output_path / "video.mp4").exists():
            (output_path / "video.mp4").unlink()
        if (output_path / "audio.m4a").exists():
            (output_path / "audio.m4a").unlink()

        filename = output_path / f"{output_name}.mp4"
        if not filename.exists():
            raise FileNotFoundError("Merged video file not found.")

        duration_cmd = f'ffmpeg -i "{filename}"'
        process = await asyncio.create_subprocess_shell(
            duration_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        stdout, _ = await process.communicate()
        duration_output = stdout.decode()
        duration_line = next((line for line in duration_output.splitlines() if "Duration" in line), "Duration not found")
        print(f"Duration info: {duration_line}")
        return str(filename)
    except Exception as e:
        print(f"Error during decryption and merging: {str(e)}")
        raise

async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if proc.returncode == 1:
        return False
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'

#================================================================================================================================
def old_download(url, file_name, chunk_size = 1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name

#================================================================================================================================
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

#================================================================================================================================
def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"

#==============================================================================================================================
async def download_video(url,cmd, name):
    download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    global failed_counter
    print(download_cmd)
    logging.info(download_cmd)
    loop = asyncio.get_running_loop() 
    k = await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True))
    if "visionias" in cmd and k.returncode != 0 and failed_counter <= 10:
        failed_counter += 1
        await asyncio.sleep(5)
        await download_video(url, cmd, name)
    failed_counter = 0
    try:
        if os.path.isfile(name):
            return name
        elif os.path.isfile(f"{name}.webm"):
            return f"{name}.webm"
        name = name.split(".")[0]
        if os.path.isfile(f"{name}.mkv"):
            return f"{name}.mkv"
        elif os.path.isfile(f"{name}.mp4"):
            return f"{name}.mp4"
        elif os.path.isfile(f"{name}.mp4.webm"):
            return f"{name}.mp4.webm"

        return name
    except FileNotFoundError as exc:
        return os.path.isfile.splitext[0] + "." + "mp4"

#================================================================================================================================
async def send_doc(bot: Client, m: Message, cc, ka, cc1, prog, count, name, channel_id):
    #reply = await m.reply_text(channel_id, f"**★彡 ᵘᵖˡᵒᵃᵈⁱⁿᵍ 彡★ ...⏳**\n\n📚𝐓𝐢𝐭𝐥𝐞 » `{name}`\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎🐦")
    reply = await bot.send_message(channel_id, f"Pdf Downloading:\n<pre><code>`{name}`</code></pre>\n")
    time.sleep(1)
    start_time = time.time()
    await bot.send_document(ka, caption=cc1)
    count+=1
    await reply.delete (True)
    time.sleep(1)
    os.remove(ka)
    time.sleep(3) 

#================================================================================================================================
def decrypt_file(file_path, key):  
    if not os.path.exists(file_path): 
        return False  

    with open(file_path, "r+b") as f:  
        num_bytes = min(28, os.path.getsize(file_path))  
        with mmap.mmap(f.fileno(), length=num_bytes, access=mmap.ACCESS_WRITE) as mmapped_file:  
            for i in range(num_bytes):  
                mmapped_file[i] ^= ord(key[i]) if i < len(key) else i 
    return True  

#================================================================================================================================
async def download_and_decrypt_video(url, cmd, name, key):  
    video_path = await download_video(url, cmd, name)  
    
    if video_path:  
        decrypted = decrypt_file(video_path, key)  
        if decrypted:  
            print(f"File {video_path} decrypted successfully.")  
            return video_path  
        else:  
            print(f"Failed to decrypt {video_path}.")  
            return None  

#================================================================================================================================
async def download_and_decrypt_pdf(url, name, key):
    download_cmd = f'yt-dlp -o "{name}.pdf" "{url}" -R 25 --fragment-retries 25'
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, lambda: subprocess.run(download_cmd, shell=True, check=True))
        print(f"Downloaded PDF: {name}.pdf")
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e}")
        return False
        
    file_path = f"{name}.pdf"
    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return False

    try:
        with open(file_path, "r+b") as f:
            num_bytes = min(28, os.path.getsize(file_path))
            with mmap.mmap(f.fileno(), length=num_bytes, access=mmap.ACCESS_WRITE) as mmapped_file:
                for i in range(num_bytes):
                    mmapped_file[i] ^= ord(key[i]) if i < len(key) else i

        print(f"Decryption completed for {file_path}.")
        return file_path
    except Exception as e:
        print(f"Error during decryption: {e}")
        return False
#================= Spliting According to File Size ==================

def duration(filename):
    result = subprocess.run(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{filename}"', 
                            shell=True, 
                            capture_output=True, 
                            text=True)
    return float(result.stdout.strip())

def duration(part):
    result = subprocess.run(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{part}"', 
                            shell=True, 
                            capture_output=True, 
                            text=True)
    return float(result.stdout.strip())

def split_video(filename, max_size):
    parts = []
    part_prefix = filename.split('.')[0]  # Get the filename without extension

    # Calculate the total duration of the video
    total_duration = duration(filename)
    
    # Estimate the duration of each segment to be under the max_size
    file_size = os.path.getsize(filename)
    segment_duration = ceil((total_duration * max_size) / file_size)
    
    # Command to split the video, using MKV container
    #split_command = f'ffmpeg -y -i "{filename}" -c copy -map 0 -segment_time {segment_duration} -f segment "{part_prefix}_part_%03d.mkv"'
    split_command = f'ffmpeg -y -i "{filename}" -c copy -map 0 -f segment -segment_time {segment_duration} -reset_timestamps 1 "{part_prefix}_part_%03d.mkv"'
    subprocess.run(split_command, shell=True)
    
    for part in os.listdir():
        if part.startswith(part_prefix) and part.endswith('.mkv'):
            parts.append(part)
    
    return parts

#================================================================================================================================
#-----------------------Emoji handler------------------------------------
EMOJIS = ["🦁", "🐶", "🐼", "🐱", "👻", "🐻‍❄️", "☁️", "🚹", "🚺", "🐠", "🦋"]
emoji_counter = 0  # Initialize a global counter

def get_next_emoji():
    global emoji_counter
    emoji = EMOJIS[emoji_counter]
    emoji_counter = (emoji_counter + 1) % len(EMOJIS)
    return emoji

#================================================================================================================================
async def create_text_thumbnail(text, user_id, filename="thumb.png", width=1280, height=720, override_font=None):
    # 1. Create image with fully transparent background
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 2. Load user's saved font color and style
    user_data = get_user_global_variables(user_id)
    
    # Fallbacks
    hex_color = user_data.get("font_color", "00008B")  # default: Dark Blue
    # 🔄 Use override font if given, else from database
    font_file = override_font or user_data.get("font_style", "TTF (5).ttf")

    # Convert hex color to RGBA
    try:
        font_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    except:
        font_color = (0, 0, 139, 255)  # fallback to dark blue

    # 3. Font path
    font_dir = "Fonts"
    font_path = os.path.join(font_dir, font_file)

    if not os.path.isfile(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # 4. Fit text with font size
    max_font_size = 200
    for font_size in range(max_font_size, 10, -2):
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        if text_width < width * 0.9 and text_height < height * 0.9:
            break

    # 5. Center and draw text
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), text, font=font, fill=font_color)

    # 6. Save image
    img.save(filename, format="PNG")
    return filename

#================================================================================================================================
async def send_vid(bot: Client, m: Message,cc,filename,thumb,name,prog, channel_id, topic_id=None, reply_markup=None):
    await prog.delete (True)
    result = subprocess.run(
        f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{filename}.jpg"',
        shell=True,
        check=True,  # This will raise a CalledProcessError if the command fails
    )
    if result.returncode == 0:
        reply1 = await bot.send_message(channel_id, f"**📩 Uploading Video 📩:-**\n<blockquote>**{name}**</blockquote>", message_thread_id=topic_id if topic_id else None)
        #reply1 = await bot.send_message(channel_id, f"**📩 Uploading Video 📩:-**\n<blockquote>**{name}**</blockquote>")
        reply = await m.reply_text(f"**Generate Thumbnail:**\n<blockquote>**{name}**</blockquote>")

    try:
        if thumb == "/d":
            thumbnail = f"{filename}.jpg"
        elif thumb == "No":
            thumbnail = f"{filename}.jpg"
        elif thumb.startswith("http://") or thumb.startswith("https://"):
            getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
            thumbnail = "thumb.jpg"
        elif hasattr(thumb, "photo") and thumb.photo:
            thumbnail = thumb
        else:
            with Image.open(f"{filename}.jpg") as base_img:
                width, height = base_img.size
            thumb_text = thumb if isinstance(thumb, str) else str(thumb)
            thumb_png = await create_text_thumbnail(
                thumb_text,
                m.from_user.id,  # <-- Pass user_id here
                filename="text_thumb.png",
                width=width,
                height=height
            )
            overlay_cmd = f'ffmpeg -i "{filename}.jpg" -i "text_thumb.png" -filter_complex "[0][1]overlay=0:0" -y "{filename}.jpg"'
            getstatusoutput(overlay_cmd)
            thumbnail = f"{filename}.jpg"

    except Exception as e:
        await m.reply_text(str(e))

    dur = int(duration(filename))
    start_time = time.time()

    # Check if the file size exceeds 1.8GB
    max_size = 1.8 * 1024 * 1024 * 1024  # 1.8GB in bytes
    file_size = os.path.getsize(filename)
    
    if file_size > max_size:
        # Notify user that the video is being split
        splitting_msg = await bot.send_message(channel_id, f"<blockquote>🛠 **Splitting video into parts**...\n⏰ **Please wait few minutes**...⏳</blockquote>")
        
        # Split the video into parts
        parts = split_video(filename, max_size)
        parts.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))  # Sort by part number
        
        # Upload each part
        for i, part in enumerate(parts):
            part_dur = int(duration(part))
            await splitting_msg.edit_text(f"<blockquote>**★彡 UPLOADING SPILT PART {i + 1} OF {len(parts)} 彡★**</blockquote>")
            try:
                part_caption = f"⋅ ⋅ ─ ─ **Part {i + 1}** ─ ─ ⋅ ⋅ \n\n{cc}"
                await bot.send_video(channel_id, part, caption=part_caption, supports_streaming=True, height=720, width=1280, thumb=thumbnail, duration=part_dur, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=topic_id if topic_id else None)
                
            except Exception:
                await bot.send_document(channel_id, part, caption=part_caption, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=topic_id if topic_id else None)
            os.remove(part)
            await asyncio.sleep(3)
        
        # Delete the splitting message after all parts are uploaded
        await splitting_msg.delete()
        
    
    else:      
        try:
            await bot.send_video(channel_id, filename, caption=cc, supports_streaming=True, height=720, width=1280, thumb=thumbnail, duration=dur, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=topic_id if topic_id else None, reply_markup=reply_markup)
        except Exception:
            await bot.send_document(channel_id, filename, caption=cc, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=topic_id if topic_id else None, reply_markup=reply_markup)
    await reply.delete(True)
    await reply1.delete(True)
    os.remove(filename)
    os.remove(f"{filename}.jpg")
#================================================================================================================================
async def log_send_vid(bot: Client, m: Message,cc,filename,thumb,name,prog, channel_id, log_channel_id, thread_id=None, main_thread_id=None, reply_markup=None):
    await prog.delete (True)
    result = subprocess.run(
        f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{filename}.jpg"',
        shell=True,
        check=True,  # This will raise a CalledProcessError if the command fails
    )
    if result.returncode == 0:
        reply1 = await bot.send_message(channel_id, f"**📩 Uploading Video 📩:-**\n<blockquote>**{name}**</blockquote>", message_thread_id=main_thread_id if main_thread_id else None)
        #reply1 = await bot.send_message(channel_id, f"**📩 Uploading Video 📩:-**\n<blockquote>**{name}**</blockquote>")
        reply = await m.reply_text(f"**Generate Thumbnail:**\n<blockquote>**{name}**</blockquote>")

    try:
        if thumb == "/d":
            thumbnail = f"{filename}.jpg"
        elif thumb == "No":
            thumbnail = f"{filename}.jpg"
        elif thumb.startswith("http://") or thumb.startswith("https://"):
            getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
            thumbnail = "thumb.jpg"
        elif hasattr(thumb, "photo") and thumb.photo:
            thumbnail = thumb
        else:
            with Image.open(f"{filename}.jpg") as base_img:
                width, height = base_img.size
            thumb_text = thumb if isinstance(thumb, str) else str(thumb)
            thumb_png = await create_text_thumbnail(
                thumb_text,
                m.from_user.id,  # <-- Pass user_id here
                filename="text_thumb.png",
                width=width,
                height=height
            )
            overlay_cmd = f'ffmpeg -i "{filename}.jpg" -i "text_thumb.png" -filter_complex "[0][1]overlay=0:0" -y "{filename}.jpg"'
            getstatusoutput(overlay_cmd)
            thumbnail = f"{filename}.jpg"

    except Exception as e:
        await m.reply_text(str(e))

    dur = int(duration(filename))
    start_time = time.time()

    # Check if the file size exceeds 1.8GB
    max_size = 1.8 * 1024 * 1024 * 1024  # 1.8GB in bytes
    file_size = os.path.getsize(filename)
    
    if file_size > max_size:
        # Notify user that the video is being split
        splitting_msg = await bot.send_message(channel_id, f"<blockquote>🛠 **Splitting video into parts**...\n⏰ **Please wait few minutes**...⏳</blockquote>")
        
        # Split the video into parts
        parts = split_video(filename, max_size)
        parts.sort(key=lambda x: int(x.split('_')[-1].split('.')[0]))  # Sort by part number
        
        # Upload each part
        for i, part in enumerate(parts):
            part_dur = int(duration(part))
            await splitting_msg.edit_text(f"<blockquote>**★彡 UPLOADING SPILT PART {i + 1} OF {len(parts)} 彡★**</blockquote>")
            try:
                part_caption = f"⋅ ⋅ ─ ─ **Part {i + 1}** ─ ─ ⋅ ⋅ \n\n{cc}"
                message = await bot.send_video(channel_id, part, caption=part_caption, supports_streaming=True, height=720, width=1280, thumb=thumbnail, duration=part_dur, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=main_thread_id if main_thread_id else None)
                file_id = message.video.file_id  # Ca
                
            except Exception:
                message = await bot.send_document(channel_id, part, caption=part_caption, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=main_thread_id if main_thread_id else None)
                file_id = message.document.file_id
            try:
                await bot.send_video(log_channel_id, file_id, caption=part_caption, supports_streaming=True, message_thread_id=thread_id)
            except Exception as e:
                await bot.send_document(log_channel_id, file_id, caption=cc, message_thread_id=thread_id)
                
            os.remove(part)
            await asyncio.sleep(3)
        
        # Delete the splitting message after all parts are uploaded
        await splitting_msg.delete()
        
    
    else:      
        try:
            message = await bot.send_video(channel_id, filename, caption=cc, supports_streaming=True, height=720, width=1280, thumb=thumbnail, duration=dur, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=main_thread_id if main_thread_id else None, reply_markup=reply_markup)
            file_id = message.video.file_id  # Ca
        except Exception:
            message = await bot.send_document(channel_id, filename, caption=cc, progress=progress_bar, progress_args=(reply, start_time), message_thread_id=main_thread_id if main_thread_id else None, reply_markup=reply_markup)
            file_id = message.document.file_id
        try:
            await bot.send_video(log_channel_id, file_id, caption=cc, supports_streaming=True, message_thread_id=thread_id, reply_markup=reply_markup)
        except Exception as e:
            await bot.send_document(log_channel_id, file_id, caption=cc, message_thread_id=thread_id, reply_markup=reply_markup)
    
    await reply.delete(True)
    await reply1.delete(True)
    os.remove(filename)
    os.remove(f"{filename}.jpg")
#================================================================================================================================
def add_watermark_to_pdf(input_pdf_path, output_pdf_path, watermark_text):
    # Watermark bana ke memory me rakho
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 36)
    can.setFillAlpha(0.2)
    can.saveState()
    can.translate(300, 400)
    can.rotate(45)
    can.drawCentredString(0, 0, watermark_text)
    can.restoreState()
    can.save()
    packet.seek(0)
    watermark_pdf = PdfReader(packet)
    watermark_page = watermark_pdf.pages[0]

    # Original PDF read
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.merge_page(watermark_page)
        writer.add_page(page)
    with open(output_pdf_path, "wb") as out_file:
        writer.write(out_file)
