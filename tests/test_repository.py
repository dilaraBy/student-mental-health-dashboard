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
