import discord
from discord.ext import commands
import datetime
import asyncio
import random
import os
from keep_alive import keep_alive

# Setup intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands globally with Discord
        await self.tree.sync()
        print("Slash commands synced successfully!")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Bot is ready for action!")

# 1. GIVEAWAY SLASH COMMAND
@bot.tree.command(name="giveaway", description="Host a giveaway in the server")
@discord.app_commands.describe(duration="Duration in seconds", prize="Name of the prize")
@discord.app_commands.checks.has_permissions(manage_guild=True)
async def giveaway(interaction: discord.Interaction, duration: int, prize: str):
    await interaction.response.send_message(f"Starting giveaway for **{prize}**...", ephemeral=True)
    
    embed = discord.Embed(
        title="🎉 **GIVEAWAY TIME** 🎉",
        description=f"Prize: **{prize}**\nReact with 🎉 to enter!\nHosted by: {interaction.user.mention}",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Ends in {duration} seconds.")
    
    g_msg = await interaction.channel.send(embed=embed)
    await g_msg.add_reaction("🎉")

    await asyncio.sleep(duration)

    new_msg = await interaction.channel.fetch_message(g_msg.id)
    
    users = []
    for reaction in new_msg.reactions:
        if str(reaction.emoji) == "🎉":
            async for user in reaction.users():
                if not user.bot:
                    users.append(user)

    if len(users) > 0:
        winner = random.choice(users)
        await interaction.channel.send(f"🎊 Congratulations {winner.mention}! You won the **{prize}**!")
    else:
        await interaction.channel.send("❌ Giveaway cancelled. No valid entries.")

# 2. PURGE SLASH COMMAND
@bot.tree.command(name="purge", description="Delete a specific number of messages")
@discord.app_commands.describe(amount="Number of messages to delete")
@discord.app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Successfully deleted {len(deleted)} messages.", ephemeral=True)

# 3. TIMEOUT SLASH COMMAND
@bot.tree.command(name="timeout", description="Timeout a server member")
@discord.app_commands.describe(member="The member to timeout", minutes="Duration in minutes", reason="Reason for timeout")
@discord.app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "No reason provided"):
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await interaction.response.send_message(f"🔇 {member.mention} has been timed out for {minutes} minutes. Reason: {reason}")

# 4. KICK SLASH COMMAND
@bot.tree.command(name="kick", description="Kick a member from the server")
@discord.app_commands.describe(member="The member to kick", reason="Reason for kicking")
@discord.app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member.mention} has been kicked from the server. Reason: {reason}")

# Error handling for slash command permissions
@giveaway.error
@purge.error
@timeout.error
@kick.error
async def slash_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.MissingPermissions):
        if interaction.response.is_done():
            await interaction.followup.send("❌ You do not have permissions to use this command!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ You do not have permissions to use this command!", ephemeral=True)

# Start Flask Keep-Alive Server
keep_alive()

# Run Bot using Render Environment Variable
bot.run(os.environ.get("MTUzOTk5MjY5ODU0NTYzNTM1OA.G32Xon.iTeVq_xvXe4Cjw0tf5_skXufTjUoF4b3GO-E9Q"))
                                             
