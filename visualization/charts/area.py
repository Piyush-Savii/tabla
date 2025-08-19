import matplotlib.pyplot
import seaborn
import io
from typing import List, Dict, Union, Optional

from matplotlib.ticker import FuncFormatter

from visualization.charts.validations import format_value
from visualization.types import PaletteTypeLiteral, CATEGORICAL, SEQUENTIAL, DIVERGING

def _get_area_chart_colors(data_type: PaletteTypeLiteral, num_colors: int) -> list:
    """
    Get appropriate colors for area chart based on data type.

    Args:
        data_type (str): Type of data - CATEGORICAL, SEQUENTIAL, or DIVERGING
        num_colors (int): Number of colors needed

    Returns:
        list: List of color values appropriate for area charts
    """
    data_type_upper = data_type.upper()

    if data_type_upper == CATEGORICAL:
        # Use distinct colors for categorical data
        return seaborn.color_palette("Dark2", num_colors)

    elif data_type_upper == SEQUENTIAL:
        # Use seaborn's plasma palette for sequential data
        return seaborn.color_palette("plasma", num_colors)

    elif data_type_upper == DIVERGING:
        # Use seaborn's RdYlGn palette for diverging data
        return seaborn.color_palette("RdYlGn", num_colors)

    else:
        # Default to categorical
        return seaborn.color_palette("Dark2", num_colors)


# Type Aliases for plot_area_chart
AreaChartDataPoint = Dict[str, Union[int, float]]
SingleAreaDataList = List[AreaChartDataPoint]


def plot_area_chart(data_dict: SingleAreaDataList, title: str, x_label: str, y_label: str,
                    palette_type: PaletteTypeLiteral,value_type:str) -> Optional[bytes]:

    # --- Enhanced Input Validation ---
    if not isinstance(data_dict, list):
        print("Error: data_dict must be a list.")
        return None
    if not data_dict:
        print("Error: data_dict cannot be empty.")
        return None

    for i, point in enumerate(data_dict):
        if not isinstance(point, dict):
            print(f"Error: data_dict items must be dictionaries. Found item at index {i}: {type(point)}")
            return None
        if 'x' not in point or 'y' not in point:
            print(f"Error: data_dict items must have 'x' and 'y' keys. Found at index {i}: {point}")
            return None
        if not isinstance(point['x'], (int, float)):
            print(f"Error: 'x' values must be numeric. Found at index {i}: {point['x']} of type {type(point['x'])}")
            return None
        if not isinstance(point['y'], (int, float)):
            print(f"Error: 'y' values must be numeric. Found at index {i}: {point['y']} of type {type(point['y'])}")
            return None

    if not isinstance(title, str) or not title:
        print("Error: title must be a non-empty string.")
        return None
    if not isinstance(x_label, str) or not x_label:
        print("Error: x_label must be a non-empty string.")
        return None
    if not isinstance(y_label, str) or not y_label:
        print("Error: y_label must be a non-empty string.")
        return None

    allowed_palettes = [CATEGORICAL, SEQUENTIAL, DIVERGING]
    if not isinstance(palette_type, str) or not palette_type:
        print("Error: palette_type must be a non-empty string.")
        return None
    if palette_type.upper() not in allowed_palettes:
        print(f"Error: palette_type must be one of {allowed_palettes}. Got: {palette_type}")
        return None
    # --- End of Enhanced Input Validation ---

    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)

    try:
        # Single area chart: extract x and y values from list of points
        colors = _get_area_chart_colors(palette_type, 1)

        # Sort points by x-value and extract coordinates
        sorted_points = sorted(data_dict, key=lambda p: p['x'])
        x_vals = [point['x'] for point in sorted_points]
        y_vals = [point['y'] for point in sorted_points]

        ax.fill_between(x_vals, y_vals, color=colors[0], alpha=0.7)
        ax.plot(x_vals, y_vals, color=colors[0], linewidth=2)

        # Add grid
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_value(x,value_type)))

        for i in ax.patches:
            ax.annotate(format_value(i.get_height(),value_type), (i.get_x() + i.get_width() / 2., i.get_height()),
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points')

        # Set title and labels
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_value(x,value_type)))
        ax.set_title(title, pad=20)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    except Exception as e:
        print(f"Error creating area chart: {e}")
        matplotlib.pyplot.close(fig)
        return None

    fig.tight_layout()

    # Save plot to a BytesIO object
    img_bytes = io.BytesIO()
    try:
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        matplotlib.pyplot.close(fig)
        return img_bytes.getvalue()
    except Exception as e:
        print(f"Error saving figure to bytes: {e}")
        matplotlib.pyplot.close(fig)
        return None

StackedAreaDataPoint = Dict[str, Union[int, float]]
StackedAreaSeries = Dict[str, Union[str, List[StackedAreaDataPoint]]]
StackedAreaDataList = List[StackedAreaSeries]

def plot_stacked_area_chart(data_dict: StackedAreaDataList, title: str, x_label: str, y_label: str,
                            palette_type: PaletteTypeLiteral, value_type:str) -> Optional[bytes]:
    # --- Enhanced Input Validation ---
    if not isinstance(data_dict, list):
        print("Error: data_dict must be a list.")
        return None
    if not data_dict:
        print("Error: data_dict cannot be empty.")
        return None

    for i, series in enumerate(data_dict):
        if not isinstance(series, dict):
            print(f"Error: data_dict items must be dictionaries. Found item at index {i}: {type(series)}")
            return None
        if 'name' not in series or 'points' not in series:
            print(f"Error: Series objects must have 'name' and 'points' keys. Found at index {i}: {series}")
            return None
        if not isinstance(series['name'], str) or not series['name']:
            print(f"Error: Series 'name' must be a non-empty string. Found at index {i}: {series['name']}")
            return None
        if not isinstance(series['points'], list):
            print(f"Error: Series 'points' must be a list. Found at index {i}: {type(series['points'])}")
            return None
        if not series['points']:
            print(f"Error: Series 'points' cannot be empty for series '{series['name']}'.")
            return None

        # Validate each point in the series
        for j, point in enumerate(series['points']):
            if not isinstance(point, dict):
                print(
                    f"Error: Points must be dictionaries. Found in series '{series['name']}' at point index {j}: {type(point)}")
                return None
            if 'x' not in point or 'y' not in point:
                print(
                    f"Error: Points must have 'x' and 'y' keys. Found in series '{series['name']}' at point index {j}: {point}")
                return None
            if not isinstance(point['x'], (int, float)):
                print(
                    f"Error: Point 'x' values must be numeric. Found in series '{series['name']}' at point index {j}: {point['x']} of type {type(point['x'])}")
                return None
            if not isinstance(point['y'], (int, float)):
                print(
                    f"Error: Point 'y' values must be numeric. Found in series '{series['name']}' at point index {j}: {point['y']} of type {type(point['y'])}")
                return None

    if not isinstance(title, str) or not title:
        print("Error: title must be a non-empty string.")
        return None
    if not isinstance(x_label, str) or not x_label:
        print("Error: x_label must be a non-empty string.")
        return None
    if not isinstance(y_label, str) or not y_label:
        print("Error: y_label must be a non-empty string.")
        return None

    allowed_palettes = [CATEGORICAL, SEQUENTIAL, DIVERGING]
    if not isinstance(palette_type, str) or not palette_type:
        print("Error: palette_type must be a non-empty string.")
        return None
    if palette_type.upper() not in allowed_palettes:
        print(f"Error: palette_type must be one of {allowed_palettes}. Got: {palette_type}")
        return None
    # --- End of Enhanced Input Validation ---

    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)

    try:
        # Stacked area.py chart: each item is a series with name and points
        required_colors = len(data_dict)
        colors = _get_area_chart_colors(palette_type, required_colors)

        # Get all unique x values and sort them
        all_x = set()
        for series in data_dict:
            for point in series['points']:
                all_x.add(point['x'])
        x_labels = sorted(all_x)  # e.g., ['Jan', 'Feb', 'Mar']
        x_vals = list(range(len(x_labels)))

        # Create matrix of y values for stacking
        y_matrix = []
        labels = []
        for series in data_dict:
            # Create a dictionary for quick lookup of y values by x
            point_dict = {point['x']: point['y'] for point in series['points']}
            y_vals = [point_dict.get(x, 0) for x in x_vals]
            y_matrix.append(y_vals)
            labels.append(series['name'])

        # Create stacked area.py plot
        x_vals = sorted(all_x)

        ax.stackplot(x_vals,  # type: ignore
                     *y_matrix,
                     labels=labels,
                     colors=colors,
                     alpha=0.7
                     )
        ax.legend(loc='upper left')

        # Add grid
        ax.grid(True, alpha=0.3)

        # Set title and labels
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_value(x,value_type)))

        ax.set_title(title,pad=20)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    except Exception as e:
        print(f"Error creating stacked area.py chart: {e}")
        matplotlib.pyplot.close(fig)
        return None

    fig.tight_layout()

    # Save plot to a BytesIO object
    img_bytes = io.BytesIO()
    try:
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        matplotlib.pyplot.close(fig)
        return img_bytes.getvalue()
    except Exception as e:
        print(f"Error saving figure to bytes: {e}")
        matplotlib.pyplot.close(fig)
        return None


