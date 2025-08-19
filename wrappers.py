"""
Visualization Wrapper Functions for OpenAI Function Calling

This module provides wrapper functions for all visualization tools that handle
base64 encoding of images for proper OpenAI API integration.
"""

from typing import Dict, Any, Union, Literal, List
from messages import create_success_response, create_error_response
from visualization.charts.area import plot_area_chart, plot_stacked_area_chart
from visualization.charts.bar import bar_chart_plot
from visualization.charts.line import plot_single_line, plot_multiple_lines
from visualization.charts.pie import pie_chart_plot
#from
from logger_setup import logger
from visualization.helpers.encoding import encode_image_to_base64

# Data type constants for chart categorization

def create_bar_chart(categories: List[str],
                     values: List[float],
                     title: str,
                     x_label: str,
                     y_label: str,
                     palette_type: Literal["CATEGORICAL", "SEQUENTIAL", "DIVERGING"],
                     value_type: str
                     ) -> Dict[str, Any]:
    """
    Generates a styled bar chart and returns it as a base64-encoded image.
    """
    try:
        logger.info(f"Creating bar chart with {len(categories)} data points")

        # Call the actual bar chart function from BarChart.py
        image_bytes = bar_chart_plot(categories, values, title, x_label, y_label, palette_type, value_type)

        if image_bytes:
            base64_image = encode_image_to_base64(image_bytes)
            return create_success_response({
                "chart_type": "bar_chart",
                "title": title,
                "image": base64_image
            }, f"Bar chart '{title}' created successfully")
        else:
            return create_error_response("Failed to generate bar chart")

    except Exception as e:
        logger.error(f"Error creating bar chart: {e}")
        return create_error_response("Error creating bar chart", str(e))


def create_pie_chart(data_dict: Dict[str, float], title: str, explode_largest: bool,
                     palette_type: Literal["CATEGORICAL", "SEQUENTIAL", "DIVERGING"]) -> Dict[str, Any]:
    try:
        logger.info(f"Creating pie chart with {len(data_dict)} data points")
        image_bytes = pie_chart_plot(data_dict, title, explode_largest, palette_type)

        if not image_bytes:
            return create_error_response("Failed to generate pie chart")
        else:
            base64_image = encode_image_to_base64(image_bytes)
            return create_success_response({
                "chart_type": "pie_chart",
                "title": title,
                "image": base64_image
            }, f"Pie chart '{title}' created successfully")

    except Exception as e:
        logger.error(f"Error creating pie chart: {e}")
        return create_error_response("Error creating pie chart", str(e))


def create_single_line_graph(data_dict: List[Dict[str, Union[int, float, str]]],
                             title: str, x_label: str, y_label: str,
                             palette_type: Literal["CATEGORICAL", "SEQUENTIAL", "DIVERGING"],
                             value_type: str) -> Dict[str, Any]:
    try:
        logger.info(f"Creating single line graph with {len(data_dict)} data points")
        image_bytes = plot_single_line(data_dict, title, x_label, y_label, palette_type, value_type)
        if image_bytes:
            base64_image = encode_image_to_base64(image_bytes)
            return create_success_response({
                "chart_type": "single_line_graph",
                "title": title,
                "image": base64_image
            }, f"Single line graph '{title}' created successfully")
        else:
            return create_error_response("Failed to generate single line graph")

    except Exception as e:
        logger.error(f"Error creating single line graph: {e}")
        return create_error_response("Error creating single line graph", str(e))


def create_multiple_line_graph(
        data_dict: List[Dict[str, Union[str, List[Dict[str, Union[int, float, str]]]]]],
        title: str,
        x_label: str,
        y_label: str,
        palette_type: Literal["CATEGORICAL", "SEQUENTIAL", "DIVERGING"],
        value_type: str) -> Dict[str, Any]:
    """
    Create a multiple line graph and return it as base64 encoded image for OpenAI display.
    """
    try:
        logger.info(f"Creating multiple line graph with {len(data_dict)} lines")
        image_bytes = plot_multiple_lines(data_dict, title, x_label, y_label, palette_type, value_type)

        if image_bytes:
            base64_image = encode_image_to_base64(image_bytes)
            return create_success_response({
                "chart_type": "multiple_line_graph",
                "title": title,
                "image": base64_image
            }, f"Multiple line graph '{title}' created successfully")
        else:
            return create_error_response("Failed to generate multiple line graph")

    except Exception as e:
        logger.error(f"Error creating multiple line graph: {e}")
        return create_error_response("Error creating multiple line graph", str(e))


def create_single_area_chart(data_dict: List[Dict[str, Union[int, float]]],
                             title: str, x_label: str, y_label: str,
                             palette_type: Literal["CATEGORICAL", "SEQUENTIAL", "DIVERGING"],
                             value_type: str) -> Dict[str, Any]:
    try:
        logger.info(f"Creating single area.py chart with {len(data_dict)} data points")
        image_bytes = plot_area_chart(data_dict, title, x_label, y_label, palette_type, value_type)

        if image_bytes:
            base64_image = encode_image_to_base64(image_bytes)
            return create_success_response({
                "chart_type": "single_area_chart",
                "title": title,
                "image": base64_image
            }, f"Single area.py chart '{title}' created successfully")
        else:
            return create_error_response("Failed to generate single area.py chart")

    except Exception as e:
        logger.error(f"Error creating single area.py chart: {e}")
        return create_error_response("Error creating single area.py chart", str(e))


def create_stacked_area_chart(data_dict: List[Dict[str, Union[str, List[Dict[str, Union[int, float]]]]]],
                              title: str, x_label: str, y_label: str,
                              palette_type: Literal["CATEGORICAL", "SEQUENTIAL", "DIVERGING"],
                              value_type: str) -> Dict[str, Any]:
    try:
        logger.info(f"Creating stacked area.py chart with {len(data_dict)} series")
        image_bytes = plot_stacked_area_chart(data_dict, title, x_label, y_label, palette_type, value_type)

        if image_bytes:
            base64_image = encode_image_to_base64(image_bytes)
            return create_success_response({
                "chart_type": "stacked_area_chart",
                "title": title,
                "image": base64_image
            }, f"Stacked area.py chart '{title}' created successfully")
        else:
            return create_error_response("Failed to generate stacked area.py chart")

    except Exception as e:
        logger.error(f"Error creating stacked area.py chart: {e}")
        return create_error_response("Error creating stacked area.py chart", str(e))
