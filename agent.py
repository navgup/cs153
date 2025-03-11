import os
from mistralai import Mistral
import discord
from feedback import Feedback
from menus import Menus
from datetime import datetime, timedelta
import asyncio

MISTRAL_MODEL = "mistral-large-latest"
SYSTEM_PROMPT = "You are a helpful assistant."

CLASSIFY_MESSAGE_PROMPT = """

    Classify the message as one of the following categories:
    1. new feedback
    2. question about menu
    3. question about feedback

    Return just the name of the category and nothing else. If the message does not fall 
    into any of the categories, return "None". 

    Example:
    Message: Dinner today was great!
    Response: new feedback

    Example: 
    Message: Whats for lunch tomorrow?
    Response: question about menu

    Example:
    Message: What did people think of the food today?
    Response: question about feedback


    """

MENU_QUESTION_PROMPT = """

    The user is asking about the menu for this week. 

    If the user asks a question about the macronutrient profile of the menu,
    or an item on the menu, please give your best breakdown. 

    Example:
    User: “Can you give me the macros for the Wednesday dinner?”

    Response:
    “Per serving, here’s the approximate macronutrient profile:

    Calories: ~450
    Protein: ~35g
    Carbohydrates: ~40g
    Fat: ~15g
    ”

    The menu is attached below as a csv file:


"""


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
        this_week_start_date = this_week_start_date - timedelta(
            days=this_week_start_date.weekday()
        )
        self.menus.add_menu(this_week_start_date, message)

    def add_new_feedback(self, date: str, message: str):
        """
        Add a new feedback to the feedback class
        """
        self.feedback.add_feedback(date, message)

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

        # if message has a csv file, add new menu
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename.endswith(".csv"):
                    # Read the CSV content as text
                    csv_content = await attachment.read()
                    csv_content = csv_content.decode("utf-8")
                    self.add_new_menu(csv_content)
                    return "Menu added successfully!"  # + csv_content[:100]

        messages = [
            {"role": "system", "content": CLASSIFY_MESSAGE_PROMPT},
            {"role": "user", "content": message.content},
        ]

        response = await self.client.chat.complete_async(
            model=MISTRAL_MODEL,
            messages=messages,
        )

        # add delay for rate limit avoidance for 1 second
        await asyncio.sleep(1)
        if response.choices[0].message.content == "new feedback":
            ADD_FEEDBACK_PROMPT = f"""

            The user is providing feedback about the meal today. Here is the menu for the week:

            {self.menus.get_latest_menu()}

            Today's date is: {datetime.now().strftime("%Y-%m-%d")}

            The user feedback is: {message.content}

            Please return a processed feedback message that explains the user's feedback with context from the menu on
            the meal the user is referring to.

            """
            messages = [
                {"role": "system", "content": ADD_FEEDBACK_PROMPT},
                {"role": "user", "content": message.content},
            ]

            reply = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=messages,
            )
            self.add_new_feedback(
                message.created_at.strftime("%Y-%m-%d"), message.content
            )
            return "Thanks for your feedback! We will take it into account."

        elif response.choices[0].message.content == "question about menu":
            cur_menu = self.menus.get_latest_menu()

            messages = [
                {"role": "system", "content": MENU_QUESTION_PROMPT + cur_menu},
                {"role": "user", "content": message.content},
            ]

            reply = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=messages,
            )
            return reply.choices[0].message.content

        elif response.choices[0].message.content == "question about feedback":
            feedback = self.feedback.get_feedback()
            poll_results = self.feedback.get_poll_results()

            messages = [
                {
                    "role": "system",
                    "content": "The feedback is: "
                    + str(feedback)
                    + "The poll results are: "
                    + str(poll_results),
                },
                {"role": "user", "content": message.content},
            ]

            reply = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=messages,
            )
            return reply.choices[0].message.content

        else:
            return None
        #     return "lol ! 8==D" + str(response.choices[0].message.content)
