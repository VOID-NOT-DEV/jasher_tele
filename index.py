# bot_resmi.py
import os, json, subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from telethon import TelegramClient
from dotenv import load_dotenv
load_dotenv()
# ========= KONFIGURASI =========
BOT_TOKEN  = os.getenv("BOT_TOKEN", "ISI_TOKEN_BOT_RESMI")
API_ID     = int(os.getenv("API_ID", "123456"))     # API_ID kamu
API_HASH   = os.getenv("API_HASH", "API_HASH_KAMU") # API_HASH kamu
OWNER_MAIN = int(os.getenv("OWNER_ID", "0"))        # Owner utama (super admin)
SESS_DIR   = "sessions"
AKSES_FILE = "akses.json"

os.makedirs(SESS_DIR, exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(bot)

LOGIN_STATE = {}   # {telegram_admin_id: {"phone": str, "client": TelegramClient}}
PROCESSES   = {}   # {phone: subprocess.Popen}


# ========= UTIL AKSES =========
def _default_akses():
    return {"murid": [], "partner": [], "owner": []}

def load_akses():
    if not os.path.exists(AKSES_FILE):
        with open(AKSES_FILE, "w") as f:
            json.dump(_default_akses(), f, indent=2)
    with open(AKSES_FILE, "r") as f:
        return json.load(f)

def save_akses(data):
    with open(AKSES_FILE, "w") as f:
        json.dump(data, f, indent=2)

def role_of(uid: int) -> str:
    """Balikkan role user: 'owner_main', 'owner', 'partner', 'murid', 'none'."""
    data = load_akses()
    if uid == OWNER_MAIN:
        return "owner_main"
    if uid in data.get("owner", []):
        return "owner"
    if uid in data.get("partner", []):
        return "partner"
    if uid in data.get("murid", []):
        return "murid"
    return "none"

def can_manage(uid: int, target: str) -> bool:
    """
    Cek apakah uid boleh add/del role target.
    target: 'owner', 'partner', 'murid'
    """
    r = role_of(uid)
    if r == "owner_main":
        return True  # full akses
    if r == "owner":
        return target in ["partner", "murid"]   # ❌ tidak bisa kelola owner
    if r == "partner":
        return target == "murid"
    return False

def cek_akses(uid: int) -> bool:
    return role_of(uid) in ["owner_main", "owner", "partner", "murid"]

def normalize_phone(s: str) -> str:
    s = s.strip()
    if not s.startswith("+"):
        raise ValueError("Nomor harus diawali '+' contoh: +628123456789")
    return s

def session_path_for(phone: str) -> str:
    safe = phone.replace("/", "_")
    return os.path.join(SESS_DIR, f"{safe}.session")


# ========= MANAJEMEN PROSES UBOT =========

async def help_cmd(msg: types.Message):
    uid = msg.from_user.id
    role = role_of(uid)

    teks = [f"📖 Daftar Fitur untuk {role.upper()}"]

    # umum (semua role yg terdaftar bisa akses)
    teks.append("\n🔹 **Umum:**")
    teks.append("/whoami - Cek role kamu")
    teks.append("/listubot - Lihat daftar userbot")
    teks.append("/buatubot +62xxx - Buat userbot (login pakai nomor)")
    teks.append("/otp 12345 - Verifikasi OTP saat buat ubot")
    teks.append("/startubot +62xxx - Start userbot yang sudah ada session")
    teks.append("/stopubot +62xxx - Stop userbot aktif")

    # khusus partner & owner & owner_main
    if role in ["partner", "owner", "owner_main"]:
        teks.append("\n🤝 **Kelola Murid:**")
        teks.append("/addmurjs <id> - Tambah murid")
        teks.append("/delmurjs <id> - Hapus murid")

    # khusus owner biasa & owner_main
    if role in ["owner", "owner_main"]:
        teks.append("\n👑 **Kelola Partner:**")
        teks.append("/addptjs <id> - Tambah partner")
        teks.append("/delptjs <id> - Hapus partner")

    # khusus owner_main saja
    if role == "owner_main":
        teks.append("\n👑 **Kelola Owner:**")
        teks.append("/addownjs <id> - Tambah owner")
        teks.append("/delownjs <id> - Hapus owner")

    teks.append("\nℹ️ Gunakan /whoami untuk melihat role kamu.")
    await msg.reply("\n".join(teks))

def start_userbot(phone: str):
    spath = session_path_for(phone)
    env = os.environ.copy()
    env["SESSION_FILE"] = spath    # patch di ubot.py wajib
    env["API_ID"]   = str(API_ID)
    env["API_HASH"] = str(API_HASH)
    proc = subprocess.Popen(["python3", "ubot.py"], env=env)
    PROCESSES[phone] = proc

def stop_userbot(phone: str):
    proc = PROCESSES.get(phone)
    if proc:
        proc.terminate()
        proc.wait(timeout=10)
        del PROCESSES[phone]


# ========= COMMAND: MANAJEMEN ROLE =========
async def add_to_role(msg: types.Message, role: str):
    if not can_manage(msg.from_user.id, role):
        return await msg.reply(f"❌ Kamu tidak punya izin menambah {role}.")
    arg = msg.get_args().strip()
    if not arg.isdigit():
        return await msg.reply(f"⚠️ Format: /add{role[:2]}js 123456789")
    uid = int(arg)
    data = load_akses()
    if uid not in data[role]:
        data[role].append(uid)
        save_akses(data)
        return await msg.reply(f"✅ {uid} ditambahkan ke {role}.")
    await msg.reply(f"⚠️ User sudah ada di {role}.")

async def del_from_role(msg: types.Message, role: str):
    if not can_manage(msg.from_user.id, role):
        return await msg.reply(f"❌ Kamu tidak punya izin menghapus {role}.")
    arg = msg.get_args().strip()
    if not arg.isdigit():
        return await msg.reply(f"⚠️ Format: /del{role[:2]}js 123456789")
    uid = int(arg)
    data = load_akses()
    if uid in data[role]:
        data[role].remove(uid)
        save_akses(data)
        return await msg.reply(f"🗑️ {uid} dihapus dari {role}.")
    await msg.reply(f"❌ User tidak ada di {role}.")

async def whoami(msg: types.Message):
    uid = msg.from_user.id
    role = role_of(uid)
    if role == "none":
        return await msg.reply(f"👤 ID kamu: {uid}\n❌ Kamu belum terdaftar di akses.json")
    elif role == "owner_main":
        return await msg.reply(f"👑 ID kamu: {uid}\nRole: OWNER UTAMA (akses penuh)")
    elif role == "owner":
        return await msg.reply(f"👑 ID kamu: {uid}\nRole: Owner Biasa")
    elif role == "partner":
        return await msg.reply(f"🤝 ID kamu: {uid}\nRole: Partner")
    elif role == "murid":
        return await msg.reply(f"📚 ID kamu: {uid}\nRole: Murid")

# Murid
@dp.message_handler(commands=["addmurjs"])
async def _(msg): await add_to_role(msg, "murid")
@dp.message_handler(commands=["delmurjs"])
async def _(msg): await del_from_role(msg, "murid")
@dp.message_handler(commands=["whoami"])

# Partner
@dp.message_handler(commands=["addptjs"])
async def _(msg): await add_to_role(msg, "partner")
@dp.message_handler(commands=["delptjs"])
async def _(msg): await del_from_role(msg, "partner")

# Owner (hanya owner_main yg boleh)
@dp.message_handler(commands=["addownjs"])
async def _(msg): await add_to_role(msg, "owner")
@dp.message_handler(commands=["delownjs"])
async def _(msg): await del_from_role(msg, "owner")

@dp.message_handler(commands=["help", "menu"])

# ========= COMMAND: BUAT UBOT =========
@dp.message_handler(commands=["buatubot"])
async def buatubot(msg: types.Message):
    if not cek_akses(msg.from_user.id):
        return await msg.reply("❌ Kamu belum terdaftar di akses.json")

    try:
        phone = normalize_phone(msg.get_args())
    except Exception as e:
        return await msg.reply(f"⚠️ {e}")

    spath  = session_path_for(phone)
    client = TelegramClient(spath, API_ID, API_HASH)

    await msg.reply(f"📲 Mengirim kode OTP ke {phone}...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            await msg.reply("🔑 Masukkan kode OTP dengan: /otp 12345")
            LOGIN_STATE[msg.from_user.id] = {"phone": phone, "client": client}
        else:
            await msg.reply("✅ Session sudah ada. Menjalankan userbot...")
            start_userbot(phone)
    except Exception as e:
        await msg.reply(f"❌ Error: {e}")


@dp.message_handler(commands=["otp"])
async def otp(msg: types.Message):
    kode = msg.get_args().strip()
    if not kode:
        return await msg.reply("⚠️ Format: /otp 12345")

    st = LOGIN_STATE.get(msg.from_user.id)
    if not st:
        return await msg.reply("❌ Tidak ada proses login aktif.")

    phone  = st["phone"]
    client = st["client"]

    try:
        await client.sign_in(phone, kode)
        await client.disconnect()
        await msg.reply("✅ Login berhasil. Menjalankan userbot...")
        start_userbot(phone)
    except Exception as e:
        return await msg.reply(f"❌ Gagal login: {e}")
    finally:
        LOGIN_STATE.pop(msg.from_user.id, None)


# ========= COMMAND: LIST / STOP / START UBOT =========
@dp.message_handler(commands=["listubot"])
async def listubot(msg: types.Message):
    if not cek_akses(msg.from_user.id):
        return await msg.reply("❌ Akses ditolak.")
    teks = ["📋 Userbot:"]
    if PROCESSES:
        teks.append("\nAktif:")
        for phone in PROCESSES:
            teks.append(f"• {phone}")
    else:
        teks.append("\nAktif: (kosong)")
    files = [f for f in os.listdir(SESS_DIR) if f.endswith(".session")]
    if files:
        teks.append("\nTersimpan:")
        for f in files:
            teks.append("• " + f[:-8])
    await msg.reply("\n".join(teks))

@dp.message_handler(commands=["stopubot"])
async def stopubot_cmd(msg: types.Message):
    if not cek_akses(msg.from_user.id):
        return await msg.reply("❌ Akses ditolak.")
    try:
        phone = normalize_phone(msg.get_args())
    except Exception as e:
        return await msg.reply(f"⚠️ {e}")
    if phone not in PROCESSES:
        return await msg.reply("❌ Userbot tidak ditemukan/aktif.")
    try:
        stop_userbot(phone)
        await msg.reply(f"🛑 Userbot {phone} dihentikan.")
    except Exception as e:
        await msg.reply(f"❌ Gagal stop: {e}")

@dp.message_handler(commands=["startubot"])
async def startubot_cmd(msg: types.Message):
    if not cek_akses(msg.from_user.id):
        return await msg.reply("❌ Akses ditolak.")
    try:
        phone = normalize_phone(msg.get_args())
    except Exception as e:
        return await msg.reply(f"⚠️ {e}")
    spath = session_path_for(phone)
    if not os.path.exists(spath):
        return await msg.reply("❌ Session tidak ditemukan. Login dulu dengan /buatubot.")
    if phone in PROCESSES:
        return await msg.reply("⚠️ Sudah aktif.")
    try:
        start_userbot(phone)
        await msg.reply(f"✅ Userbot {phone} dijalankan.")
    except Exception as e:
        await msg.reply(f"❌ Gagal start: {e}")


# ========= RUN =========
if __name__ == "__main__":
    print("Bot resmi berjalan...")
    executor.start_polling(dp, skip_updates=True)