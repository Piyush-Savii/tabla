import matplotlib.pyplot
import io
from typing import Dict

from visualization.charts.validations import validate_data_type, check_pie_label
from visualization.helpers.colors import get_palette_colors
from visualization.types import PaletteTypeLiteral

def pie_chart_plot(data_dict: Dict[str, float],
                   title: str,
                   explode_largest: bool,
                   palette_type: PaletteTypeLiteral) -> bytes:
    func = "pie_chart_plot"
    validate_data_type(name="data_dict", value=data_dict, expected_type=list)
    validate_data_type(name="title", value=title, expected_type=str)
    validate_data_type(name="explode_largest", value=explode_largest, expected_type=bool)
    validate_data_type(name="palette_type", value=palette_type, expected_type=str)
    validate_data_type(name="palette_type", value=palette_type, expected_type=PaletteTypeLiteral)
    for item in data_dict:
        validate_data_type(name="item", value=item, expected_type=dict)
        check_pie_label(name="item", value=item)

    try:
        labels = [item['label'] for item in data_dict] # type: ignore
        values = [item['value'] for item in data_dict] # type: ignore
        colors = get_palette_colors(palette_type, len(labels))
        if explode_largest:
            max_index = values.index(max(values))
            explode = [0.1 if i == max_index else 0 for i in range(len(values))]
        else:
            explode = [0] * len(values)
    except Exception as e:
        raise RuntimeError(f"in {func} Error processing data or getting colors: {e}")


    fig, ax = matplotlib.pyplot.subplots(nrows=1, ncols=1)

    try:
        ax.pie(values, labels=labels, explode=explode, autopct='%1.1f%%', startangle=90, colors=colors)
        ax.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle.
        ax.set_title(title)
        fig.tight_layout()
    except Exception as e:
        matplotlib.pyplot.close(fig)
        raise RuntimeError(f"in {func} Error creating pie chart: {e}")

    img_bytes = io.BytesIO()

    try:
        fig.savefig(img_bytes, format='png', dpi=300, bbox_inches='tight')
        img_bytes.seek(0)
        matplotlib.pyplot.close(fig)
        return img_bytes.getvalue()
    except Exception as e:
        matplotlib.pyplot.close(fig)
        raise RuntimeError(f"in {func} Error saving figure to bytes: {e}")


