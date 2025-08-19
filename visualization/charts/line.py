import matplotlib.pyplot
import seaborn
import pandas
import io
from typing import List, Dict, Union
from matplotlib.ticker import FuncFormatter

from logger_setup import logger
from visualization.charts.validations import validate_data_type, format_value
from visualization.helpers.colors import get_palette_colors
from visualization.types import PaletteTypeLiteral

def plot_single_line(data_dict: List[Dict[str, Union[int, float, str]]],
                     title: str,
                     x_label: str,
                     y_label: str,
                     palette_type: PaletteTypeLiteral,
                     value_type : str = None) -> bytes:

    func = "plot_single_line"
    logger.info(f"in {func} starting validations")
    validate_data_type(name="data_dict", value=data_dict, expected_type=list)
    validate_data_type(name="data_dict_sub", value=data_dict[0], expected_type=Dict)
    validate_data_type(name="title", value=title, expected_type=str)
    validate_data_type(name="x_label", value=x_label, expected_type=str)
    validate_data_type(name="y_label", value=y_label, expected_type=str)
    validate_data_type(name="palette_type", value=palette_type, expected_type=str)
    validate_data_type(name="palette_type", value=palette_type, expected_type=PaletteTypeLiteral)

    fig, ax = matplotlib.pyplot.subplots()

    try:
        x_vals = [item['x'] for item in data_dict]
        y_vals = [item['y'] for item in data_dict]
        ax.plot(x_vals, y_vals, marker='o', color=get_palette_colors(palette_type, 1)[0], linewidth=2)
        for x, y in zip(x_vals, y_vals):
            ax.text(x, y, format_value(y,value_type), ha='center', va='bottom', fontsize=8)

        ax.yaxis.set_major_formatter(FuncFormatter(lambda i, _: format_value(i, value_type)))

        ax.grid(True, alpha=0.3)
        ax.set_title(title, pad=20)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

    except Exception as e:
        matplotlib.pyplot.close(fig)
        raise RuntimeError(f"in {func} Error creating single line plot: {e}")

    fig.tight_layout()

    img_bytes = io.BytesIO()
    try:
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        matplotlib.pyplot.close(fig)
        return img_bytes.getvalue()
    except Exception as e:
        matplotlib.pyplot.close(fig)
        raise RuntimeError(f"in {func} Error saving single line figure to bytes: {e}")


def plot_multiple_lines(
    data_dict: List[Dict[str, Union[str, List[Dict[str, Union[int, float, str]]]]]],
    title: str,
    x_label: str,
    y_label: str,
    palette_type: PaletteTypeLiteral,
    value_type: str = None
) -> bytes:
    """
    Normalize input and generate multiple line chart.
    """
    func = "plot_multiple_lines"
    logger.info(f"in {func} starting validations")

    # Flatten and normalize data
    records = []
    for series in data_dict:
        series_name = series["name"]
        for point in series["data"]:
            records.append({
                x_label: point["x"],
                y_label: point["y"],
                "group": series_name
            })

    df = pandas.DataFrame(records)
    df = df.sort_values(by=x_label)

    fig, ax = matplotlib.pyplot.subplots()
    palette = get_palette_colors(palette_type, df["group"].nunique())
    seaborn.lineplot(data=df, x=x_label, y=y_label, hue="group", palette=palette, ax=ax)

    ax.yaxis.set_major_formatter(FuncFormatter(lambda i, _: format_value(i, value_type)))

    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    matplotlib.pyplot.xticks(rotation=45, ha='right')
    fig.tight_layout()

    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
    img_bytes.seek(0)
    matplotlib.pyplot.close(fig)
    return img_bytes.getvalue()

