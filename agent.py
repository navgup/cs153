import os
from mistralai import Mistral
import discord
from feedback import Feedback
from menus import Menus

MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = "You are a helpful assistant."


class KitchentBotAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        self.feedback = Feedback()
        self.menus = Menus()
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    async def run(self, message: discord.Message):
        """
        Super function that gets the intent of the user's message and
        calls the appropriate function:
        - new menu
        - new feedback
        - question about menu
        - question about feedback
        """
        # The simplest form of an agent
        # Send the message's content to Mistral's API and return Mistral's response

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message.content},
        ]

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        return response.choices[0].message.content
