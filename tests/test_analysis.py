# Tests for analysis module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from services import analysis as an


def test_compute_prevalence_simple():
    df = pd.DataFrame({
        "depression": ["Yes", "No", "Yes", "Yes", "No"]
    })

    result = an.compute_prevalence(df, "depression")

    # 3 Yes, 2 No out of 5
    assert result["yes_count"] == 3
    assert result["no_count"] == 2
    assert result["total"] == 5
    assert result["yes_percentage"] == 60.0
    assert result["no_percentage"] == 40.0


def test_compute_all_prevalence_multiple_columns():
    df = pd.DataFrame({
        "depression": ["Yes", "No", "Yes"],
        "anxiety":    ["No", "No", "Yes"],
    })

    result = an.compute_all_prevalence(df, ["depression", "anxiety"])

    assert "depression" in result
    assert "anxiety" in result

    # For depression: 2 Yes, 1 No
    assert result["depression"]["yes_count"] == 2
    assert result["depression"]["no_count"] == 1

    # For anxiety: 1 Yes, 2 No
    assert result["anxiety"]["yes_count"] == 1
    assert result["anxiety"]["no_count"] == 2

def test_group_comparison_by_gender():
    df = pd.DataFrame({
        "Gender": ["Male", "Female", "Female", "Male"],
        "depression": ["Yes", "Yes", "No", "No"],
    })

    comp = an.group_comparison(df, group_by="Gender", condition="depression")

    # Expect two rows: Male and Female
    assert set(comp["Gender"]) == {"Male", "Female"}

    # For Female: 1 Yes, 1 No → 50% Yes
    female_row = comp[comp["Gender"] == "Female"].iloc[0]
    assert female_row["yes_count"] == 1
    assert female_row["total"] == 2
    assert female_row["yes_percentage"] == 50.0

    # For Male: 1 Yes, 1 No → 50% Yes
    male_row = comp[comp["Gender"] == "Male"].iloc[0]
    assert male_row["yes_count"] == 1
    assert male_row["total"] == 2
    assert male_row["yes_percentage"] == 50.0

