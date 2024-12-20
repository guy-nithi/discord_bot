DISCORD_TOKEN=your_token_here# Advanced Discord Bot

A feature-rich Discord bot with moderation, music, fun commands, and more!

## Features

### Music Commands
- `!play <url>` - Play music from YouTube
- `!stop` - Stop playing music

### General Commands
- `!ping` - Check bot latency
- `!roll NdN` - Roll dice (e.g., !roll 2d6)
- `!clear <amount>` - Clear messages (requires permissions)

### Moderation Commands
- `!kick <member> [reason]` - Kick a member
- `!ban <member> [reason]` - Ban a member
- `!warn <member> [reason]` - Warn a member

### Fun Commands
- `!meme` - Get a random meme
- `!joke` - Get a random joke

## Setup Instructions

1. Install Python 3.8 or higher
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Install FFmpeg (required for music features):
   - On macOS: `brew install ffmpeg`
   - On Ubuntu: `sudo apt install ffmpeg`
   - On Windows: Download from FFmpeg website and add to PATH

4. Create a Discord Bot:
   - Go to Discord Developer Portal
   - Create a new application
   - Go to the Bot section
   - Create a bot and copy the token
   - Enable all Privileged Gateway Intents

5. Set up environment:
   - Copy `.env.example` to `.env`
   - Replace `your_token_here` with your bot token

6. Run the bot:
   ```bash
   python bot.py
   ```

## Required Permissions

The bot needs the following permissions:
- Read Messages/View Channels
- Send Messages
- Manage Messages
- Embed Links
- Attach Files
- Read Message History
- Connect (Voice)
- Speak (Voice)
- Use Voice Activity
- Kick Members (for moderation)
- Ban Members (for moderation)

## Security Note

Never share your bot token with anyone or commit it to version control. Always use environment variables for sensitive information.

## Contributing

Feel free to submit issues and enhancement requests!
