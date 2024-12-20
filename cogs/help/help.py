from discord.ext import commands
import discord

class HelpCog(commands.Cog):
    """Help commands"""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def help(self, ctx):
        """Shows this help message"""
        embed = discord.Embed(
            title="Bot Commands",
            description="Here are all available commands:",
            color=discord.Color.blue()
        )
        
        # Music Commands
        music_commands = """
        `!play` - Play a song from YouTube
        `!stop` - Stop playing music
        `!join` - Join voice channel
        `!leave` - Leave voice channel
        """
        embed.add_field(name="🎵 Music", value=music_commands, inline=False)
        
        # AI Mix Commands
        ai_mix_commands = """
        `!moodplay` - Play songs based on mood
        `!createplaylist` - Create a custom playlist
        `!playplaylist` - Play from custom playlist
        `!listplaylists` - Show all playlists
        """
        embed.add_field(name="🎧 AI Mix", value=ai_mix_commands, inline=False)
        
        # Fun Commands
        fun_commands = """
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
        embed.add_field(name="🎮 Fun", value=fun_commands, inline=False)
        
        # Games Commands
        games_commands = """
        `!tictactoe` - Play Tic Tac Toe
        `!hangman` - Play Hangman
        `!trivia` - Play Trivia
        """
        embed.add_field(name="🎲 Games", value=games_commands, inline=False)
        
        # Economy Commands
        economy_commands = """
        **Basic Commands:**
        `!balance` - Check your wallet and bank balance
        `!work <job>` - Work at a specific job
        `!deposit <amount>` - Deposit money into your bank
        `!withdraw <amount>` - Withdraw money from your bank
        `!gamble <amount>` - Gamble your money
        `!stats` - View your levels and progress
        `!bankrob` - Rob someones bank. Requires 5 people.
        

        **Jobs System:**
        • All jobs start at $200-500 base salary
        • Level up every 15 jobs
        • Each level increases salary by $100
        • Available jobs: fireman, police, doctor, nurse, teacher, chef

        **Gambling System:**
        • Start with 50% win chance
        • Level up every 8 gambles
        • Each level increases win chance by 1%
        • Maximum win chance: 60% (Level 80)
        """
        embed.add_field(name="💰 Economy", value=economy_commands, inline=False)

        # Leveling Commands
        leveling_commands = """
        `!rank` - Check your rank
        `!leaderboard` - View leaderboard
        `!givexp` - Give XP (Admin)
        `!resetxp` - Reset XP (Admin)
        """
        embed.add_field(name="⭐ Leveling", value=leveling_commands, inline=False)
        
        # Moderation Commands
        mod_commands = """
        `!warn` - Warn a user
        `!kick` - Kick a user
        `!ban` - Ban a user
        `!unban` - Unban a user
        `!purge` - Delete messages
        `!timeout` - Timeout a user
        `!untimeout` - Remove timeout
        `!clearwarns` - Clear warnings
        `!addrole` - Add role to a user
        `!removerole` - Remove role from a user
        
        """
        embed.add_field(name="🛡️ Moderation", value=mod_commands, inline=False)
        
        # Utility Commands
        utility_commands = """
        `!ping` - Check bot latency
        `!serverinfo` - Server information
        `!help` - Show this message
        """
        embed.add_field(name="🔧 Utility", value=utility_commands, inline=False)

        # Add footer
        embed.set_footer(text="Use !help <command> for more details about a specific command")
        
        await ctx.send(embed=embed)

    @commands.command()
    async def helpeconomy(self, ctx):
        """Shows detailed economy help"""
        embed = discord.Embed(
            title="💰 Economy System Help",
            description="Detailed guide for the economy system",
            color=discord.Color.gold()
        )

        basic_commands = """
        `!balance` - Check your wallet and bank balance
        `!deposit <amount/all>` - Deposit money to bank
        `!withdraw <amount/all>` - Withdraw money from bank
        `!rob <@user>` - Try to rob another user (risky!)
        """
        embed.add_field(name="📋 Basic Commands", value=basic_commands, inline=False)

        work_system = """
        `!work` - Basic work (1hr cooldown)
        `!work <job>` - Work specific job (30min cooldown)

        Available Jobs:
        • Fireman - $300-800 + fire_hose
        • Police - $400-900 + badge
        • Doctor - $500-1000 + stethoscope
        • Nurse - $300-700 + medical_kit
        • Teacher - $200-600 + textbook
        • Chef - $250-650 + cooking_utensils

        💫 Advance Work:
        • Unlocks after working 150 times
        • Doubles all work earnings
        """
        embed.add_field(name="💼 Work System", value=work_system, inline=False)

        gambling = """
        `!gamble <amount>` - Gamble your money
        • Win: 2x your bet
        • Advance Gamble: 3x your bet (unlocks after 75 wins)
        """
        embed.add_field(name="🎲 Gambling", value=gambling, inline=False)

        market = """
        `!market` - View available items
        `!market sell <item>` - Sell items for money
        • Items are obtained from jobs (10% chance)
        • Sell prices range from $100-500
        """
        embed.add_field(name="🏪 Market", value=market, inline=False)

        pets = """
        `!pet` - View your current pet
        `!pet buy <type>` - Buy a new pet ($1000)
        `!challenge <@user> <bet>` - Battle pets
        • Each pet has random strength (50-100)
        • Battle outcome depends on strength + luck
        • Winner takes the bet amount
        """
        embed.add_field(name="🐾 Pet System", value=pets, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
