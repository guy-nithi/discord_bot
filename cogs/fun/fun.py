import discord
from discord.ext import commands
import random
import aiohttp
import json
import asyncio
from datetime import datetime

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.eight_ball_responses = [
            "It is certain.", "It is decidedly so.", "Without a doubt.",
            "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
            "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
            "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.",
            "Don't count on it.", "My reply is no.", "My sources say no.",
            "Outlook not so good.", "Very doubtful."
        ]

    @commands.command(name='8ball')
    async def eight_ball(self, ctx, *, question):
        """Ask the magic 8 ball a question"""
        response = random.choice(self.eight_ball_responses)
        embed = discord.Embed(title="🎱 Magic 8 Ball", color=discord.Color.blue())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def roll(self, ctx, dice: str = "1d6"):
        """Roll dice in NdN format"""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send("Format has to be in NdN!")
            return

        if rolls > 25:
            await ctx.send("Too many dice! Maximum is 25")
            return

        results = [random.randint(1, limit) for _ in range(rolls)]
        embed = discord.Embed(title="🎲 Dice Roll", color=discord.Color.green())
        embed.add_field(name="Rolls", value=', '.join(map(str, results)), inline=False)
        embed.add_field(name="Total", value=sum(results), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def choose(self, ctx, *choices: str):
        """Choose between multiple choices"""
        if len(choices) < 2:
            await ctx.send("Please provide at least 2 choices!")
            return
        embed = discord.Embed(title="🤔 Choice Made", color=discord.Color.blue())
        embed.add_field(name="Options", value=', '.join(choices), inline=False)
        embed.add_field(name="I choose", value=random.choice(choices), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def joke(self, ctx):
        """Get a random joke"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://official-joke-api.appspot.com/random_joke') as response:
                if response.status == 200:
                    joke = await response.json()
                    embed = discord.Embed(title="😄 Random Joke", color=discord.Color.gold())
                    embed.add_field(name="Setup", value=joke['setup'], inline=False)
                    embed.add_field(name="Punchline", value=joke['punchline'], inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Couldn't fetch a joke right now!")

    @commands.command()
    async def meme(self, ctx):
        """Get a random meme"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as response:
                if response.status == 200:
                    meme = await response.json()
                    embed = discord.Embed(title=meme['title'], color=discord.Color.random())
                    embed.set_image(url=meme['url'])
                    embed.set_footer(text=f"👍 {meme['ups']} | From r/{meme['subreddit']}")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Couldn't fetch a meme right now!")

    @commands.command()
    async def fact(self, ctx):
        """Get a random fact"""
        async with aiohttp.ClientSession() as session:
            async with session.get('https://uselessfacts.jsph.pl/random.json?language=en') as response:
                if response.status == 200:
                    data = await response.json()
                    embed = discord.Embed(title="🤓 Random Fact", description=data['text'], color=discord.Color.blue())
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Couldn't fetch a fact right now!")

    @commands.command()
    async def poll(self, ctx, question, *options):
        """Create a poll with up to 10 options"""
        if len(options) < 2:
            await ctx.send("Please provide at least 2 options!")
            return
        if len(options) > 10:
            await ctx.send("Maximum 10 options allowed!")
            return

        # Emoji numbers for options
        emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        # Create the poll embed
        embed = discord.Embed(title="📊 Poll", color=discord.Color.blue())
        embed.add_field(name="Question", value=question, inline=False)
        
        # Add options to the embed
        description = []
        for i, option in enumerate(options):
            description.append(f"{emoji_numbers[i]} {option}")
        
        embed.add_field(name="Options", value='\n'.join(description), inline=False)
        embed.set_footer(text=f"Poll by {ctx.author.name}")
        
        # Send poll and add reactions
        poll_message = await ctx.send(embed=embed)
        for i in range(len(options)):
            await poll_message.add_reaction(emoji_numbers[i])

    @commands.command()
    async def rps(self, ctx):
        """Play Rock, Paper, Scissors"""
        embed = discord.Embed(title="Rock, Paper, Scissors", description="React to play!", color=discord.Color.blue())
        embed.add_field(name="Options", value="🗿 - Rock\n📄 - Paper\n✂️ - Scissors", inline=False)
        message = await ctx.send(embed=embed)
        
        options = ['🗿', '📄', '✂️']
        for option in options:
            await message.add_reaction(option)
            
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in options
            
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Time's up!")
            return
            
        bot_choice = random.choice(options)
        user_choice = str(reaction.emoji)
        
        # Determine winner
        if user_choice == bot_choice:
            result = "It's a tie!"
        elif (user_choice == '🗿' and bot_choice == '✂️') or \
             (user_choice == '📄' and bot_choice == '🗿') or \
             (user_choice == '✂️' and bot_choice == '📄'):
            result = "You win!"
        else:
            result = "I win!"
            
        result_embed = discord.Embed(title="Rock, Paper, Scissors Results", color=discord.Color.green())
        result_embed.add_field(name="Your Choice", value=user_choice, inline=True)
        result_embed.add_field(name="My Choice", value=bot_choice, inline=True)
        result_embed.add_field(name="Result", value=result, inline=False)
        await ctx.send(embed=result_embed)

    @commands.command()
    async def flip(self, ctx):
        """Flip a coin"""
        result = random.choice(['Heads', 'Tails'])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"Result: **{result}**", color=discord.Color.gold())
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
