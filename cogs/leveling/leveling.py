import discord
from discord.ext import commands
import json
import random
import asyncio
import datetime
from typing import Dict, Optional
import os

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels_file = 'levels.json'
        self.levels: Dict[str, Dict[str, int]] = self.load_levels()
        self.xp_cooldown = {}
        self.xp_rate = 15  # XP gained per message
        self.cooldown_time = 60  # Cooldown in seconds

    def load_levels(self) -> Dict[str, Dict[str, int]]:
        if os.path.exists(self.levels_file):
            with open(self.levels_file, 'r') as f:
                return json.load(f)
        return {}

    def save_levels(self):
        with open(self.levels_file, 'w') as f:
            json.dump(self.levels, f, indent=4)

    def get_level_xp(self, level: int) -> int:
        return 5 * (level ** 2) + 50 * level + 100

    def get_level_from_xp(self, xp: int) -> int:
        level = 0
        while xp >= self.get_level_xp(level):
            xp -= self.get_level_xp(level)
            level += 1
        return level

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check cooldown
        user_id = str(message.author.id)
        guild_id = str(message.guild.id)
        current_time = datetime.datetime.now().timestamp()

        if user_id in self.xp_cooldown:
            if current_time - self.xp_cooldown[user_id] < self.cooldown_time:
                return

        self.xp_cooldown[user_id] = current_time

        # Initialize user data if not exists
        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "messages": 0}

        # Add XP
        self.levels[guild_id][user_id]["xp"] += self.xp_rate
        self.levels[guild_id][user_id]["messages"] += 1

        # Check for level up
        current_xp = self.levels[guild_id][user_id]["xp"]
        current_level = self.levels[guild_id][user_id]["level"]
        new_level = self.get_level_from_xp(current_xp)

        if new_level > current_level:
            self.levels[guild_id][user_id]["level"] = new_level
            embed = discord.Embed(
                title="🎉 Level Up!",
                description=f"{message.author.mention} has reached level {new_level}!",
                color=discord.Color.green()
            )
            await message.channel.send(embed=embed)

        self.save_levels()

    @commands.command(name='rank')
    async def rank(self, ctx, member: Optional[discord.Member] = None):
        """Show your or another member's rank"""
        member = member or ctx.author
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.levels or user_id not in self.levels[guild_id]:
            await ctx.send(f"{member.name} hasn't earned any XP yet!")
            return

        user_data = self.levels[guild_id][user_id]
        current_xp = user_data["xp"]
        current_level = user_data["level"]
        messages = user_data["messages"]

        # Calculate progress to next level
        xp_for_current_level = sum(self.get_level_xp(i) for i in range(current_level))
        xp_to_next_level = self.get_level_xp(current_level)
        current_level_xp = current_xp - xp_for_current_level
        progress = (current_level_xp / xp_to_next_level) * 100

        # Create progress bar
        progress_bar_length = 20
        filled_length = int(progress_bar_length * progress / 100)
        bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)

        embed = discord.Embed(title=f"Rank - {member.name}", color=member.color)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Level", value=current_level, inline=True)
        embed.add_field(name="Total XP", value=current_xp, inline=True)
        embed.add_field(name="Messages", value=messages, inline=True)
        embed.add_field(name=f"Progress to Level {current_level + 1}", value=f"{bar} {progress:.1f}%", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='leaderboard', aliases=['lb'])
    async def leaderboard(self, ctx):
        """Show the server's XP leaderboard"""
        guild_id = str(ctx.guild.id)
        if guild_id not in self.levels:
            await ctx.send("No one has earned XP yet!")
            return

        # Sort users by XP
        sorted_users = sorted(
            self.levels[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )

        embed = discord.Embed(title=f"🏆 {ctx.guild.name} Leaderboard", color=discord.Color.gold())
        
        # Add top 10 users to embed
        for i, (user_id, data) in enumerate(sorted_users[:10], 1):
            member = ctx.guild.get_member(int(user_id))
            if member:
                name = member.name
                value = f"Level: {data['level']} | XP: {data['xp']} | Messages: {data['messages']}"
                embed.add_field(name=f"{i}. {name}", value=value, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='givexp')
    @commands.has_permissions(administrator=True)
    async def give_xp(self, ctx, member: discord.Member, amount: int):
        """Give XP to a member (Admin only)"""
        if amount <= 0:
            await ctx.send("Amount must be positive!")
            return

        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.levels:
            self.levels[guild_id] = {}
        if user_id not in self.levels[guild_id]:
            self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "messages": 0}

        self.levels[guild_id][user_id]["xp"] += amount
        new_level = self.get_level_from_xp(self.levels[guild_id][user_id]["xp"])
        self.levels[guild_id][user_id]["level"] = new_level
        self.save_levels()

        await ctx.send(f"Gave {amount} XP to {member.name}!")

    @commands.command(name='resetxp')
    @commands.has_permissions(administrator=True)
    async def reset_xp(self, ctx, member: Optional[discord.Member] = None):
        """Reset XP for a member or the entire server (Admin only)"""
        guild_id = str(ctx.guild.id)

        if member:
            user_id = str(member.id)
            if guild_id in self.levels and user_id in self.levels[guild_id]:
                self.levels[guild_id][user_id] = {"xp": 0, "level": 0, "messages": 0}
                await ctx.send(f"Reset XP for {member.name}")
        else:
            if guild_id in self.levels:
                self.levels[guild_id] = {}
                await ctx.send("Reset XP for the entire server")

        self.save_levels()

async def setup(bot):
    await bot.add_cog(Leveling(bot))
