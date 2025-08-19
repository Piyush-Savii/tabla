import seaborn as sns
from typing import List
from visualization.types import CATEGORICAL, SEQUENTIAL, DIVERGING

def get_palette_colors(data_type: str, num_colors: int) -> List:
    data_type_upper = data_type.upper()

    if data_type_upper == CATEGORICAL:
        return sns.color_palette("Set2", num_colors)
    elif data_type_upper == SEQUENTIAL:
        return sns.color_palette("Blues", num_colors)
    elif data_type_upper == DIVERGING:
        return sns.color_palette("coolwarm", num_colors)
    else:
        return sns.color_palette("Set2", num_colors)

def get_heatmap_colormap(data_type: str) -> str:
    data_type_upper = data_type.upper()

    if data_type_upper == CATEGORICAL:
        return "tab20"
    elif data_type_upper == SEQUENTIAL:
        return "plasma"
    elif data_type_upper == DIVERGING:
        return "RdBu_r"
    else:
        return "viridis"