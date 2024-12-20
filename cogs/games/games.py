import discord
from discord.ext import commands
import random
import asyncio
import json
import os

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.trivia_questions = self.load_trivia()
        self.active_games = {}

    def load_trivia(self):
        questions = [
            {
                "question": "What is the capital of France?",
                "answer": "paris",
                "options": ["London", "Paris", "Berlin", "Madrid"]
            },
            # Add more questions here
        ]
        return questions

    @commands.command(name='tictactoe', help='Start a game of Tic Tac Toe')
    async def tictactoe(self, ctx, opponent: discord.Member = None):
        if opponent is None:
            await ctx.send("Please mention an opponent to play with!")
            return
        
        if opponent.bot:
            await ctx.send("You can't play against bots!")
            return

        board = [["\u2B1C" for _ in range(3)] for _ in range(3)]
        current_player = ctx.author
        game_msg = None

        def check(reaction, user):
            return user == current_player and str(reaction.emoji) in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]

        def check_winner(board):
            # Check rows
            for row in board:
                if row.count(row[0]) == 3 and row[0] != "\u2B1C":
                    return True
            # Check columns
            for col in range(3):
                if board[0][col] == board[1][col] == board[2][col] != "\u2B1C":
                    return True
            # Check diagonals
            if board[0][0] == board[1][1] == board[2][2] != "\u2B1C":
                return True
            if board[0][2] == board[1][1] == board[2][0] != "\u2B1C":
                return True
            return False

        while True:
            board_str = ""
            for i, row in enumerate(board):
                board_str += "".join(row) + "\n"

            embed = discord.Embed(title=f"Tic Tac Toe: {ctx.author.name} vs {opponent.name}",
                                description=f"Current turn: {current_player.name}\n\n{board_str}",
                                color=discord.Color.blue())

            if game_msg:
                await game_msg.edit(embed=embed)
            else:
                game_msg = await ctx.send(embed=embed)
                for emoji in ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]:
                    await game_msg.add_reaction(emoji)

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send(f"Game over! {current_player.name} took too long to play.")
                return

            position = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"].index(str(reaction.emoji))
            row = position // 3
            col = position % 3

            if board[row][col] != "\u2B1C":
                await ctx.send("That position is already taken! Try again.")
                continue

            board[row][col] = "❌" if current_player == ctx.author else "⭕"
            await game_msg.remove_reaction(reaction.emoji, user)

            if check_winner(board):
                await ctx.send(f"🎉 {current_player.name} wins! 🎉")
                return

            if all(cell != "\u2B1C" for row in board for cell in row):
                await ctx.send("It's a tie!")
                return

            current_player = opponent if current_player == ctx.author else ctx.author

    @commands.command(name='hangman', help='Start a game of Hangman')
    async def hangman(self, ctx):
        words = ['python', 'programming', 'computer', 'algorithm', 'database', 'network', 'security']
        word = random.choice(words)
        guessed = set()
        tries = 6
        
        def get_display_word():
            return ' '.join(letter if letter in guessed else '_' for letter in word)
        
        while tries > 0:
            display = get_display_word()
            embed = discord.Embed(title="Hangman",
                                description=f"Word: {display}\nGuesses left: {tries}\nGuessed letters: {', '.join(sorted(guessed))}",
                                color=discord.Color.blue())
            await ctx.send(embed=embed)
            
            if '_' not in display:
                await ctx.send("🎉 You win! The word was: " + word)
                return
            
            try:
                msg = await self.bot.wait_for(
                    'message',
                    timeout=30.0,
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await ctx.send("Game over! You took too long to respond.")
                return
            
            guess = msg.content.lower()
            if len(guess) != 1:
                await ctx.send("Please guess one letter at a time!")
                continue
                
            if guess in guessed:
                await ctx.send("You already guessed that letter!")
                continue
                
            guessed.add(guess)
            if guess not in word:
                tries -= 1
                if tries == 0:
                    await ctx.send(f"Game Over! The word was: {word}")
                    return

    @commands.command(name='trivia', help='Start a trivia game')
    async def trivia(self, ctx):
        question = random.choice(self.trivia_questions)
        options = question['options']
        random.shuffle(options)
        
        embed = discord.Embed(title="Trivia Time!",
                            description=question['question'],
                            color=discord.Color.green())
        
        for i, option in enumerate(options):
            embed.add_field(name=f"Option {i+1}", value=option, inline=False)
            
        msg = await ctx.send(embed=embed)
        
        for i in range(len(options)):
            await msg.add_reaction(f"{i+1}\u20e3")
            
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20e3" for i in range(len(options))]
            
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            selected_option = options[int(str(reaction.emoji)[0]) - 1]
            
            if selected_option.lower() == question['answer'].lower():
                await ctx.send("🎉 Correct! Well done!")
            else:
                await ctx.send(f"❌ Wrong! The correct answer was: {question['answer']}")
        except asyncio.TimeoutError:
            await ctx.send("Time's up! No answer was given.")

async def setup(bot):
    await bot.add_cog(Games(bot))
