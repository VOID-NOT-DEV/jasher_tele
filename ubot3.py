#         IMPORTS            #
# ========================== #

import os
import re
import time
import json
import uuid
import shutil
import zipfile
import base64
import random
import string
import asyncio
import subprocess
import requests
import requests
import os
import mimetypes
import random
import asyncio
import time
import shutil
from telethon.tl.types import ChannelParticipantsSearch
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import PhoneCodeInvalidError
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from dotenv import load_dotenv

# Load variabel dari .env
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
owner_id = int(os.getenv("OWNER_ID"))
owner = os.getenv("OWNER")
CATBOX_API = os.getenv("CATBOX_API")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")

EMOJI_LIST = ["🔥", "💥", "✨", "🌟", "⚡", "🍀", "🎯", "🎉", "🌈", "💎", "🚀", "💫", "🧲", "🌪️", "🧨"] #ubah aja
DEPLOY_PATH = "./vercel_temp"
bl_file = "blacklist.json" #B
session_file = "userbot.session" #A sama B sama ini jangan di ubah

def get_akses_list():
    try:
        
        url = "https://raw.githubusercontent.com/NocturnVoxx/DATABASE/refs/heads/main/akses.json"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            return res.json() 
        else:
            print("⚠️ Gagal fetch akses.json dari GitHub")
            return []
    except Exception as e:
        print(f"⚠️ Error fetch akses.json dari GitHub: {e}")
        return []

try:
    with open(bl_file) as f:
        blacklist = json.load(f)
except:
    blacklist = []

client = TelegramClient(session_file, api_id, api_hash)

from telethon.tl.functions.users import GetFullUserRequest

from telethon.tl.functions.users import GetFullUserRequest
from telethon import events
import html  # untuk menghindari error nama user yang aneh

from telethon import events, Button
import asyncio

@client.on(events.NewMessage(pattern=r'\.zhelp'))
async def zhelp_menu(event):
    # kirim pesan teks untuk loading
    msg = await event.reply("🔄 Loading... 0%")

    for i in range(0, 101, 20):
        bar = "█" * (i // 10)
        empty = "░" * (10 - (i // 10))
        await msg.edit(f"🔄 Loading... {i}%\n[{bar}{empty}]")
        await asyncio.sleep(0.3)

    await msg.edit("✅ Selamat menggunakan Nocturn Userbot!\n\nTunggu sebentar...")
    await asyncio.sleep(2)

    # ambil data user
    user = await event.get_sender()
    username = f"@{user.username}" if user.username else "Tidak ada"
    user_id = user.id

    # teks menu utama
    buttons_caption = (
        "🌌 <b>Nocturn Userbot - Menu Bantuan</b> 🌌\n"
        f"🔥 <b>Dibuat oleh {owner}</b>\n"
        "📢 Gunakan perintah dengan bijak untuk pengalaman terbaik!\n\n"

        "⦗ ♱ ⦘ <b>INFO PENGGUNA</b>\n"
        f"⚝ <b>Username</b>: {username}\n"
        f"⚝ <b>ID</b>: {user_id}\n\n"

        "⦗ ♱ ⦘ <b>INFO BOT</b>\n"
        "⚝ <b>Nama</b>: Nocturn Ubot\n"
        "⚝ <b>Versi</b>: 1.0.0\n"
        "⚝ <b>Developer</b>: — 919 NOCTURN\n"
        f"⚝ <b>Owner</b>: {owner}\n\n"

        "📋 <b>Pilih menu di bawah:</b>"
    )

    # tombol URL (hanya bisa link, inline callback tidak jalan di userbot)
    buttons = [
        [Button.url("📚 Zhelp", "https://t.me/")],
        [Button.url("🚫 Addbl", "https://t.me/")],
        [Button.url("✅ Unbl", "https://t.me/")],
        [Button.url("📢 Broadcast", "https://t.me/")],
        [Button.url("🆔 Cekid", "https://t.me/")],
        [Button.url("👥 Groupmenu", "https://t.me/")],
        [Button.url("🏓 Ping", "https://t.me/")],
        [Button.url("📜 Listgrup", "https://t.me/")],
        [Button.url("🛠️ Tools", "https://t.me/")],
        [Button.url("🙏 TQTO", "https://t.me/")]
    ]

    # kirim pesan teks dengan tombol URL
    await event.client.send_message(
        event.chat_id,
        buttons_caption,
        buttons=buttons,
        parse_mode="html"
    )

    await msg.delete()
    
    
@client.on(events.CallbackQuery)
async def callback_handler(event):
    data = event.data.decode("utf-8")

    help_texts = {
        "help_zhelp": "📌 <b>Zhelp</b>\nMenampilkan menu bantuan utama.\n<b>Penggunaan:</b> `.zhelp`",
        "help_addbl": "📌 <b>Addbl</b>\nMenambahkan grup ke blacklist.\n<b>Penggunaan:</b> `.addbl`",
        "help_unbl": "📌 <b>Unbl</b>\nMenghapus grup dari blacklist.\n<b>Penggunaan:</b> `.unbl`",
        "help_boardcast": "📌 <b>Broadcast</b>\nMengirim pesan ke semua grup.\n<b>Penggunaan:</b> `.jpm <pesan>`",
        "help_cekid": "📌 <b>Cekid</b>\nMelihat ID user/grup.\n<b>Penggunaan:</b> `.cekid <username/link>`",
        "help_groupmenu": "📌 <b>Groupmenu</b>\nMenampilkan perintah grup.",
        "help_ping": "📌 <b>Ping</b>\nMengukur kecepatan respons bot.\n<b>Penggunaan:</b> `.ping`",
        "help_listgrup": "📌 <b>Listgrup</b>\nMenampilkan semua grup yang dimasuki bot.",
        "help_tools": "📌 <b>Tools</b>\nMenampilkan menu tools tambahan.",
        "help_tqto": "📌 <b>TQTO</b>\nMenampilkan ucapan terima kasih."
    }

    if data in help_texts:
        await event.answer(help_texts[data], alert=True)
        
@client.on(events.NewMessage(pattern=r'^.boardcast$'))
async def boarcast_handler(event):
    user = await client(GetFullUserRequest(event.sender_id))
    pengguna = user.users[0]  # ambil objek User dari list
    nama = html.escape(pengguna.first_name or "Pengguna")
    uid = pengguna.id

    teks = f"""
<blockquote>
𝗕𝗢𝗔𝗥𝗗𝗖𝗔𝗦𝗧𝗠𝗘𝗡𝗨
• /jpm [teks] — Kirim ke semua grup  
• /jpm (reply) — Forward pesan ke semua grup
</blockquote>
"""

    await event.reply(teks, parse_mode='html')
   
@client.on(events.NewMessage(pattern=r"\.viewpp\s+(https?://t\.me/[@]?\w+)"))
async def viewpp_handler(event):
    try:
        # Ambil username dari link
        link = event.pattern_match.group(1)
        username = link.split("/")[-1].lstrip("@")

        # Download foto profil
        file_path = await client.download_profile_photo(username)
        if not file_path:
            await event.reply("❌ Tidak ada foto profil.")
            return

        # Upload ke catbox
        with open(file_path, 'rb') as f:
            resp = requests.post(CATBOX_API, data={"reqtype": "fileupload"}, files={"fileToUpload": f})
        
        if resp.status_code == 200 and resp.text.startswith("http"):
            await event.reply(f"✅ Foto profil:\n{resp.text.strip()}")
        else:
            await event.reply("❌ Gagal upload ke Catbox.")

        # Hapus file lokal
        os.remove(file_path)

    except Exception as e:
        await event.reply(f"⚠️ Error: {e}")

@client.on(events.NewMessage(pattern=r'^.groupmenu$'))
async def group_handler(event):
    user = await client(GetFullUserRequest(event.sender_id))
    pengguna = user.users[0]  # ambil objek User dari list
    nama = html.escape(pengguna.first_name or "Pengguna")
    uid = pengguna.id

    teks = f"""
<blockquote>
𝗚𝗥𝗢𝗨𝗣𝗠𝗘𝗡𝗨
• .spam id|jumlah|pesan — Spam ke user  
• .listgrup — Lihat semua grup aktif  
• .tagall [teks] — Mention semua member pakai emoji acak
</blockquote>
"""

    await event.reply(teks, parse_mode='html')

@client.on(events.NewMessage(pattern=r'^.blockirmenu$'))
async def block_handler(event):
    user = await client(GetFullUserRequest(event.sender_id))
    pengguna = user.users[0]  # ambil objek User dari list
    nama = html.escape(pengguna.first_name or "Pengguna")
    uid = pengguna.id

    teks = f"""
<blockquote>
𝗕𝗟𝗢𝗖𝗞𝗜𝗥𝗠𝗘𝗡𝗨
• .addbl t.me/link — Blacklist grup  
• .unbl t.me/link — Hapus dari blacklist
</blockquote>
"""

    await event.reply(teks, parse_mode='html')
    
@client.on(events.NewMessage(pattern=r'^.toolsmenu$'))
async def tools_handler(event):
    user = await client(GetFullUserRequest(event.sender_id))
    pengguna = user.users[0]  # ambil objek User dari list
    nama = html.escape(pengguna.first_name or "Pengguna")
    uid = pengguna.id

    teks = f"""
<blockquote>
𝗧𝗢𝗢𝗟𝗦𝗠𝗘𝗡𝗨
• .zhelp — Tampilkan menu ini  
• .cekid username/link — Lihat ID Telegram  
• .getcode [link] — Simpan website jadi file HTML  
• .tourl (reply media) — Upload media ke Catbox
</blockquote>
"""

    await event.reply(teks, parse_mode='html')
@client.on(events.NewMessage(pattern=r'^.tqto$'))
async def tqto_handler(event):
    user = await client(GetFullUserRequest(event.sender_id))
    pengguna = user.users[0]  # ambil objek User dari list
    nama = html.escape(pengguna.first_name or "Pengguna")
    uid = pengguna.id

    teks = f"""
```
╭━─━⊱ *THANKS TO*
│ anymous
╰━──────────────────────────❏
```"""

    await event.reply(teks, parse_mode='html')

@client.on(events.NewMessage(pattern=r'^/getcode (https?://[^\s]+)'))
async def getcode_handler(event):
    if event.sender_id not in get_akses_list():
        return await event.reply("❌ Kamu tidak punya akses.")

    url = event.pattern_match.group(1)
    msg = await event.reply("⏳ Mengambil dan memproses website...")

    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
    except Exception as e:
        return await msg.edit(f"❌ Gagal mengambil website:\n{e}")

    soup = BeautifulSoup(r.text, 'html.parser')
    tags = soup.find_all(['img', 'video', 'source'])

    media_attrs = ['src', 'data-src', 'srcset', 'poster']

    for tag in tags:
        for attr in media_attrs:
            val = tag.get(attr)
            if not val:
                continue

            if attr == 'srcset' and ',' in val:
                val = val.split(',')[0].strip().split(' ')[0]

            media_url = urljoin(url, val)
            try:
                media = requests.get(media_url, timeout=10)
                media.raise_for_status()
                ext = os.path.splitext(urlparse(media_url).path)[1]
                if not ext or len(ext) > 5:
                    ext = '.jpg'

                fname = ''.join(random.choices(string.ascii_lowercase, k=10)) + ext
                with open(fname, 'wb') as f:
                    f.write(media.content)

                with open(fname, 'rb') as f:
                    files = {
                        'reqtype': (None, 'file'),
                        'fileToUpload': (fname, f)
                    }
                    res = requests.post("https://catbox.moe/user/api.php", files=files)
                    new_url = res.text.strip()
                    if res.status_code == 200 and new_url.startswith("https://"):
                        tag[attr] = new_url
            except Exception as e:
                print(f"❌ Gagal proses {attr}: {e}")
            finally:
                if os.path.exists(fname):
                    os.remove(fname)

    full_html = f"<!DOCTYPE html>\\n<html>\\n{str(soup)}\\n</html>"
    out_file = "result_getcode.html"

    try:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(full_html)
        await client.send_file(event.chat_id, out_file, caption="✅ Berikut hasil /getcode (media asli)")
    except Exception as e:
        await msg.edit(f"❌ Gagal mengirim file:\\n{e}")
    finally:
        if os.path.exists(out_file):
            os.remove(out_file)
    

@client.on(events.NewMessage(pattern=r'^.tourl$'))
async def tourl_handler(event):
    if not event.is_reply:
        return await event.reply("❌ Balas ke file (foto/video/dokumen) yang ingin diupload.")

    reply = await event.get_reply_message()
    if not reply.file:
        return await event.reply("❌ Pesan yang dibalas tidak berisi file.")

    msg = await event.reply("⏳ Mengunduh file...")

    # Download file dari reply
    file_path = await reply.download_media(file="catbox_temp")

    if not file_path or not os.path.exists(file_path):
        return await msg.edit("❌ Gagal mengunduh file.")

    await msg.edit("⏳ Mengupload ke Catbox...")

    try:
        with open(file_path, "rb") as f:
            response = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f})

        if response.status_code != 200 or not response.text.startswith("https://"):
            return await msg.edit("❌ Gagal upload ke Catbox.moe.")

        url = response.text.strip()
        file_size = os.path.getsize(file_path)
        size_mb = round(file_size / 1024 / 1024, 2)
        mime_type = mimetypes.guess_type(file_path)[0] or "Unknown"
        file_name = os.path.basename(file_path)
        created_at = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

        teks = f"""
✅ <b>Berhasil Upload ke Catbox.moe</b>

🌐 <b>URL:</b> <a href="{url}">{url}</a>
📄 <b>Nama:</b> <code>{file_name}</code>
📦 <b>Ukuran:</b> {size_mb} MB
📁 <b>Tipe:</b> {mime_type}
🕒 <b>Dibuat:</b> {created_at}
"""
        await msg.edit(teks, parse_mode='html', link_preview=False)

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
    
@client.on(events.NewMessage(pattern=r'^\.ping$'))
async def ping_handler(event):
    if event.sender_id not in get_akses_list():
        return

    msg = await event.reply("⏳ Tes koneksi...")
    await asyncio.sleep(0.5)

    await msg.edit("⚡ Mengukur delay...")
    start = time.time()
    await asyncio.sleep(0.5)

    me = await client.get_me()
    nama = getattr(me, "first_name", "Unknown")
    uid = getattr(me, "id", "Unknown")

    jumlah_grup = 0
    async for dialog in client.iter_dialogs():
        if getattr(dialog, "is_group", False):
            jumlah_grup += 1

    delay = round((time.time() - start) * 1000)
    teks = (
        f"🏓 <b>BOT ONLINE!</b>\n\n"
        f"👤 <b>Nama:</b> {nama}\n"
        f"🆔 <b>ID:</b> <code>{uid}</code>\n"
        f"👥 <b>Jumlah Grup:</b> {jumlah_grup}\n"
        f"⚡ <b>Respons:</b> {delay} ms"
    )
    await msg.edit(teks, parse_mode="html")

@client.on(events.NewMessage(pattern=r'\.listgrup'))
async def listgrup_handler(event):
    if event.sender_id not in get_akses_list():
        return

    msg = "**📋 Daftar Grup yang Dimasuki:**\n\n"
    count = 0

    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if dialog.is_group or (dialog.is_channel and getattr(entity, 'megagroup', False)):
            count += 1
            msg += f"{count}. {entity.title} - `{entity.id}`\n"

    if count == 0:
        return await event.reply("🤖 Tidak ada grup yang terdeteksi.")

    if len(msg) > 4000:
        file_path = "list_grup.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(msg)
        await event.respond("📄 Daftar grup terlalu panjang, dikirim sebagai file:", file=file_path)
        os.remove(file_path)
    else:
        await event.respond(msg)

@client.on(events.NewMessage(pattern=r'.cekid (.+)'))
async def cekid_handler(event):
    if event.sender_id not in get_akses_list():
        return

    try:
        link = event.pattern_match.group(1)
        if "t.me/" in link:
            username = link.split("t.me/")[1].replace("@", "").strip()
        else:
            username = link.replace("@", "").strip()

        user = await client.get_entity(username)
        await event.reply(f"✅ ID Telegram dari {username}: `{user.id}`")
    except Exception:
        await event.reply("❌ Gagal mengambil ID. Pastikan link atau username valid.")

@client.on(events.NewMessage(pattern=r'^\.addbl$'))
async def addbl_handler(event):
    if event.sender_id not in get_akses_list():
        return

    group_id = event.chat_id
    if group_id not in blacklist:
        blacklist.append(group_id)
        with open(bl_file, "w") as f:
            json.dump(blacklist, f)
        await event.reply("```Berhasil menambahkan grup ini ke blacklist```")
    else:
        await event.reply("```Grup ini sudah ada di blacklist```")
        
@client.on(events.NewMessage(pattern=r'.spam (\d+)\|(\d+)\|(.+)'))
async def spam_handler(event):
    if event.sender_id not in get_akses_list():
        return

    user_id = int(event.pattern_match.group(1))
    jumlah = int(event.pattern_match.group(2))
    teks = event.pattern_match.group(3)

    await event.reply(
        f"🚀 Mulai spam ke ID: {user_id}\nJumlah: {jumlah}x\nPesan: {teks[:30]}..."
    )

    sukses, gagal = 0, 0
    for i in range(jumlah):
        try:
            await client.send_message(user_id, teks)
            sukses += 1
        except:
            gagal += 1
        await asyncio.sleep(1)  # delay 1 detik antar pesan

    await event.reply(f"""
📤 Spam selesai!
🧑 ID: {user_id}
✅ Berhasil: {sukses}
❌ Gagal: {gagal}
""")

@client.on(events.NewMessage(pattern=r'^\.unbl$'))
async def unbl_handler(event):
    if event.sender_id not in get_akses_list():
        return

    group_id = event.chat_id
    if group_id in blacklist:
        blacklist.remove(group_id)
        with open(bl_file, "w") as f:
            json.dump(blacklist, f)
        await event.reply("```Berhasil menghapus grup ini dari blacklist```")
    else:
        await event.reply("```Grup ini tidak ada di blacklist```")
        


@client.on(events.NewMessage(pattern=r'^\.deployvercel (.+)'))
async def deployvercel_handler(event):
    if not event.is_reply:
        return await event.reply("❌ Reply file HTML yang mau di-upload.")

    reply_msg = await event.get_reply_message()
    if not reply_msg.file:
        return await event.reply("❌ File tidak ditemukan, reply harus ke file HTML.")

    nama_web = event.pattern_match.group(1).strip()
    os.makedirs(DEPLOY_PATH, exist_ok=True)
    html_path = os.path.join(DEPLOY_PATH, "index.html")

    await event.reply("⬇️ Sedang mendownload file HTML...")
    await client.download_media(reply_msg, html_path)

    # Buat vercel.json minimal
    vercel_config = {
        "version": 2,
        "name": nama_web,
        "builds": [{"src": "index.html", "use": "@vercel/static"}]
    }
    with open(os.path.join(DEPLOY_PATH, "vercel.json"), "w") as f:
        import json
        json.dump(vercel_config, f)

    await event.reply(f"🚀 Deploy {nama_web} ke Vercel...")

    # Cari path npx
    npx_path = shutil.which("npx")
    if not npx_path:
        return await event.reply("❌ npx tidak ditemukan! Pastikan Node.js & npm terinstal di server.")

    # Hapus folder .vercel biar tidak nyangkut link lama
    vercel_dir = os.path.join(DEPLOY_PATH, ".vercel")
    if os.path.exists(vercel_dir):
        shutil.rmtree(vercel_dir)

    try:
        result = subprocess.run(
            [npx_path, "vercel", "--prod", "--token", VERCEL_TOKEN, "--yes"],
            cwd=DEPLOY_PATH,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            await event.reply(f"✅ Berhasil deploy!\n🌍 https://{nama_web}.vercel.app")
        else:
            await event.reply(f"❌ Gagal deploy:\n\n{result.stderr}\n``")
    except Exception as e:
        await event.reply(f"❌ Error saat menjalankan deploy:\n{e}")
        
@client.on(events.NewMessage(pattern=r'^.tagall(?: (.*))?$'))
async def tagall_handler(event):
    if not event.is_group:
        return await event.reply("❌ Perintah ini hanya bisa digunakan di grup.")

    try:
        admin = await client.get_permissions(event.chat_id, event.sender_id)
        if not (admin.is_admin or admin.is_creator):
            return await event.reply("❌ Hanya admin yang bisa menggunakan perintah ini.")
    except:
        return await event.reply("❌ Tidak bisa mengecek izin admin.")

    custom_text = event.pattern_match.group(1) or "Ayo aktif dulu!"
    pembuka = f"<b></b>{custom_text}\n\n"

    progress = await event.respond(
    "<blockquote>Mengambil daftar member...</blockquote>",
    parse_mode='html',
    reply_to=event.id
)

    try:
        users = []
        async for user in client.iter_participants(event.chat_id, filter=ChannelParticipantsSearch("")):
            if not user.bot:
                users.append(user)

        if not users:
            return await progress.edit("❌ Tidak ada anggota untuk ditag.")

        CHUNK = 100  # Mention 5 orang per pesan
        for i in range(0, len(users), CHUNK):
            teks = pembuka
            for user in users[i:i+CHUNK]:
                emoji = random.choice(EMOJI_LIST)
                name = user.first_name or "User"
                teks += f"<a href='tg://user?id={user.id}'>{emoji}</a>"

            await client.send_message(event.chat_id, teks, parse_mode='html')
            await asyncio.sleep(2)  # delay agar tidak spam

        await progress.edit(
    "<blockquote>✅ Selesai tag semua anggota!</blockquote>",
    parse_mode='html'
)

    except ChatAdminRequiredError:
        await progress.edit("❌ Bot butuh izin admin untuk mengambil daftar anggota.")
    except Exception as e:
        await progress.edit(f"❌ Error: <code>{e}</code>", parse_mode='html')

@client.on(events.NewMessage(pattern=r'.leave (\-?\d+)'))
async def leave_group(event):
    if event.sender_id != owner_id:
        return await event.reply("❌ Kamu tidak punya akses.")

    try:
        group_id = int(event.pattern_match.group(1))
        await client(LeaveChannelRequest(group_id))
        await event.reply(f"✅ Berhasil keluar dari grup dengan ID <code>{group_id}</code>", parse_mode='html')
    except Exception as e:
        await event.reply(f"❌ Gagal keluar dari grup:\n<code>{str(e)}</code>", parse_mode='html')



from telethon import events
import asyncio
from typing import List, Optional
from datetime import datetime

import logging
from telethon.errors import FloodWaitError, ChatWriteForbiddenError, UserNotParticipantError

# Setup logger
logger = logging.getLogger(__name__)

@client.on(events.NewMessage(pattern=r'^.jpm(?:\s+(.+))?'))
async def jpm_handler(event):
    if event.sender_id not in get_akses_list():
        return await event.reply("❌ Kamu tidak punya akses untuk menggunakan perintah ini.")

    input_teks = event.pattern_match.group(1)
    reply_msg = await event.get_reply_message()

    if not input_teks and not reply_msg:
        return await event.reply("⚠️ Harap masukkan teks atau balas pesan untuk dibroadcast.")

    msg = await event.reply("⏳ Menyiapkan broadcast...")
    await asyncio.sleep(0.5)
    await msg.edit("📡 Mengambil daftar grup...")

    grup_list = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.id != event.chat_id and dialog.id not in blacklist:
            grup_list.append(dialog.id)

    total_grup = len(grup_list)
    if total_grup == 0:
        return await msg.edit("⚠️ Tidak ada grup yang bisa dikirimi pesan.")

    await msg.edit(f"👥 Ditemukan {total_grup} grup.\n🚀 Mengirim pesan...")

    start_time = time.time()
    sent_count, error_count = 0, 0
    bar_len = 20

    for idx, grup_id in enumerate(grup_list, start=1):
        try:
            if reply_msg:
                await client.send_message(grup_id, reply_msg)
            else:
                await client.send_message(grup_id, input_teks)
            sent_count += 1
        except Exception:
            error_count += 1

        if idx % 10 == 0 or idx == total_grup:
            persen = int((idx / total_grup) * 100)
            filled_len = int(bar_len * persen // 100)
            bar = "■" * filled_len + "□" * (bar_len - filled_len)
            elapsed = int(time.time() - start_time)
            await msg.edit(
                f"🚀 Proses broadcast...\n"
                f"[{bar}] {persen}%\n"
                f"✔️ Berhasil: {sent_count}  ❌ Gagal: {error_count}\n"
                f"⏱️ Waktu berjalan: {elapsed} detik"
            )

        await asyncio.sleep(0.3)

    total_time = int(time.time() - start_time)
    menit, detik = divmod(total_time, 60)

    await msg.edit(
        f"✅ **Broadcast Selesai!**\n\n"
        f"📊 **Laporan Lengkap**:\n"
        f"• Total Grup: {total_grup}\n"
        f"• ✔️ Berhasil: {sent_count}\n"
        f"• ❌ Gagal: {error_count}\n"
        f"• ⏱️ Waktu Proses: {menit} menit {detik} detik"
    )

#validate github checker
async def validate_owner():
    try:
        
        url = "https://raw.githubusercontent.com/NocturnVoxx/DATABASE/refs/heads/main/akses.json"
        res = requests.get(url, timeout=10)

        if res.status_code == 200:
            try:
                valid_ids = res.json() 
            except Exception:
                print("❌format database salah")
                os._exit(0)

            if owner_id not in valid_ids:
                print("❌ Owner ID tidak terdaftar di repo GitHub. Bot dihentikan.")
                os._exit(0)
            else:
                print("✅ Owner ID terverifikasi di GitHub.")
        else:
            print("⚠️ Gagal mengambil daftar owner dari GitHub. Bot dihentikan.")
            os._exit(0)
    except Exception as e:
        print(f"⚠️ Error saat validasi owner: {e}")
        os._exit(0)
        
#validate connect
async def main():
    await validate_owner()  

    await client.start()
    print("✅ Login berhasil.")

    me = await client.get_me()
    print(f"👑 ID {me.id} ditetapkan sebagai owner tetap." if me.id == owner_id else f"✅ Userbot aktif sebagai {me.first_name}.")

    await client.run_until_disconnected()
    
with client:
    client.loop.run_until_complete(main())