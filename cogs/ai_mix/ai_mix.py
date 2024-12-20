import discord
from discord.ext import commands
import random
import json
import os
import asyncio
import yt_dlp

class AIMix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playlists_file = 'playlists.json'
        self.playlists = self.load_playlists()
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'noplaylist': True
        }
        
        # Default playlists
        self.default_playlists = {
            "happy": [
                "Mr. Blue Sky ELO",
                "Happy Pharrell Williams",
                "Walking on Sunshine Katrina & The Waves",
                "Don't Stop Believin' Journey",
                "I Wanna Dance with Somebody Whitney Houston"
            ],
            "sad": [
                "Someone Like You Adele",
                "Say Something A Great Big World",
                "All By Myself Celine Dion",
                "Yesterday The Beatles",
                "The Sound of Silence Simon & Garfunkel"
            ],
            "study": [
                "lofi hip hop mix",
                "classical piano study music",
                "ambient study beats",
                "concentration music",
                "study with me playlist"
            ],
            "workout": [
                "Eye of the Tiger Survivor",
                "Stronger Kanye West",
                "Till I Collapse Eminem",
                "Thunderstruck AC/DC",
                "All I Do Is Win DJ Khaled"
            ],
            "party": [
                "Uptown Funk Bruno Mars",
                "Can't Stop the Feeling Justin Timberlake",
                "I Wanna Dance with Somebody Whitney Houston",
                "Dancing Queen ABBA",
                "Shake It Off Taylor Swift"
            ]
        }

    def load_playlists(self):
        if os.path.exists(self.playlists_file):
            with open(self.playlists_file, 'r') as f:
                return json.load(f)
        return {}

    def save_playlists(self):
        with open(self.playlists_file, 'w') as f:
            json.dump(self.playlists, f, indent=4)

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

    async def play_song(self, ctx, song_query):
        """Play a song in voice channel"""
        try:
            async with ctx.typing():
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    try:
                        # Get video info
                        info = await asyncio.get_event_loop().run_in_executor(
                            None, 
                            lambda: ydl.extract_info(f"ytsearch:{song_query}", download=False)
                        )
                        
                        if not info or 'entries' not in info or not info['entries']:
                            await ctx.send(f"❌ Couldn't find: {song_query}")
                            return False

                        video = info['entries'][0]
                        url = video.get('url')
                        title = video.get('title', 'Unknown title')

                        if not url:
                            await ctx.send("❌ Couldn't get stream URL")
                            return False

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
                        return True

                    except Exception as e:
                        await ctx.send(f"❌ Error playing song: {str(e)}")
                        return False

        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
            return False

    @commands.command()
    async def moodplay(self, ctx, mood: str):
        """Play music based on your mood (happy, sad, study, workout, party)"""
        mood = mood.lower()
        if mood not in self.default_playlists:
            moods = ", ".join(self.default_playlists.keys())
            await ctx.send(f"❌ Invalid mood. Available moods: {moods}")
            return

        if not await self.ensure_voice_connected(ctx):
            return

        playlist = self.default_playlists[mood]
        song = random.choice(playlist)

        await ctx.send(f"🎵 Playing a {mood} song...")
        await self.play_song(ctx, song)

    @commands.command()
    async def createplaylist(self, ctx, name: str, *, songs: str):
        """Create a custom playlist (songs separated by commas)"""
        name = name.lower()
        song_list = [s.strip() for s in songs.split(",")]
        
        self.playlists[name] = song_list
        self.save_playlists()
        
        embed = discord.Embed(
            title="✅ Playlist Created",
            description=f"Created playlist '{name}' with {len(song_list)} songs",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def playplaylist(self, ctx, name: str):
        """Play a song from your custom playlist"""
        name = name.lower()
        if name not in self.playlists:
            await ctx.send(f"❌ Playlist '{name}' not found. Use !createplaylist to create one.")
            return

        if not await self.ensure_voice_connected(ctx):
            return

        playlist = self.playlists[name]
        song = random.choice(playlist)

        await ctx.send(f"🎵 Playing from playlist '{name}'...")
        await self.play_song(ctx, song)

    @commands.command()
    async def listplaylists(self, ctx):
        """List all available playlists"""
        embed = discord.Embed(
            title="📝 Available Playlists",
            color=discord.Color.blue()
        )
        
        # Add default playlists
        default_playlists_str = "\n".join(f"• {name} ({len(songs)} songs)" 
                                        for name, songs in self.default_playlists.items())
        embed.add_field(
            name="Default Mood Playlists",
            value=default_playlists_str or "No default playlists",
            inline=False
        )
        
        # Add custom playlists
        custom_playlists_str = "\n".join(f"• {name} ({len(songs)} songs)" 
                                       for name, songs in self.playlists.items())
        embed.add_field(
            name="Custom Playlists",
            value=custom_playlists_str or "No custom playlists",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AIMix(bot))
