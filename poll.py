import discord
from discord.ext import commands

import asyncio
from discord.ext import tasks
from datetime import datetime, time, timedelta
import pytz

async def send_poll(channel, question, options=None):
    """
    Send a poll to the specified channel
    
    Parameters:
    - channel: The discord channel to send the poll to
    - question: The poll question (string)
    - options: List of poll options (strings)
    
    Returns:
    - The poll message object
    """
    # Define emoji options (up to 10)
    emoji_numbers = ['😋', '👍', '😐', '👎', '😢']
    
    # Create poll embed
    embed = discord.Embed(
        title=f"📊 POLL: {question}",
        color=discord.Color.blue()
    )
    
    # Add options to the embed
    description = ""
    if options is not None:
        for i, option in enumerate(options):
            if i < len(emoji_numbers):  # Limit to 10 options
                description += f"{emoji_numbers[i]} {option}\n\n"
    
    embed.description = description
    embed.set_footer(text="React to vote! Poll closes in 1 hour.")
    
    # Send the poll message
    poll_message = await channel.send(embed=embed)
    
    # Add reaction options
    for i in range(len(emoji_numbers)):
        await poll_message.add_reaction(emoji_numbers[i])
    
    return poll_message

async def collect_poll_results(message, emoji_numbers):
    """
    Collect results from a poll after it ends
    
    Parameters:
    - message: The poll message
    - options: List of poll options
    - emoji_numbers: List of emoji numbers used
    
    Returns:
    - Dictionary with poll results
    """
    results = []
    message = await message.channel.fetch_message(message.id)
    
    for i, option in enumerate(emoji_numbers):
        if i < len(emoji_numbers):
            print(f"Reaction:{emoji_numbers[i][-1]}")
            print("message.reactions:", message.reactions)
            reaction = discord.utils.get(message.reactions, emoji=f"{emoji_numbers[i][-1]}")
            print(f"Reaction: {reaction}")
            count = reaction.count - 1 if reaction else 0  # Subtract 1 to exclude bot's reaction
            results.append({option: count})
    
    return results

def is_weekday():
    """Check if today is a weekday"""
    return datetime.now().weekday() < 5

@tasks.loop(time=[
    time(hour=13, tzinfo=pytz.timezone('US/Pacific')),  # 1 PM PST
    time(hour=19, tzinfo=pytz.timezone('US/Pacific'))   # 7 PM PST
])
# @tasks.loop(minutes=3)
async def meal_poll(bot, channel, agent):
    """
    Send a poll at 10pm PST
    
    Parameters:
    - bot: The discord bot instance
    - channel: The discord channel to send polls to
    - agent: The bot agent instance for storing results
    """
    print("Checking if it's a weekday")
    if not is_weekday():
        print("Not a weekday")
        return
        
    # Determine meal type based on current time
    current_time = datetime.now(pytz.timezone('US/Pacific'))
    lunch_time = current_time.replace(hour=13, minute=0)
    dinner_time = current_time.replace(hour=19, minute=0)
    
    # Calculate time differences
    time_to_lunch = abs((current_time - lunch_time).total_seconds())
    time_to_dinner = abs((current_time - dinner_time).total_seconds())
    
    meal_type = "lunch" if time_to_lunch < time_to_dinner else "dinner"
    
    question = f"How was today's {meal_type}?"
    # options = ["Great! 😋", "Good 👍", "Okay 😐", "Not good 👎", "Bad 😢"]
    emoji_numbers = ['1️😋', '2️👍', '3️😐', '4️👎', '5️😢']
    print(f"Sending poll to channel: {channel.name}")
    poll_message = await send_poll(channel, question)
    
    # Wait 1 hour
    await asyncio.sleep(3600)
    
    # Collect results
    results = await collect_poll_results(poll_message, emoji_numbers)
    
    # Store results in feedback
    current_date = datetime.now().strftime("%m/%d")
    poll_name = f"{meal_type} {current_date}"
    agent.feedback.add_poll_result(poll_name, results)
    
    # Update poll to show it's closed
    embed = poll_message.embeds[0]
    embed.set_footer(text="Poll closed! Results have been recorded.")
    await poll_message.edit(embed=embed)

def setup_meal_polls(bot, channel_id, agent):
    """
    Setup the meal polls task
    
    Parameters:
    - bot: The discord bot instance
    - channel_id: The ID of the channel to send polls to
    - agent: The bot agent instance for storing results
    """
    channel = bot.get_channel(channel_id)
    if channel:
        meal_poll.start(bot, channel, agent)
        print(f"Started meal polls in channel: {channel.name}")
    else:
        print(f"Could not find channel with ID: {channel_id}")