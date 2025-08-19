from logger_setup import logger
from visualization.helpers.responses import create_success_response, create_error_response
from visualization.helpers.encoding import encode_image_to_base64
from typing import Any, Callable, Dict

def generate_chart_response(chart_type: str, title: str, image_bytes: bytes) -> Dict[str, Any]:
    if image_bytes:
        base64_image = encode_image_to_base64(image_bytes)
        return create_success_response({
            "chart_type": chart_type,
            "title": title,
            "image": base64_image
        }, f"{chart_type.replace('_', ' ').title()} '{title}' created successfully")
    return create_error_response(f"Failed to generate {chart_type}")

def safe_chart_plot(plot_func: Callable[..., Any], chart_type: str, *args, **kwargs) -> Dict[str, Any]:
    try:
        logger.info(f"Creating {chart_type} chart")
        image_bytes = plot_func(*args, **kwargs)
        return generate_chart_response(chart_type, kwargs.get("title", ""), image_bytes)
    except Exception as e:
        logger.error(f"Error creating {chart_type}: {e}")
        return create_error_response(f"Error creating {chart_type}", str(e))
