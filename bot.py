import os
from datetime import datetime
from zoneinfo import ZoneInfo
from neet_code.database import (
    get_current_rotation,
    get_used_problem_ids,
)
from neet_code.problems import load_problems
import discord
from discord import app_commands
from dotenv import load_dotenv

from neet_code.database import (
    get_registered_users,
    get_current_rotation,
    get_used_problem_ids,
    initialize_database,
    register_user,
    unregister_user,
)
from neet_code.rotation import (
    select_daily_problems,
)
from neet_code.scheduler import (
    create_daily_task,
)


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

TOKEN = os.getenv(
    "DISCORD_TOKEN"
)

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing "
        "from .env"
    )


INDIA_TIMEZONE = ZoneInfo(
    "Asia/Kolkata"
)


# =========================================================
# DISCORD
# =========================================================

intents = discord.Intents.default()

client = discord.Client(
    intents=intents
)

tree = discord.app_commands.CommandTree(
    client
)

daily_task = create_daily_task(
    client
)


# =========================================================
# READY
# =========================================================

@client.event
async def on_ready():
    initialize_database()

    synced = await tree.sync()

    print(
        f"Logged in as {client.user}"
    )

    print(
        f"Synced {len(synced)} commands:"
    )

    for command in synced:
        print(
            f"  /{command.name}"
        )

    if not daily_task.is_running():
        daily_task.start()

        print(
            "Daily scheduler started."
        )

        print(
            "Daily problems: "
            "12:00 PM IST"
        )


# =========================================================
# /PING
# =========================================================

@tree.command(
    name="ping",
    description="Check if the bot is alive",
)
async def ping(
    interaction: discord.Interaction,
):
    await interaction.response.send_message(
        "🏓 Pong!"
    )


# =========================================================
# /REGISTER
# =========================================================

@tree.command(
    name="register",
    description=(
        "Register yourself for "
        "NeetCode Daily in this channel"
    ),
)
async def register(
    interaction: discord.Interaction,
):
    if interaction.guild_id is None:
        await interaction.response.send_message(
            "❌ You can only register "
            "inside a Discord server.",
            ephemeral=True,
        )
        return

    register_user(
        user_id=interaction.user.id,
        guild_id=interaction.guild_id,
        channel_id=interaction.channel_id,
    )

    await interaction.response.send_message(
        f"✅ {interaction.user.mention}, "
        f"you are now registered for "
        f"NeetCode Daily in this channel."
    )


# =========================================================
# /UNREGISTER
# =========================================================

@tree.command(
    name="unregister",
    description=(
        "Stop receiving NeetCode Daily "
        "in this server"
    ),
)
async def unregister(
    interaction: discord.Interaction,
):
    if interaction.guild_id is None:
        await interaction.response.send_message(
            "❌ You can only unregister "
            "inside a Discord server.",
            ephemeral=True,
        )
        return

    removed = unregister_user(
        user_id=interaction.user.id,
        guild_id=interaction.guild_id,
    )

    if removed:
        await interaction.response.send_message(
            f"✅ {interaction.user.mention}, "
            f"you have been unregistered "
            f"from NeetCode Daily."
        )
    else:
        await interaction.response.send_message(
            f"ℹ️ {interaction.user.mention}, "
            f"you were not registered."
        )


# =========================================================
# /PROBLEMS
# =========================================================

@tree.command(
    name="problems",
    description=(
        "Get today's two NeetCode problems"
    ),
)
async def problems(
    interaction: discord.Interaction,
):
    today = datetime.now(
        INDIA_TIMEZONE
    ).date().isoformat()

    try:
        selected = select_daily_problems(
            today
        )

    except Exception as error:
        print(
            f"Problem selection failed: "
            f"{error}"
        )

        await interaction.response.send_message(
            "❌ I couldn't get today's "
            "problems.",
            ephemeral=True,
        )

        return

    await interaction.response.send_message(
        build_problem_message(
            selected
        )
    )


# =========================================================
# /STATUS
# =========================================================

@tree.command(
    name="status",
    description=(
        "Show NeetCode Daily registration "
        "status"
    ),
)
async def status(
    interaction: discord.Interaction,
):
    registrations = (
        get_registered_users()
    )

    await interaction.response.send_message(
        f"📊 **NeetCode Daily**\n\n"
        f"Registered users: "
        f"**{len(registrations)}**"
    )


# =========================================================
# MESSAGE FORMAT
# =========================================================

def build_problem_message(
    problems,
):
    lines = [
        "🧠 **NeetCode Daily**",
        "",
        "Today's two problems:",
        "",
    ]

    for index, problem in enumerate(
        problems,
        start=1,
    ):
        lines.append(
            f"**{index}. "
            f"[{problem['title']}]"
            f"({problem['url']})**"
        )

        lines.append(
            f"Difficulty: "
            f"`{problem['difficulty']}`"
        )

        lines.append(
            f"Category: "
            f"`{problem['category']}`"
        )

        lines.append("")

    lines.append(
        "Good luck! 💪"
    )

    return "\n".join(lines)

@tree.command(
    name="rotation",
    description="Show the current NeetCode rotation",
)
async def rotation(
    interaction: discord.Interaction,
):
    rotation = get_current_rotation()

    if rotation is None:
        await interaction.response.send_message(
            "ℹ️ No active rotation yet."
        )
        return

    problems = load_problems()

    used_ids = get_used_problem_ids(
        rotation["id"]
    )

    available = [
        problem
        for problem in problems
        if problem["id"] not in used_ids
    ]

    await interaction.response.send_message(
        f"🔄 **NeetCode Rotation**\n\n"
        f"Rotation: **#{rotation['id']}**\n"
        f"Used: **{len(used_ids)}**\n"
        f"Remaining: **{len(available)}**\n"
        f"Total: **{len(problems)}**"
    )
# =========================================================
# START
# =========================================================

client.run(TOKEN)