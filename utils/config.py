# Configuration: paths, constants, YES/NO mapping

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent  #this will point to the project root directory

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "Student_Mental_Health.csv"

DB_DIR = PROJECT_ROOT / "db"
DB_PATH = DB_DIR / "student_mental_health.db"

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Ensure dirs
DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_DIR.mkdir(exist_ok=True, parents=True)
LOG_DIR.mkdir(exist_ok=True, parents=True)

DEFAULT_GENDER = "Unknown"
DEFAULT_DIVISION = "Unknown"

YES_NO_COLUMNS = [
    "Marital Status",
    "Do you have Depression?",
    "Do you have Anxiety?",
    "Do you have Panic attack?",
    "Family History of Mental Illness",
    "Did you seek any specialist for a treatment?",
]

YES_NO_MAPPING = {
    "yes": "Yes",
    "y": "Yes",
    "true": "Yes",
    "1": "Yes",
    "no": "No",
    "n": "No",
    "false": "No",
    "0": "No",
}

