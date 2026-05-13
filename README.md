# Student Mental Health Dashboard

A comprehensive Python-based data analytics platform for exploring and analyzing student mental health data from Bangladeshi universities. This system provides interactive visualizations, statistical analysis, and database management capabilities to help public health researchers and university stakeholders understand mental health patterns among students.

## Project Overview

The aim of this project is to design and implement a Python-based data insights dashboard that allows public health and university stakeholders to explore, filter, and analyze student mental health data from a Bangladeshi university context. The system provides interactive summaries, visualizations, and basic database operations, following software engineering best practices such as layered architecture, Test-Driven Development (TDD), and FURPS-based requirements analysis.

### Key Features

- **Interactive Dashboard**: Multi-page Streamlit application with intuitive navigation
- **Comprehensive Analysis**: Statistical analysis including prevalence rates, correlations, and demographic breakdowns
- **Geographic Visualization**: Interactive choropleth maps showing regional mental health patterns across Bangladesh divisions
- **Data Management**: Full CRUD operations with data validation and CSV import/export capabilities
- **PDF Export**: Download analysis reports as PDF files for sharing and documentation
- **Real-time Filtering**: Dynamic data filtering by demographics, academic factors, and mental health conditions
- **Data Quality Monitoring**: Automated data cleaning pipeline with quality metrics and validation

## Technical Architecture

### Layered Architecture

The project follows a clean layered architecture pattern:

- **Presentation Layer**: Streamlit pages (`pages/`)
- **Service Layer**: Business logic and analysis services (`services/`)
- **Data Access Layer**: Repository pattern for database operations (`db/`)
- **Utility Layer**: Configuration, logging, and helper functions (`utils/`)

### Project Structure

```
student_mental_health_dashboard/
├── app.py                      # Main application entry point
├── pages/                      # Streamlit pages
│   ├── 01_Overview.py          # Key metrics and summary stats
│   ├── 02_Data_View_and_CRUD.py # Data management and CRUD operations
│   ├── 03_Detailed_Analysis.py # In-depth statistical analysis
│   └── 04_Comparison_Explorer.py # Demographic group comparisons
├── services/                   # Business logic layer
│   ├── overview_analysis.py    # KPI computation and summary stats
│   ├── detailed_analysis.py    # Advanced statistical analysis
│   ├── comparison_analysis.py  # Comparative analysis between groups
│   ├── data_processing.py      # Data cleaning and preprocessing
│   ├── data_management.py      # CRUD operations and data validation
│   ├── geographic_analysis.py  # Geographic analysis for Bangladesh
│   ├── visualization.py        # Chart generation functions
│   └── visualization_detailed.py # Advanced visualization components
├── db/                         # Data access layer
│   └── repository.py           # SQLite database operations
├── utils/                      # Utility layer
│   ├── config.py               # Configuration and constants
│   ├── logger.py               # Logging configuration
│   └── download_utils.py       # PDF generation utilities
├── tests/                      # Test suite (191 test cases)
│   ├── test_*.py               # Comprehensive test coverage
│   └── pytest.ini             # Test configuration
├── data/                       # Data storage
│   ├── raw/                    # Original data files
│   └── processed/              # Cleaned data files
├── logs/                       # Application logs
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning the repository)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/dilaraBy/student-mental-health-dashboard.git
   cd student-mental-health-dashboard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Bootstrap the data and database**
   Downloads the Bangladesh GeoJSON (~14 MB) and initialises the SQLite DB from the bundled CSV.
   ```bash
   python -m scripts.setup_data
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**
   - Open your web browser to `http://localhost:8501`
   - Use the sidebar navigation to explore different pages

## Usage Guide

### Navigation

The dashboard consists of four main pages accessible via the sidebar:

1. **Welcome Page**: Project overview and navigation guide
2. **Overview**: Key performance indicators and summary statistics
3. **Data View & CRUD**: Raw data exploration and management operations
4. **Detailed Analysis**: In-depth statistical analysis and correlations
5. **Comparison Explorer**: Interactive comparison between demographic groups

### Core Functionality

#### Data Analysis Features
- **Prevalence Calculations**: Depression, anxiety, and panic attack rates
- **Demographic Analysis**: Breakdowns by gender, division, year of study, and academic course
- **Correlation Analysis**: Statistical relationships between variables
- **Trend Analysis**: Temporal patterns in mental health data
- **Risk Profiling**: Multi-dimensional risk assessment

#### Data Management Features
- **Data Import**: CSV file upload with validation
- **CRUD Operations**: Create, read, update, and delete records
- **Data Quality Monitoring**: Completeness metrics and validation reports
- **Export Capabilities**: CSV and PDF export options
- **Filter and Search**: Dynamic data filtering with multiple criteria

#### Visualization Features
- **Interactive Charts**: Plotly-based interactive visualizations
- **Geographic Maps**: Choropleth maps for Bangladesh divisions
- **Statistical Plots**: Box plots, correlation heatmaps, and trend lines
- **PDF Reports**: Generate downloadable analysis reports

## Development and Testing

### Software Engineering Practices

- **Test-Driven Development (TDD)**: Comprehensive test suite with 191 test cases
- **FURPS Requirements**: Functionality, Usability, Reliability, Performance, and Supportability
- **Clean Architecture**: Separation of concerns with layered design
- **Code Quality**: Automated linting, type hints, and documentation
- **Version Control**: Git-based version control with structured commits

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test modules
python -m pytest tests/test_overview_analysis.py -v

# Run tests with coverage
python -m pytest tests/ --cov=services --cov=db
```

### Test Coverage

The project maintains comprehensive test coverage across:
- Data processing and cleaning pipelines
- Statistical analysis functions
- Visualization components
- Database operations
- CRUD functionality
- Data validation logic

## Data Processing Pipeline

### Data Cleaning Features

1. **Missing Value Handling**
   - Target variable validation (drops rows with missing depression values)
   - Smart imputation strategies (mode for categorical, median for numerical)
   - High-cardinality column handling

2. **Data Validation**
   - Timestamp validation and conversion
   - Academic data validation (year of study, CGPA)
   - Categorical variable normalization

3. **Quality Monitoring**
   - Completeness metrics calculation
   - Data quality scoring
   - Automated cleaning reports

## Technical Dependencies

### Core Technologies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **SQLite**: Lightweight database engine
- **Plotly**: Interactive visualization library
- **Matplotlib/Seaborn**: Statistical plotting
- **Pytest**: Testing framework

### Analysis Libraries
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing and statistics
- **GeoPandas**: Geographic data processing (for Bangladesh maps)

## Configuration

### Environment Variables
The application uses configuration files in `utils/config.py` for:
- Database paths and connection settings
- Data file locations
- Logging configuration
- Default values and constants

### Database Configuration
- **Database**: SQLite (student_mental_health.db)
- **Table Structure**: Normalized schema with proper indexing
- **Data Types**: Optimized column types for efficient storage

## Logging and Monitoring

- **Structured Logging**: Comprehensive logging with different levels
- **Error Tracking**: Detailed error capture and reporting
- **Performance Monitoring**: Database query optimization
- **User Activity**: Interaction tracking for usage analytics


---

**Version**: 1.0  
**Last Updated**: December 2025  
**Python Version**: 3.8+  
**Framework**: Streamlit 1.28+
