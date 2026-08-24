from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from discord.ext import tasks

from .database import get_registered_users
from .rotation import select_daily_problems


INDIA_TIMEZONE = ZoneInfo("Asia/Kolkata")

# TESTING:
# Run once, one minute after the bot starts.
TEST_MODE = True


def create_daily_task(bot):
    if TEST_MODE:
        @tasks.loop(
            count=1,
            seconds=10,
        )
        async def daily_task():
            await send_daily_problems(bot)

    else:
        from datetime import time

        DAILY_TIME = time(
            hour=0,
            minute=10,
            second=0,
            tzinfo=INDIA_TIMEZONE,
        )

        @tasks.loop(time=DAILY_TIME)
        async def daily_task():
            await send_daily_problems(bot)

    return daily_task


async def send_daily_problems(bot):
    registrations = get_registered_users()

    if not registrations:
        print("No registered users.")
        return

    today = datetime.now(
        INDIA_TIMEZONE
    ).date().isoformat()

    try:
        problems = select_daily_problems(today)
    except Exception as error:
        print(
            f"Failed to select daily problems: {error}"
        )
        return

    users_by_channel = defaultdict(list)

    for registration in registrations:
        users_by_channel[
            registration["channel_id"]
        ].append(
            registration["user_id"]
        )

    message = build_message(problems)

    for channel_id, user_ids in users_by_channel.items():
        try:
            channel = bot.get_channel(channel_id)

            if channel is None:
                channel = await bot.fetch_channel(channel_id)

            mentions = " ".join(
                f"<@{user_id}>"
                for user_id in user_ids
            )

            final_message = (
                f"{mentions}\n\n"
                f"{message}"
            )

            await channel.send(final_message)

            print(
                f"Sent daily problems to "
                f"channel {channel_id}"
            )

        except Exception as error:
            print(
                f"Failed to send to channel "
                f"{channel_id}: {error}"
            )


def build_message(problems):
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
            f"Difficulty: `{problem['difficulty']}`"
        )

        lines.append(
            f"Category: `{problem['category']}`"
        )

        lines.append("")

    lines.append("Good luck! 💪")

    return "\n".join(lines)