from visualization.types import PaletteTypeLiteral
from logger_setup import logger


def validate_data_type(name: str, value:any, expected_type: type) -> None:
    """
    Validates that a variable is of the correct type and, if a string, is not empty or whitespace.

    Args:
        name (str): The name of the variable (used in error messages).
        value: The actual value to validate.
        expected_type (type): The expected data type (e.g., str, int, list).

    Raises:
        TypeError: If value is not of the expected type.
        ValueError: If value is an empty or whitespace-only string.

    Returns:
        None
    """

    func = "validate_variable"
    allowed_palette_types = ["CATEGORICAL", "SEQUENTIAL", "DIVERGING"]

    logger.info(f"in {func} starting validations for {name}")
    if expected_type == PaletteTypeLiteral:
        if value not in allowed_palette_types:
            error = f"in {func}, palette_type must be exactly one of {allowed_palette_types}, got '{value}'"
            logger.info(error)
            raise TypeError(error)
        return
    elif not isinstance(value, expected_type):
        error = f"in {func}, {name} must be of type {expected_type.__name__}, got {type(value).__name__}"
        logger.info(error)
        raise TypeError(error)
    if expected_type == str and not value.strip(): #type:ignore
        error = f"in {func}, {name} cannot be empty or whitespace"
        logger.info(error)
        raise TypeError(error)

    # Validate list contents
    if name == 'categories' and  expected_type == str:
        for i, value in enumerate(value):
            if not isinstance(value, str):
                error = f"in {func}, All items in categories must be strings, found item of type {type(value)} at index {i}"
                logger.info(error)
                raise TypeError(error)
            if value.strip() == "":
                error = f"in {func}, All category names must be non-empty strings, found empty string at index {i}"
                logger.info(error)
                raise TypeError(error)
    if name == 'values' and expected_type == str:
        for i, value in enumerate(value):
            if not isinstance(value, (int, float)):
                error = f"in {func}, All items in values must be numeric (int or float), found item of type {type(value)} at index {i}"
                logger.info(error)
                raise TypeError(error)



def format_value(value, currency_symbol: str = None):
    """
    Formats a number into currency with scale suffix: K, M, B
    """
    if currency_symbol is None:
        currency_symbol = ''
    elif currency_symbol == "%":
        return f"{value * 100:.2f}%"

    if value >= 1_000_000_000:
        return f"{currency_symbol}{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{currency_symbol}{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{currency_symbol}{value / 1_000:.1f}K"
    else:
        return f"{currency_symbol}{value:.0f}"


def check_pie_label(name, value):
    func = "check_label"
    logger.info(f"in {func} starting validations for {name}")
    if 'label' not in value or 'value' not in value:
        raise ValueError("Each dictionary in data_dict must contain 'label' and 'value' keys.")
    label = value['label']
    value = value['value']
    if not isinstance(label, str):
        raise TypeError(
            f"All 'label' values in data_dict must be strings, found label of type {type(label)} for {name}")
    if not label.strip():
        raise ValueError(f"All 'label' values in data_dict must be non-empty strings for {name}")
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"All 'value' values in data_dict must be numeric (int or float), found value of type {type(value)} for label '{label}' for {name}")
    if value <= 0:
        raise ValueError(
            f"All 'value' values in data_dict must be positive for pie chart, found value {value} for label '{label}'")
