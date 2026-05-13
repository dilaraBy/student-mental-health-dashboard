# Detailed Analysis Page - In-depth Statistical Analysis and Trends
import streamlit as st
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from db.repository import StudentMentalHealthRepository
from services.analysis import (
    depression_vs_cgpa,
    depression_rate_by_year,
    depression_rate_by_financial_stress,
    depression_rate_by_family_history,
    depression_rate_by_condition,
    build_correlation_matrix
)
from services.detailed_analysis import (
    plot_cgpa_boxplot,
    plot_depression_by_year_bar,
    plot_depression_by_financial_stress_bar,
    plot_depression_by_family_history_bar,
    plot_depression_by_condition_grouped_bar,
    plot_correlation_heatmap
)
from utils.config import DB_PATH
from utils.download_utils import create_download_section

# Page configuration  
st.title("🔍 Detailed Analysis")

st.write("Comprehensive statistical analysis exploring relationships between depression and various factors affecting student mental health.")

# Download section - will be populated after figures are created
download_placeholder = st.empty()

# Initialize data repository and load data
try:
    data_repo = StudentMentalHealthRepository(str(DB_PATH))
    df = data_repo.get_all_data()
    
    if df.empty:
        st.error("No data available for analysis.")
        st.stop()
    
    st.success(f"Loaded {len(df)} student records for analysis")
    
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Analysis Layout
# Collect figures for download
figures = []

st.markdown("---")

# CGPA vs Depression Analysis
st.subheader("📚 Academic Performance & Depression")
st.write("Analyzing the relationship between CGPA performance and depression levels")

try:
    # Get analysis data
    cgpa_analysis = depression_vs_cgpa(df)
    
    # Create and display boxplot
    fig = plot_cgpa_boxplot(cgpa_analysis)
    st.pyplot(fig)
    figures.append(fig)
    

        
except Exception as e:
    st.error(f"Error in CGPA analysis: {str(e)}")

st.markdown("---")

# Year of Study Analysis
st.subheader("🎓 Depression by Academic Year")
st.write("Depression prevalence across different years of study")

try:
    # Get analysis data
    year_analysis = depression_rate_by_year(df)
    
    # Create and display bar chart
    fig = plot_depression_by_year_bar(year_analysis)
    st.pyplot(fig)
    figures.append(fig)
    

        
except Exception as e:
    st.error(f"Error in year analysis: {str(e)}")

st.markdown("---")

# Financial Stress Analysis
st.subheader("💰 Financial Stress Impact")
st.write("How financial stress affects depression rates among students")

try:
    # Get analysis data
    financial_analysis = depression_rate_by_financial_stress(df)
    
    # Create and display bar chart
    fig = plot_depression_by_financial_stress_bar(financial_analysis)
    st.pyplot(fig)
    figures.append(fig)
    

        
except Exception as e:
    st.error(f"Error in financial stress analysis: {str(e)}")

st.markdown("---")

# Family History Analysis
st.subheader("👨‍👩‍👧‍👦 Family History of Mental Illness")
st.write("Impact of family mental health history on student depression")

try:
    # Get analysis data
    family_analysis = depression_rate_by_family_history(df)
    
    # Create and display bar chart
    fig = plot_depression_by_family_history_bar(family_analysis)
    st.pyplot(fig)
    figures.append(fig)
    

        
except Exception as e:
    st.error(f"Error in family history analysis: {str(e)}")

st.markdown("---")

# Comorbid Conditions Analysis
st.subheader("🧠 Depression & Other Mental Health Conditions")
st.write("Relationship between depression and anxiety/panic attacks")

try:
    # Get analysis data for anxiety and panic attacks
    anxiety_analysis = depression_rate_by_condition(df, 'anxiety')
    panic_analysis = depression_rate_by_condition(df, 'panic_attack')
    
    # Create separate charts in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Anxiety & Depression**")
        fig_anxiety = plot_depression_by_condition_grouped_bar(anxiety_analysis, 'Anxiety')
        st.pyplot(fig_anxiety)
        figures.append(fig_anxiety)
        

    
    with col2:
        st.write("**Panic Attacks & Depression**")
        fig_panic = plot_depression_by_condition_grouped_bar(panic_analysis, 'Panic Attack')
        st.pyplot(fig_panic)
        figures.append(fig_panic)
        

        
except Exception as e:
    st.error(f"Error in conditions analysis: {str(e)}")

st.markdown("---")

# Correlation Matrix Analysis
st.subheader("🔗 Correlation Analysis")
st.write("Exploring relationships between depression and all key factors")

try:
    # Build correlation matrix
    correlation_matrix = build_correlation_matrix(df)
    
    # Create and display heatmap
    fig = plot_correlation_heatmap(correlation_matrix)
    st.pyplot(fig)
    figures.append(fig)
    

        
    # Key insights
    with st.expander("🔍 Key Correlations"):
        depression_corr = correlation_matrix['depression'].drop('depression').abs().sort_values(ascending=False)
        st.write("**Strongest correlations with depression:**")
        for var, corr in depression_corr.head().items():
            direction = "positive" if correlation_matrix['depression'][var] > 0 else "negative"
            st.write(f"• **{var}**: {corr:.3f} ({direction})")
            
except Exception as e:
    st.error(f"Error in correlation analysis: {str(e)}")

st.markdown("---")

# Populate download section at the top
with download_placeholder.container():
    create_download_section("detailed_analysis", figures)

# Analysis Summary
st.subheader("📝 Analysis Summary")
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Data Coverage:**")
        st.write(f"• Total students analyzed: {len(df)}")
        try:
            dep_rate = (df['depression'] == 'Yes').sum() / len(df) * 100
            st.write(f"• Overall depression rate: {dep_rate:.1f}%")
        except:
            st.write("• Depression rate calculation unavailable")
    
    with col2:
        st.write("**Analysis Components:**")
        st.write("• CGPA vs Depression relationship")
        st.write("• Year of study patterns")
        st.write("• Financial stress impact")
        st.write("• Family history influence")
        st.write("• Comorbid conditions analysis")
        st.write("• Comprehensive correlation matrix")