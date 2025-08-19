# core/llm_client.py

import json
import os
from typing import List, Dict

# OpenAI SDK for interacting with GPT models
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Internal modules
import router  # Routes tool/function calls
from core.user import User  # User session data
from logger_setup import logger  # Central logging
from messages import create_simplified_tool_response  # Cleaned response generator
from yaml_read import get_provider_config  # Load LLM config from YAML
import tools  # Available tool/function definitions


# Load available tool definitions for function calling
AVAILABLE_TOOLS = [
    tools.googlebigquery,
    tools.bar_chart,
    tools.pie_chart,
    tools.single_line_graph,
    tools.multiple_line_graph,
    tools.single_area_chart,
    tools.stacked_area_chart,
    tools.resolve_name
]

from enum import EnumMeta
import copy

def sanitize_tool_for_gemini(tool):
    tool = copy.deepcopy(tool)
    if tool.get("type") != "function":
        return tool

    fn = tool["function"]
    params = fn.get("parameters", {})

    # Remove unsupported keys
    params.pop("strict", None)
    for k, v in params.get("properties", {}).items():
        v.pop("examples", None)
        v.pop("strict", None)
        if isinstance(v.get("enum"), EnumMeta):
            v["enum"] = [e.value for e in v["enum"]]
        elif isinstance(v.get("enum"), list):
            v["enum"] = [e for e in v["enum"] if e is not None]

    fn["parameters"] = params
    return tool


class LLMClient:
    """
    Connects to a Language Model (LLM) provider like OpenAI.
    Responsible for sending user conversations to the AI and receiving replies.
    """

    def __init__(self, llm_provider: str):
        # Load provider-specific configuration (API key, model, etc.)
        self.llm_provider = llm_provider
        self.llm_config = get_provider_config(self.llm_provider)
        self.llm_api_key = os.getenv("AI_KEY")
        self.llm_model = self.llm_config["model"]

        if self.llm_provider == "gemini":
            self.llm_client = OpenAI(
                api_key=self.llm_api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        else:
            self.llm_client = OpenAI(api_key=self.llm_api_key)

#        if "base_url" in self.llm_config:
#            openai.base_url = self.llm_config["base_url"]

        self._validate()

    def _validate(self):
        """
        Validates if API key and selected model are correctly configured.
        Logs any configuration issues.
        """
        func = "_validate"
        if not self.llm_api_key:
            logger.error(f" in {func} ⚠️ API_KEY missing for {self.llm_provider}\n")
        if self.llm_model not in self.llm_config.get("all_models", []):
            logger.warning(
                f" in {func} ⚠️ Model '{self.llm_model}' not listed in supported models: {self.llm_config.get('all_models', [])}\n"
            )

    def respond(
        self,
        messages: List[Dict[str, str]],
        user_name: str = "User"
    ) -> ChatCompletion | None:
        """
        Sends the conversation history to the LLM and gets a response.

        Args:
            messages: List of messages with roles (system/user/assistant) and text.
            user_name: For logging purposes.

        Returns:
            A response object from the LLM or None if an error occurred.
        """
        func = "respond"
        logger.info(f" in {func} 💬 {user_name} reached LLM module with {len(messages)} messages\n")
        logger.debug(f"in {func} Message: {messages}\n")

        try:
            if self.llm_provider == "gemini":
                safe_tools = [sanitize_tool_for_gemini(t) for t in AVAILABLE_TOOLS]
            else:
                safe_tools = AVAILABLE_TOOLS

            response = self.llm_client.chat.completions.create(
                model=self.llm_model, # default gpt-4o
                messages=messages,
                user=user_name,
                tools=safe_tools,
                tool_choice="auto"  # LLM decides whether to call tools/functions
            )
            logger.info(f" in {func} ✅ LLM responded: {response.choices[0].message.content}\n")
            return response

        except Exception as e:
            logger.error(f" in {func} ❌ LLM API call failed for {user_name}: {e}\n")
            return None

    def process_user_request(
            self,
            conversation_history: List[Dict[str, str]],
            user: User,
            depth: int = 0,
            max_depth: int = 5
    ) -> List[Dict[str, str]]:
        """
        Recursive function to process a user request through OpenAI and tool calls.

        Args:
            conversation_history: History of the messages (user + assistant + tool)
            user: The current user object
            depth: Current recursion depth
            max_depth: Max recursion allowed to avoid infinite loops

        Returns:
            Updated conversation history with assistant and tool responses
        """
        func = "process_user_request"
        logger.info(f" entered {func}\n")

        assistant_clarification_message = {
            "role": "assistant",
            "content": (
                "I'm sorry, I couldn't understand the query clearly. "
                "Could you please rephrase or provide more details about what you're looking for?"
            )
        }

        if depth > max_depth:
            logger.warning(f" in {func} 🔁 Max recursion depth reached ({max_depth})\n")
            conversation_history.append(assistant_clarification_message)
            return conversation_history

        completion = self.respond(messages=conversation_history, user_name=user.get_name())
        if not completion or not completion.choices or (completion.choices[0].message.content is None and completion.choices[0].message.tool_calls is None):
            logger.warning(f" in {func} ⚠️ LLM did not return a valid response. Asking user to clarify.")
            conversation_history.append(assistant_clarification_message)
            return conversation_history

        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls

        # No tools used, just return assistant's message
        if not tool_calls:
            assistant_message = {
                "role": "assistant",
                "content": response_message.content
            }
            conversation_history.append(assistant_message)
            logger.info(f" in {func} ✅ Final assistant message, no more tools\n")
            return conversation_history

        # Add assistant response that includes tool calls
        assistant_message = {
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        }
        conversation_history.append(assistant_message)
        logger.info(f" in {func} 🛠 Assistant triggered {len(tool_calls)} tool calls\n")

        # Process each tool call and add tool response
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments)
            except Exception as e:
                logger.error(f" in {func} ❌ Failed to parse arguments for '{function_name}': {e}")
                function_args = {}

            execution_result = router.execute_function_call(function_name, function_args)

            if execution_result is None:
                logger.error(f" in {func} ❌ Function '{function_name}' returned None")
                tool_response = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": f"Function '{function_name}' failed to execute"
                }
            elif isinstance(execution_result, dict):
                simplified = create_simplified_tool_response(execution_result)
                tool_response = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(simplified),
                    "_original_content": execution_result
                }
            else:
                tool_response = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(execution_result)
                }

            conversation_history.append(tool_response)

        # Recursively call the LLM with new context including tool responses
        return self.process_user_request(conversation_history, user, depth=depth + 1, max_depth=max_depth)


def test_llm_connections(ai_provider: str) -> str:
    """
    Runs a quick test to verify the LLM provider is working.

    Args:
        ai_provider: Name of the provider to test (e.g. openai)

    Returns:
        The name of the provider, regardless of success/failure.
    """
    func = "test_llm_connections"
    logger.info(f" entered {func} with provider {ai_provider}")

    client = LLMClient(ai_provider)
    try:
        result = client.respond([
            {"role": "system", "content": f"You are a friendly assistant from {ai_provider}."},
            {"role": "user", "content": "Say hi and tell me your provider identity."}
        ])
        if result and result.choices:
            content = result.choices[0].message.content
            logger.info(f"✅ in {func} Connection to {ai_provider} succeeded with: {content}\n")
        else:
            logger.warning(f"⚠️ in {func} API returned no response\n")
    except Exception as e:
        logger.warning(f"❌ in {func} Unexpected error: {e}\n")

    return ai_provider
