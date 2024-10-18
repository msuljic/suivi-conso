# Suivi Conso EDF

This is a simple program that plots EDF electricity and gas consumption data in a more analytical way than what is provided on the EDF website and app.

## Quickstart

### 1. Install the dependencies

    pip install -r requirements.txt

### 2. Download the data

Go to <https://suiviconso.edf.fr/>, log in, select `ÉLEC` and click on "Télécharger mes données". Repeat for `GAZ` and unzip the downloaded files.

### 3. Set up the config file

Copy [`examples/basic-config.toml`](examples/basic-config.toml) to top directory.

    cp ./examples/basic-config.toml ./my-config.toml

Edit `my-config.toml` so that the `dir_path` parameters point to the directories you have downloaded in previous step.

You can see all available config file parameters and usage examples in [`examples/full-config.toml`](examples/full-config.toml)

### 4. Run

Execute the following command:

    python run.py my-config.toml

For additional options, see:

    python run.py -h

## Description

A simple Python program that uses `pandas` and `matplotlib` to process and plot data. Although initially designed to plot only EDF "suivi conso" data, it can also read generic CSV files and `influxdb` line protocol files.

Data reading, processing, and plotting is controlled via a `TOML` config file. Each `[HEADER]` in the config file instatiates a module that can read, filter, ot plot the data. See the config files in the [`examples/`](examples/) directory for more information.

### Reading modules

1. `edf_elec_reader`: Reads data from EDF suivi conso electricity directory.
2. `edf_gaz_reader`: Reads data from EDF suivi conso gaz directory.
3. `csv_reader`: Reads data from a CSV file.
4. `influxdb_lp_reader`: Reads data from an `influxdb` line protocol file.

### Filtering modules

1. `basic_filter`: Provides basic filtering functionalty such as time slicing and resampling.

### Plotting modules

1. `info_printer`: Prints some info about the data to the terminal (no plots produced).
2. `daily_plotter`: Plots daily trends over the year.
3. `hourly_plotter`: Plots average hourly trends over 24 hours.
4. `weekly_plotter`: Plots trends over a week.
5. `correlation_plotter`: Plots correlations between variables.

Plotting style can be tweaked by adjusting the [`suiviconso.mplstyle`](suiviconso.mplstyle) file.

## Example plots

### Daily trend over the year (`daily_plotter`)

How gas consumption changes day to day over the year:

<img src="examples/plots/Gas (m3) - Daily sum over the year.png" alt="Gas (m3) - Daily sum over the year" width=700>

How temperature changes day to day over the year:

<img src="examples/plots/T (°C) - Daily mean over the year.png" alt="T (°C) - Daily mean over the year" width=700>

### Daily trend over the week (`weekly_plotter`)

You can see slightly higher gas consumption on Sundays, which is when I like to take a bath:

<img src="examples/plots/Gas (m3) - Trend over the week.png" alt="Gas (m3) - Trend over the week" width=700>

### Hourly trehn over the day (`hourly_plotter`)

You can observe a more regular pattern on working days, with peaks during lunch and dinner preparation:

<img src="examples/plots/Electricity (kWh) - Hourly mean over the day.png" alt="Electricity (kWh) - Hourly mean over the day" width=700>

### Correlation between variables

As expected, gas consumption and temperature are negatively correlated:

<img src="examples/plots/Gas (m3) vs T (°C).png" alt="Gas (m3) vs T (°C)" width=700>
