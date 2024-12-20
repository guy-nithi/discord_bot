import discord
from discord.ext import commands
import json
import random
import asyncio
import os
from datetime import datetime, timedelta

class Economy(commands.Cog):
    """A cog for economy-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.bank_file = 'bank.json'
        self.stats_file = 'stats.json'
        self.items_file = 'items.json'
        self.pets_file = 'pets.json'
        
        # Real life jobs with base ranges
        self.jobs = {
            'fireman': {'base_salary': (200, 500)},
            'police': {'base_salary': (200, 500)},
            'doctor': {'base_salary': (200, 500)},
            'nurse': {'base_salary': (200, 500)},
            'teacher': {'base_salary': (200, 500)},
            'chef': {'base_salary': (200, 500)}
        }
        
        # Load data files
        self.bank = self.load_bank()
        self.stats = self.load_stats()
        self.items = self.load_items()
        self.pets = self.load_pets()
        self.cooldowns = {}
        
        # Initialize default stats for all users
        for user_id in self.stats:
            if 'gamble_count' not in self.stats[user_id]:
                self.stats[user_id]['gamble_count'] = 0
            if 'work_count' not in self.stats[user_id]:
                self.stats[user_id]['work_count'] = 0
            if 'gamble_wins' not in self.stats[user_id]:
                self.stats[user_id]['gamble_wins'] = 0
            for job in self.jobs:
                if f'{job}_count' not in self.stats[user_id]:
                    self.stats[user_id][f'{job}_count'] = 0
        self.save_stats()
        
    def load_bank(self):
        """Load bank data from JSON file"""
        try:
            with open(self.bank_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.bank_file, 'w') as f:
                json.dump({}, f)
            return {}

    def load_stats(self):
        """Load stats data from JSON file"""
        try:
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.stats_file, 'w') as f:
                json.dump({}, f)
            return {}

    def load_items(self):
        """Load items data from JSON file"""
        try:
            with open(self.items_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.items_file, 'w') as f:
                json.dump({}, f)
            return {}

    def load_pets(self):
        """Load pets data from JSON file"""
        try:
            with open(self.pets_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.pets_file, 'w') as f:
                json.dump({}, f)
            return {}

    def save_bank(self):
        """Save bank data to JSON file"""
        with open(self.bank_file, 'w') as f:
            json.dump(self.bank, f, indent=4)

    def save_stats(self):
        """Save stats data to JSON file"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=4)

    def save_items(self):
        """Save items data to JSON file"""
        with open(self.items_file, 'w') as f:
            json.dump(self.items, f, indent=4)

    def save_pets(self):
        """Save pets data to JSON file"""
        with open(self.pets_file, 'w') as f:
            json.dump(self.pets, f, indent=4)

    def get_balance(self, user_id):
        return self.bank.get(str(user_id), {"wallet": 0, "bank": 0})

    def get_job_level(self, user_id, job):
        """Get job level based on number of times worked"""
        if user_id not in self.stats:
            return 1
        job_count = self.stats[user_id].get(f'{job}_count', 0)
        return (job_count // 15) + 1  # Level up every 15 jobs

    def get_gamble_level(self, user_id):
        """Get gambling level based on number of gambles"""
        if user_id not in self.stats:
            return 1
        gamble_count = self.stats[user_id].get('gamble_count', 0)
        return (gamble_count // 8) + 1  # Level up every 8 gambles

    def get_gamble_win_chance(self, level):
        """Get gambling win chance based on level"""
        base_chance = 50
        increase_per_level = 1
        max_chance = 60
        chance = min(base_chance + (level - 1) * increase_per_level, max_chance)
        return chance

    def get_salary_range(self, job, level):
        """Get salary range based on job and level"""
        base_min, base_max = self.jobs[job]['base_salary']
        level_bonus = (level - 1) * 100  # Increase by 100 for each level
        return (base_min + level_bonus, base_max + level_bonus)

    def initialize_user_stats(self, user_id):
        """Initialize stats for a new user"""
        if user_id not in self.stats:
            self.stats[user_id] = {
                'gamble_count': 0,
                'work_count': 0,
                'gamble_wins': 0
            }
            for job in self.jobs:
                self.stats[user_id][f'{job}_count'] = 0
            self.save_stats()
        return self.stats[user_id]

    @commands.command(name='balance', aliases=['bal'])
    async def balance(self, ctx, member: discord.Member = None):
        """Check your balance or someone else's balance"""
        member = member or ctx.author
        user_id = str(member.id)

        if user_id not in self.bank:
            self.bank[user_id] = {"wallet": 0, "bank": 0}
            self.save_bank()

        wallet = self.bank[user_id]["wallet"]
        bank = self.bank[user_id]["bank"]
        total = wallet + bank

        embed = discord.Embed(
            title=f"💰 {member.name}'s Balance",
            color=discord.Color.gold()
        )
        embed.add_field(name="Wallet", value=f"${wallet:,}", inline=True)
        embed.add_field(name="Bank", value=f"${bank:,}", inline=True)
        embed.add_field(name="Total", value=f"${total:,}", inline=False)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        await ctx.send(embed=embed)

    @commands.command(name='work', help='Work to earn money')
    async def work(self, ctx, job=None):
        user_id = str(ctx.author.id)
        user_stats = self.initialize_user_stats(user_id)
        
        # Check if advance work is unlocked
        has_advance = user_stats['work_count'] >= 150
        
        # Check cooldown
        if user_id in self.cooldowns.get('work', {}):
            remaining = self.cooldowns['work'][user_id] - datetime.now()
            if remaining.total_seconds() > 0:
                await ctx.send(f"You must wait {int(remaining.total_seconds())} seconds before working again!")
                return

        if job and job not in self.jobs:
            await ctx.send(f"Invalid job! Available jobs: {', '.join(self.jobs.keys())}")
            return

        # Generate random amount based on job
        if job:
            job_level = self.get_job_level(user_id, job)
            min_salary, max_salary = self.get_salary_range(job, job_level)
            amount = random.randint(min_salary, max_salary)
            # Chance to get job-specific item
            if random.random() < 0.1:  # 10% chance
                if user_id not in self.items:
                    self.items[user_id] = {}
                self.items[user_id][job] = self.items[user_id].get(job, 0) + 1
                self.save_items()
                await ctx.send(f"You found a {job}!")
        else:
            amount = random.randint(100, 1000)

        # Apply advance work bonus
        if has_advance:
            amount *= 2

        # Add to wallet
        if user_id not in self.bank:
            self.bank[user_id] = {"wallet": 0, "bank": 0}
        self.bank[user_id]["wallet"] += amount
        
        # Update stats
        user_stats['work_count'] += 1
        if job:
            user_stats[f'{job}_count'] += 1
        self.save_stats()
        
        # Set cooldown (30 minutes for real jobs, 1 hour for regular work)
        if 'work' not in self.cooldowns:
            self.cooldowns['work'] = {}
        self.cooldowns['work'][user_id] = datetime.now() + timedelta(minutes=30 if job else 60)
        
        # Save changes
        self.save_bank()
        
        if job:
            await ctx.send(f"You worked as a {job} and earned ${amount}!")
        else:
            jobs = [
                "wrote some code", "fixed a bug", "deployed an app",
                "designed a website", "managed servers", "created content"
            ]
            await ctx.send(f"You {random.choice(jobs)} and earned ${amount}!")

    @commands.command(name='deposit', help='Deposit money into your bank')
    async def deposit(self, ctx, amount: str):
        user_id = str(ctx.author.id)
        balance = self.get_balance(user_id)
        
        if amount.lower() == 'all':
            amount = balance['wallet']
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send("Please enter a valid amount!")
                return

        if amount <= 0:
            await ctx.send("Please enter a positive amount!")
            return

        if amount > balance['wallet']:
            await ctx.send("You don't have enough money in your wallet!")
            return

        self.bank[user_id]['wallet'] -= amount
        self.bank[user_id]['bank'] += amount
        self.save_bank()

        await ctx.send(f"Successfully deposited ${amount:,} into your bank!")

    @commands.command(name='withdraw', help='Withdraw money from your bank')
    async def withdraw(self, ctx, amount: str):
        user_id = str(ctx.author.id)
        balance = self.get_balance(user_id)
        
        if amount.lower() == 'all':
            amount = balance['bank']
        else:
            try:
                amount = int(amount)
            except ValueError:
                await ctx.send("Please enter a valid amount!")
                return

        if amount <= 0:
            await ctx.send("Please enter a positive amount!")
            return

        if amount > balance['bank']:
            await ctx.send("You don't have enough money in your bank!")
            return

        self.bank[user_id]['bank'] -= amount
        self.bank[user_id]['wallet'] += amount
        self.save_bank()

        await ctx.send(f"Successfully withdrew ${amount:,} from your bank!")

    @commands.command(name='rob', help='Try to rob someone')
    async def rob(self, ctx, target: discord.Member):
        if target.bot:
            await ctx.send("You can't rob bots!")
            return

        thief_id = str(ctx.author.id)
        target_id = str(target.id)

        if thief_id == target_id:
            await ctx.send("You can't rob yourself!")
            return

        # Check cooldown
        if thief_id in self.cooldowns.get('rob', {}):
            remaining = self.cooldowns['rob'][thief_id] - datetime.now()
            if remaining.total_seconds() > 0:
                await ctx.send(f"You must wait {int(remaining.total_seconds())} seconds before robbing again!")
                return

        target_balance = self.get_balance(target_id)
        if target_balance['wallet'] < 100:
            await ctx.send("This user doesn't have enough money to rob!")
            return

        # 40% chance of successful robbery
        if random.random() < 0.4:
            stolen = random.randint(1, min(target_balance['wallet'], 1000))
            self.bank[target_id]['wallet'] -= stolen
            self.bank[thief_id]['wallet'] = self.bank.get(thief_id, {"wallet": 0, "bank": 0})['wallet'] + stolen
            await ctx.send(f"You successfully robbed ${stolen:,} from {target.name}!")
        else:
            fine = random.randint(200, 1000)
            self.bank[thief_id]['wallet'] = max(0, self.bank.get(thief_id, {"wallet": 0, "bank": 0})['wallet'] - fine)
            await ctx.send(f"You were caught and fined ${fine:,}!")

        # Set cooldown
        if 'rob' not in self.cooldowns:
            self.cooldowns['rob'] = {}
        self.cooldowns['rob'][thief_id] = datetime.now() + timedelta(hours=2)
        
        self.save_bank()

    @commands.command(name='gamble', help='Gamble your money (use "all" to gamble everything in wallet)')
    async def gamble(self, ctx, amount: str):
        """Gamble your money with a chance to double it"""
        user_id = str(ctx.author.id)
        
        # Initialize user if they don't exist
        if user_id not in self.bank:
            self.bank[user_id] = {"wallet": 0, "bank": 0}
            self.save_bank()

        # Initialize stats if needed
        if user_id not in self.stats:
            self.stats[user_id] = {"work_count": 0, "gamble_count": 0}
            self.save_stats()

        # Handle 'all' parameter
        if amount.lower() == 'all':
            bet_amount = self.bank[user_id]["wallet"]
            if bet_amount <= 0:
                await ctx.send("❌ You don't have any money in your wallet to gamble!")
                return
        else:
            try:
                bet_amount = int(amount)
            except ValueError:
                await ctx.send("❌ Please enter a valid number or 'all'!")
                return

        if bet_amount <= 0:
            await ctx.send("❌ Please enter a positive amount!")
            return

        if bet_amount > self.bank[user_id]["wallet"]:
            await ctx.send(f"❌ You don't have enough money! You only have ${self.bank[user_id]['wallet']:,} in your wallet!")
            return

        # Calculate win chance based on gambling level
        gamble_level = self.stats[user_id]["gamble_count"] // 8  # Level up every 8 gambles
        win_chance = min(0.60, 0.50 + (gamble_level * 0.01))  # Max 60% win chance

        # Gamble logic
        if random.random() < win_chance:
            # Win
            winnings = bet_amount * 2
            self.bank[user_id]["wallet"] += bet_amount  # They get their bet back plus equal amount
            self.save_bank()
            
            embed = discord.Embed(
                title="🎰 Gambling Results",
                description=f"Congratulations! You won ${bet_amount:,}!",
                color=discord.Color.green()
            )
            embed.add_field(name="Total Winnings", value=f"${winnings:,}", inline=True)
            embed.add_field(name="New Balance", value=f"${self.bank[user_id]['wallet']:,}", inline=True)
            embed.add_field(name="Win Chance", value=f"{win_chance*100:.1f}%", inline=True)
            embed.set_footer(text=f"Gamble Level: {gamble_level}")
        else:
            # Lose
            self.bank[user_id]["wallet"] -= bet_amount
            self.save_bank()
            
            embed = discord.Embed(
                title="🎰 Gambling Results",
                description=f"Sorry! You lost ${bet_amount:,}!",
                color=discord.Color.red()
            )
            embed.add_field(name="Loss", value=f"-${bet_amount:,}", inline=True)
            embed.add_field(name="New Balance", value=f"${self.bank[user_id]['wallet']:,}", inline=True)
            embed.add_field(name="Win Chance", value=f"{win_chance*100:.1f}%", inline=True)
            embed.set_footer(text=f"Gamble Level: {gamble_level}")

        # Update gamble count
        self.stats[user_id]["gamble_count"] += 1
        self.save_stats()
        
        await ctx.send(embed=embed)

    @gamble.error
    async def gamble_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Please specify an amount to gamble or 'all'! Example: `!gamble 1000` or `!gamble all`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Please enter a valid number or 'all'!")

    @commands.command(name='market', help='View or buy/sell items')
    async def market(self, ctx, action=None, item=None, price: int=None):
        user_id = str(ctx.author.id)
        
        if not action:
            # Display market items
            embed = discord.Embed(title="🏪 Market", color=discord.Color.blue())
            for job in self.jobs:
                embed.add_field(name=self.jobs[job]['base_salary'], 
                              value=f"Job: {job}\nValue: $100-500", 
                              inline=False)
            await ctx.send(embed=embed)
            return

        if action.lower() == 'sell' and item:
            if user_id not in self.items or item not in self.items[user_id] or self.items[user_id][item] <= 0:
                await ctx.send("You don't have this item!")
                return
            
            sell_price = random.randint(100, 500)
            self.items[user_id][item] -= 1
            self.bank[user_id]['wallet'] += sell_price
            self.save_items()
            self.save_bank()
            await ctx.send(f"You sold {item} for ${sell_price}!")

    @commands.command(name='challenge', help='Challenge another user to a pet battle')
    async def challenge(self, ctx, opponent: discord.Member, bet: int):
        user_id = str(ctx.author.id)
        opponent_id = str(opponent.id)

        if user_id not in self.pets or opponent_id not in self.pets:
            await ctx.send("Both players need to have pets to battle!")
            return

        if bet > self.bank[user_id]['wallet'] or bet > self.bank[opponent_id]['wallet']:
            await ctx.send("Both players need to have enough money for the bet!")
            return

        # Battle logic
        user_pet = self.pets[user_id]
        opponent_pet = self.pets[opponent_id]
        
        user_power = user_pet['strength'] * random.uniform(0.8, 1.2)
        opponent_power = opponent_pet['strength'] * random.uniform(0.8, 1.2)

        # Determine winner
        if user_power > opponent_power:
            self.bank[user_id]['wallet'] += bet
            self.bank[opponent_id]['wallet'] -= bet
            winner = ctx.author
        else:
            self.bank[opponent_id]['wallet'] += bet
            self.bank[user_id]['wallet'] -= bet
            winner = opponent

        self.save_bank()
        
        embed = discord.Embed(title="🐾 Pet Battle", color=discord.Color.purple())
        embed.add_field(name=f"{ctx.author.name}'s Pet", value=f"Power: {user_power:.2f}", inline=True)
        embed.add_field(name=f"{opponent.name}'s Pet", value=f"Power: {opponent_power:.2f}", inline=True)
        embed.add_field(name="Winner", value=f"{winner.name} wins ${bet}!", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='pet', help='View or buy pets')
    async def pet(self, ctx, action=None, pet_type=None):
        user_id = str(ctx.author.id)
        
        if not action:
            if user_id in self.pets:
                pet = self.pets[user_id]
                embed = discord.Embed(title="🐾 Your Pet", color=discord.Color.purple())
                embed.add_field(name="Type", value=pet['type'], inline=True)
                embed.add_field(name="Strength", value=pet['strength'], inline=True)
                await ctx.send(embed=embed)
            else:
                await ctx.send("You don't have a pet! Use `!pet buy <type>` to get one.")
            return

        if action.lower() == 'buy' and pet_type:
            cost = 1000
            if self.bank[user_id]['wallet'] < cost:
                await ctx.send(f"You need ${cost} to buy a pet!")
                return
            
            self.bank[user_id]['wallet'] -= cost
            self.pets[user_id] = {
                'type': pet_type,
                'strength': random.randint(50, 100)
            }
            self.save_bank()
            self.save_pets()
            await ctx.send(f"You bought a {pet_type} pet!")

    @commands.command(name='stats', help='View your stats')
    async def stats(self, ctx):
        user_id = str(ctx.author.id)
        user_stats = self.initialize_user_stats(user_id)
        
        embed = discord.Embed(
            title=f"{ctx.author.name}'s Stats",
            color=discord.Color.blue()
        )

        # Job stats
        embed.add_field(
            name="💼 Jobs Overview",
            value="Level up every 15 jobs. Each level increases salary by $100.",
            inline=False
        )
        
        for job in self.jobs:
            job_count = user_stats.get(f'{job}_count', 0)
            job_level = self.get_job_level(user_id, job)
            min_salary, max_salary = self.get_salary_range(job, job_level)
            next_level_jobs = 15 - (job_count % 15)
            
            embed.add_field(
                name=f"{job.title()}",
                value=f"Level: {job_level}\nTimes Worked: {job_count}\nSalary: ${min_salary}-{max_salary}\nTo Next Level: {next_level_jobs} jobs",
                inline=True
            )

        # Gambling stats
        gamble_count = user_stats.get('gamble_count', 0)
        gamble_level = self.get_gamble_level(user_id)
        win_chance = self.get_gamble_win_chance(gamble_level)
        next_level_gambles = 8 - (gamble_count % 8)
        
        embed.add_field(
            name="🎲 Gambling",
            value=f"Level: {gamble_level}\nTimes Gambled: {gamble_count}\nWin Chance: {win_chance}%\nTo Next Level: {next_level_gambles} gambles",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='advancework', help='Use advanced work feature (requires 150 works)')
    async def advancework(self, ctx, job=None):
        user_id = str(ctx.author.id)
        user_stats = self.initialize_user_stats(user_id)
        
        if user_stats['work_count'] < 150:
            remaining = 150 - user_stats['work_count']
            await ctx.send(f"❌ You need {remaining} more works to unlock advanced work!")
            return
            
        # Use regular work command with double earnings
        await self.work(ctx, job)

    @commands.command(name='advancegamble', help='Use advanced gambling feature (requires 75 wins)')
    async def advancegamble(self, ctx, amount: int):
        user_id = str(ctx.author.id)
        user_stats = self.initialize_user_stats(user_id)
        
        if user_stats['gamble_wins'] < 75:
            remaining = 75 - user_stats['gamble_wins']
            await ctx.send(f"❌ You need {remaining} more gambling wins to unlock advanced gambling!")
            return
            
        # Use regular gamble command with triple multiplier
        await self.gamble(ctx, amount)

    @commands.command(name='givemoney', help='[Owner Only] Give money to a user')
    @commands.has_guild_permissions(administrator=True)
    async def givemoney(self, ctx, member: discord.Member, amount: int):
        """Give money to a user (Owner Only)"""
        # Check if the command user is the server owner
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ Only the server owner can use this command!")
            return

        if amount <= 0:
            await ctx.send("❌ Please enter a positive amount!")
            return

        user_id = str(member.id)
        if user_id not in self.bank:
            self.bank[user_id] = {"wallet": 0, "bank": 0}

        # Add money to user's wallet
        self.bank[user_id]["wallet"] += amount
        self.save_bank()

        embed = discord.Embed(
            title="💰 Money Given",
            description=f"Successfully given ${amount:,} to {member.mention}",
            color=discord.Color.green()
        )
        embed.add_field(
            name="New Balance",
            value=f"Wallet: ${self.bank[user_id]['wallet']:,}\nBank: ${self.bank[user_id]['bank']:,}",
            inline=False
        )
        embed.set_footer(text=f"Given by {ctx.author.name}")

        await ctx.send(embed=embed)

    @givemoney.error
    async def givemoney_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: !givemoney @user <amount>")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid arguments! Usage: !givemoney @user <amount>")

    @commands.command(name='removemoney', help='[Owner Only] Remove money from a user')
    @commands.has_guild_permissions(administrator=True)
    async def removemoney(self, ctx, member: discord.Member, amount: int):
        """Remove money from a user (Owner Only)"""
        # Check if the command user is the server owner
        if ctx.author.id != ctx.guild.owner_id:
            await ctx.send("❌ Only the server owner can use this command!")
            return

        if amount <= 0:
            await ctx.send("❌ Please enter a positive amount!")
            return

        user_id = str(member.id)
        if user_id not in self.bank:
            await ctx.send("❌ This user doesn't have any money!")
            return

        # Check if user has enough money in wallet
        if self.bank[user_id]["wallet"] < amount:
            await ctx.send(f"❌ User only has ${self.bank[user_id]['wallet']:,} in their wallet!")
            return

        # Remove money from user's wallet
        self.bank[user_id]["wallet"] -= amount
        self.save_bank()

        embed = discord.Embed(
            title="💸 Money Removed",
            description=f"Successfully removed ${amount:,} from {member.mention}",
            color=discord.Color.red()
        )
        embed.add_field(
            name="New Balance",
            value=f"Wallet: ${self.bank[user_id]['wallet']:,}\nBank: ${self.bank[user_id]['bank']:,}",
            inline=False
        )
        embed.set_footer(text=f"Removed by {ctx.author.name}")

        await ctx.send(embed=embed)

    @removemoney.error
    async def removemoney_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Usage: !removemoney @user <amount>")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid arguments! Usage: !removemoney @user <amount>")

    @commands.command(name='bankrob')
    @commands.cooldown(1, 3600, commands.BucketType.guild)  # Once per hour per server
    async def bankrob(self, ctx, target: discord.Member):
        """Start a bank robbery (requires 5 people)"""
        if ctx.author == target:
            await ctx.send("❌ You can't rob yourself!")
            return

        target_id = str(target.id)
        if target_id not in self.bank or self.bank[target_id]["bank"] < 1000:
            await ctx.send("❌ This user doesn't have enough money in their bank to rob!")
            return

        # Create heist embed
        embed = discord.Embed(
            title="🏦 Bank Heist",
            description=f"A heist is being planned on {target.mention}'s bank!\n"
                       f"Need 5 people to join! React with 💰 to join.\n"
                       f"You have 30 minutes to gather your crew!",
            color=discord.Color.red()
        )
        embed.add_field(name="Potential Loot", value=f"${self.bank[target_id]['bank']:,}")
        embed.add_field(name="Success Rate", value="50%")
        embed.add_field(name="Join Cost", value="$1,000")
        embed.add_field(name="Time Limit", value="30 minutes", inline=False)
        
        heist_message = await ctx.send(embed=embed)
        await heist_message.add_reaction("💰")

        # Wait for reactions
        joined_users = set()
        joined_users.add(ctx.author.id)  # Add the initiator

        def check(reaction, user):
            if user.bot or user == target or user.id in joined_users:
                return False
            return str(reaction.emoji) == "💰" and reaction.message.id == heist_message.id

        try:
            while len(joined_users) < 5:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=1800.0, check=check)  # 30 minutes timeout
                user_id = str(user.id)
                
                # Check if user has enough money to join
                if user_id not in self.bank or self.bank[user_id]["wallet"] < 1000:
                    await ctx.send(f"{user.mention} doesn't have enough money to join the heist!")
                    continue

                joined_users.add(user.id)
                await ctx.send(f"{user.mention} joined the heist! ({len(joined_users)}/5 people)")

        except asyncio.TimeoutError:
            await ctx.send("❌ Not enough people joined the heist in time! The heist has been cancelled.")
            return

        # Start the heist
        await ctx.send("🏃‍♂️ The heist is starting...")
        await asyncio.sleep(3)

        # Calculate success (50% chance)
        success = random.random() < 0.5

        if success:
            # Calculate loot (20-40% of target's bank)
            loot_percentage = random.uniform(0.2, 0.4)
            total_loot = int(self.bank[target_id]["bank"] * loot_percentage)
            share = total_loot // len(joined_users)

            # Remove money from target
            self.bank[target_id]["bank"] -= total_loot

            # Give money to participants
            for user_id in joined_users:
                user_id = str(user_id)
                self.bank[user_id]["wallet"] += share
                self.bank[user_id]["wallet"] -= 1000  # Deduct join cost

            self.save_bank()

            # Success embed
            success_embed = discord.Embed(
                title="🎉 Heist Successful!",
                description=f"The crew successfully robbed ${total_loot:,} from {target.mention}'s bank!\n"
                           f"Each participant got ${share:,}!",
                color=discord.Color.green()
            )
            await ctx.send(embed=success_embed)

        else:
            # Deduct join cost from participants
            for user_id in joined_users:
                user_id = str(user_id)
                self.bank[user_id]["wallet"] -= 1000

            self.save_bank()

            # Failure embed
            fail_embed = discord.Embed(
                title="❌ Heist Failed!",
                description="The police caught the crew! Everyone lost their $1,000 join cost!",
                color=discord.Color.red()
            )
            await ctx.send(embed=fail_embed)

    @bankrob.error
    async def bankrob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after / 60)
            await ctx.send(f"❌ A bank robbery was recently attempted! Try again in {minutes} minutes!")

async def setup(bot):
    """Setup function for the economy cog"""
    await bot.add_cog(Economy(bot))
