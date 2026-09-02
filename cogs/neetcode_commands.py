import discord
from discord.ext import commands
from datetime import datetime
from discord import app_commands
from zoneinfo import ZoneInfo
from neet_code.problems import load_problems
from neet_code.rotation import (select_daily_problems)
from neet_code.database import (get_current_rotation,get_used_problem_ids)
from neet_code.database import (get_registered_users,get_current_rotation,get_used_problem_ids,register_user,unregister_user)
from message_formats.formats import build_problem_message


class NeetCodeCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- PING ----
    @app_commands.command(name="ping",description="Check if the bot is alive")
    async def ping(self, interaction: discord.Interaction): await interaction.response.send_message("🏓 Pong!")
        
    # ---- REGISTER ----
    @app_commands.command(name="register",description="Register yourself for NeetCode Daily in this channel")
    async def register(self, interaction: discord.Interaction,):
        if interaction.guild_id is None: await interaction.response.send_message("❌ You can only register inside a Discord server.",ephemeral=True); return
        register_user(user_id=interaction.user.id,guild_id=interaction.guild_id,channel_id=interaction.channel_id)
        await interaction.response.send_message(f"✅ {interaction.user.mention}, you are now registered for NeetCode Daily in this channel.")

    # ---- UNREGISTER ----
    @app_commands.command(name="unregister",description="Stop receiving NeetCode Daily in this server")
    async def unregister(self, interaction: discord.Interaction):
        if interaction.guild_id is None:await interaction.response.send_message("❌ You can only unregister inside a Discord server.",ephemeral=True); return
        removed = unregister_user(user_id=interaction.user.id,guild_id=interaction.guild_id)
        if removed: await interaction.response.send_message(f"✅ {interaction.user.mention}, you have been unregistered from NeetCode Daily.")
        else:await interaction.response.send_message(f"ℹ️ {interaction.user.mention}, you were not registered.")

    # ---- PROBLEMS ----
    @app_commands.command(name="problems",description="Get today's two NeetCode problems")
    async def problems(self, interaction: discord.Interaction):
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
        try:selected = select_daily_problems(today)
        except Exception as error:
            print(f"Problem selection failed: {error}")
            await interaction.response.send_message("❌ I couldn't get today's problems.",ephemeral=True)
            return
        await interaction.response.send_message(build_problem_message(selected))

    # ---- STATUS ---
    @app_commands.command(name="status",description="Show NeetCode Daily registration status")
    async def status(self, interaction: discord.Interaction):
        registrations = (get_registered_users())
        await interaction.response.send_message(f"📊 **NeetCode Daily**\n\nRegistered users: **{len(registrations)}**")

    # ---- ROTATION ----
    @app_commands.command(name="rotation",description="Show the current NeetCode rotation")
    async def rotation(self, interaction: discord.Interaction):
        rotation = get_current_rotation()
        if rotation is None: await interaction.response.send_message("ℹ️ No active rotation yet."); return
        problems = load_problems()
        used_ids = get_used_problem_ids(rotation["id"])
        available = [problem for problem in problems if problem["id"] not in used_ids]
        await interaction.response.send_message(f" 🔄 **NeetCode Rotation**\n\n Rotation: **#{rotation['id']}**\n Used: **{len(used_ids)}**\n Remaining: **{len(available)}**\n Total: **{len(problems)}**")

async def setup(bot):
    await bot.add_cog(NeetCodeCommands(bot))