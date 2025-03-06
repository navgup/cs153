import discord
from discord.ext import commands

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
    embed.set_footer(text="React to vote!")
    
    # Send the poll message
    poll_message = await channel.send(embed=embed)
    
    # Add reaction options
    for i in range(min(len(options), len(emoji_numbers))):
        await poll_message.add_reaction(emoji_numbers[i])
    
    return poll_message