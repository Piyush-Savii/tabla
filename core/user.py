# core/user.py

import os
from collections import deque
from dotenv import load_dotenv

from logger_setup import logger


class User:
    """
    Represents a user interacting with the assistant.
    Stores user identity, conversation history, and context like role and company.
    """

    def __init__(
        self,
        user_id: str,
        user_name: str,
        bot_name: str = None,
        user_role: str = None,
        user_context: str = None,
        max_history: int = 100
    ):
        load_dotenv()  # Load environment variables from .env if present

        self.user_id = user_id  # Unique identifier for the user (e.g., from Slack)
        self.user_name = user_name  # Display name

        # Chat history: most recent 100 messages (or configured max)
        self.history = deque(maxlen=max_history)

        # Contextual settings for personalized responses
        self.bot_name = bot_name or os.getenv("BOT_NAME", "EIRANA")
        self.user_role = user_role or os.getenv("USER_ROLE", "a growth analyst")
        self.user_context = user_context or os.getenv(
            "USER_CONTEXT",
            "a fintech startup operating in retail lending in Philippines"
        )

    def add_message(self, role: str, content: str):
        """
        Adds a message to the user's chat history.

        Args:
            role: 'user' or 'assistant'
            content: Text content of the message
        """
        func = "add_message"
        logger.info(f" entered {func}\n")
        self.history.append({"role": role, "content": content})

    def get_history(self):
        """
        Returns:
            List of messages exchanged with the assistant.
        """
        func = "get_history"
        logger.info(f" entered {func}\n")
        return list(self.history)

    def get_name(self):
        """
        Returns:
            User's display name.
        """
        func = "get_name"
        logger.info(f" entered {func}\n")
        return self.user_name

    def update_user_role(self, user_role: str):
        """
        Updates the user's role (e.g., 'data analyst', 'founder').
        """
        func = "update_user_role"
        logger.info(f" entered {func}\n")
        self.user_role = user_role

    def update_user_context(self, user_context: str):
        """
        Updates the user's context (e.g., company type, industry).
        """
        func = "update_user_context"
        logger.info(f" entered {func}\n")
        self.user_context = user_context
