"""Filtering modules/functions
Input: DataFrame to process based on config file parameters
Output: processed Dataframe"""

import logging
from typing import Callable
from dateutil import parser as dparser
import pandas as pd


def is_filter(function: Callable) -> bool:
    """Return true if function is suiviconso filter"""
    return "filter" in function.__name__


def basic_filter(  # pylint: disable=too-many-arguments
    df: pd.DataFrame,
    *,
    remove_duplicates: str | None = "keep_last",
    resample: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    query: str | None = None,
) -> pd.DataFrame:
    """Basic filtering capabilities
    ### Arguments:
     `df` : DataFrame to process
    - `remove_duplicates` : 'keep_first' or 'keep_last' or None
    - `resample` : rule for resampling (with mean aggregator)
    - `start_date` : remove data before the given date
    - `end_date` : remove data after the given date
    - `query` : arbitrary pandas DataFrame query
    ### Returns
    - processed DataFrame"""

    assert not remove_duplicates or remove_duplicates in [
        "keep_first",
        "keep_last",
    ], f"Unkown option {remove_duplicates=}"
    remove_duplicates = remove_duplicates.removeprefix("keep_")

    if remove_duplicates:
        logging.info(f"Removing duplicates - keeping {remove_duplicates} entry")
        df = df[~df.index.duplicated(keep=remove_duplicates)]

    if resample:
        logging.info(f"Resampling with rule {resample}")
        df = df.resample(resample).mean()

    if start_date:
        logging.info(f"Removing data before {start_date}")
        df = df.loc[df.index >= dparser.parse(start_date)]

    if end_date:
        logging.info(f"Removing data after {end_date}")
        df = df.loc[df.index < dparser.parse(end_date)]

    if query:
        logging.info(f"Querying data with '{query}'")
        df = df.query(query)

    return df
