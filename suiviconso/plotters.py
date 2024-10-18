"""Plotting/printing modules/functions
Input: DataFrame with DateTimeIndex and config file parameters
Output: matplotlib plots and text to terminal"""

import logging
from io import StringIO
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from rich import print  # pylint: disable=redefined-builtin


def info_printer(df: pd.DataFrame, *, to_csv_file: str | None = None, **kwargs):
    """Print some info about the data to terminal, no plots produced.
    # Arguments:
    - `to_csv_file` : file path to dump DataFrame in csv format
    - `kwargs` : passed to df.info() method"""

    print("\n", "-" * 20, "DATA INFO BEG", "-" * 20)
    buf = StringIO()
    df.info(buf=buf, **kwargs)
    print(buf.getvalue())
    print(df)
    print("-" * 20, "DATA INFO END", "-" * 20, "\n")
    if to_csv_file:
        df.to_csv(to_csv_file)
        logging.info(f"Dumped data to file {to_csv_file}")


def _process_variables_arg(df: pd.DataFrame, variables: list[str] | None) -> list[str]:
    """Helper function to check compliance of 'variables' argument provided
    in config file. Returnes correctly initialised variable."""
    if not variables:
        return df.columns.values
    if not isinstance(variables, list):
        variables = [variables]
    for var in variables:
        assert (
            var in df.columns
        ), f"{var} not found in data! Possible options: {df.columns.values}"
    return variables


def daily_plotter(
    df: pd.DataFrame,
    *,
    variables: list[str] | None = None,
    rolling_average_days: int = 1,
    aggfunc: str = "sum",
) -> None:
    """Plots daily trend over the year.
    ### Arugments:
    - `variables` : list of variable names, if empty plot all variables
    - `rolling_average_days` : smooth the data by calculating rolling of N days
    - `aggfunc` : aggregator function, e.g. 'mean' to calculate daily average"""

    variables = _process_variables_arg(df, variables)

    title = f"Daily {aggfunc} over the year"
    logging.info(f"Plotting '{title}'")

    years = sorted(set(dt.year for dt in df.index))
    ref_year = years[0]

    df = df.resample("D").aggregate(aggfunc)
    if rolling_average_days > 1:
        df = df.rolling(rolling_average_days).mean()

    for var in variables:
        plt.figure()
        for year in years:
            ydf: pd.DataFrame = df[df.index.year == year]
            if ref_year % 4 != 0 and year % 4 == 0:  # handle leap years
                ydf = ydf.drop(
                    pd.Timestamp(year=year, month=2, day=29), errors="ignore"
                )
            ydf.index = pd.to_datetime(
                [
                    pd.Timestamp(year=ref_year, month=dt.month, day=dt.day)
                    for dt in ydf.index
                ]
            )
            plt.plot(ydf.index, ydf[var], label=f"{year}")
        plt.title(f"{var} - {title}")
        xax = plt.gca().xaxis
        xax.set_major_locator(mdates.MonthLocator())
        xax.set_minor_locator(mdates.WeekdayLocator())
        xax.set_major_formatter(mdates.DateFormatter("%b"))
        plt.xlim(
            pd.Timestamp(year=ref_year, month=1, day=1),
            pd.Timestamp(year=ref_year, month=12, day=31),
        )
        plt.ylabel(var)
        plt.grid(axis="x", which="major")
        plt.grid(axis="x", which="minor", linestyle="dotted")
        plt.legend()


def _sort_by_condition(
    df: pd.DataFrame, condition: str | list
) -> dict[str, pd.DataFrame]:
    """Helper function to sort DataFrame in multiple DataFrames based on condition.
    ### Arugments:
    - `df` : DataFrame to split
    - `condition` : 'year', 'hot-cold', 'quarter', 'weekend' or list of text queries
    ### Returns:
    - dict of condition names and corresponding DataFrames"""

    sorted_dfs: dict[str, pd.DataFrame] = {}
    match condition:
        case "year":
            years = sorted(set(dt.year for dt in df.index))
            for year in years:
                sorted_dfs[str(year)] = df[df.index.year == year]
        case "hot-cold":
            cond = (4 < df.index.month) & (df.index.month <= 10)
            sorted_dfs["Nov-Apr"] = df[~cond]
            sorted_dfs["May-Oct"] = df[cond]
        case "weekend":
            sorted_dfs["Work day"] = df[df.index.weekday < 5]
            sorted_dfs["Weekend"] = df[df.index.weekday >= 5]
        case "quarter":
            for q in range(1, 5):
                sorted_dfs[f"Q{q}"] = df[df.index.quarter == q]
        case list():
            for query in condition:
                sorted_dfs[query] = df.query(query)
        case _:
            raise ValueError(f"Unrecognised option '{condition}' for sorting")
    return sorted_dfs


def hourly_plotter(
    df: pd.DataFrame,
    *,
    variables: list[str] | None = None,
    sort_by: str | list = "year",
    aggfunc: str = "mean",
) -> None:
    """Plots average hourly trend over 24 hours.
    ### Arugments:
    - `variables` : list of variable names, if empty plot all variables
    - `sort_by` : 'year', 'hot-cold', 'quarter', 'weekend' or list of text queries
    - `aggfunc` : aggregator function, e.g. 'mean' to calculate hourly average"""

    variables = _process_variables_arg(df, variables)

    title = f"Hourly {aggfunc} over the day"
    logging.info(f"Plotting '{title}'")

    df["hour"] = df.index.hour + df.index.minute / 60.0
    sorted_dfs = _sort_by_condition(df, sort_by)
    for label, sorted_df in sorted_dfs.items():
        sorted_dfs[label] = sorted_df.pivot_table(index="hour", aggfunc=aggfunc)

    for var in variables:
        fig = plt.figure()
        for label, sorted_df in sorted_dfs.items():
            if var not in sorted_df.columns:
                logging.info(f"No data for '{var}' in '{label}'.")
                continue
            sorted_df = sorted_df[var].dropna()
            if sorted_df.size < 12:
                logging.info(
                    f"Insufficent data ({sorted_df.size}) for '{var}' in '{label}'."
                )
                continue
            sorted_df.loc[24] = sorted_df.iloc[0]
            plt.plot(sorted_df, label=label)
        if len(fig.get_children()) <= 1:  # empty figure
            logging.warning(f"No data for '{var}'.")
            plt.close(fig)
            return
        plt.title(f"{var} - {title}")
        plt.xlim(0, 24)
        plt.xticks(list(range(0, 27, 3)))
        plt.xticks(list(range(0, 25, 1)), minor=True)
        plt.xlabel("Hour")
        plt.ylabel(var)
        plt.grid(axis="both", which="both", linestyle="dotted")
        plt.legend()


def weekly_plotter(
    df: pd.DataFrame,
    variables: list[str] | None = None,
    sort_by: str | list = "year",
) -> None:
    """Plots trend over a week.
    ### Arugments:
    - `variables` : list of variable names, if empty plot all variables
    - `sort_by` : 'year', 'hot-cold', 'quarter', 'weekend' or list of text queries
    """
    variables = _process_variables_arg(df, variables)

    title = "Trend over the week"
    logging.info(f"Plotting '{title}'")

    dfm = df.resample("d").mean()
    dfm["day"] = dfm.index.weekday + 0.5
    dfm = dfm.pivot_table(index="day", aggfunc="mean")
    dfm.loc[0], dfm.loc[7] = dfm.loc[0.5], dfm.loc[6.5]
    dfm = dfm.sort_index()

    df["day"] = (
        df.index.weekday + (df.index.hour + df.index.minute / 60.0) / 24.0
    ).round(2)
    sorted_dfs = _sort_by_condition(df, sort_by)
    for label, sorted_df in sorted_dfs.items():
        sorted_dfs[label] = sorted_df.pivot_table(index="day", aggfunc="mean")

    for var in variables:
        plt.figure()
        for label, sorted_df in sorted_dfs.items():
            if var not in sorted_df.columns:
                logging.info(f"No data for '{var}' in '{label}'.")
                continue
            plt.plot(sorted_df[var].dropna(), label=label)
        plt.step(
            dfm.index, dfm[var], where="mid", label="Daily mean", c="grey", alpha=0.5
        )
        plt.title(f"{var} - {title}")
        plt.xlim(0, 7)
        plt.xticks(list(range(0, 7)), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        plt.xticks(list(np.arange(0, 7, 0.25)), minor=True)
        plt.ylabel(var)
        plt.grid(axis="both", linestyle="dotted")
        plt.legend()


def correlation_plotter(
    df: pd.DataFrame, x_vars: str | list = None, y_vars: str | list | None = None
):
    """Plots correlation between variables. Resamples the data to match the variable
    measured with lower frequency.
    ### Arguments:
    - `x_vars` : list of variable names to plot on x axis, if empty plot all variables
    - `y_vars` : list of variable names to plot on y axis, if empty plot all variables

        Leaving both `x_vars` and `y_vars` empty will plot all possible combinations."""

    x_vars = _process_variables_arg(df, x_vars)
    y_vars = _process_variables_arg(df, y_vars)
    df.sort_index()

    plotted_combinations = []
    for x in x_vars:
        for y in y_vars:
            if x == y or {x, y} in plotted_combinations:
                continue
            plotted_combinations.append({x, y})

            title = f"{y} vs {x}"
            logging.info(f"Plotting '{title}'")

            dfc = df[[x, y]].dropna(how="all")
            cnt = dfc.count()
            f = pd.Timedelta(
                np.median(np.diff(df[y if cnt[y] < cnt[x] else x].dropna().index))
            )
            fstr = ", ".join(
                f"{v} {k}" for k, v in f.components._asdict().items() if v > 0
            )
            dfc = dfc.resample(f).mean().dropna()
            dfc.plot(
                x=x,
                y=y,
                kind="scatter",
                alpha=1.0 / np.log10(dfc.index.size),
                label=f"Mean values over {fstr}",
            )
            plt.title(title)
            plt.grid(linestyle="dotted")
