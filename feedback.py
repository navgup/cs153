# feedback.py
# This file implements a feedback class
"""
Feedback Abstraction:
- init
feedback: dict
poll_results: dict
- add poll result (poll_name, poll_results)
poll_result format:
poll_name string
poll_results: [{“lunch 2/10”: 0.1}, {“dinner 2/10”: 0.2}, … {“dinner 2/14”: }]
- add feedback (user: str, feedback_message: str)
"""


class Feedback:
    def __init__(self):
        """Initialize empty feedback and poll results dictionaries"""
        self.feedback = {}  # Store user feedback messages
        self.poll_results = {}  # Store poll results by poll name

    def add_poll_result(self, poll_name: str, poll_results: list):
        """
        Add poll results for a given poll
        Args:
            poll_name: Name/identifier of the poll
            poll_results: List of dictionaries containing poll results
        """
        self.poll_results[poll_name] = poll_results
        print(f"Added poll result for {poll_name}: {poll_results}")
        print(f"Poll results: {self.poll_results}")

    def add_feedback(self, date: str, feedback_message: str):
        """
        Add feedback from a date
        Args:
            date: Date of feedback
            feedback_message: The feedback message content
        """
        if date not in self.feedback:
            self.feedback[date] = []
        self.feedback[date].append(feedback_message)

    def get_feedback(self):
        """
        Get all feedback messages
        Returns:
            Dictionary containing all feedback messages
        """
        print(f"Getting feedback: {self.feedback}")
        return self.feedback

    def get_poll_results(self):
        """
        Get all poll results
        Returns:
            Dictionary containing all poll results
        """
        print(f"Getting poll results: {self.poll_results}")

        return self.poll_results
