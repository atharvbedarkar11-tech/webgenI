"""MODULE 3 - Data Cleaning & Transformation Agent (pandas)."""
import re

import numpy as np
import pandas as pd


def _snake(name: str) -> str:
    name = re.sub(r"\[.*?\]", "", str(name))
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return name or "col"


def _to_number(series: pd.Series):
    """Try to convert a text column like '1,234', '$5.5', '12%' to numbers."""
    s = series.astype(str).str.replace(r"[,\$€£%\s]", "", regex=True)
    s = s.replace({"": np.nan, "nan": np.nan, "None": np.nan, "-": np.nan, "—": np.nan})
    num = pd.to_numeric(s, errors="coerce")
    ok = num.notna().sum()
    total = series.notna().sum()
    if total > 0 and ok / total >= 0.8:
        return num, True
    return series, False


def clean_and_transform(df: pd.DataFrame, deduplicate=True, fill_missing=True) -> dict:
    ops = []
    raw_rows, raw_cols = df.shape
    raw_missing = int(df.isna().sum().sum())
    df = df.copy()

    # 1. normalize column names
    old = list(df.columns)
    df.columns = [_snake(c) for c in df.columns]
    # make unique
    seen = {}
    new_cols = []
    for c in df.columns:
        seen[c] = seen.get(c, 0) + 1
        new_cols.append(c if seen[c] == 1 else f"{c}_{seen[c]}")
    df.columns = new_cols
    ops.append("Normalized column names to snake_case")

    # 2. strip text, remove footnote markers like [1]
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            df[c] = (
                df[c].astype(str)
                .str.replace(r"\[[^\]]*\]", "", regex=True)
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .replace({"": np.nan, "nan": np.nan, "None": np.nan})
            )
    ops.append("Trimmed whitespace and removed footnote markers")

    # 3. drop empty rows/cols
    before = df.shape
    df = df.dropna(how="all").dropna(axis=1, how="all")
    if df.shape != before:
        ops.append(f"Dropped {before[0]-df.shape[0]} empty row(s) and {before[1]-df.shape[1]} empty column(s)")

    # 4. convert numeric-looking columns
    converted = []
    for c in df.columns:
        if not pd.api.types.is_numeric_dtype(df[c]):
            new, ok = _to_number(df[c])
            if ok:
                df[c] = new
                converted.append(c)
    if converted:
        ops.append(f"Converted to numeric: {', '.join(converted)}")

    # 5. deduplicate
    dups = 0
    if deduplicate:
        dups = int(df.duplicated().sum())
        df = df.drop_duplicates()
        ops.append(f"Removed {dups} duplicate row(s)")

    # 6. handle missing values
    filled = 0
    if fill_missing:
        for c in df.columns:
            n = int(df[c].isna().sum())
            if n == 0:
                continue
            if pd.api.types.is_numeric_dtype(df[c]):
                df[c] = df[c].fillna(df[c].median())
            else:
                df[c] = df[c].fillna("Unknown")
            filled += n
        ops.append(f"Filled {filled} missing value(s) (median for numbers, 'Unknown' for text)")

    df = df.reset_index(drop=True)
    return {
        "df": df,
        "operations": ops,
        "stats": {
            "raw_rows": raw_rows,
            "raw_cols": raw_cols,
            "raw_missing": raw_missing,
            "clean_rows": int(df.shape[0]),
            "clean_cols": int(df.shape[1]),
            "duplicates_removed": dups,
            "missing_filled": filled,
            "numeric_columns": [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])],
        },
    }
