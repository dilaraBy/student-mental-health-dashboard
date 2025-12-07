# Tests for data processing module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from services import data_processing as dp


def test_load_data_file_not_found():
    """Test that load_data raises FileNotFoundError for missing file."""
    try:
        dp.load_data("/nonexistent/path/file.csv")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "not found" in str(e)


def test_load_data_valid_csv(tmp_path):
    """Test loading a valid CSV file."""
    # Create a temporary CSV file
    test_file = tmp_path / "test_data.csv"
    test_df = pd.DataFrame({
        "Name": ["Alice", "Bob"],
        "Age": [25, 30],
        "Timestamp": ["2023-01-01 10:00", "2023-01-02 11:00"]
    })
    test_df.to_csv(test_file, index=False)

    # Load the file
    loaded_df = dp.load_data(str(test_file))

    # Verify data
    assert len(loaded_df) == 2
    assert list(loaded_df.columns) == ["Name", "Age", "Timestamp"]
    assert loaded_df["Name"].tolist() == ["Alice", "Bob"]
    assert loaded_df["Age"].tolist() == [25, 30]

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

def test_fill_missing_values_and_drop_depression():
    df = pd.DataFrame({
        "Gender": ["Male", None, "Female"],
        "Division": [None, "Dhaka", None],
        "Do you have Depression?": ["Yes", None, "No"]
    })

    cleaned = dp.fill_missing_values(df)

    # Row 1 should be dropped because depression is missing
    assert len(cleaned) == 2

    # Check remaining rows
    assert cleaned["Gender"].tolist() == ["Male", "Female"]
    assert cleaned["Division"].tolist() == ["Unknown", "Unknown"]
    assert cleaned["Do you have Depression?"].tolist() == ["Yes", "No"]

def test_remove_duplicates_keeps_first():
    df = pd.DataFrame(
        {
            "timestamp": ["2023-01-01 10:00", "2023-01-01 10:00", "2023-01-02 11:00"],
            "depression": ["Yes", "Yes", "No"],
        }
    )

    cleaned = dp.remove_duplicates(df)

    # Row 0 and 1 are duplicates → only one of them should remain
    assert len(cleaned) == 2

    # First row should be preserved
    assert cleaned.iloc[0]["timestamp"] == "2023-01-01 10:00"
    assert cleaned.iloc[0]["depression"] == "Yes"

def test_standardize_column_names_renames_known_columns():
    df = pd.DataFrame(
        {
            "Do you have Depression?": ["Yes", "No"],
            "Choose your gender": ["Male", "Female"],
            "Some Other Column": [1, 2],
        }
    )

    out = dp.standardize_column_names(df)

    # New names should be present
    assert "depression" in out.columns
    assert "gender" in out.columns
    # Unmapped column should stay as is
    assert "Some Other Column" in out.columns

    # Old names should be gone
    assert "Do you have Depression?" not in out.columns
    assert "Choose your gender" not in out.columns

def test_clean_data_pipeline_end_to_end(tmp_path):
    # Create a small raw dataset resembling the real one
    raw_df = pd.DataFrame(
        {
            "Timestamp": [
                "2023-01-01 10:00",
                "2023-01-01 10:00",  # duplicate of row 0
                "2023-01-02 11:00",
            ],
            "Do you have Depression?": ["yes", "yes", None],  # last row missing
            "Choose your gender": ["Male", "Male", "Female"],
            "Division": [None, None, "Dhaka"],
        }
    )

    csv_path = tmp_path / "raw.csv"
    raw_df.to_csv(csv_path, index=False)

    cleaned = dp.clean_data(str(csv_path))

    # 1) Duplicates: rows 0 and 1 are identical → one should be removed
    # 2) Row with missing depression (row 2) should be dropped
    # → only ONE row left
    assert len(cleaned) == 1

    # 3) Column names should be standardized
    expected_cols = {"timestamp", "depression", "gender", "division"}
    assert expected_cols.issubset(set(cleaned.columns))

    # 4) Timestamp should be converted to datetime
    assert pd.api.types.is_datetime64_any_dtype(cleaned["timestamp"])

    # 5) Yes/No normalized and depression missing rows dropped
    assert cleaned["depression"].tolist() == ["Yes"]

    # 6) Division was None → should be filled with "Unknown"
    assert cleaned["division"].iloc[0] == "Unknown"

    # 7) Temporal columns added
    for col in ["year", "month", "day_of_week"]:
        assert col in cleaned.columns


