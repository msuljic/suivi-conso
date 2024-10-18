"""suiviconso module"""

from typing import Callable
import pandas as pd
from .readers import (
    csv_reader,
    edf_elec_reader,
    edf_gaz_reader,
    influxdb_lp_reader,
    is_reader,
)
from .filters import basic_filter, is_filter
from .plotters import (
    info_printer,
    daily_plotter,
    hourly_plotter,
    weekly_plotter,
    correlation_plotter,
)

MODULES: list[Callable[..., pd.DataFrame]] = [
    csv_reader,
    edf_elec_reader,
    edf_gaz_reader,
    influxdb_lp_reader,
    basic_filter,
    info_printer,
    daily_plotter,
    hourly_plotter,
    weekly_plotter,
    correlation_plotter,
]
