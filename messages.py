import json
from typing import List, Dict, Any, Tuple, Union, Optional, Deque

# Import the logger for consistent logging output
from logger_setup import logger

import re

def create_error_response(message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    This function ensures all error responses follow a consistent format
    throughout the application, making error handling more predictable.

    Args:
        message: The main error message describing what went wrong
        details: Optional additional details about the error (exception info, stack trace, etc.)

    Returns:
        Dict[str, Any]: A standardized error response dictionary

    Example:
        >>> error = create_error_response("Database connection failed", "Connection timeout after 30s")
        >>> print(error)
        {'type': 'error', 'data': {'message': 'Database connection failed', 'details': 'Connection timeout after 30s'}}
    """
    response = {
        "type": "error",
        "data": {
            "message": message
        }
    }

    if details:
        response["data"]["details"] = details

    logger.debug(f"Created error response: {message}")
    return response


def create_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized success response dictionary.

    Args:
        data: The main response data (query results, processed information, etc.)
        message: Optional success message to include

    Returns:
        Dict[str, Any]: A standardized success response dictionary

    Example:
        >>> result = create_success_response([{"id": 1, "name": "John"}], "Query executed successfully")
        >>> print(result["type"])  # "success"
    """
    response = {
        "type": "success",
        "data": data
    }

    if message:
        response["message"] = message

    logger.debug("Created success response")
    return response


def validate_event(body: Dict, user_manager) -> Union[Dict[str, str], None]:
    """
    Validates an incoming Slack event request.

    Args:
        body (Dict): The JSON payload from the Slack event request.
        user_manager: Object with `is_duplicate_event(event_id)` method.

    Returns:
        Dict[str, str] if early return is needed (challenge, duplicate, or error),
        or None if the event is valid and of type 'app_mention'.
    """
    func ="validate_event"
    logger.info(f" entered {func}\n")
    # Handle Slack URL verification challenge
    if "challenge" in body:
        return {"challenge": body["challenge"]}

    # Check for duplicate event
    event_id: str = body.get("event_id")
    if user_manager.is_duplicate_event(event_id):
        logger.info(f" in {func} ⚠️ Duplicate event received, ignoring: {event_id}\n")
        return {"status": "duplicate"}

    # Validate event type
    event = body.get("event", {})
    if event.get("type") != "app_mention":
        logger.info(f" in {func} 📥 Not an app_mention\n")
        return {"status": "error"}

    logger.info(f" in {func} 📥 Received Slack request: {body['event']['text']}\n")
    return None  # Event is valid and can be processed

def extract_query_and_metadata(event: Dict, bot_name: str) -> Tuple[str, str, str]:
    """
    Extracts the cleaned query text and metadata (channel_id and user_id)
    from a Slack event.

    Args:
        event (Dict): The Slack event payload.
        bot_name (str): The bot's display name to replace Slack mention tags.

    Returns:
        Tuple[str, str, str]: (query, channel_id, user_id)
    """
    func = "extract_query_and_metadata"
    logger.info(f" entered {func}\n")
    user_text = event.get("text", "")
    channel_id = event.get("channel")
    user_id = event.get("user")
    query = re.sub(r"<@[^>]+>", bot_name, user_text).strip()

    return query, channel_id, user_id


def sanitize_incoming_messages(
    messages: Deque[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Sanitize raw messages before sending to OpenAI:
    - Keep only 'user' and 'assistant' roles.
    - Flatten 'tool_calls' into 'content' if needed.
    - Add a system prompt at the beginning.
    """

    sanitized: List[Dict[str, Any]] = []

    for msg in messages:
        role = msg.get("role")
        if role not in ("user", "assistant"):
            continue

        new_msg: Dict[str, Any] = {
            "role": role,
            "content": msg.get("content", "") or ""
        }

        if role == "assistant" and msg.get("tool_calls"):
            try:
                tool_calls_str = json.dumps(msg["tool_calls"], ensure_ascii=False)
            except (TypeError, ValueError):
                tool_calls_str = str(msg["tool_calls"])

            if new_msg["content"]:
                new_msg["content"] += "\n"
            new_msg["content"] += f"[tool_calls]: {tool_calls_str}"

        sanitized.append(new_msg)

    return sanitized

def create_simplified_tool_response(tool_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a simplified version of tool response for sending to LLM.

    For image responses, strips out the base64 image data and replaces it with
    a simple success message, while preserving metadata like chart_type and title.
    This optimization prevents sending large base64 image data to the LLM.

    Args:
        tool_result: Original tool response dictionary

    Returns:
        Dict[str, Any]: Simplified tool response suitable for LLM processing
    """
    func = "create_simplified_tool_response"
    # Check if this is an image response (success type with image data)
    if (isinstance(tool_result, dict) and
            tool_result.get("type") == "success" and
            isinstance(tool_result.get("data"), dict) and
            "image" in tool_result["data"]):
        logger.info(f" in {func} Stripping image data from tool response for LLM processing (keeping original for API response)")

        # Create simplified response without image data
        simplified_data = {
            "chart_type": tool_result["data"].get("chart_type", "chart"),
            "title": tool_result["data"].get("title", "Chart"),
            "image": "generated successfully"
        }

        return {
            "type": "success",
            "data": simplified_data
        }

    # For non-image responses, return as-is
    return tool_result

