# core/platform.py

import os
import base64
import io

from fastapi import APIRouter, Request
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from core.llm_client import LLMClient
from logger_setup import logger
from messages import extract_query_and_metadata, validate_event
from prompts import get_system_prompt
from yaml_read import load_yaml
from core.user_manager import UserManager

#TODO error response to slack


class PlatformBase:
    """
    Initializes and configures the chatbot platform (e.g., Slack).
    Sets up routing and integrates with the AI model client.
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client
        self.platform = os.getenv("BOT_SOURCE", "slack")
        self.bot_token = os.getenv("BOT_TOKEN")
        self.bot_secret = os.getenv("BOT_SECRET_KEY")
        self.bot_name = os.getenv("BOT_NAME", "EIRANA")

        self.router = APIRouter()
        self.user_manager = UserManager()
        self.slack_client = WebClient(token=self.bot_token)

        self._validate()
        self._register_routes()

    def _validate(self):
        config = load_yaml()
        allowed = config.get("allowed_bots", [])
        func = "_validate"

        if self.platform not in allowed:
            logger.error(f" in {func} ❌ Platform '{self.platform}' not allowed. Allowed: {allowed}\n")
        if not self.bot_token:
            logger.error(f" in {func} ❌ BOT_TOKEN not set in environment.\n")

        logger.info(f" in {func} ✅ Loaded and validated bot platform: {self.platform}\n")

    def _register_routes(self):
        func = "_register_routes"
        if self.platform == "slack":
            self.router.post("/slack/events")(self.slack_events)
            logger.info(f" in {func} ✅ Slack route registered at /slack/events\n")
        else:
            logger.warning(f" in {func} ⚠️ Platform '{self.platform}' route registration not implemented.\n")

    async def slack_events(self, request: Request):
        func = "slack_events"
        logger.info(f" entered {func}\n")

        body = await request.json()

        validation_response = validate_event(body, self.user_manager)
        if validation_response:
            logger.info(f"in {func} validation_response returned not None\n")
            return validation_response

        event = body.get("event", {})
        user_query, channel_id, user_id = extract_query_and_metadata(event, self.bot_name)

        slack_user_info = self.slack_client.users_info(user=user_id)
        slack_user = slack_user_info.get("user", {})
        display_name = slack_user.get("real_name") or slack_user.get("name")

        #for terminal testing
        #query = "Give me Bar graph of disbursed amount of loans by month for year 2024."
        #channel_id = "ABCD"
        #user_id = "P1434"
        #display_name = "Piyush"

        user_obj = self.user_manager.get_or_create_user(user_id, display_name)

        logger.info(f" in {func} 📨 Mentioned by user {display_name} ({user_id}) in {channel_id}: {user_query}\n")

        if user_query is None:
            logger.error(f" in {func} Message validation failed\n")
            return {"status": "error"}

        conversation_history = user_obj.get_history()
        if conversation_history:
            logger.debug(f" in {func} conversation_history - {conversation_history[0]}")
        else:
            logger.debug(f" in {func} conversation_history is empty ❌")
        conversation_history.append({"role": "user", "content": user_query})

        temp_history = conversation_history.copy()
        temp_history.insert(0, {
            "role": "system",
            "content": get_system_prompt(prompt_type="data_analyst", user=user_obj)
        })

        logger.info(f" in {func} Processing conversation with {len(temp_history)} messages\n")
        response = self.llm.process_user_request(
            conversation_history=temp_history,
            user=user_obj
        )

#        new_messages = extract_new_messages_from_conversation(conversation_history, response)

        output = response[-1]["content"]
        user_obj.add_message(role="user", content=user_query)
        user_obj.add_message(role="assistant", content=output)

        # Extract the image data from _original_content
#        base64_image = response[-2]["_original_content"]["data"]["image"]

        logger.info(f" in {func} 🧠 AI responded: {output}...\n")

        # ✅ Handle image upload if present in the tool response
        last_tool_response = next(
            (msg for msg in reversed(response) if msg.get("role") == "tool" and isinstance(msg.get("_original_content"), dict)),
            None
        )

        if last_tool_response:
            content = last_tool_response["_original_content"]
            if isinstance(content, dict):
                image_base64 = content.get("data")["image"]
                image_title = content["data"].get("title", "visual.png")
                if image_base64:
                    try:
                        # Strip prefix if present
                        if image_base64.startswith("data:image"):
                            image_base64 = image_base64.split(",")[1]

                        # Fix padding if needed
                        missing_padding = len(image_base64) % 4
                        if missing_padding:
                            image_base64 += "=" * (4 - missing_padding)

                        image_bytes = base64.b64decode(image_base64)
                        image_file = io.BytesIO(image_bytes)
                        image_file.name = image_title  # Needed for Slack
                        self.slack_client.files_upload_v2(
                            channel=channel_id,
                            file_uploads=[
                                {
                                    "file": image_file,
                                    "filename": image_title,
                                    "title": image_title
                                }
                            ]
                        )
                        logger.info(f" in {func} 📊 Image uploaded to Slack\n")
                    except SlackApiError as e:
                        logger.error(f" in {func} ❌ Failed to upload image to Slack: {e.response['error']}\n")
                    except Exception as e:
                        logger.error(f" in {func} ❌ Unexpected error during image upload: {str(e)}\n")
                else:
                    logger.info(f" in {func} 📊 No Image created\n")

        # ✅ Send the assistant's text response
        try:
            self.slack_client.chat_postMessage(channel=channel_id, text=output)
            logger.info(f" in {func} 📤 Response sent to Slack channel {channel_id}\n")
        except SlackApiError as e:
            logger.error(f" in {func} ❌ Failed to send message to Slack: {e.response['error']}\n")

        return {"status": "ok"}
