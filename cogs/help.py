import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def help(self, ctx):
        """Shows all available commands"""
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )

        # Music Commands
        music = """
        🎵 **Music**
        `!play` - Play a song from YouTube
        `!stop` - Stop playing music
        `!join` - Join voice channel
        `!leave` - Leave voice channel
        """
        embed.add_field(name="Music", value=music, inline=False)

        # AI Mix Commands
        ai_mix = """
        🎵 **AI Mix**
        `!moodplay` - Play songs based on mood
        `!createplaylist` - Create a custom playlist
        `!playplaylist` - Play from custom playlist
        `!listplaylists` - Show all playlists
        """
        embed.add_field(name="AI Mix", value=ai_mix, inline=False)

        # Fun Commands
        fun = """
        🎲 **Fun**
        `!8ball` - Ask the magic 8-ball
        `!roll` - Roll a dice
        `!choose` - Make a choice
        `!joke` - Get a random joke
        `!meme` - Get a random meme
        `!fact` - Get a random fact
        `!poll` - Create a poll
        `!rps` - Rock Paper Scissors
        `!flip` - Flip a coin
        """
        embed.add_field(name="Fun", value=fun, inline=False)

        # Games Commands
        games = """
        🎮 **Games**
        `!tictactoe` - Play Tic Tac Toe
        `!hangman` - Play Hangman
        `!trivia` - Play Trivia
        """
        embed.add_field(name="Games", value=games, inline=False)

        # Economy Commands
        economy = """
        💰 **Economy**
        Basic Commands:
        `!balance` - Check your wallet and bank balance
        `!work <job>` - Work your job
        `!deposit <amount>` - Deposit money into your bank
        `!withdraw <amount>` - Withdraw money from your bank
        `!gamble <amount>` - Gamble your money or Gamble all
        `!stats` - View your levels and progress
        `!bankrob` - Rob someones bank. Requires 5 people.


        Jobs System:
        • All jobs start at $200-500 base salary
        • Level up every 15 jobs
        • Each level increases salary by $100
        • Available jobs: fireman, police, doctor, nurse, teacher, chef

        Gambling System:
        • Start with 50% win chance
        • Level up every 8 gambles
        • Each level increases win chance by 1%
        • Maximum win chance: 60% (Level 80)
        """
        embed.add_field(name="Economy", value=economy, inline=False)



        # Leveling Commands
        leveling = """
        ⭐ **Leveling**
        `!rank` - Check your rank
        `!leaderboard` - View leaderboard
        `!givexp` - Give XP (Admin)
        `!resetxp` - Reset XP (Admin)
        """
        embed.add_field(name="Leveling", value=leveling, inline=False)

        # Moderation Commands
        moderation = """
        🛡️ **Moderation** (Admin Only)
        `!warn @user [reason]` - Warn a user
        `!warnings @user` - Check user's warnings
        `!clearwarns @user` - Clear all warnings
        `!kick @user [reason]` - Kick a user
        `!ban @user [reason]` - Ban a user
        `!unban user#1234` - Unban a user
        `!purge <amount>` - Delete messages
        `!timeout @user <minutes> [reason]` - Timeout a user
        `!untimeout @user` - Remove timeout
        `!addrole @user @role` - Add role to a user
        `!removerole @user @role` - Remove role from a user

        Note: All moderation commands require Administrator permissions
        • Can't moderate users with higher or equal roles
        • Bot's role must be higher than target user's role
        """
        embed.add_field(name="Moderation System", value=moderation, inline=False)

        # Utility Commands
        utility = """
        🔧 **Utility**
        `!ping` - Check bot latency
        `!serverinfo` - Server information
        `!help` - Show this message

        """
        embed.add_field(name="Utility", value=utility, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
