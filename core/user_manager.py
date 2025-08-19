# core/user_manager.py

from core.user import User
from logger_setup import logger


class UserManager:
    """
    Handles creation and retrieval of user objects during conversations.
    Also helps detect and prevent duplicate event processing.
    """

    def __init__(self):
        # Stores user_id → User object mapping
        self.users = {}

        # Stores recently processed Slack event IDs to avoid duplication
        self.recent_event_ids = set()

    def get_or_create_user(self, user_id: str, user_name: str = "user") -> User:
        """
        Returns an existing user or creates a new one if it doesn't exist.

        Args:
            user_id: Unique identifier from Slack or other platform
            user_name: Optional display name for logging or context

        Returns:
            User: An instance of the User class with conversation history
        """
        func = "get_or_create_user"
        logger.info(f" entered {func}\n")
        if user_id not in self.users:
            self.users[user_id] = User(user_id=user_id, user_name=user_name)
        return self.users[user_id]

    def is_duplicate_event(self, event_id: str) -> bool:
        """
        Checks whether a Slack event has already been processed.

        Args:
            event_id: Unique Slack event ID

        Returns:
            bool: True if the event has already been processed
        """
        if event_id in self.recent_event_ids:
            return True

        self.recent_event_ids.add(event_id)

        # Prune the set to prevent memory from growing unbounded
        if len(self.recent_event_ids) > 1000:
            self.recent_event_ids = set(list(self.recent_event_ids)[-500:])

        return False
