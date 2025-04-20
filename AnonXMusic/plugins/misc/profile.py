from pyrogram import Client, filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery
)
from datetime import datetime, timedelta
from operator import itemgetter
from AnonXMusic import app
from AnonXMusic.utils.database import song_stats_db
import random

# Default placeholder image
DEFAULT_IMAGES = [
    "https://graph.org/file/f20072ed0125e05c4a179-749b57b82ab375adfb.jpg",
    "https://telegra.ph/file/xxxx2.jpg",
    "https://telegra.ph/file/xxxx3.jpg"
]

# ───── Helpers ─────────────────────────────────────────

async def update_song_count(group_id: int, user_id: int):
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        await song_stats_db.update_one(
            {"group_id": group_id},
            {
                "$inc": {
                    "overall_count": 1,
                    f"daily.{today}": 1,
                    f"users.{user_id}": 1
                }
            },
            upsert=True
        )
        print("Song count updated successfully!")
    except Exception as e:
        print(f"Error updating song count: {e}")

async def get_user_profile(user_id: int):
    user_counter = {}
    async for rec in song_stats_db.find({}):
        for u, c in rec.get("users", {}).items():
            user_counter[u] = user_counter.get(u, 0) + c

    sorted_users = sorted(user_counter.items(), key=itemgetter(1), reverse=True)
    count = user_counter.get(str(user_id), 0)
    rank = next((i+1 for i, (u, _) in enumerate(sorted_users) if u == str(user_id)), None)
    return count, rank
    print(f"User counter: {user_counter}")
# ───── Handlers ────────────────────────────────────────

@app.on_message(filters.command("leaderboard") & filters.group)
async def leaderboard_menu(client: Client, message: Message):
    print("Leaderboard command received")
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎶 ᴏᴠᴇʀᴀʟʟ ᴛᴏᴘ ɢʀᴏᴜᴘs", callback_data="overall_songs")],
        [InlineKeyboardButton("📅 ᴛᴏᴅᴀʏ ᴛᴏᴘ ɢʀᴏᴜᴘs", callback_data="today_songs")],
        [InlineKeyboardButton("📊 ᴡᴇᴇᴋʟʏ ᴛᴏᴘ ɢʀᴏᴜᴘs", callback_data="weekly_songs")],
        [InlineKeyboardButton("🏆 ᴏᴠᴇʀᴀʟʟ ᴛᴏᴘ ᴜsᴇʀs", callback_data="top_users")], 
        [InlineKeyboardButton("⏹ ᴄʟᴏsᴇ", callback_data="close_profile")]
    ])
    await message.reply_text("📈 Music Leaderboard — choose one:", reply_markup=kb)


@app.on_message(filters.command("profile") & filters.group)
async def user_profile(client: Client, message: Message):
    uid = message.from_user.id
    count, rank = await get_user_profile(uid)

    try:
        photos = await client.get_user_profile_photos(uid)
        if photos.total_count > 0:
            photo = photos.photos[0][0].file_id
        else:
            photo = random.choice(DEFAULT_IMAGES)
    except Exception as e:
        print(e)
        photo = random.choice(DEFAULT_IMAGES)

    uname = message.from_user.username or "N/A"
    name = message.from_user.first_name

    if count == 0:
        text = (
            f"🎶 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 𝗠𝘂𝘀𝗶𝗰 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 🎶\n\n"
            f"👤 𝗡𝗮𝗺𝗲: {name}\n"
            f"✨ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{uname}\n"
            f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: {uid}\n\n"
            f"🎧 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱: 0\n"
            f"📊 𝗥𝗮𝗻𝗸: Unranked\n\n"
            f"💡 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲𝗻'𝘁 𝗽𝗹𝗮𝘆𝗲𝗱 𝗮𝗻𝘆 𝘀𝗼𝗻𝗴𝘀 𝘆𝗲𝘁. 𝗦𝘁𝗮𝗿𝘁 𝘃𝗶𝗯𝗶𝗻𝗴 𝘄𝗶𝘁𝗵 𝘁𝗵𝗲 𝗽𝗹𝗮𝘆𝗹𝗶𝘀𝘁!"
        )
    else:
        text = (
            f"🎶 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 𝗠𝘂𝘀𝗶𝗰 𝗣𝗿𝗼𝗳𝗶𝗹𝗲 🎶\n\n"
            f"👤 𝗡𝗮𝗺𝗲: {name}\n"
            f"✨ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: @{uname}\n"
            f"🆔 𝗨𝘀𝗲𝗿 𝗜𝗗: {uid}\n\n"
            f"🎧 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱: {count}\n"
            f"📊 𝗥𝗮𝗻𝗸: #{rank}\n\n"
            f"🔥 𝗞𝗲𝗲𝗽 𝘁𝗵𝗲 𝗯𝗲𝗮𝘁𝘀 𝗮𝗹𝗶𝘃𝗲!"
        )

    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("⏹ 𝗖𝗹𝗼𝘀𝗲", callback_data="close_profile")]]
    )

    await message.reply_photo(photo, caption=text, reply_markup=kb)

@app.on_callback_query(filters.regex("^close_profile$"))
async def close_profile(client: Client, cq: CallbackQuery):
    await cq.message.delete()

@app.on_callback_query(filters.regex("^(overall_songs|today_songs|weekly_songs|top_users)$"))
async def leaderboard_callback(client: Client, cq: CallbackQuery):
    data = cq.data
    print(f"Callback received: {data}")
    if data == "overall_songs":
        await show_overall_leaderboard(client, cq)
    elif data == "today_songs":
        await show_today_leaderboard(client, cq)
    elif data == "weekly_songs":
        await show_weekly_leaderboard(client, cq)
    elif data == "top_users":
        await show_top_users(client, cq)

# ───── Leaderboard Views ───────────────────────────────

async def show_overall_leaderboard(client: Client, cq: CallbackQuery):
    leaderboard = []
    async for record in song_stats_db.find({}):
        leaderboard.append((record["group_id"], record.get("overall_count", 0)))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard:
        return await cq.message.edit_text("No data found!")

    text = "🏆 𝗧𝗼𝗽 𝟭𝟬 𝗚𝗿𝗼𝘂𝗽𝘀 (𝗢𝘃𝗲𝗿𝗮𝗹𝗹 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱) 🏆\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"{i}. {chat.title} — {count} songs\n"
        except:
            text += f"{i}. [Group ID: {group_id}] — {count} songs\n"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
    await cq.message.edit_text(text, reply_markup=kb)


async def show_today_leaderboard(client: Client, cq: CallbackQuery):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    leaderboard = []
    async for record in song_stats_db.find({}):
        count = record.get("daily", {}).get(today, 0)
        leaderboard.append((record["group_id"], count))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard or leaderboard[0][1] == 0:
        return await cq.message.edit_text("No songs played today!")

    text = "📅 𝗧𝗼𝗽 𝟭𝟬 𝗚𝗿𝗼𝘂𝗽𝘀 (𝗧𝗼𝗱𝗮𝘆’𝘀 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱) 📅\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"{i}. {chat.title} — {count} songs\n"
        except:
            text += f"{i}. [Group ID: {group_id}] — {count} songs\n"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
    await cq.message.edit_text(text, reply_markup=kb)

async def show_weekly_leaderboard(client: Client, cq: CallbackQuery):
    today = datetime.utcnow()
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    leaderboard = []

    async for record in song_stats_db.find({}):
        total = sum(record.get("daily", {}).get(d, 0) for d in dates)
        leaderboard.append((record["group_id"], total))

    leaderboard = sorted(leaderboard, key=itemgetter(1), reverse=True)[:10]
    if not leaderboard or leaderboard[0][1] == 0:
        return await cq.message.edit_text("No songs played this week!")

    text = "📊 𝗧𝗼𝗽 𝟭𝟬 𝗚𝗿𝗼𝘂𝗽𝘀 (𝗧𝗵𝗶𝘀 𝗪𝗲𝗲𝗸’𝘀 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱) 📊\n\n"
    for i, (group_id, count) in enumerate(leaderboard, 1):
        try:
            chat = await client.get_chat(group_id)
            text += f"{i}. {chat.title} — {count} songs\n"
        except:
            text += f"{i}. [Group ID: {group_id}] — {count} songs\n"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
    await cq.message.edit_text(text, reply_markup=kb)

async def show_top_users(client: Client, cq: CallbackQuery):
    user_counter = {}
    async for record in song_stats_db.find({}):
        for user_id, count in record.get("users", {}).items():
            user_counter[user_id] = user_counter.get(user_id, 0) + count

    leaderboard = sorted(user_counter.items(), key=itemgetter(1), reverse=True)[:10]
    if not leaderboard:
        return await cq.message.edit_text("No user data found!")

    text = "🏆 𝗧𝗼𝗽 𝟭𝟬 𝗨𝘀𝗲𝗿𝘀 (𝗢𝘃𝗲𝗿𝗮𝗹𝗹 𝗦𝗼𝗻𝗴𝘀 𝗣𝗹𝗮𝘆𝗲𝗱) 🏆\n\n"
    for i, (user_id, count) in enumerate(leaderboard, 1):
        try:
            user = await client.get_users(int(user_id))
            text += f"{i}. {user.first_name} [{user.id}] — {count} songs\n"
        except:
            text += f"{i}. [{user_id}] — {count} songs\n"

    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_leaderboard")]])
    await cq.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)

@app.on_callback_query(filters.regex("^back_leaderboard$"))
async def back_to_leaderboard(client: Client, cq: CallbackQuery):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎶 ᴏᴠᴇʀᴀʟʟ ᴛᴏᴘ ɢʀᴏᴜᴘs", callback_data="overall_songs")],
        [InlineKeyboardButton("📅 ᴛᴏᴅᴀʏ ᴛᴏᴘ ɢʀᴏᴜᴘs", callback_data="today_songs")],
        [InlineKeyboardButton("📊 ᴡᴇᴇᴋʟʏ ᴛᴏᴘ ɢʀᴏᴜᴘs", callback_data="weekly_songs")],
        [InlineKeyboardButton("🏆 ᴏᴠᴇʀᴀʟʟ ᴛᴏᴘ ᴜsᴇʀs", callback_data="top_users")], 
        [InlineKeyboardButton("⏹ ᴄʟᴏsᴇ", callback_data="close_profile")]
    ])
    await cq.message.edit_text("📈 𝐌𝐮𝐬𝐢𝐜 𝐋𝐞𝐚𝐝𝐞𝐫𝐛𝐨𝐚𝐫𝐝𝐬 — choose one:", reply_markup=kb)

