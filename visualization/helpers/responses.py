from typing import Dict, Any

def create_success_response(data: Dict[str, Any], message: str) -> Dict[str, Any]:
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def create_error_response(message: str, error: str = "") -> Dict[str, Any]:
    return {
        "status": "error",
        "message": message,
        "error": error
    }
