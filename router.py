

"""
Function Router Module

This module acts as the "dispatcher" for all AI-triggered function calls.
It routes each request (like 'create_bar_chart') to the correct internal Python function,
runs it, handles errors, and returns results.
"""

from typing import Dict, Any, Optional, List, Tuple

#import visualization.charts.bar
from logger_setup import logger

import googledb
import wrappers

# ---------------------------------------------
# FUNCTION REGISTRY: Maps function names to real code implementations
# ---------------------------------------------
FUNCTION_REGISTRY = {
    # 🔍 Data query functions
    "execute_sql_query": googledb.run_query,
    # 📊 Data visualization functions
    "create_bar_chart": wrappers.create_bar_chart,
    "create_pie_chart": wrappers.create_pie_chart,
    "create_single_line_graph": wrappers.create_single_line_graph,
    "create_multiple_line_graph": wrappers.create_multiple_line_graph,
    "create_single_area_chart": wrappers.create_single_area_chart,
    "create_stacked_area_chart": wrappers.create_stacked_area_chart,
    "resolve_name":googledb.resolve_name_tool
}


logger.info(f"✅ Function registry initialized with {len(FUNCTION_REGISTRY)} functions\n")

# ---------------------------------------------
# ERROR RESPONSE BUILDER
# ---------------------------------------------

def create_error_response(message: str, details: Optional[Any] = None) -> Dict[str, Any]:
    """
    Returns a standardized error dictionary used across all functions.

    Args:
        message: What went wrong
        details: (Optional) Stack trace, error details, etc.

    Returns:
        A dictionary in this structure:
        {
            "type": "error",
            "data": {
                "message": "...",
                "details": "..." (optional)
            }
        }
    """
    func = "create_error_response"
    response = {
        "type": "error",
        "data": {"message": message}
    }

    if details:
        response["data"]["details"] = details

    logger.debug(f" in {func} 🚨 Error response created: {message}\n")
    return response

# ---------------------------------------------
# MAIN EXECUTION DISPATCHER
# ---------------------------------------------

def execute_function_call(function_name: str, function_arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Executes a function based on name and arguments. This is the main dispatcher.

    Args:
        function_name: Name from the AI's response (e.g., "create_bar_chart")
        function_arguments: Dictionary of arguments passed from AI

    Returns:
        The result of the function execution, or an error dict if something failed
    """

    func = "execute_function_call"
    try:
        # Check if the requested function exists in our registry
        if function_name not in FUNCTION_REGISTRY:
            error_message = f"in {func} Function '{function_name}' not found in registry\n"
            logger.warning(error_message)
            return create_error_response(error_message)

        # Get the function handler from registry
        function_handler = FUNCTION_REGISTRY[function_name]
        logger.info(f" in {func} Routing function call to: {function_name}\n")
        logger.debug(f" in {func}  Function arguments: {function_arguments}\n")

        # Execute the function with provided arguments
        execution_result = function_handler(**function_arguments)
        logger.info(f" in {func} Function '{function_name}' executed successfully\n")

        return execution_result

    except TypeError as e:
        # Handle cases where function arguments don't match the function signature
        error_message = f" in {func} Invalid arguments for function '{function_name}': {str(e)}\n"
        logger.error(error_message)
        return create_error_response(
            message=f" in {func} Invalid arguments for function '{function_name}'",
            details=str(e)
        )

    except Exception as e:
        # Handle any other errors during function execution
        error_message = f" in {func} Error executing function '{function_name}': {str(e)}\n"
        logger.error(error_message)
        return create_error_response(
            message=f" in {func} Error executing function '{function_name}'",
            details=str(e)
        )


# ---------------------------------------------
# SUPPORTING UTILITIES
# ---------------------------------------------

def get_available_functions() -> List[str]:
    """
    Lists all function names that can be used in tool calls.

    Returns:
        List of function names (strings)
    """
    return list(FUNCTION_REGISTRY.keys())


def get_function_categories() -> Dict[str, List[str]]:
    """
    Groups functions into categories for docs or UI display.

    Returns:
        Dictionary with categories like 'database' and 'visualization'
    """
    return {
        "database": [
            "execute_sql_query"
        ],
        "visualization": [
            "create_bar_chart",
            "create_pie_chart",
            "create_single_line_graph",
            "create_multiple_line_graph",
            "create_single_area_chart",
            "create_stacked_area_chart",
            "create_single_product_radar_chart",
            "create_multiple_products_radar_chart",
            "create_scatter_plot",
            "create_heatmap",
            "create_bubble_chart",
            "create_waterfall_chart",
            "create_funnel_chart"
        ]
    }


def validate_function_call(function_name: str, function_arguments: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Checks if a function call is valid before attempting execution.

    Returns:
        A tuple: (is_valid, error_message)
    """
    if function_name not in FUNCTION_REGISTRY:
        return False, f"Function '{function_name}' not found in registry"

    if not isinstance(function_arguments, dict):
        return False, f"Function arguments must be a dictionary, got {type(function_arguments)}"

    return True, ""  # Valid
