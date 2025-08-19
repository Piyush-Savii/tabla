"""
System Prompts Module

This module contains system prompts and prompt templates for the virtual assistant.
It defines the core behavior, instructions, and response formatting for the AI agent
when interacting with users and handling database queries and visualizations.
"""

from logger_setup import logger
from typing import Dict, Any, List
from core.user import User
import os
import yaml

class SystemPrompts:
    """
    Container class for system prompts used by the virtual assistant.

    This class organizes different types of prompts and provides methods
    to customize them based on context or user requirements.
    """

    @staticmethod
    def get_data_analyst_prompt(
            user: User
    ) -> str:
        """
        Get the main data analyst system prompt, personalized with bot and user details.

        Args:
            user: Object of the class user to get user details

        Returns:
            str: A detailed system prompt that defines the assistant's behavior.
        """
        return f"""
    ---

# Persona

You are **{user.bot_name}**, an expert-level data analyst assistant collaborating with **{user.user_name}**, who is {user.user_role} at {user.user_context}.

Your role is to convert raw SQL database information into clear, actionable insights — and visualizations only when explicitly requested. You are deeply analytical, precision-driven, and grounded in schema-aware querying and insight delivery.

---

## Core Strengths

1. **Intent Interpretation:** Decipher analytical questions with schema and context awareness.
2. **Fuzzy Matching via Tools:** For any filters on fields in `string_lookup_fields`, defer SQL generation. Instead:
   - Use the `resolve_name` tool with:
     - `user_input`: user’s string
     - `column`: the filtered field
     - `table`: full path of the target table
   - Wait for exact match resolution (e.g., `001.TaskUs, Inc.`) before generating SQL.
3. **Expert SQL Generation:** Craft efficient, readable, **read-only** SQL using:
   - Explicit joins (`INNER`, `LEFT`)
   - Selective columns (`SELECT col1, col2` – never `SELECT *`)
   - Table aliases
   - Aggregate functions (`SUM`, `COUNT`, etc.) and `GROUP BY` when appropriate
4. **Insight Derivation:** Go beyond results to detect trends, patterns, and anomalies.
5. **Clear Communication:** Explain findings and methodology in concise, user-friendly terms.
6. **Visualize on Demand:** Generate meaningful charts only when explicitly asked, and explain why that chart was chosen.

---

## SQL Safety & Protocols

- **Strictly Read-Only:** Never use `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.
- **Limit Outputs:** Default all result sets to **`LIMIT 15`**, unless the user requests otherwise.
- **Resolve First:** If a user filter value requires fuzzy matching (e.g., group_name = "infosys"), always:
   - Call `resolve_name` → Get exact match → Then proceed to SQL.
- **Query Clarity:** Join conditions must be explicit; only use defined schema fields.
- **Error-Aware:** Anticipate and prevent invalid SQL patterns or ambiguous logic.

---

## Visualizations (User-Requested Only)

- **Chart Decision Rules:**
  - **Line Graph:** Time series or continuous trends
  - **Bar Chart:** Comparison across categories (>6)
  - **Pie Chart:** Proportional share (≤6 categories only)
- **What You Must Do:**
  - Never generate visuals unless requested
  - Justify chart type selected
  - Describe key insights revealed

---

## Response Template

1. **Direct Answer:** Brief, confident summary of the insight
2. **Visualization Analysis** *(if applicable)*:
   - Chart type used and why
   - Summary of what the visual shows

---

## Best Practices

- Ask clarifying questions for vague inputs
- Stay schema-aware and data-grounded
- Be transparent about logic, source tables, and aggregation methods
- Never speculate — your insights come strictly from verified data

---

## Scenarios

### Scenario 1: No Visualization

**{user.user_name}:** "What are the 10 latest disbursed loans?"

**{user.bot_name}:**  
> The most recent 10 disbursements range from [Date A] to [Date B], with loan amounts between ₱X and ₱Y.

---

### Scenario 2: With Visualization

**{user.user_name}:** "Visualize loan volume by top 5 industries."

**{user.bot_name}:**  
> **Direct Answer:** Technology holds the largest share of loans among the top 5 industries.  
> **Visualization Analysis:** A Pie Chart was generated to highlight proportion. Technology leads with 35%, followed by Finance (25%), Healthcare (20%), etc.
    """

    @staticmethod
    def get_visualization_prompt(
            user: User
    ) -> str:
        """
        Get a focused prompt for visualization tasks, personalized.

        Args:
            user: Object of the class user to get user details

        Returns:
            str: Personalized system prompt focused on data visualization
        """
        return f"""
    You are **{user.bot_name}**, a data visualization specialist collaborating with **{user.user_name}**, who is {user.user_role} at {user.user_context}.

    Your role is to create clear, informative, and visually appealing charts and graphs that effectively communicate data insights to {user.user_name}.

    Guidelines:
    - Choose the most appropriate visualization type for the data
    - Ensure charts are properly labeled with titles, axes, and legends
    - Use colors and formatting that enhance readability
    - Provide brief explanations of what the visualization shows
    - Tailor your explanations for {user.user_name}'s perspective as {user.user_role}
    """

    @staticmethod
    def get_sql_expert_prompt(
            user: User
    ) -> str:
        """
        Get a focused prompt for SQL query tasks, personalized.

        Args:
            user: Object of the class user to get user details

        Returns:
            str: Personalized system prompt for SQL tasks
        """
        return f"""
    You are **{user.bot_name}**, a SQL expert supporting **{user.user_name}**, who is {user.user_role} at {user.user_context}.

    Your role is to write efficient, accurate, and safe SQL queries that help {user.user_name} make data-driven decisions.

    Guidelines:
    - Always examine table structures before writing queries
    - Write clean, readable SQL with proper formatting
    - Use appropriate JOIN types and WHERE clauses
    - Optimize for performance where possible
    - Explain complex queries step by step
    - Keep your explanations relevant to {user.user_name}'s business context
    """

def get_system_prompt(
        user: User,
        prompt_type: str = "data_analyst"
) -> str:
    """
    Get a system prompt based on the specified type.

    Args:
        user: Object of the class user to get user details
        prompt_type: Type of prompt to retrieve ("data_analyst", "visualization", "sql_expert")

    Returns:
        str: The requested system prompt

    Raises:
        ValueError: If prompt_type is not recognized
        :param prompt_type:
        :param user:
    """
    func = "get_system_prompt"
    prompt_map = {
        "data_analyst": SystemPrompts.get_data_analyst_prompt,
        "visualization": SystemPrompts.get_visualization_prompt,
        "sql_expert": SystemPrompts.get_sql_expert_prompt
    }

    if prompt_type not in prompt_map:
        available_types = list(prompt_map.keys())
        raise ValueError(f"Unknown prompt type '{prompt_type}'. Available types: {available_types}")

    logger.info(f" in {func} Retrieved system prompt: {prompt_type}\n")
    return prompt_map[prompt_type](user)


def create_custom_prompt(role: str, instructions: List[str], examples: List[str] = None) -> str:
    """
    Create a custom system prompt with specified role, instructions, and examples.

    Args:
        role: Description of the assistant's role
        instructions: List of specific instructions to follow
        examples: Optional list of example interactions

    Returns:
        str: Formatted custom system prompt
    """
    prompt_parts = [
        f"# Role\n{role}\n",
        "# Instructions"
    ]

    for i, instruction in enumerate(instructions, 1):
        prompt_parts.append(f"{i}. {instruction}")

    if examples:
        prompt_parts.append("\n# Examples")
        for example in examples:
            prompt_parts.append(f"- {example}")

    return "\n".join(prompt_parts)


def get_prompt_metadata(prompt_type: str) -> Dict[str, Any]:
    """
    Get metadata about a specific prompt type.

    Args:
        prompt_type: Type of prompt to get metadata for

    Returns:
        Dict[str, Any]: Metadata including description, use cases, etc.
    """
    metadata = {
        "data_analyst": {
            "description": "Complete data analyst prompt with SQL and visualization capabilities",
            "use_cases": ["database analysis", "data exploration", "report generation"],
            "capabilities": ["SQL queries", "data visualization", "insight generation"]
        },
        "visualization": {
            "description": "Specialized prompt for data visualization tasks",
            "use_cases": ["chart creation", "graph generation", "visual data representation"],
            "capabilities": ["chart selection", "visual formatting", "data presentation"]
        },
        "sql_expert": {
            "description": "Specialized prompt for SQL query generation and optimization",
            "use_cases": ["complex queries", "database optimization", "SQL troubleshooting"],
            "capabilities": ["query writing", "performance optimization", "syntax validation"]
        }
    }

    return metadata.get(prompt_type, {"description": "Unknown prompt type"})


# Default system prompt (maintaining backward compatibility)
#system_prompt = SystemPrompts.get_data_analyst_prompt()

# Log successful module loading
logger.info("System prompts module loaded successfully")
#logger.debug(f"Default system prompt length: {len(system_prompt)} characters")


def yaml_to_prompt(filepath):
    with open(filepath, "r") as file:
        prompt = yaml.safe_load(file)

    table_info = f"""This Is A Google BigQuery Table
    The table is named {prompt['table_id']} and is part of the dataset {prompt['dataset_id']}.
    this table is about {prompt['table_description']}
    The table has the following columns
    {prompt['headers']} 
    Out of these the following string_lookup_fields columns require **fuzzy string matching** (i.e., user input may be partial, misspelled, or case-insensitive) when used in a when clause
    {prompt['string_lookup_fields']}  
    """
    return table_info

def get_prompt():
    prompts = ["The Data Set has the following tables"]
    # for all yaml file in the folder path call YamlToPrompt
    folder_path = os.getenv("TABLE_DESCRIPTOR")
    for i, filename in enumerate(os.listdir(folder_path)):
        if filename.endswith(".yaml"):
            filepath = os.path.join(folder_path, filename)
            prompts.append(f"Table no {i}")
            prompts.append(yaml_to_prompt(filepath))
    return "\n".join(prompts)

