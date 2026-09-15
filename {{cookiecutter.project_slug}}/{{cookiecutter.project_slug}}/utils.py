from pathlib import Path
from typing import Callable

from pyprojroot import here


def make_dir_function(*parts: str) -> Callable[..., Path]:
    """Build a function returning a path under the project root, extended by any given parts."""

    def dir_path(*args: str) -> Path:
        return here().joinpath(*parts, *args)

    return dir_path


project_dir = make_dir_function()
data_dir = make_dir_function("data")
data_raw_dir = make_dir_function("data", "raw")
data_processed_dir = make_dir_function("data", "processed")
data_interim_dir = make_dir_function("data", "interim")
outputs_dir = make_dir_function("outputs")
outputs_figures_dir = make_dir_function("outputs", "figures")
outputs_tables_dir = make_dir_function("outputs", "tables")
assets_dir = make_dir_function("assets")
