from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from config import API_ID, API_HASH, BOT_TOKEN
from database import users
import random
import time

app = Client("AdvancedBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# ---------------- USER DATABASE ----------------

async def get_user(user_id):
    user = await users.find_one({"_id": user_id})
    if not user:
        user = {
            "_id": user_id,
            "xp": 0,
            "level": 1,
            "coins": 0,
            "last_daily": 0
        }
        await users.insert_one(user)
    return user


# ---------------- AUTO XP SYSTEM ----------------

@app.on_message(filters.group & filters.text)
async def auto_xp(client, message):
    if not message.from_user:
        return

    user = await get_user(message.from_user.id)

    new_xp = user["xp"] + 5
    level = user["level"]

    if new_xp >= level * 100:
        level += 1
        await message.reply(f"🎉 {message.from_user.mention} leveled up to {level}!")

    await users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"xp": new_xp, "level": level}}
    )


# ---------------- PROFILE ----------------

@app.on_message(filters.command("profile"))
async def profile(client, message):
    user = await get_user(message.from_user.id)

    await message.reply(
        f"👤 {message.from_user.mention}\n"
        f"⭐ Level: {user['level']}\n"
        f"🔥 XP: {user['xp']}\n"
        f"💰 Coins: {user['coins']}"
    )


# ---------------- DAILY ----------------

@app.on_message(filters.command("daily"))
async def daily_reward(client, message):
    user = await get_user(message.from_user.id)
    now = time.time()

    if now - user["last_daily"] < 86400:
        await message.reply("⏳ Already claimed today.")
        return

    coins = random.randint(50, 150)

    await users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"last_daily": now}, "$inc": {"coins": coins}}
    )

    await message.reply(f"🎁 You received {coins} coins!")


# ---------------- LEADERBOARD ----------------

@app.on_message(filters.command("leaderboard"))
async def leaderboard(client, message):
    top = users.find().sort("xp", -1).limit(10)

    text = "🏆 Top 10 Leaderboard\n\n"
    rank = 1
    async for user in top:
        text += f"{rank}. {user['_id']} - {user['xp']} XP\n"
        rank += 1

    await message.reply(text)


# ---------------- ADMIN SYSTEM ----------------

def admin_only(func):
    async def wrapper(client, message):
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            return await message.reply("❌ Admin only command.")
        return await func(client, message)
    return wrapper


@app.on_message(filters.command("mute") & filters.group)
@admin_only
async def mute(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=False)
        )
        await message.reply("🔇 User muted.")


@app.on_message(filters.command("unmute") & filters.group)
@admin_only
async def unmute(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            ChatPermissions(can_send_messages=True)
        )
        await message.reply("🔊 User unmuted.")


@app.on_message(filters.command("ban") & filters.group)
@admin_only
async def ban(client, message):
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply("🚫 User banned.")


@app.on_message(filters.command("unban") & filters.group)
@admin_only
async def unban(client, message):
    if len(message.command) > 1:
        user_id = int(message.command[1])
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply("✅ User unbanned.")


# ---------------- ANTI LINK ----------------

@app.on_message(filters.group & filters.text)
async def anti_link(client, message):
    if "http" in message.text or "t.me" in message.text:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.delete()
            await message.reply("🚫 Links not allowed!")


# ---------------- WELCOME ----------------

@app.on_message(filters.new_chat_members)
async def welcome(client, message):
    for user in message.new_chat_members:
        await message.reply(f"👋 Welcome {user.mention} to {message.chat.title}!")


app.run() 