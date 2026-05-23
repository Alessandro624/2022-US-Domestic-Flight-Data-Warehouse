from pathlib import Path
from typing import Mapping

import pandas as pd
from .config import RECONCILED_PATHS, CLEANED_PATHS, ORIGINAL_PATHS, DW_PATHS


def _normalize_columns(df: pd.DataFrame, normalize_cols: str) -> pd.DataFrame:
    if normalize_cols == "lower":
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")
    elif normalize_cols == "upper":
        df.columns = df.columns.str.upper().str.strip().str.replace(" ", "_")
    elif normalize_cols == "strip":
        df.columns = df.columns.str.strip().str.replace(" ", "_")
    else:
        raise ValueError("normalize_cols must be one of: 'lower', 'upper', 'strip'")
    return df


def load_tables(
    source: str | Mapping[str, str | Path],
    *,
    normalize_cols: str = "lower",
    verbose: bool = True,
) -> dict[str, pd.DataFrame]:
    """
    Load CSV tables into a dict of DataFrames with normalised column names.
    """
    if isinstance(source, str):
        source_map: dict[str, dict[str, Path]] = {
            "original": ORIGINAL_PATHS,
            "reconciled": RECONCILED_PATHS,
            "cleaned": CLEANED_PATHS,
            "dw": DW_PATHS,
        }
        if source not in source_map:
            raise ValueError(f"Unknown source '{source}'. Use 'original', 'reconciled', 'cleaned', 'dw', or a dict.")
        path_map = source_map[source]
    elif isinstance(source, Mapping):
        path_map = {table_name: Path(path) for table_name, path in source.items()}
    else:
        raise TypeError("source must be a string or a dict")

    dfs: dict[str, pd.DataFrame] = {}

    for table_name, path in path_map.items():
        if not path.exists():
            msg = f"[{table_name}] NOT FOUND at {path}"
            if verbose:
                print(msg)
            continue

        df = pd.read_csv(path)

        dfs[table_name] = _normalize_columns(df, normalize_cols)

        if verbose:
            print(f"[{table_name}] {len(df):,} rows x {len(df.columns)} cols")

    return dfs
