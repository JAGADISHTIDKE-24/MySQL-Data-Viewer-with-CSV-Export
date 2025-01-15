import streamlit as st
import mysql.connector
import pandas as pd

# Function to connect to the MySQL database
def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",  # MySQL host
            user="root",  # MySQL username
            password="Jagadish@24",  # MySQL password
            database="data_gain"  # Updated database name
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None

# Function to check if a table exists in the database
def check_table_exists(table_name):
    connection = get_connection()  # here we create a connection to the database
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        return result is not None
    finally:
        cursor.close()
        connection.close()


def insert_unique_data(df, table_name):
    connection = get_connection()
    if connection is None:
        return "Failed to connect to the database."

    try:
        cursor = connection.cursor()
        for _, row in df.iterrows():
            
            query = f"SELECT * FROM {table_name} WHERE "
            conditions = " AND ".join([f"`{col}` = %s" for col in df.columns])
            query += conditions
            cursor.execute(query, tuple(row))
            result = cursor.fetchone()


            if result is None:
                insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(df.columns))})"
                cursor.execute(insert_query, tuple(row))
        connection.commit()
        return "Data uploaded successfully!"
    except mysql.connector.Error as err:
        return f"Error inserting data: {err}"
    finally:
        cursor.close()
        connection.close()


def create_table_from_csv(file, table_name):
    try:
        # Sanitize table name by replacing spaces with underscores
        sanitized_table_name = table_name.replace(" ", "_")

        # Read the CSV file
        df = pd.read_csv(file)

        # Validate table name
        if not sanitized_table_name:
            return "Table name cannot be empty."


        columns = []
        for col in df.columns:
            if pd.api.types.is_integer_dtype(df[col]):
                columns.append(f"`{col}` BIGINT")
            elif pd.api.types.is_float_dtype(df[col]):
                columns.append(f"`{col}` DOUBLE")
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                columns.append(f"`{col}` DATETIME")
            else:
                max_length = df[col].astype(str).str.len().max()
                if max_length > 255:
                    columns.append(f"`{col}` TEXT") 
                else:
                    columns.append(f"`{col}` VARCHAR({max(255, int(max_length))})")

        create_table_query = f"CREATE TABLE IF NOT EXISTS {sanitized_table_name} ({', '.join(columns)});"

        # Connect to the database
        connection = get_connection()
        if connection is None:
            return "Failed to connect to the database."

        cursor = connection.cursor()

        # Check if the table exists
        if not check_table_exists(sanitized_table_name):
           
            cursor.execute(create_table_query)
            connection.commit()

       
        result = insert_unique_data(df, sanitized_table_name)
        return result

    except mysql.connector.Error as err:
        return f"Error creating table or uploading data: {err}"
    except Exception as e:
        return f"Error processing CSV file: {e}"

# Streamlit App
st.title("UPLOAD CSV")

# Upload CSV Tab
st.header("Upload CSV File")
uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Use the sanitized CSV file name as the table name
    table_name = uploaded_file.name.replace(".csv", "")  # Remove ".csv" extension
    if st.button("Upload CSV File"):
        result = create_table_from_csv(uploaded_file, table_name)
        st.text(result)  # Display the result
