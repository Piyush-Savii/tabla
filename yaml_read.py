# yaml_read.py

import yaml
from typing import Dict, Any, List

def load_yaml(file_path="config.yaml") -> dict:
    """
    Loads the entire YAML configuration file.

    Args:
        file_path (str): Path to the YAML configuration file.

    Returns:
        dict: Parsed YAML content as a dictionary.
    """
    with open(file_path, "r") as f:
        return yaml.safe_load(f)


def get_model_config(model_name: str, file_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Fetches the configuration for a given model name, including its provider, URL, and all available models.

    Args:
        model_name (str): The model to search for.
        file_path (str): YAML file containing model/provider configuration.

    Returns:
        dict: Configuration dictionary for the model.

    Raises:
        ValueError: If the model is not found in any provider.
    """
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)

    for provider_name, details in config.get("llms", {}).items():
        if model_name in details.get("models", []):
            return {
                "model": model_name,
                "provider": details.get("provider", provider_name),
                "url": details.get("url"),
                "all_models": sum(
                    [v.get("models", []) for v in config.get("llms", {}).values()],
                    []
                )
            }

    raise ValueError(f"Model '{model_name}' not found in config '{file_path}'.")


def get_provider_config(provider: str, file_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Retrieves the configuration for a specific provider (e.g., openai, google).

    Args:
        provider (str): The provider name.
        file_path (str): YAML configuration file path.

    Returns:
        dict: Provider config including default model, API key, and URL.

    Raises:
        ValueError: If the provider is not found in the config.
    """
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)

    for name, details in config.get("llms", {}).items():
        if details.get("provider") == provider:
            return {
                "model": details.get("default_model"),
                "api_key": details.get("LLM_API_KEY"),
                "url": details.get("url"),
                "all_models": details.get("models", [])
            }

    raise ValueError(f"Provider '{provider}' not found in config '{file_path}'.")


def load_llm_providers(file_path: str = "config.yaml", include_missing: bool = False) -> List[Dict]:
    """
    Loads all available LLM provider configurations from the YAML config.

    Args:
        file_path (str): Path to the config YAML file.
        include_missing (bool): If True, includes providers with 'LLM_API_KEY' as 'missing'.

    Returns:
        List[Dict]: A list of dictionaries, each containing:
            - provider (str)
            - url (str)
            - api_key (str)
            - default_model (str)
            - models (List[str])
    """
    with open(file_path, "r") as f:
        config = yaml.safe_load(f)

    providers = []
    for name, details in config.get("llms", {}).items():
        api_key = details.get("LLM_API_KEY")

        # Skip providers without a valid API key if include_missing is False
        if not include_missing and (not api_key or api_key.lower() == "missing"):
            continue

        providers.append({
            "provider": details.get("provider", name),
            "url": details.get("url"),
            "api_key": api_key,
            "default_model": details.get("default_model"),
            "models": details.get("models", [])
        })

    return providers
