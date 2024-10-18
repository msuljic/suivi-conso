"""Run Suivi Conso CLI"""

import sys
import logging
import argparse
import tomllib
from pathlib import Path
import pandas as pd
from rich.logging import RichHandler
from matplotlib import pyplot as plt
import matplotlib.style as mstyle
from suiviconso import MODULES, is_reader, is_filter

mstyle.use("suiviconso.mplstyle")


def main():
    """Run Suivi Conso CLI"""

    parser = argparse.ArgumentParser(
        "Suivi Conso CLI", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "config",
        default="config-template.toml",
        type=argparse.FileType("rb"),
        help="Path to config file",
    )
    parser.add_argument("--log-level", "-l", default="INFO", help="Loggging level")
    parser.add_argument(
        "--save-plots-dir", "-s", help="Path to directory where plots will be saved."
    )
    args = parser.parse_args()

    logging.basicConfig(
        format="%(funcName)s: %(message)s",
        handlers=[RichHandler()],
        level=args.log_level,
    )

    config: dict[str, dict] = tomllib.load(args.config)
    data = pd.DataFrame()

    for module_name, module_config in config.items():
        try:
            module = next(m for m in MODULES if m.__name__ in module_name.lower())
        except StopIteration:
            logging.fatal(
                f"Module {module_name} not found! "
                f"Available modules: {[m.__name__ for m in MODULES]}"
            )
            sys.exit(f"Module {module_name} not found!")
        if is_reader(module):
            new_data = module(**module_config)
            if data.empty:
                data = new_data
            elif set(new_data.columns) == set(data.columns) & set(new_data.columns):
                data = pd.concat((data, new_data))
            else:
                data = data.join(new_data, how="outer")
        elif is_filter(module):
            data = module(data.copy(), **module_config)
        else:
            module(data.copy(), **module_config)

    if args.save_plots_dir:
        plots_dir = Path(args.save_plots_dir)
        plots_dir.mkdir(exist_ok=True)
        for i in plt.get_fignums():
            fig = plt.figure(i)
            fig.savefig(plots_dir / fig.axes[0].get_title())
    plt.show()


if __name__ == "__main__":
    main()
