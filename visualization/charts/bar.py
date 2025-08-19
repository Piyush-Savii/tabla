import matplotlib.pyplot
import seaborn
import pandas
import io
from typing import List

from matplotlib.ticker import FuncFormatter

from logger_setup import logger
from visualization.charts.validations import validate_data_type, format_value
from visualization.helpers.colors import get_palette_colors
from visualization.types import PaletteTypeLiteral

def bar_chart_plot(categories: List[str],
                   values: List[float],
                   title: str,
                   x_label: str,
                   y_label: str,
                   palette_type: PaletteTypeLiteral,
                   value_type : str = None) -> bytes:

    func = "bar_chart_plot"
    logger.info(f"in {func} starting validations")

    validate_data_type(name="categories", value=categories, expected_type=list)
    validate_data_type(name="categories_sub", value=categories[0], expected_type=str)
    validate_data_type(name="values", value=values, expected_type=list)
    validate_data_type(name="values_sub", value=values[0], expected_type=float)
    validate_data_type(name="title", value=title, expected_type=str)
    validate_data_type(name="x_label", value=x_label, expected_type=str)
    validate_data_type(name="y_label", value=y_label, expected_type=str)
    validate_data_type(name="palette_type", value=palette_type, expected_type=str)
    validate_data_type(name="palette_type", value=palette_type, expected_type=PaletteTypeLiteral)

    if len(categories) != len(values):
        error = f"in {func} categories and values lists must have the same length. Got {len(categories)} categories and {len(values)} values"
        logger.info(error)
        raise TypeError(error)

    try:
        df = pandas.DataFrame({x_label: categories, y_label: values})
        colors = get_palette_colors(palette_type, len(categories))
    except Exception as e:
        error = f"in {func} Error creating DataFrame or getting colors: {e}"
        logger.info(error)
        raise TypeError(error)

    fig, ax = matplotlib.pyplot.subplots(nrows=1, ncols=1)

    try:
        seaborn.barplot(x=x_label, y=y_label, data=df, palette=colors, hue=x_label, legend=False, dodge=False, ax=ax)
        for p in ax.patches:
            ax.annotate(format_value(p.get_height(),value_type), (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points')

        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: format_value(x,value_type)))

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        matplotlib.pyplot.xticks(rotation=45, ha='right')
        fig.tight_layout()

    except Exception as e:
        matplotlib.pyplot.close(fig)
        error = f"in {func} Error creating bar chart: {e}"
        logger.info(error)
        raise TypeError(error)

    img_bytes = io.BytesIO()

    try:
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        matplotlib.pyplot.close(fig)
        return img_bytes.getvalue()
    except Exception as e:
        matplotlib.pyplot.close(fig)
        error = f"in {func} Error saving figure to bytes: {e}"
        logger.info(error)
        raise TypeError(error)

