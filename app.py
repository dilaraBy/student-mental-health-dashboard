# Student Mental Health Dashboard - Main App
import streamlit as st

# Configure the Streamlit page
st.set_page_config(
    page_title="Welcome Page - Student Mental Health Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main page content
st.title("🧠 Welcome Page - Student Mental Health Dashboard")

st.markdown("""
### Welcome to the Student Mental Health Analytics Platform

The aim of this project is to design and implement a Python-based data insights dashboard that allows public health and university stakeholders to explore, filter, and analyse student mental health data from a Bangladeshi university context. The system will provide interactive summaries, visualisations, and basic database operations, following software engineering best practices such as layered architecture, TDD, and FURPS-based requirements analysis.

#### Available Pages:
- **📊 Overview**: Key metrics and summary statistics
- **📋 Data View & CRUD**: Raw data exploration and management 
- **🔍 Detailed Analysis**: In-depth statistical analysis and trends
- **⚖️ Comparison Explorer**: Compare different demographic groups

#### How to Navigate:
Use the sidebar on the left to navigate between different pages. Each page offers specialized tools for exploring and understanding the mental health data from different perspectives.

---
*Select a page from the sidebar to get started with your analysis.*
""")

# Sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("### 📖 About")
st.sidebar.markdown("This multi-page dashboard enables comprehensive analysis of student mental health survey data.")
st.sidebar.markdown("**Version**: 1.0")
st.sidebar.markdown("**Last Updated**: December 2025")