import discord
from discord.ext import commands
import random
import json
import os

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "What do you call a fake noodle? An impasta!",
            "Why did the cookie go to the doctor? Because it was feeling crumbly!",
            "What do you call a can opener that doesn't work? A can't opener!",
            "Why did the math book look so sad? Because it had too many problems!",
            "What do you call a pig that does karate? A pork chop!",
            "Why don't eggs tell jokes? They'd crack up!",
            "What do you call a sleeping bull? A bulldozer!"
        ]
        
        self.facts = [
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!",
            "A day on Venus is longer than its year. Venus takes 243 Earth days to rotate on its axis but only 225 Earth days to orbit the Sun.",
            "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after just 38 minutes.",
            "The first oranges weren't orange! The original oranges from Southeast Asia were actually green.",
            "A group of flamingos is called a 'flamboyance'.",
            "Bananas are berries, but strawberries aren't!",
            "The average person spends 6 months of their lifetime waiting for red lights to turn green.",
            "Cows have best friends and get stressed when separated from them.",
            "The first person convicted of speeding was going eight mph.",
            "Nintendo was founded in 1889 as a playing card company."
        ]

    @commands.command()
    async def joke(self, ctx):
        """Get a random joke"""
        joke = random.choice(self.jokes)
        embed = discord.Embed(
            title="😄 Here's a joke!",
            description=joke,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def fact(self, ctx):
        """Get a random interesting fact"""
        fact = random.choice(self.facts)
        embed = discord.Embed(
            title="🤓 Here's an interesting fact!",
            description=fact,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AI(bot))
