import discord
from discord.ext import commands
import datetime
import pytz
import requests
import json
import os
import platform
import psutil
import asyncio
from typing import Optional

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = {}

    @commands.command(name='serverinfo', help='Get information about the server')
    async def serverinfo(self, ctx):
        guild = ctx.guild
        
        # Get member counts
        total_members = len(guild.members)
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bot_count = len([m for m in guild.members if m.bot])
        
        # Get channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Create embed
        embed = discord.Embed(title=f"{guild.name} Server Information",
                            color=discord.Color.blue(),
                            timestamp=datetime.datetime.utcnow())
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Region", value=str(guild.region), inline=True)
        embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        
        embed.add_field(name="Members", value=f"Total: {total_members}\nOnline: {online_members}\nBots: {bot_count}", inline=True)
        embed.add_field(name="Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {categories}", inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        
        embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier}", inline=True)
        embed.add_field(name="Boosters", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Verification Level", value=str(guild.verification_level), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name='userinfo', help='Get information about a user')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
        
        embed = discord.Embed(title=f"User Information - {member.name}",
                            color=member.color,
                            timestamp=datetime.datetime.utcnow())
        
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick if member.nick else "None", inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
        
        if roles:
            embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles), inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name='remind', help='Set a reminder')
    async def remind(self, ctx, time: str, *, reminder: str):
        # Convert time string to seconds
        time_dict = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        try:
            amount = int(time[:-1])
            unit = time[-1].lower()
            if unit not in time_dict:
                await ctx.send("Invalid time unit! Use s/m/h/d")
                return
            seconds = amount * time_dict[unit]
        except:
            await ctx.send("Invalid time format! Example: 30s, 5m, 2h, 1d")
            return
        
        if seconds < 1:
            await ctx.send("Time must be positive!")
            return
        
        await ctx.send(f"I'll remind you about '{reminder}' in {time}!")
        
        await asyncio.sleep(seconds)
        await ctx.author.send(f"Reminder: {reminder}")
        await ctx.send(f"{ctx.author.mention}, here's your reminder: {reminder}")

    @commands.command(name='poll', help='Create a poll')
    async def poll(self, ctx, question: str, *options):
        if len(options) < 2:
            await ctx.send("You need at least 2 options!")
            return
        if len(options) > 10:
            await ctx.send("You can only have up to 10 options!")
            return

        # Create the embed
        embed = discord.Embed(title="📊 Poll",
                            description=question,
                            color=discord.Color.blue())
        
        # Add options to the embed
        number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i+1}", value=f"{number_emojis[i]} {option}", inline=False)

        # Send the poll and add reactions
        poll_message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await poll_message.add_reaction(number_emojis[i])

    @commands.command(name='ping', help='Check the bot\'s latency')
    async def ping(self, ctx):
        """Get the bot's current websocket latency."""
        start_time = ctx.message.created_at
        message = await ctx.send("Pinging...")
        end_time = message.created_at
        
        # Calculate the ping time
        ping_time = (end_time - start_time).total_seconds() * 1000
        ws_latency = self.bot.latency * 1000
        
        # Create an embed for the ping response
        embed = discord.Embed(title="🏓 Pong!", color=discord.Color.green())
        embed.add_field(name="Message Latency", value=f"{ping_time:.2f}ms", inline=True)
        embed.add_field(name="WebSocket Latency", value=f"{ws_latency:.2f}ms", inline=True)
        
        await message.edit(content=None, embed=embed)

    @commands.command(name='system', help='Get system information')
    async def system(self, ctx):
        embed = discord.Embed(title="System Information",
                            color=discord.Color.blue())
        
        # CPU Information
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        embed.add_field(name="CPU",
                       value=f"Usage: {cpu_usage}%\nCores: {cpu_count}",
                       inline=True)
        
        # Memory Information
        memory = psutil.virtual_memory()
        embed.add_field(name="Memory",
                       value=f"Total: {memory.total/1024/1024/1024:.2f}GB\n"
                             f"Used: {memory.used/1024/1024/1024:.2f}GB\n"
                             f"Free: {memory.free/1024/1024/1024:.2f}GB",
                       inline=True)
        
        # Disk Information
        disk = psutil.disk_usage('/')
        embed.add_field(name="Disk",
                       value=f"Total: {disk.total/1024/1024/1024:.2f}GB\n"
                             f"Used: {disk.used/1024/1024/1024:.2f}GB\n"
                             f"Free: {disk.free/1024/1024/1024:.2f}GB",
                       inline=True)
        
        # Bot Information
        embed.add_field(name="Bot",
                       value=f"Python: {platform.python_version()}\n"
                             f"Discord.py: {discord.__version__}",
                       inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
