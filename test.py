import streamlit as st
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
import os
load_dotenv()

# Database connection
def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 4121)),

        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root_password"),
        database=os.getenv("DB_NAME", "HostelManagement"),
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'  # Replace with your database name
    )

# Function to get table columns for the search
def get_columns(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name};")
    columns = cursor.fetchall()
    conn.close()
    return [column[0] for column in columns]

# Function to search in a table by a selected column
def search_data(table_name, column, search_value):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM {table_name} WHERE {column} LIKE %s"
    cursor.execute(query, (f"%{search_value}%",))
    results = cursor.fetchall()
    conn.close()
    return pd.DataFrame(results)

# Function to display search UI
def display_search_ui():
    st.title("Hostel Management Search")

    # Select table to search
    table_option = st.selectbox("Select Table", ["STUDENT", "ROOM", "FEE", "EMPLOYEE", "HOSTEL_SERVICE", "HOSTEL", "ROOM_OCCUPANCY"])

    # Get columns of selected table
    columns = get_columns(table_option)

    # Select column to search
    column_option = st.selectbox("Select Column", columns)

    # Input for search value
    search_value = st.text_input(f"Enter {column_option} to search:")

    if st.button("Search"):
        if search_value:
            # Fetch and display search results
            results = search_data(table_option, column_option, search_value)
            if results.empty:
                st.write(f"No results found for {search_value} in column {column_option}.")
            else:
                st.write(f"Search Results for {search_value} in {table_option} ({column_option}):")
                st.dataframe(results)
        else:
            st.warning("Please enter a search term.")

# Run the search UI
display_search_ui()
