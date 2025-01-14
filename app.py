import streamlit as st
import mysql.connector
import pandas as pd

# Connect to the MySQL database
def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # Database host
            user="root",  # Username
            password="Jagadish@24",  # Password
            database="data_gain"  # Database name
        )
        return connection  # Return the connection if successful
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None  # Return None if there is an error

# Fetch the list of countries based on the selected region
def fetch_countries(region):
    connection = get_connection()
    if connection is None:
        return []  # Return an empty list if no connection is available

    try:
        cursor = connection.cursor()
        # Query to get countries from the selected region
        cursor.execute("SELECT TRIM(country), TRIM(region) FROM sample_world WHERE TRIM(region) = %s;", (region,))
        countries = cursor.fetchall()  # Fetch all the countries for the selected region
        return countries
    except mysql.connector.Error as err:
        st.error(f"Error fetching countries: {err}")
        return []  # Return an empty list if there is an error
    finally:
        cursor.close()
        connection.close()  # Close the connection after use

# Streamlit page layout and functionality
st.title("View Countries by Region")

# Fetch the list of regions from the database
connection = get_connection()
if connection:
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT TRIM(region) FROM sample_world;")  # Get unique regions
    regions = [region[0] for region in cursor.fetchall()]  # Store regions in a list
    cursor.close()
    connection.close()

# If regions are available, show them in a dropdown
if regions:
    selected_region = st.selectbox("Type to search", ["Type to search"] + regions)

    if selected_region != "Type to search":
        st.subheader(f"Countries in {selected_region}:")
        countries = fetch_countries(selected_region)

        if countries:
            # Display the list of countries for the selected region
            for country, region in countries:
                st.write(f"- {country} ({region})")

            # Convert the countries and region to CSV format for download
            csv_data = pd.DataFrame(countries, columns=["Country", "Region"]).to_csv(index=False)

            # Add a button to download the CSV
            st.download_button(
                label="Export",  # Button label
                data=csv_data,  # Data to download
                file_name=f"{selected_region}.csv",  # CSV file name
                mime="text/csv"  # MIME type
            )
        else:
            st.warning("No countries found for the selected region.")
else:
    st.warning("No regions found in the database.")
