import os
from mistralai import Mistral
import discord
from feedback import Feedback
from menus import Menus
from datetime import datetime

MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = "You are a helpful assistant."


class KitchentBotAgent:
    def __init__(self):
        MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
        self.feedback = Feedback()
        self.menus = Menus()
        self.client = Mistral(api_key=MISTRAL_API_KEY)

    def add_new_menu(self, message: str):
        """
        Add a new menu to the menus class
        """
        this_week_start_date = datetime.now().date()
        # Adjust to previous Sunday if not already Sunday
        this_week_start_date = this_week_start_date - datetime.timedelta(
            days=this_week_start_date.weekday()
        )
        self.menus.add_menu(this_week_start_date, message)

    def add_new_feedback(self, user: str, message: str):
        """
        Add a new feedback to the feedback class
        """
        self.feedback.add_feedback(user, message)

    def question_about_menu(self, message: str):
        """
        Question about the menu
        """
        # TODO: Arnav implement this
        pass

    def question_about_feedback(self, message: str):
        """
        Question about the feedback
        """
        # TODO: Arnav implement this
        pass

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
