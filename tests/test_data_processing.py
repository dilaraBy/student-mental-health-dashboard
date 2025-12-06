# Tests for data processing module
import pandas as pd
from services import data_processing as dp

def test_convert_timestamps_valid_and_invalid():
    df = pd.DataFrame({"Timestamp": ["2023-01-01 10:00", "not a date"]})
    converted = dp.convert_timestamps(df)

    assert converted["Timestamp"].dtype.name.startswith("datetime64")
    # should coerce invalid to NaT
    assert converted["Timestamp"].isna().sum() == 1


def test_normalize_yes_no_columns():
    df = pd.DataFrame({
        "Do you have Depression?": ["yes", "NO", " Y ", "n"],
        "Do you have Anxiety?": ["True", "false", "1", "0"],
    })

    normalized = dp.normalize_yes_no(df)

    assert normalized["Do you have Depression?"].tolist() == ["Yes", "No", "Yes", "No"]
    assert normalized["Do you have Anxiety?"].tolist() == ["Yes", "No", "Yes", "No"]


def test_add_temporal_columns_from_timestamp():
    df = pd.DataFrame({"Timestamp": ["2023-01-01 10:00", "2023-06-15 12:00"]})
    df = dp.convert_timestamps(df)
    result = dp.add_temporal_columns(df)

    assert all(col in result.columns for col in ["year", "month", "day_of_week"])
    assert result.loc[0, "year"] == 2023
    assert result.loc[0, "month"] == 1
    assert result.loc[0, "day_of_week"] in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
