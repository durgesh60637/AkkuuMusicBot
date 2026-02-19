import os
import random
import asyncio
import sqlite3
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

# ---------------- CONFIG (Railway Ready) ----------------
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

app = Client("CombinedBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("economy.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    kills INTEGER DEFAULT 0,
    status TEXT DEFAULT 'alive'
)
""")
conn.commit()

# ---------------- FUNCTIONS ----------------

def get_user(user_id):
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    data = c.fetchone()

    if not data:
        c.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
        conn.commit()
        return {"balance": 0, "kills": 0, "status": "alive"}

    return {
        "balance": data[1],
        "kills": data[2],
        "status": data[3]
    }


def update_user(user_id, balance=None, kills=None, status=None):
    data = get_user(user_id)

    balance = balance if balance is not None else data["balance"]
    kills = kills if kills is not None else data["kills"]
    status = status if status is not None else data["status"]

    c.execute(
        "UPDATE users SET balance=?, kills=?, status=? WHERE user_id=?",
        (balance, kills, status, user_id)
    )
    conn.commit()


# ---------------- COOLDOWN SYSTEM ----------------
cooldowns = set()

def on_cooldown(user_id, cmd, seconds):
    key = f"{user_id}_{cmd}"
    if key in cooldowns:
        return True

    cooldowns.add(key)

    async def remove():
        await asyncio.sleep(seconds)
        cooldowns.discard(key)

    asyncio.create_task(remove())
    return False


# ---------------- BASIC TEST ----------------

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    await message.reply_text("✅ Bot is working in Group & Private!")


@app.on_message(filters.group)
async def group_check(client, message):
    print("Group message received:", message.text)


# ---------------- WALLET COMMANDS ----------------

@app.on_message(filters.command("collect"))
async def collect(client, message: Message):
    user_id = message.from_user.id

    if on_cooldown(user_id, "collect", 86400):
        return await message.reply_text("⏳ You already claimed today.")

    data = get_user(user_id)
    update_user(user_id, balance=data["balance"] + 1000)

    await message.reply_text("💸 1000 coins added to your wallet!")


@app.on_message(filters.command("wallet"))
async def wallet(client, message: Message):
    user_id = message.from_user.id
    data = get_user(user_id)

    await message.reply_text(
        f"💰 Balance: {data['balance']}\n"
        f"⚔ Kills: {data['kills']}\n"
        f"❤️ Status: {data['status']}"
    )


# ---------------- ATTACK (GROUP ONLY) ----------------

@app.on_message(filters.command("attack") & filters.group)
async def attack(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("⚠ Reply to someone to attack.")

    attacker = message.from_user
    victim = message.reply_to_message.from_user

    victim_data = get_user(victim.id)

    if victim_data["status"] == "dead":
        return await message.reply_text("💀 This user is already dead.")

    reward = random.randint(100, 300)

    attacker_data = get_user(attacker.id)

    update_user(victim.id, status="dead")
    update_user(
        attacker.id,
        balance=attacker_data["balance"] + reward,
        kills=attacker_data["kills"] + 1
    )

    await message.reply_text(
        f"⚔ {attacker.first_name} attacked {victim.first_name}!\n"
        f"💰 Earned: {reward} coins!"
    )


print("🔹 Combined Bot is starting...")
app.run()