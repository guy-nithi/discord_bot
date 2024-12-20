import discord
from discord.ext import commands
import os
import random
import requests
import json
import asyncio
import sys
from datetime import datetime
from dotenv import load_dotenv
import logging
from keep_alive import keep_alive
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord')

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Bot setup with all intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Load cogs
async def load_cogs():
    print("\nLoading cogs...")
    cogs_base = "cogs"
    
    for folder in os.listdir(cogs_base):
        folder_path = os.path.join(cogs_base, folder)
        if os.path.isdir(folder_path):
            print(f"\nChecking folder: {folder}")
            for filename in os.listdir(folder_path):
                if filename.endswith(".py") and not filename.startswith("__"):
                    cog_path = f"cogs.{folder}.{filename[:-3]}"
                    try:
                        print(f"  Loading: {cog_path}")
                        await bot.load_extension(cog_path)
                        print(f"  Successfully loaded: {cog_path}")
                    except Exception as e:
                        print(f"  Failed to load {cog_path}: {str(e)}")

@bot.event
async def on_ready():
    print(f'\n {bot.user} has connected to Discord!')
    print(f' Bot is in {len(bot.guilds)} guilds')
    print("\nRegistered commands:")
    for command in bot.commands:
        print(f"  - {command.name}")
    await bot.change_presence(activity=discord.Game(name="!help for commands"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found. Use !help to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    else:
        print(f'Error: {str(error)}')
        await ctx.send(f"An error occurred: {str(error)}")

# Simple test command to verify bot is working
@bot.command(name="test")
async def test(ctx):
    await ctx.send("Bot is working!")

async def main():
    try:
        keep_alive()  # Start the web server
        async with bot:
            print("Starting bot...")
            await load_cogs()
            await bot.start(TOKEN)
    except Exception as e:
        print(f"Error in main: {e}")
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(main())
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Restarting bot in 5 seconds...")
            time.sleep(5)
