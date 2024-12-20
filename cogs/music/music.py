import discord
from discord.ext import commands
import asyncio
import yt_dlp
import subprocess
import os

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'noplaylist': True
        }

    async def ensure_voice_connected(self, ctx):
        """Ensure the bot is connected to voice"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                return True
            else:
                await ctx.send("You need to be in a voice channel to use this command!")
                return False
        return True

    @commands.command()
    async def join(self, ctx):
        """Join a voice channel"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
            await ctx.send(f"✅ Joined {channel.name}")
        else:
            await ctx.send("You need to be in a voice channel to use this command!")

    @commands.command()
    async def leave(self, ctx):
        """Leave the voice channel"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel")
        else:
            await ctx.send("I'm not in a voice channel!")

    @commands.command()
    async def play(self, ctx, *, query):
        """Play a song from YouTube"""
        if not await self.ensure_voice_connected(ctx):
            return

        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    try:
                        info = await asyncio.get_event_loop().run_in_executor(
                            None, 
                            lambda: ydl.extract_info(f"ytsearch:{query}", download=False)
                        )
                        
                        if not info or 'entries' not in info or not info['entries']:
                            await ctx.send(f"❌ Couldn't find: {query}")
                            return

                        video = info['entries'][0]
                        url = video.get('url')
                        title = video.get('title', 'Unknown title')

                        if not url:
                            await ctx.send("❌ Couldn't get stream URL")
                            return

                        # Play the audio
                        if ctx.voice_client.is_playing():
                            ctx.voice_client.stop()

                        # Create FFmpeg audio source
                        source = discord.FFmpegPCMAudio(
                            url,
                            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                            options='-vn'
                        )
                        
                        # Play the audio
                        ctx.voice_client.play(source)
                        
                        embed = discord.Embed(
                            title="🎵 Now Playing",
                            description=f"🎧 **{title}**",
                            color=discord.Color.blue()
                        )
                        await ctx.send(embed=embed)

                    except Exception as e:
                        await ctx.send(f"❌ Error playing song: {str(e)}")

            except Exception as e:
                await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command()
    async def stop(self, ctx):
        """Stop playing music"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏹️ Stopped playing")
        else:
            await ctx.send("Nothing is playing!")

async def setup(bot):
    await bot.add_cog(Music(bot))
