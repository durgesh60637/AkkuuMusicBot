import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *

app = Client(
    "SuperMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ================= START =================

@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{client.me.username}?startgroup=true")],
        [InlineKeyboardButton("Support Group", url=SUPPORT_GROUP),
         InlineKeyboardButton("Channel", url=SUPPORT_CHANNEL)]
    ])
    await message.reply_text(
        "🔥 Super Music + Management Bot Active!",
        reply_markup=buttons
    )

    if message.from_user.id == OWNER_ID:
        await message.reply_text("👑 Hello Owner!")

# ================= ADMIN COMMANDS =================

@app.on_message(filters.command("mute") & filters.group)
async def mute(_, message):
    if message.reply_to_message:
        await message.chat.restrict_member(
            message.reply_to_message.from_user.id,
            permissions={}
        )
        await message.reply("🔇 User Muted")

@app.on_message(filters.command("unmute") & filters.group)
async def unmute(_, message):
    if message.reply_to_message:
        await message.chat.unban_member(
            message.reply_to_message.from_user.id
        )
        await message.reply("🔊 User Unmuted")

@app.on_message(filters.command("ban") & filters.group)
async def ban(_, message):
    if message.reply_to_message:
        await message.chat.ban_member(
            message.reply_to_message.from_user.id
        )
        await message.reply("🚫 User Banned")

@app.on_message(filters.command("unban") & filters.group)
async def unban(_, message):
    if message.reply_to_message:
        await message.chat.unban_member(
            message.reply_to_message.from_user.id
        )
        await message.reply("♻️ User Unbanned")

@app.on_message(filters.command("pin") & filters.group)
async def pin(_, message):
    if message.reply_to_message:
        await message.reply_to_message.pin()
        await message.reply("📌 Pinned")

@app.on_message(filters.command("unpin") & filters.group)
async def unpin(_, message):
    await message.chat.unpin_all_messages()
    await message.reply("📌 All Unpinned")

# ================= TAG ALL =================

@app.on_message(filters.command("tagall") & filters.group)
async def tagall(client, message):
    members = []
    async for m in client.get_chat_members(message.chat.id):
        members.append(m.user.mention)

    text = " ".join(members)
    await message.reply(text[:4000])

# ================= BROADCAST =================

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /broadcast text")

    text = message.text.split(None, 1)[1]

    async for dialog in client.get_dialogs():
        try:
            await client.send_message(dialog.chat.id, text)
        except:
            pass

    await message.reply("📢 Broadcast Sent")

# ================= OWNER =================

@app.on_message(filters.command("owner"))
async def owner(_, message):
    await message.reply(f"👑 Owner ID: `{OWNER_ID}`")

# ================= RUN =================

app.run()