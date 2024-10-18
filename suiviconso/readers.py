"""Functions for reading the data
Input: config file parameters, in particular paths to data files/directories
Output: pandas DataFrame with DateTimeIndex
"""

import logging
from datetime import datetime
from typing import Callable
from pathlib import Path
import pandas as pd


def is_reader(function: Callable) -> bool:
    """Return true if function is suiviconso reader"""
    return "reader" in function.__name__


def csv_reader(
    file_path: str | Path, index_col: str | int = 0, **kwargs
) -> pd.DataFrame:
    """Wrapper for pandas.read_csv(file_path, index_col=index_col, **kwargs).
    ### Arguments:
    - `file_path` : path to the csv file
    - `index_col` : name of the column to use as DateTimeindex (default: 0)
    ### Returns:
    - DataFrame with DateTimeIndex"""

    logging.info(f"Reading data from {file_path}")
    df = pd.read_csv(file_path, index_col=index_col, **kwargs)
    df.index = pd.to_datetime(df.index)
    return df


def edf_elec_reader(
    dir_path: str | Path,
    *,
    fname_glob: str = "mes-puissances-atteintes-30min-*.csv",
    variable_name: str = "Electricity (kWh)",
) -> pd.DataFrame:
    """Read data from EDF suivi conso electricity directory.
    ### Arguments:
    - `dir_path` : path to the data directory
    - `fname_glob` : file name glob to look for within the data directory
                     (only one file is expected to be found)
    - `variable_name` : name of the column in output DataFrame
    ### Returns:
    - DataFrame with DateTimeIndex"""
    # pylint: disable=too-many-locals

    logging.info(f"Reading data from {dir_path}")

    dir_path = Path(dir_path)
    assert dir_path.exists(), f"{dir_path} not found, check config file!"
    fpath = next(dir_path.glob(fname_glob), dir_path / fname_glob)
    assert fpath.exists(), f"{fpath.name} not found in {dir_path}, check data dir!"

    timestamps = []
    power = []
    with open(fpath, encoding="iso-8859-1") as f:
        for line in f:
            if "/" in line:
                d, m, y = [int(i) for i in line.strip().split(";", 1)[0].split("/")]
            elif ":" in line:
                t, w, _ = line.strip().split(";")
                hh, mm, ss = [int(it) for it in t.split(":")]
                if mm not in [0, 30] or ss != 0:
                    # Sometimes there are these entries at irregular interval,
                    # always in the same part of the year - to investigate?
                    # Also, sometimes some intervals are missing, also regular across years
                    logging.debug(f"Strange entry detected: {line}")
                    continue
                timestamps.append(datetime(y, m, d, hh, mm, ss))
                power.append(float(w) * 0.0005)  # power is in watts per 0.5 h
    df = pd.DataFrame(power, index=timestamps, columns=[variable_name])
    df = df[~df.index.duplicated(keep="last")]  # data from EDF can contains duplicates!
    return df


def edf_gaz_reader(
    dir_path: str | Path,
    *,
    fname_glob: str = "ma-conso-quotidienne-*.csv",
    variable_name: str = "Gas (m3)",
) -> pd.DataFrame:
    """Read data from EDF suivi conso gaz directory.
    ### Arguments:
    - `dir_path` : path to the data directory
    - `fname_glob` : file name glob to look for within the data directory
                     (only one file is expected to be found)
    - `variable_name` : name of the column in output DataFrame
    ### Returns:
    - DataFrame with DateTimeIndex"""

    # pylint: disable=too-many-locals

    logging.info(f"Reading data from {dir_path}")

    dir_path = Path(dir_path)
    assert dir_path.exists(), f"{dir_path} not found, check config file!"
    fpath = next(dir_path.glob(fname_glob), dir_path / fname_glob)
    assert fpath.exists(), f"{fpath.name} not found in {dir_path}, check data dir!"

    df = pd.read_csv(
        fpath,
        encoding="iso-8859-1",
        sep=";",
        skiprows=3,
        header=4,
        skip_blank_lines=True,
        decimal=",",
        parse_dates=[0],
        date_format="%d/%m/%Y",
        index_col=[0],
        usecols=[0, 1],
        names=["Date", variable_name],
    )
    df.index += pd.Timedelta(hours=12)  # data is daily so center it on noon
    return df


def influxdb_lp_reader(
    file_path: str | Path,
    *,
    multiple_fields: bool = True,
) -> pd.DataFrame:
    """Read data from influxdb line protocol file (e.g. output of `influx_inspect export`).
    ### Arguments:
    - `file_path` : path to the line protocol file
    - `multiple_fields` : optimises reading in case of one field per measurement/line
    ### Returns:
    - DataFrame with DateTimeIndex"""

    file_path = Path(file_path)
    assert file_path.exists(), f"{file_path} not found, check config file!"

    logging.info(f"Reading data from {file_path}")
    # Syntax (see https://docs.influxdata.com/influxdb/cloud/reference/syntax/line-protocol/):
    # <measurement>[,tags] <field_key>=<field_value>[,<field_key>=<field_value>] [<timestamp>]
    df = pd.read_table(
        file_path,
        header=None,
        sep=" ",
        skiprows=7,
        index_col=-1,
        names=["Measurement", "Fields", "Timestamp"],
        usecols=[1, 2],
        comment="#",
    )
    logging.info("Processing...")
    if multiple_fields:
        df = df["Fields"].str.split(",", expand=True)
    dfs = [
        df[col]
        .str.split("=", expand=True)
        .astype({0: str, 1: float})
        .pivot(columns=0, values=1)
        for col in df.columns
    ]
    df = dfs.pop()
    for others_df in dfs:
        df = df.join(others_df, how="outer")
    df.index = pd.to_datetime(df.index)
    df = df.resample("min").mean()
    logging.info(" ...done!")
    return df
