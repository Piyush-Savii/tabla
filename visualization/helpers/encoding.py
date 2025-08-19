import base64

#def encode_image_to_base64(image_bytes: bytes) -> Optional[str]:
#    if not image_bytes:
#        return None
#    base64_string = base64.b64encode(image_bytes).decode("utf-8")
#    return f"data:image/png;base64,{base64_string}"


def encode_image_to_base64(image_bytes: bytes) -> str|None:
    """
    Encode image bytes to base64 string for OpenAI API compatibility.

    Args:
        image_bytes: The raw image bytes from visualization functions

    Returns:
        Base64 encoded string in the format required by OpenAI: 'data:image/png;base64,{base64_string}'
    """
    if not image_bytes:
        return None

    base64_string = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:image/png;base64,{base64_string}"

