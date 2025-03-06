import os
from poll import send_poll, setup_meal_polls
import discord
import logging

from discord.ext import commands
from dotenv import load_dotenv
from agent import KitchentBotAgent

PREFIX = "!"

# Setup logging
logger = logging.getLogger("discord")

# Load the environment variables
load_dotenv()

# Create the bot with all intents
# The message content and members intent must be enabled in the Discord Developer Portal for the bot to work.
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Import the Mistral agent from the agent.py file
agent = KitchentBotAgent()


# Get the token from the environment variables
token = os.getenv("DISCORD_TOKEN")


@bot.event
async def on_ready():
    """
    Called when the client is done preparing the data received from Discord.
    Prints message on terminal when bot successfully connects to discord.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_ready
    """
    logger.info(f"{bot.user} has connected to Discord!")

    # Get the channel ID from environment variable or use a default
    channel_id = int(
        os.getenv("POLL_CHANNEL_ID", "0")
    )  # Replace 0 with your default channel ID
    if channel_id:
        setup_meal_polls(bot, channel_id, agent)
        print(f"Started meal polls in channel: {channel_id}")
        # print(f"Started meal polls in channel: {channel_id}")
    else:
        logger.warning("No POLL_CHANNEL_ID set in .env file")


@bot.event
async def on_message(message: discord.Message):
    """
    Called when a message is sent in any channel the bot can see.

    https://discordpy.readthedocs.io/en/latest/api.html#discord.on_message
    """
    # Don't delete this line! It's necessary for the bot to process commands.
    await bot.process_commands(message)

    # Ignore messages from self or other bots to prevent infinite loops.
    if message.author.bot or message.content.startswith("!"):
        return

    # Process the message with the agent you wrote
    # Open up the agent.py file to customize the agent
    logger.info(f"Processing message from {message.author}: {message.content}")
    response = await agent.run(message)
    if response:
        await message.reply(response)


# Bot sends polls at 1pm and 7pm PST every weekday
"""
Bot should send a poll at 1pm and 7pm PST every weekday after the meal, 
asking whether users liked the meal or not. Bot should then save the poll results 
to feedback class after 10 minutes.
"""
# TODO: ETHAN implement this

# to store:
# agent.feedback.add_poll_result(poll_name, poll_results)


# Commands


# This example command is here to show you how to add commands to the bot.
# Run !ping with any number of arguments to see the command in action.
# Feel free to delete this if your project will not need commands.
@bot.command(name="ping", help="Pings the bot.")
async def ping(ctx, *, arg=None):
    if arg is None:
        await ctx.send("Pong!")
    else:
        await ctx.send(f"Pong! Your argument was {arg}")


# Start the bot, connecting it to the gateway
bot.run(token)
