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
