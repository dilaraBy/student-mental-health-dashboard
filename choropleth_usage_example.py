# Usage snippet for Bangladesh choropleth map in Streamlit

```python
import streamlit as st
import pandas as pd
from services.visualization import plot_depression_choropleth

# Example usage in a Streamlit page
def add_choropleth_map_to_page(df):
    """
    Add Bangladesh choropleth map to a Streamlit page.
    
    Args:
        df: DataFrame with 'division' and 'depression' columns
    """
    st.write("**Depression Rates by Division in Bangladesh**")
    
    try:
        # Create the choropleth map
        choropleth_fig = plot_depression_choropleth(df)
        
        if choropleth_fig is not None:
            # Display the map using Plotly
            st.plotly_chart(choropleth_fig, width="stretch")
            
            # Optional: Add statistics below the map
            st.write("*Interactive map showing depression rates across Bangladesh divisions.*")
            
        else:
            st.info("Interactive choropleth map could not be created. This may be due to missing geographic data or technical limitations.")
            
    except Exception as e:
        st.warning(f"Could not create geographic map: {e}")
        st.info("Geographic visualization requires valid Bangladesh division data.")


# Sample data structure expected by the function:
sample_data = pd.DataFrame({
    'division': ['Dhaka', 'Chittagong', 'Sylhet', 'Barisal', 'Khulna', 'Rajshahi', 'Rangpur', 'Mymensingh'],
    'depression': ['Yes', 'No', 'Yes', 'Yes', 'No', 'Yes', 'No', 'Yes']
})

# Call the function
add_choropleth_map_to_page(sample_data)
```

## Key Features:

1. **Automatic GeoJSON loading**: Loads Bangladesh divisions from `data/raw/bangladesh_geojson_adm1_8_divisions_bibhags.json`
2. **Division name mapping**: Uses `properties.ADM1_EN` from GeoJSON to match with data divisions
3. **Depression rate calculation**: Automatically calculates percentage of students with depression per division
4. **Interactive visualization**: Uses Plotly Express choropleth_map for interactive geographic visualization
5. **Graceful error handling**: Falls back to simple visualizations or informative messages if map creation fails
6. **Clean separation**: Helper functions for loading GeoJSON and calculating rates are private to maintain clean API

## Requirements:

- Input DataFrame must have 'division' and 'depression' columns
- Division names should match those in the GeoJSON file (Dhaka, Chittagong, Sylhet, Barisal, Khulna, Rajshahi, Rangpur, Mymensingh)
- GeoJSON file must be present at the configured path
- Plotly must be installed and functional