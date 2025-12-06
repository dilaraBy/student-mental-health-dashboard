# Student Mental Health Dashboard

A comprehensive dashboard for analyzing student mental health data.

## Project Structure

```
student_mental_health_dashboard/
│
├── app/
│   ├── __init__.py
│   └── dashboard.py            # Streamlit UI
│
├── services/
│   ├── __init__.py
│   ├── data_processing.py      # cleaning, preprocessing
│   ├── analysis.py             # prevalence, trends, group comp
│   └── visualization.py        # plotting functions
│
├── db/
│   ├── __init__.py
│   └── repository.py           # StudentMentalHealthRepository
│
├── utils/
│   ├── __init__.py
│   ├── config.py               # paths, constants, YES/NO mapping
│   └── logger.py               # get_logger()
│
├── tests/
│   ├── __init__.py
│   ├── test_data_processing.py
│   ├── test_analysis.py
│   └── test_repository.py
│
├── data/
│   ├── raw/
│   │   └── bangladesh_mental_health.csv
│   └── processed/
│
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit dashboard:
```bash
streamlit run app/dashboard.py
```

## Testing

Run tests using pytest:
```bash
pytest tests/
```
