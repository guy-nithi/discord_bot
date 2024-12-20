import discord
from discord.ext import commands
import datetime
import asyncio
import json
import os
from discord.utils import utcnow

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_file = 'warns.json'
        self.warns = self.load_warns()

    def load_warns(self):
        if os.path.exists(self.warns_file):
            with open(self.warns_file, 'r') as f:
                return json.load(f)
        return {}

    def save_warns(self):
        with open(self.warns_file, 'w') as f:
            json.dump(self.warns, f, indent=4)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member (Admin only)"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("❌ You can't warn someone with a higher or equal role!")
            return

        guild_id = str(ctx.guild.id)
        member_id = str(member.id)
        
        if guild_id not in self.warns:
            self.warns[guild_id] = {}
        if member_id not in self.warns[guild_id]:
            self.warns[guild_id][member_id] = []
            
        warn_data = {
            'reason': reason,
            'timestamp': str(utcnow()),
            'warner': str(ctx.author.id)
        }
        
        self.warns[guild_id][member_id].append(warn_data)
        self.save_warns()
        
        warning_count = len(self.warns[guild_id][member_id])
        
        embed = discord.Embed(title="⚠️ Warning", color=discord.Color.yellow())
        embed.add_field(name="Member", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Warnings", value=f"Total: {warning_count}", inline=False)
        
        # Check if user has reached 5 warnings
        if warning_count >= 5:
            try:
                timeout_duration = utcnow() + datetime.timedelta(days=1)
                await member.timeout(timeout_duration, reason="Reached 5 warnings")
                embed.add_field(
                    name="Automatic Timeout",
                    value=f"User has been timed out until <t:{int(timeout_duration.timestamp())}:F>",
                    inline=False
                )
                embed.color = discord.Color.red()
            except discord.Forbidden:
                embed.add_field(
                    name="Error",
                    value="Could not timeout user. Make sure the bot has the necessary permissions.",
                    inline=False
                )
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warnings(self, ctx, member: discord.Member):
        """Check warnings for a member (Admin only)"""
        guild_id = str(ctx.guild.id)
        member_id = str(member.id)
        
        if guild_id not in self.warns or member_id not in self.warns[guild_id]:
            await ctx.send(f"{member.mention} has no warnings.")
            return
            
        warns = self.warns[guild_id][member_id]
        if not warns:
            await ctx.send(f"{member.mention} has no warnings.")
            return
            
        embed = discord.Embed(title=f"Warnings for {member.name}", color=discord.Color.yellow())
        
        for i, warn in enumerate(warns, 1):
            warner = ctx.guild.get_member(int(warn['warner']))
            warner_name = warner.name if warner else "Unknown"
            
            try:
                timestamp = datetime.datetime.strptime(warn['timestamp'], '%Y-%m-%d %H:%M:%S.%f%z')
            except ValueError:
                timestamp = utcnow()
            
            warn_text = f"**Reason:** {warn['reason']}\n"
            warn_text += f"**By:** {warner_name}\n"
            warn_text += f"**When:** <t:{int(timestamp.timestamp())}:R>"
            
            embed.add_field(name=f"Warning #{i}", value=warn_text, inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clearwarns(self, ctx, member: discord.Member):
        """Clear all warnings for a member (Admin only)"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("❌ You can't clear warnings for someone with a higher or equal role!")
            return

        guild_id = str(ctx.guild.id)
        member_id = str(member.id)
        
        if guild_id in self.warns and member_id in self.warns[guild_id]:
            self.warns[guild_id][member_id] = []
            self.save_warns()
            await ctx.send(f"✅ Cleared all warnings for {member.mention}")
        else:
            await ctx.send(f"{member.mention} has no warnings to clear.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member (Admin only)"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("❌ You can't kick someone with a higher or equal role!")
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(title="👢 Kick", color=discord.Color.red())
            embed.add_field(name="Member", value=member.mention, inline=False)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member (Admin only)"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("❌ You can't ban someone with a higher or equal role!")
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(title="🔨 Ban", color=discord.Color.red())
            embed.add_field(name="Member", value=member.mention, inline=False)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unban(self, ctx, *, member):
        """Unban a member (Admin only)"""
        banned_users = [entry async for entry in ctx.guild.bans()]
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed = discord.Embed(title="🔓 Unban", color=discord.Color.green())
                embed.add_field(name="Member", value=f"{user.name}#{user.discriminator}", inline=False)
                await ctx.send(embed=embed)
                return
        await ctx.send(f"❌ Couldn't find {member} in ban list.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount: int):
        """Purge messages (Admin only)"""
        if amount <= 0:
            await ctx.send("❌ Please specify a positive number!")
            return
            
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
        msg = await ctx.send(f"✅ Deleted {len(deleted)-1} messages.")
        await asyncio.sleep(3)
        await msg.delete()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def timeout(self, ctx, member: discord.Member, duration: int, *, reason=None):
        """Timeout a member (Admin only)"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("❌ You can't timeout someone with a higher or equal role!")
            return

        if duration <= 0:
            await ctx.send("❌ Duration must be positive!")
            return
            
        try:
            timeout_duration = utcnow() + datetime.timedelta(minutes=duration)
            await member.timeout(timeout_duration, reason=reason)
            embed = discord.Embed(title="🔇 Timeout", color=discord.Color.red())
            embed.add_field(name="Member", value=member.mention, inline=False)
            embed.add_field(name="Duration", value=f"{duration} minutes", inline=False)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Expires", value=f"<t:{int(timeout_duration.timestamp())}:F>", inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to timeout this member!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Remove timeout from a member (Admin only)"""
        if ctx.author.top_role <= member.top_role:
            await ctx.send("❌ You can't remove timeout from someone with a higher or equal role!")
            return

        try:
            await member.timeout(None)
            embed = discord.Embed(title="🔊 Timeout Removed", color=discord.Color.green())
            embed.add_field(name="Member", value=member.mention, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove timeout from this member!")

    # Error handlers for all commands
    @kick.error
    @ban.error
    @unban.error
    @warn.error
    @warnings.error
    @clearwarns.error
    @purge.error
    @timeout.error
    @untimeout.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need Administrator permissions to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument! Usage: {ctx.prefix}{ctx.command.name} {ctx.command.signature}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided!")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
