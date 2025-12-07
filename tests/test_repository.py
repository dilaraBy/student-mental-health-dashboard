import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from db.repository import StudentMentalHealthRepository


def create_test_repo(tmp_path):
    """Use a temporary on-disk SQLite file for each test."""
    db_path = tmp_path / "test.db"
    repo = StudentMentalHealthRepository(str(db_path))
    repo.init_tables()
    return repo


def test_init_tables_creates_table(tmp_path):
    repo = create_test_repo(tmp_path)
    conn = repo.get_connection()

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='survey_responses'"
    )
    result = cursor.fetchone()
    conn.close()

    assert result is not None, "survey_responses table should exist after init_tables()"


def test_insert_and_get_all_data(tmp_path):
    repo = create_test_repo(tmp_path)

    df_in = pd.DataFrame(
        [
            {
                "Timestamp": "2023-01-01 10:00",
                "Gender": "Male",
                "Division": "Dhaka",
                "Do you have Depression?": "Yes",
            },
            {
                "Timestamp": "2023-01-02 11:00",
                "Gender": "Female",
                "Division": "Chattogram",
                "Do you have Depression?": "No",
            },
        ]
    )

    repo.insert_data(df_in)
    df_out = repo.get_all_data()

    assert len(df_out) == 2
    assert set(df_out["Gender"]) == {"Male", "Female"}


def test_get_row_count(tmp_path):
    """Test row count functionality in various scenarios."""
    repo = create_test_repo(tmp_path)
    
    # Empty table
    assert repo.get_row_count() == 0
    
    # With data
    df = pd.DataFrame({
        "gender": ["Male", "Female", "Male"],
        "depression": ["Yes", "No", "Yes"]
    })
    repo.insert_data(df)
    assert repo.get_row_count() == 3
    
    # After replacement
    df2 = pd.DataFrame({
        "gender": ["Male", "Female", "Male", "Female"],
        "depression": ["Yes", "No", "Yes", "No"]
    })
    repo.insert_data(df2, if_exists="replace")
    assert repo.get_row_count() == 4


def test_get_unique_values(tmp_path):
    """Test getting unique values from different column types."""
    repo = create_test_repo(tmp_path)
    
    df = pd.DataFrame({
        "gender": ["Male", "Female", "Male", "Non-binary"],
        "age": [20.0, 25.0, 20.0, 30.0],
        "division": ["Dhaka", "Chittagong", None, "Dhaka"]
    })
    repo.insert_data(df)
    
    # Text column
    unique_genders = repo.get_unique_values("gender")
    assert len(unique_genders) == 3
    assert set(unique_genders) == {"Male", "Female", "Non-binary"}
    
    # Numeric column
    unique_ages = repo.get_unique_values("age")
    assert len(unique_ages) == 3
    assert set(unique_ages) == {20.0, 25.0, 30.0}
    
    # Column with nulls (should exclude nulls)
    unique_divisions = repo.get_unique_values("division")
    assert len(unique_divisions) == 2
    assert set(unique_divisions) == {"Dhaka", "Chittagong"}
    
    # Non-existent column
    assert repo.get_unique_values("nonexistent") == []


def test_filter_by_multiple(tmp_path):
    """Test filtering by multiple conditions."""
    repo = create_test_repo(tmp_path)
    
    df = pd.DataFrame({
        "gender": ["Male", "Female", "Male", "Female", "Male"],
        "division": ["Dhaka", "Dhaka", "Chittagong", "Dhaka", "Dhaka"],
        "depression": ["Yes", "No", "Yes", "Yes", "No"],
        "age": [20.0, 25.0, 30.0, 35.0, 40.0]
    })
    repo.insert_data(df)
    
    # Single filter
    result = repo.filter_by_multiple({"gender": "Male"})
    assert len(result) == 3
    assert all(result["gender"] == "Male")
    
    # Multiple filters (AND logic)
    result = repo.filter_by_multiple({
        "gender": "Male",
        "division": "Dhaka",
        "depression": "Yes"
    })
    assert len(result) == 1
    assert result.iloc[0]["age"] == 20.0
    
    # No matches
    result = repo.filter_by_multiple({"gender": "Male", "division": "Sylhet"})
    assert len(result) == 0
    
    # Empty filters (return all)
    result = repo.filter_by_multiple({})
    assert len(result) == 5
    
    # Numeric filters
    result = repo.filter_by_multiple({"age": 25.0})
    assert len(result) == 1
    assert result.iloc[0]["gender"] == "Female"
    
    # Non-existent column
    result = repo.filter_by_multiple({"nonexistent": "value"})
    assert len(result) == 0


def test_dashboard_utility_functions(tmp_path):
    """Test additional utility functions needed for dashboard."""
    repo = create_test_repo(tmp_path)
    
    df = pd.DataFrame({
        "gender": ["Male", "Female", "Male", "Male", "Female"],
        "age": [18.0, 20.0, 22.0, 25.0, 30.0],
        "division": ["Dhaka", "Dhaka", "Chittagong", "Dhaka", "Sylhet"],
        "university": ["University of Dhaka", "BUET", "University of Dhaka", "NSU", "BUET"]
    })
    repo.insert_data(df)
    
    # Test get_column_stats for numeric columns
    stats = repo.get_column_stats("age")
    assert stats["count"] == 5
    assert stats["min"] == 18.0
    assert stats["max"] == 30.0
    assert stats["mean"] == 23.0
    
    # Test get_value_counts for categorical columns
    counts = repo.get_value_counts("gender")
    assert counts["Male"] == 3
    assert counts["Female"] == 2
    
    counts = repo.get_value_counts("division")
    assert counts["Dhaka"] == 3
    assert counts["Chittagong"] == 1
    assert counts["Sylhet"] == 1
    
    # Test search_by_text
    results = repo.search_by_text("university", "University")
    assert len(results) == 2  # Two have "University" in name
    
    results = repo.search_by_text("university", "BUET")
    assert len(results) == 2  # Two BUET entries
