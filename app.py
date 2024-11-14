# Import necessary libraries
import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
from streamlit_folium import st_folium
import re

# Load the dataset
file_path = 'Electric_Vehicle_Population_Data.csv'
ev_data = pd.read_csv(file_path)

# Extract coordinates from the 'Vehicle Location' column
def extract_coordinates(location):
    match = re.search(r"POINT \(([-\d.]+) ([-\d.]+)\)", str(location))
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

# Apply function to get separate longitude and latitude columns
ev_data['Longitude'], ev_data['Latitude'] = zip(*ev_data['Vehicle Location'].map(extract_coordinates))
ev_data = ev_data.dropna(subset=['Longitude', 'Latitude'])

# Streamlit app title
st.title("EV Charging Station Location Analysis")

# Filters
city_options = ev_data['City'].dropna().unique()
city = st.selectbox("Select a City", ["All"] + list(city_options))
postal_code_options = ev_data['Postal Code'].dropna().unique()
postal_code = st.selectbox("Select a Postal Code", ["All"] + [str(code) for code in postal_code_options])

# Determine the filtered data and x-axis label
if city != "All" and postal_code == "All":
    filtered_data = ev_data[ev_data['City'] == city]
    x_axis = 'Postal Code'
elif city != "All" and postal_code != "All":
    filtered_data = ev_data[(ev_data['City'] == city) & (ev_data['Postal Code'] == float(postal_code))]
    x_axis = '2020 Census Tract'
else:
    filtered_data = ev_data
    x_axis = 'City'

# Bar chart for EV concentration based on the selection
ev_counts = filtered_data[x_axis].value_counts().head(10)
plt.figure(figsize=(10, 5))
ev_counts.plot(kind='bar', color='skyblue')
plt.title(f"Top 10 {x_axis}s with Highest Concentration of EVs")
plt.xlabel(x_axis)
plt.ylabel("Number of EVs")
plt.xticks(rotation=45)
st.pyplot(plt)

# Heatmap based on the selection
st.subheader(f"Heatmap of EV Locations in Selected {x_axis}")
map_center = [filtered_data['Latitude'].mean(), filtered_data['Longitude'].mean()]
ev_map = folium.Map(location=map_center, zoom_start=11)

heat_data = filtered_data[['Latitude', 'Longitude']].values.tolist()
HeatMap(heat_data, radius=10, blur=15, max_zoom=13).add_to(ev_map)

# Display map in Streamlit
st_data = st_folium(ev_map, width=700, height=500)
