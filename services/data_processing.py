"""Data cleaning and preprocessing utilities.

Implemented functions are minimal helpers used by tests:
- convert_timestamps(df): convert `Timestamp` column to datetime (coerce errors)
- normalize_yes_no(df): normalize common yes/no/true/false representations to 'Yes'/'No'
- add_temporal_columns(df): add `year`, `month`, `day_of_week` columns from Timestamp
"""
from typing import Iterable

import pandas as pd


def convert_timestamps(df: pd.DataFrame, column: str = "Timestamp") -> pd.DataFrame:
	"""Convert the specified timestamp column to datetime, coercing errors to NaT.

	Returns a new DataFrame with the converted column.
	"""
	out = df.copy()
	out[column] = pd.to_datetime(out[column], errors="coerce")
	return out


def _map_to_yes_no(value: object) -> object:
	if pd.isna(value):
		return value
	s = str(value).strip().lower()
	yes_values = {"yes", "y", "true", "t", "1", "yes."}
	no_values = {"no", "n", "false", "f", "0", "no."}
	if s in yes_values:
		return "Yes"
	if s in no_values:
		return "No"
	return value


def normalize_yes_no(df: pd.DataFrame, columns: Iterable[str] = None) -> pd.DataFrame:
	"""Normalize columns containing yes/no-like values to 'Yes'/'No'.

	If `columns` is None, applies to all object (string-like) columns.
	"""
	out = df.copy()
	if columns is None:
		columns = [c for c, t in out.dtypes.items() if t == object]

	for col in columns:
		out[col] = out[col].apply(_map_to_yes_no)

	return out


def add_temporal_columns(df: pd.DataFrame, column: str = "Timestamp") -> pd.DataFrame:
	"""Add `year`, `month`, and `day_of_week` columns derived from a datetime column.

	Expects the `column` to be datetime dtype. Returns a new DataFrame.
	"""
	out = df.copy()
	if not pd.api.types.is_datetime64_any_dtype(out[column]):
		out[column] = pd.to_datetime(out[column], errors="coerce")

	out["year"] = out[column].dt.year
	out["month"] = out[column].dt.month
	out["day_of_week"] = out[column].dt.day_name()
	return out

