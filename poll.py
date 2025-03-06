import discord
from discord.ext import commands

import asyncio
from discord.ext import tasks
from datetime import datetime, time, timedelta
import pytz

async def send_poll(channel, question, options):
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
    emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    # Create poll embed
    embed = discord.Embed(
        title=f"📊 POLL: {question}",
        color=discord.Color.blue()
    )
    
    # Add options to the embed
    description = ""
    for i, option in enumerate(options):
        if i < len(emoji_numbers):  # Limit to 10 options
            description += f"{emoji_numbers[i]} {option}\n\n"
    
    embed.description = description
    embed.set_footer(text="React to vote! Poll closes in 10 minutes.")
    
    # Send the poll message
    poll_message = await channel.send(embed=embed)
    
    # Add reaction options
    for i in range(min(len(options), len(emoji_numbers))):
        await poll_message.add_reaction(emoji_numbers[i])
    
    return poll_message

async def collect_poll_results(message, options, emoji_numbers):
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
    
    for i, option in enumerate(options):
        if i < len(emoji_numbers):
            reaction = discord.utils.get(message.reactions, emoji=emoji_numbers[i])
            count = reaction.count - 1 if reaction else 0  # Subtract 1 to exclude bot's reaction
            results.append({option: count})
    
    return results

def is_weekday():
    """Check if today is a weekday"""
    return datetime.now().weekday() < 5

@tasks.loop(time=[
    time(hour=13, tzinfo=pytz.timezone('US/Pacific')),  # 1 PM PST
    time(hour=22, tzinfo=pytz.timezone('US/Pacific'))   # 7 PM PST
])
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
        
    meal_type = "dinner"
    
    question = f"How was today's {meal_type}?"
    options = ["Great! 😋", "Good 👍", "Okay 😐", "Not good 👎", "Bad 😢"]
    emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    print(f"Sending poll to channel: {channel.name}")
    poll_message = await send_poll(channel, question, options)
    
    # Wait 10 minutes
    await asyncio.sleep(10)  # 10 minutes in seconds
    
    # Collect results
    results = await collect_poll_results(poll_message, options, emoji_numbers)
    
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