import prompts

from visualization.types import PaletteTypeLiteral

CATEGORY_SCHEMA = {
    "type": "array",
    "description": " MANDATORY PARAMETER: A list of category labels for the X-axis. If representing dates or time periods, format them as 'Jan'24' for months, 'Q1,23' for quarters, and '2023' for years. Example: ['Jan'24', 'Feb'24', 'Mar'24']",
    "items": {
        "type": "string",
        "minLength": 1,
        "examples": [
            ["Jan'24", "Feb'24", "Mar'24"],
            ["Q1-23", "Q2-23", "Q3-23"],
            ["2023", "2024"] ]
    }
}

PALETTE_TYPE_SCHEMA = {
    "type": "string",
    "enum": PaletteTypeLiteral,
    "description": (
        "Color palette type. MANDATORY - must be exactly one of these three values:\n"
        f"  • {PaletteTypeLiteral[0]}: Assigns distinct hues to each category.\n"
        f"  • {PaletteTypeLiteral[1]}: Applies a single-hue gradient (light to dark) according to value magnitude.\n"
        f"  • {PaletteTypeLiteral[2]}: Uses two contrasting hues diverging from a neutral midpoint, ideal when values center around a critical threshold.")
}

TITLE_SCHEMA = {
                    "type": "string",
                    "description": "The title of the chart or graph. MANDATORY - cannot be empty. Should succinctly describe the overall dataset (e.g., 'Quarterly Sales by Region').",
}

X_LABEL_SCHEMA = {
                    "type": "string",
                    "description": "The label for the X-axis. MANDATORY - cannot be empty. Indicates what the horizontal values (or categories) represent (e.g., 'Product Categories', 'Months').",
}

Y_LABEL_SCHEMA = {
                    "type": "string",
                    "description": "The label for the Y-axis that describes what the vertical values represent. MANDATORY - cannot be empty. Indicates the measurement unit or metric (e.g., 'Revenue ($)', 'Units Sold', sales, etc.).",
                }

FILL_ALPHA_SCHEMA =  {
    "type": "number",
    "description": "The transparency level for the filled area.py of the radar chart, ranging from 0.0 (completely transparent) to 1.0 (completely opaque). Typical values are between 0.2 and 0.6 for good visibility."
}

LINE_WIDTH_SCHEMA = {
    "type": "integer",
    "description": "The width of the radar chart outlines in pixels. Higher values create thicker lines. Typical values range from 1 to 4, with 2 being most common for multiple overlapping charts."
}

VALUE_TYPE_SCHEMA = {
    "type": "string",
    "description": " data format for the values. Will be either the currency symbol like $ or ₱, or % if the value is a percent or None is case it is a Unit.",
    "enum": ["₱", "$", "%", None]
}

# Google BigQuery function definition
googlebigquery = {
    "type": "function",
    "function": {
        "name": "execute_sql_query",
        "description": "Executes a SQL query on Google BigQuery and provides an explanation of what the query does" + prompts.get_prompt(),
        "strict": True,
        "parameters": {
            "type": "object",
            "required": [
                "sql_query",
                "explanation"
            ],
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQL query to be executed on Google BigQuery"
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation of what the SQL query is intended to do"
                }
            },
            "additionalProperties": False
        }
    }
}

get_group_results = {
    "type": "function",
    "function": {
        "name": "execute_sql_query",
        "description": "Executes a SQL query on Google BigQuery and provides an explanation of what the query does" + prompts.get_prompt(),
        "strict": True,
        "parameters": {
            "type": "object",
            "required": [
                "sql_query",
                "explanation"
            ],
            "properties": {
                "sql_query": {
                    "type": "string",
                    "description": "The SQL query to be executed on Google BigQuery"
                },
                "explanation": {
                    "type": "string",
                    "description": "A short explanation of what the SQL query is intended to do"
                }
            },
            "additionalProperties": False
        }
    }
}


# Bar Chart function definition
bar_chart = {
    "type": "function",
    "function": {
        "name": "create_bar_chart",
        "description": "Generates a professionally styled bar chart from provided categorical data and returns it as a base64-encoded image string. "
                       "CRITICAL: You MUST always provide both 'categories' and 'values' parameters with actual data - the function will fail without them. The chart supports customizable title, axis labels, and color palette selection. All numeric values must be non-negative and finite."
                       "IMPORTANT: If the X-axis categories represent time periods such as months, quarters, or years, they MUST be pre-formatted by the model as follows — months: 'Jan'24', 'Feb'24'; quarters: 'Q1,23', 'Q2,23'; years: '2023', '2024'. The function expects already formatted labels. Do NOT send raw formats like '2024-01' or 'Q1-2024'.",
        "parameters": {
            "type": "object",
            "required": ["categories", "values", "title", "x_label", "y_label", "palette_type", "value_type"],
            "additionalProperties": False,
            "strict": True,
            "properties": {
                "categories": CATEGORY_SCHEMA,
                "values": {
                    "type": "array",
                    "description": "MANDATORY PARAMETER: A list of numeric values corresponding to each category (Y-axis values). REQUIRED FORMAT - All items must be numeric (float/int). Must have the same length as categories list. Example: [150000, 200000] or [10.5, 25.3, 18.7, 32.1, 22.9]. YOU CANNOT SKIP THIS PARAMETER.",
                    "items": {
                        "type": "number",
                        "minimum": 0
                    },
                    "minItems": 1,
                    "examples": [
                        [150000, 200000],
                        [100, 150, 120, 180],
                        [45.7, 62.3, 38.9]
                    ]
                },
                "title": TITLE_SCHEMA,
                "x_label": X_LABEL_SCHEMA,
                "y_label": Y_LABEL_SCHEMA,
                "palette_type": PALETTE_TYPE_SCHEMA,
                "value_type": VALUE_TYPE_SCHEMA
            }
        }
    }
}

# Pie Chart function definition
pie_chart = {
    "type": "function",
    "function": {
        "name": "create_pie_chart",
        "description": "Creates a styled pie chart visualization from dictionary data and returns it as base64 encoded image for display. This function generates a professional circular chart showing proportional data with optional slice explosion and customizable styling.",

        "parameters": {
            "type": "object",
            "required": ["data_dict", "title", "explode_largest", "palette_type"],
            "properties": {
                "data_dict": {
                    "type": "array",
                    "description": "A list of data points for the pie chart. Example: [{'label': 'Marketing', 'value': 30.5}, {'label': 'Sales', 'value': 25.3}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "The label for the pie slice."
                            },
                            "value": {
                                "type": "number",
                                "description": "The value for the pie slice.",
                                "minimum": 0
                            }
                        },
                        "required": ["label", "value"]
                    }
                },
                "title": TITLE_SCHEMA,
                "explode_largest": {
                    "type": "boolean",
                    "description": "Whether to explode (separate) the largest slice from the pie for emphasis. Set to true to highlight the largest segment, false to keep all slices connected."
                },
                "palette_type": PALETTE_TYPE_SCHEMA,
            },
            "additionalProperties": False,
            "strict": True
        }
    }
}

# Single Line Graph function definition
single_line_graph = {
    "type": "function",
    "function": {
        "name": "create_single_line_graph",
        "description": "Generates a professionally styled line graph visualization from dictionary data and returns it as base64 encoded image for display. This function generates a line chart showing the relationship between X and Y values over a continuous range. IMPORTANT: If the X-axis categories represent time periods such as months, quarters, or years, they MUST be pre-formatted by the model as follows — months: 'Jan'24', 'Feb'24'; quarters: 'Q1-23', 'Q2-23'; years: '2023', '2024'. The function expects already formatted labels. Do NOT send raw formats like '2024-01' or 'Q1-2024'.",
        "parameters": {
            "type": "object",
            "required": ["data_dict", "title", "x_label", "y_label", "palette_type", "value_type"],
            "properties": {
                "data_dict": {
                    "type": "array",
                    "description": "A list of data points for the line graph. Example: [{'x': 1, 'y': 10}, {'x': 2, 'y': 15}] or [{'x': 'Jan', 'y': 100}, {'x': 'Feb', 'y': 120}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {
                                "description": "A list of category labels for the X-axis. If representing dates or time periods, format them as 'Jan'24' for months, 'Q1,23' for quarters, and '2023' for years. Example: ['Jan'24', 'Feb'24', 'Mar'24']"
                            },
                            "y": {
                                "type": "number",
                                "description": "The y-axis value."
                            }
                        },
                        "required": ["x", "y"]
                    }
                },
                "title": TITLE_SCHEMA,
                "x_label": X_LABEL_SCHEMA,
                "y_label": Y_LABEL_SCHEMA,
                "palette_type": PALETTE_TYPE_SCHEMA,
                "value_type": VALUE_TYPE_SCHEMA
            },
            "additionalProperties": False,
            "strict": True
        }
    }
}

multiple_line_graph = {
    "type": "function",
    "function": {
        "name": "create_multiple_line_graph",
        "description": "Creates a styled multiple line graph visualization from dictionary data and returns it as a base64 encoded image for display. Useful for comparing trends across different categories or time periods.",
        "parameters": {
            "type": "object",
            "required": ["data_dict", "title", "x_label", "y_label", "palette_type","value_type"],
            "properties": {
                "data_dict": {
                    "type": "array",
                    "description": "List of line series. Each contains a name and an array of {x, y} data points.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Series label used in the legend."
                            },
                            "data": {
                                "type": "array",
                                "description": "Data points for this line series.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "x": {
                                            "description": "The x-axis value (number, string, or date)."
                                        },
                                        "y": {
                                            "type": "number",
                                            "description": "The y-axis value."
                                        }
                                    },
                                    "required": ["x", "y"]
                                }
                            }
                        },
                        "required": ["name", "data"]
                    }
                },
                "title": TITLE_SCHEMA,
                "x_label": X_LABEL_SCHEMA,
                "y_label": Y_LABEL_SCHEMA,
                "palette_type": PALETTE_TYPE_SCHEMA,
                "value_type": VALUE_TYPE_SCHEMA
            },
            "additionalProperties": False
        }
    }
}

# Single Area Chart function definition
single_area_chart = {
    "type": "function",
    "function": {
        "name": "create_single_area_chart",
        "description": "Creates a styled single area.py chart visualization from dictionary data and returns it as base64 encoded image for display. This function generates an area.py chart that fills the space under a line, ideal for showing cumulative data or emphasizing volume over time.",
        "parameters": {
            "type": "object",
            "required": ["data_dict", "title", "x_label", "y_label", "palette_type","value_type"],
            "properties": {
                "data_dict": {
                    "type": "array",
                    "description": "A list of data points for the area.py chart. The area.py under the line will be filled. Example: [{'x': 1, 'y': 10}, {'x': 2, 'y': 15}, {'x': 3, 'y': 12}]. IMPORTANT: x and y both must be numeric",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number", "description": "The x-axis value."},
                            "y": {"type": "number", "description": "The y-axis value."}
                        },
                        "required": ["x", "y"]
                    }
                },
                "title": TITLE_SCHEMA,
                "x_label": X_LABEL_SCHEMA,
                "y_label": Y_LABEL_SCHEMA,
                "palette_type": PALETTE_TYPE_SCHEMA,
                "value_type": VALUE_TYPE_SCHEMA
            },
            "additionalProperties": False,
            "strict": True
        }
    }
}

# Stacked Area Chart function definition
stacked_area_chart = {
    "type": "function",
    "function": {
        "name": "create_stacked_area_chart",
        "description": "Creates a styled stacked area.py chart visualization from dictionary data and returns it as base64 encoded image for display. This function generates multiple area.py series stacked on top of each other, perfect for showing how different components contribute to a total over time.",

        "parameters": {
            "type": "object",
            "required": ["data_dict", "title", "x_label", "y_label", "palette_type","value_type"],
            "properties": {
                "data_dict": {
                    "type": "array",
                    "description": "A list of data series for the stacked area.py chart. All series should have the same x-values. Example: [{'name': 'Product A', 'points': [{'x': 1, 'y': 10}, {'x': 2, 'y': 15}]}, {'name': 'Product B', 'points': [{'x': 1, 'y': 8}, {'x': 2, 'y': 12}]}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "The name of the data series."},
                            "points": {
                                "type": "array",
                                "description": "The data points for this series.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "x": {"type": "number", "description": "The x-axis value."},
                                        "y": {"type": "number", "description": "The y-axis value."}
                                    },
                                    "required": ["x", "y"]
                                }
                            }
                        },
                        "required": ["name", "points"]
                    }
                },
                "title": TITLE_SCHEMA,
                "x_label": X_LABEL_SCHEMA,
                "y_label": Y_LABEL_SCHEMA,
                "palette_type": PALETTE_TYPE_SCHEMA,
                "value_type": VALUE_TYPE_SCHEMA
            },
            "additionalProperties": False,
            "strict": True
        }
    }
}

resolve_name = {
    "type": "function",
    "function": {
        "name": "resolve_name",
        "description": "Resolves a fuzzy user-entered string into a known value from the database for a specific column.",
        "parameters": {
            "type": "object",
            "required": ["user_input","column", "table"],
            "properties": {
                "user_input": {
                    "type": "string",
                    "description":  "The fuzzy or partial user input to match"
                },
                "column": {
                    "type": "string",
                    "description":  "The column in which it will be found"
                },
                "table": {
                  "type": "string",
                  "description": "The table where to search the column"
                }
            }
        }
    }
}
