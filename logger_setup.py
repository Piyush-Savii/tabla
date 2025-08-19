# logger_setup.py
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get desired log level from environment, default to "INFO"
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Get a custom name for the logger (e.g., chatbot name), fallback to 'chatbot'
chatbot_name = os.getenv("CHATBOT_NAME", "chatbot").lower()

# Create or retrieve the logger instance using chatbot name
logger = logging.getLogger(chatbot_name)

# Convert log level string to numeric level, fallback to INFO
numeric_level = getattr(logging, log_level, logging.INFO)
logger.setLevel(numeric_level)

# Log the startup log level once (should be before handlers to ensure output)
logger.info(f"Logging started at level: {log_level} for '{chatbot_name}'")

# Create a handler for console (stdout) output
console_handler = logging.StreamHandler()
console_handler.setLevel(numeric_level)

# Define the log message format
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Avoid adding multiple handlers if logger is reused
if not logger.hasHandlers():
    logger.addHandler(console_handler)

#logger = logging.getLogger(os.getenv("CHATBOT_NAME", "palindrome-bot"))
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("logs/slackbot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


#file_handler = logging.FileHandler("logs/app.log")
#file_handler.setLevel(numeric_level)
#file_handler.setFormatter(formatter)
#logger.addHandler(file_handler)
