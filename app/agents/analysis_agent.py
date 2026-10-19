"""MODULE 4 - Analysis & Validation Agent.

Produces: summary statistics, insights, chart data and a data-quality score.
"""
import numpy as np
import pandas as pd


def validate(raw_shape, raw_missing, df: pd.DataFrame, dups_removed: int) -> dict:
    raw_rows, raw_cols = raw_shape
    total_cells = max(raw_rows * raw_cols, 1)
    completeness = 1 - raw_missing / total_cells
    retention = df.shape[0] / raw_rows if raw_rows else 0
    numeric_share = len(df.select_dtypes("number").columns) / max(df.shape[1], 1)

    score = round(100 * (0.5 * completeness + 0.3 * retention + 0.2 * min(numeric_share * 2, 1)), 1)
    checks = [
        {"check": "Completeness of source data", "value": f"{completeness*100:.1f}%", "pass": completeness >= 0.9},
        {"check": "Row retention after cleaning", "value": f"{retention*100:.1f}%", "pass": retention >= 0.8},
        {"check": "Duplicates removed", "value": str(dups_removed), "pass": True},
        {"check": "Dataset not empty", "value": f"{df.shape[0]} rows", "pass": df.shape[0] > 0},
        {"check": "Numeric columns detected", "value": str(len(df.select_dtypes('number').columns)), "pass": numeric_share > 0},
    ]
    return {"quality_score": score, "checks": checks}


def analyze(df: pd.DataFrame) -> dict:
    insights = []
    num = df.select_dtypes("number")
    text_cols = [c for c in df.columns if c not in num.columns]
    label_col = text_cols[0] if text_cols else None

    summary = {}
    if not num.empty:
        desc = num.describe().T[["count", "mean", "min", "max", "std"]].round(2)
        summary = desc.reset_index().rename(columns={"index": "column"}).to_dict(orient="records")

        for c in list(num.columns)[:3]:
            i_max, i_min = num[c].idxmax(), num[c].idxmin()
            if label_col:
                insights.append(
                    f"'{c}': highest is {df.loc[i_max, label_col]} ({num.loc[i_max, c]:,.2f}), "
                    f"lowest is {df.loc[i_min, label_col]} ({num.loc[i_min, c]:,.2f}); average {num[c].mean():,.2f}."
                )
            else:
                insights.append(f"'{c}': min {num[c].min():,.2f}, max {num[c].max():,.2f}, average {num[c].mean():,.2f}.")

        if num.shape[1] >= 2:
            corr = num.corr().abs().to_numpy(copy=True)
            np.fill_diagonal(corr, 0)
            a, b = np.unravel_index(np.argmax(corr), corr.shape)
            if corr[a, b] > 0.5:
                real = num.corr().iloc[a, b]
                insights.append(f"Strongest relationship: '{num.columns[a]}' vs '{num.columns[b]}' (correlation {real:.2f}).")
    else:
        insights.append("No numeric columns found; dataset is text-based.")

    for c in text_cols[:2]:
        top = df[c].value_counts().head(1)
        if len(top) and df[c].nunique() < len(df):
            insights.append(f"Most frequent '{c}': {top.index[0]} ({int(top.iloc[0])} times).")

    # chart: top 10 of first numeric column by label
    chart = None
    if not num.empty and label_col:
        col = num.columns[0]
        top = df.nlargest(10, col)
        chart = {
            "title": f"Top {len(top)} by {col}",
            "labels": top[label_col].astype(str).tolist(),
            "values": [float(v) for v in top[col]],
        }

    return {"summary": summary, "insights": insights, "chart": chart}
