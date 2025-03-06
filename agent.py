import os
from mistralai import Mistral
import discord
from feedback import Feedback
from menus import Menus
from datetime import datetime, timedelta

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

    def add_new_feedback(self, user: str, message: str):
        """
        Add a new feedback to the feedback class
        """
        self.feedback.add_feedback(user, message)
              

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

        if response.choices[0].message.content == "new feedback":

            ADD_FEEDBACK_PROMPT = f"""

            The user is providing feedback about the meal today. Here is the menu for today:

            {self.menus.get_latest_menu()}

            The user feedback is: {message.content}

            """


            self.add_new_feedback(message.author.name, message.content)

        elif response.choices[0].message.content == "question about menu":
            cur_menu = self.menus.get_latest_menu() 

            messages = [
                {"role": "system", "content": MENU_QUESTION_PROMPT + cur_menu},
                {"role": "user", "content": message},
            ]

            reply = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=messages,
            )
            return reply.choices[0].message.content 
        
        elif response.choices[0].message.content == "question about feedback":
            feedback = self.feedback.get_feedback()

            

            messages = [
                {"role": "system", "content": "The feedback is: " + feedback},
                {"role": "user", "content": message.content},
            ]

            reply = await self.client.chat.complete_async(
                model=MISTRAL_MODEL,
                messages=messages,
            )
            return reply.choices[0].message.content


        else:
            return "lol ! 8==D"
