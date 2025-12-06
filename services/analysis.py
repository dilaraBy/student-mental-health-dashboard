# Analysis functions: prevalence, trends, group comparisons

import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

def compute_prevalence(df: pd.DataFrame, column: str) -> dict:
    """
    Compute prevalence of 'Yes'/'No' values in a given column.
    Assumes values are already normalized to 'Yes'/'No'.
    """
    if column not in df.columns:
        logger.warning(f"Column {column} not in DataFrame")
        return {"yes_count": 0, "no_count": 0, "total": 0,
                "yes_percentage": 0.0, "no_percentage": 0.0}

    series = df[column].dropna()

    yes_count = (series == "Yes").sum()
    no_count = (series == "No").sum()
    total = len(series)

    if total == 0:
        yes_pct = no_pct = 0.0
    else:
        yes_pct = yes_count / total * 100
        no_pct = no_count / total * 100

    result = {
        "yes_count": yes_count,
        "no_count": no_count,
        "total": total,
        "yes_percentage": round(yes_pct, 2),
        "no_percentage": round(no_pct, 2),
    }

    logger.debug(f"Prevalence for {column}: {result}")
    return result


def compute_all_prevalence(df: pd.DataFrame, columns: list[str]) -> dict:
    """
    Compute prevalence for multiple yes/no columns.
    Returns a dict: {column_name: prevalence_dict}
    """
    results: dict[str, dict] = {}

    for col in columns:
        results[col] = compute_prevalence(df, col)

    logger.info(f"Computed prevalence for columns: {columns}")
    return results

def group_comparison(df: pd.DataFrame, group_by: str, condition: str) -> pd.DataFrame:
    """
    For each value in `group_by`, compute prevalence of 'Yes' in `condition`.
    Returns a DataFrame with columns:
    [group_by, yes_count, no_count, total, yes_percentage]
    """
    if group_by not in df.columns or condition not in df.columns:
        logger.warning(f"Columns {group_by} or {condition} not in DataFrame")
        return pd.DataFrame()

    grouped = df.dropna(subset=[group_by, condition]).groupby(group_by)

    rows = []
    for group_value, group_df in grouped:
        prev = compute_prevalence(group_df, condition)
        row = {
            group_by: group_value,
            "yes_count": prev["yes_count"],
            "no_count": prev["no_count"],
            "total": prev["total"],
            "yes_percentage": prev["yes_percentage"],
        }
        rows.append(row)

    result = pd.DataFrame(rows)
    logger.info(f"Computed group comparison for {condition} by {group_by}")
    return result

