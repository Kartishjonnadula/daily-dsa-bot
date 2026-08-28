import os
import discord
from datetime import datetime
from zoneinfo import ZoneInfo
from discord import app_commands
from dotenv import load_dotenv
from neet_code.problems import load_problems
from neet_code.rotation import (select_daily_problems)
from neet_code.scheduler import (create_daily_task)
from neet_code.database import (get_current_rotation,get_used_problem_ids)
from neet_code.database import (get_registered_users,get_current_rotation,get_used_problem_ids,initialize_database,register_user,unregister_user)

footerIcon = discord.File("assets/icon.png", filename="icon.png")

# ---- MESSAGE FORMAT ----
def build_problem_message(problems):
    lines = ["🧠 **NeetCode Daily**","","Today's two problems:",""]
    for index, problem in enumerate(problems,start=1):
        lines.append(f"**{index}.[{problem['title']}]({problem['url']})**")
        lines.append(f"Difficulty: `{problem['difficulty']}`")
        lines.append(f"Category: `{problem['category']}`")
        lines.append("")
    lines.append("Good luck! 💪")
    return "\n".join(lines)

# ---- CONFIG ----
load_dotenv()
INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN: raise RuntimeError("DISCORD_TOKEN is missing from .env")

# ---- DISCORD INITIALIZATION ----
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)
daily_task = create_daily_task(client)

# ---- READY ----
@client.event
async def on_ready():
    initialize_database()
    synced = await tree.sync()
    print(f"Logged in as {client.user}")
    print(f"Synced {len(synced)} commands:")
    for command in synced: print(f"  /{command.name}")
    if not daily_task.is_running():
        daily_task.start()
        print("Daily scheduler started.")
        print("Daily problems: 12:00 PM IST")


# ---- BOT COMMANDS ----
@tree.command(name="unregister",description="Stop receiving NeetCode Daily in this server")
@tree.command(name="register",description="Register yourself for NeetCode Daily in this channel")
@tree.command(name="ping",description="Check if the bot is alive")
@tree.command(name="status",description="Show NeetCode Daily registration status")
@tree.command(name="problems",description="Get today's two NeetCode problems")
@tree.command(name="rotation",description="Show the current NeetCode rotation")


# ---- IMPLEMENTATIONS ----
async def ping(interaction: discord.Interaction): await interaction.response.send_message("🏓 Pong!")

async def register(interaction: discord.Interaction,):
    if interaction.guild_id is None: await interaction.response.send_message("❌ You can only register inside a Discord server.",ephemeral=True); return
    register_user(user_id=interaction.user.id,guild_id=interaction.guild_id,channel_id=interaction.channel_id)
    embed = discord.Embed(
            title="Registration Confirmed",
            description=(f"**{interaction.user.display_name}**, you're all set.\n\nYou've been registered for **NeetCode Daily** in {interaction.channel.mention}.\n\n"
                    "━━━━━━━━━━━━━━━━━━━━\n"
                    "🧠  **Daily Practice**\nBuild consistency. Sharpen your problem-solving.\n"
                    "━━━━━━━━━━━━━━━━━━━━"
                ),
                color=discord.Color.from_rgb(88, 101, 242)
            )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(
        text="NeetCode Daily  •  Two Problems a day.",
        icon_url="attachment://icon.png"
    )
    await interaction.response.send_message(embed=embed,file=footerIcon)

async def unregister(interaction: discord.Interaction):
    if interaction.guild_id is None:await interaction.response.send_message("❌ You can only unregister inside a Discord server.",ephemeral=True); return
    removed = unregister_user(user_id=interaction.user.id,guild_id=interaction.guild_id)
    if removed: await interaction.response.send_message(f"✅ {interaction.user.mention}, you have been unregistered from NeetCode Daily.")
    else:await interaction.response.send_message(f"ℹ️ {interaction.user.mention}, you were not registered.")

async def problems(interaction: discord.Interaction):
    today = datetime.now(INDIA_TIMEZONE).date().isoformat()
    try:selected = select_daily_problems(today)
    except Exception as error:
        print(f"Problem selection failed: {error}")
        await interaction.response.send_message("❌ I couldn't get today's problems.",ephemeral=True)
        return
    await interaction.response.send_message(build_problem_message(selected))

async def status(interaction: discord.Interaction):
    registrations = (get_registered_users())
    await interaction.response.send_message(f"📊 **NeetCode Daily**\n\nRegistered users: **{len(registrations)}**")

async def rotation(interaction: discord.Interaction):
    rotation = get_current_rotation()
    if rotation is None: await interaction.response.send_message("ℹ️ No active rotation yet."); return
    problems = load_problems()
    used_ids = get_used_problem_ids(rotation["id"])
    available = [problem for problem in problems if problem["id"] not in used_ids]
    await interaction.response.send_message(f" 🔄 **NeetCode Rotation**\n\n Rotation: **#{rotation['id']}**\n Used: **{len(used_ids)}**\n Remaining: **{len(available)}**\n Total: **{len(problems)}**")


# --- START ----
client.run(TOKEN)