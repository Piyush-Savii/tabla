from datetime import datetime
from typing import List


def format_value(value, style="currency", currency_symbol="₱", compact=True, decimals=1):
    try:
        if style == "currency":
            if compact:
                if abs(value) >= 1_000_000_000:
                    return f"{currency_symbol}{value / 1_000_000_000:.{decimals}f}B"
                elif abs(value) >= 1_000_000:
                    return f"{currency_symbol}{value / 1_000_000:.{decimals}f}M"
                elif abs(value) >= 1_000:
                    return f"{currency_symbol}{value / 1_000:.{decimals}f}K"
            return f"{currency_symbol}{value:,.{decimals}f}"

        elif style == "percentage":
            return f"{value:.{decimals}f}%"

        elif style == "count":
            if compact:
                if abs(value) >= 1_000_000:
                    return f"{value / 1_000_000:.{decimals}f}M"
                elif abs(value) >= 1_000:
                    return f"{value / 1_000:.{decimals}f}K"
            return f"{int(value)}"

        else:
            return str(value)
    except Exception as e:
        return str(e)

def format_x_labels(categories: List[str], time_format: str) -> List[str]:
    if time_format == "month":
        return [
            datetime.strptime(cat, "%Y-%m").strftime("%b'%y")  # e.g., "2024-01" → "Jan'24"
            for cat in categories
        ]
    elif time_format == "quarter":
        return [cat.replace("Q", "Q").replace("-", ",") for cat in categories]  # e.g., "Q1-2023" → "Q1,23"
    elif time_format == "year":
        return categories  # Assume plain years already
    else:
        return categories

