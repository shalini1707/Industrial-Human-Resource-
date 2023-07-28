import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster



# Function to load data into a Pandas DataFrame
def load_data(file_path):
    data_frame = pd.read_csv(file_path)
    return data_frame

# Function to preprocess the data
def preprocess_data(data_frame):
    # Split the 'IndiaStates' column using a regular expression to extract 'Type' and 'Name'
    data_frame[['Type', 'Name']] = data_frame['IndiaStates'].str.extract(r'(.+?)\s+(.+)')

    # Sort the DataFrame by 'Type' and 'Name' to display states and districts in alphabetical order
    data_frame.sort_values(by=['Type', 'Name'], inplace=True)
    return data_frame

# Function to display selected state and district data
def display_data(data_frame, selected_state, selected_district):
    # Filter data based on user selections
    state_data = data_frame[(data_frame['Type'] == 'STATE') & (data_frame['Name'] == selected_state)]
    district_data = data_frame[(data_frame['Type'] == 'District') & (data_frame['Name'] == selected_district)]

    # Display the filtered data for the selected state, district, and NIC Name
    st.write(f"Showing data for {selected_state} - {selected_district}")

    # Total number of state workers
    total_state_workers = state_data['MainWorkersTotalPersons'].sum()
    st.write(f"Total number of state workers: {total_state_workers}")

    # Total number of district workers
    total_district_workers = district_data['MainWorkersTotalPersons'].sum()
    st.write(f"Total number of district workers: {total_district_workers}")

    # Data summary
    st.subheader("Data Summary")
    st.write(data_frame.describe())
    # Plotting data for Rural, Main, and Urban workers
    rural_cols = ['MainWorkersRuralPersons', 'MainWorkersRuralMales', 'MainWorkersRuralFemales']
    urban_cols = ['MainWorkersUrbanPersons', 'MainWorkersUrbanMales', 'MainWorkersUrbanFemales']

    rural_data = state_data[rural_cols].sum().values
    main_data = state_data[['MainWorkersTotalPersons', 'MainWorkersTotalMales', 'MainWorkersTotalFemales']].iloc[0].values
    urban_data = state_data[urban_cols].sum().values

    # Plotting Rural, Main, and Urban data
    fig, ax = plt.subplots(figsize=(10, 6))
    x_labels = ['Rural', 'Main', 'Urban']
    ax.bar(x_labels, rural_data, color='#1f77b4', label='Rural')
    ax.bar(x_labels, main_data, bottom=rural_data, color='#ff7f0e', label='Main')
    ax.bar(x_labels, urban_data, bottom=rural_data + main_data, color='#2ca02c', label='Urban')
    ax.set_title(f"{selected_state} - {selected_district} - Workers Distribution")
    ax.legend()
    st.pyplot(fig)

    # Plotting data for Marginal workers (using pie chart)
    marginal_cols_rural = ['MarginalWorkersRuralPersons', 'MarginalWorkersRuralMales', 'MarginalWorkersRuralFemales']
    marginal_cols_urban = ['MarginalWorkersUrbanPersons', 'MarginalWorkersUrbanMales', 'MarginalWorkersUrbanFemales']

    marginal_data_rural = district_data[marginal_cols_rural].sum().values
    marginal_data_urban = district_data[marginal_cols_urban].sum().values

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(marginal_data_rural, labels=marginal_cols_rural, autopct='%1.1f%%', startangle=90, colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax.set_title(f"{selected_state} - {selected_district} - Rural Marginal Workers Distribution")
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.pie(marginal_data_urban, labels=marginal_cols_urban, autopct='%1.1f%%', startangle=90, colors=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax.set_title(f"{selected_state} - {selected_district} - Urban Marginal Workers Distribution")
    st.pyplot(fig)

def visualize_point_map(data_frame, selected_state, selected_district):
    # Get the data for the selected state and district
    state_data = data_frame[(data_frame['Type'] == 'STATE') & (data_frame['Name'] == selected_state)]
    district_data = data_frame[(data_frame['Type'] == 'District') & (data_frame['Name'] == selected_district)]

    # Create a folium map centered at Delhi, India
    folium_map = folium.Map(location=[28.6139, 77.2090], zoom_start=5)

    # Create marker cluster for the points
    marker_cluster = MarkerCluster().add_to(folium_map)

    # Plot main workers for the selected state
    for idx, row in state_data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        total_workers = row['MainWorkersTotalPersons']
        male_female_ratio = row['MaleFemaleRatio']
        popup_text = f"State: {selected_state}<br>District: {selected_district}<br>Total Workers: {total_workers}<br>Male-Female Ratio: {male_female_ratio}"
        folium.Marker([lat, lon], popup=popup_text).add_to(marker_cluster)

    # Plot main workers for the selected district
    for idx, row in district_data.iterrows():
        lat, lon = row['Latitude'], row['Longitude']
        total_workers = row['MainWorkersTotalPersons']
        male_female_ratio = row['MaleFemaleRatio']
        popup_text = f"State: {selected_state}<br>District: {selected_district}<br>Total Workers: {total_workers}<br>Male-Female Ratio: {male_female_ratio}"
        folium.Marker([lat, lon], popup=popup_text).add_to(marker_cluster)

    # Display the map using Streamlit
    folium_map.save('map.html')  # Save the map as an HTML file
    st.components.v1.html(open('map.html', 'r', encoding='utf-8').read())  # Display the map in Streamlit using the HTML component

def main():
    st.title("Industrial Human Resource Geo-Visualization")

    # Load data using the load_data function
    file_path = r'C:\Users\ADMIN\Desktop\hr\df.csv'  # Replace with the actual path to your data file
    data_frame = load_data(file_path)

    # Preprocess the data
    data_frame = preprocess_data(data_frame)

    # Get the unique states, districts, and NIC Names
    unique_states = data_frame[data_frame['Type'] == 'STATE']['Name'].unique()
    unique_districts = data_frame[data_frame['Type'] == 'District']['Name'].unique()
    unique_nic_names = data_frame['NICName'].unique()

    # Sort the unique states and districts in alphabetical order
    unique_states.sort()
    unique_districts.sort()

    # Sidebar: State, District, and NIC Name selection
    selected_state = st.sidebar.selectbox("Select State", unique_states)
    selected_district = st.sidebar.selectbox("Select District", unique_districts)
    selected_nic_name = st.sidebar.selectbox("Select NIC Name", unique_nic_names)

    # Display the selected state and district data
    display_data(data_frame, selected_state, selected_district)

    # Visualize the map
    visualize_point_map(data_frame, selected_state, selected_district)

if __name__ == "__main__":
    main()
