import streamlit as st
from ui_helpers import display_data,displayhtml_data
from data_management import load_data, load_employee_names
import pandas as pd
import streamlit as st
import pandas as pd
import os
from data_management import employee_csv  # ensure this variable is correctly imported

def custom_table_style():
    table_style = """
    <style>
    thead tr th {
        background-color: #f0f0f0;
        color: black;
        font-size: 22pt;
    }
    tbody tr td {
        color: black;
        font-size: 20pt;
    }
    </style>
    """
    st.markdown(table_style, unsafe_allow_html=True)

def load_employee_details():
    if os.path.exists(employee_csv):
        return pd.read_csv(employee_csv)
    else:
        return pd.DataFrame(columns=["Name", "Mobile No", "DOJ"])

def save_employee_details(data):
    data.to_csv(employee_csv, index=False,encoding="utf-8")

def display_employee_details():
    st.title("Employee Details")
    data = load_employee_details()
    if data.empty:
        st.error("No data found. Please check if the CSV file exists and is not empty.")
        return

    # Create a form for editing details
    with st.form("employee_details_form"):
        # Create a row for each employee
        for i in range(len(data)):
            cols = st.columns(3)  # Create three columns for Name, Mobile No, and DOJ
            with cols[0]:  # Name column
                data.at[i, 'Name'] = st.text_input("Name", value=data.at[i, 'Name'], key=f"name_{i}")
            with cols[1]:  # Mobile No column
                data.at[i, 'Mobile No'] = st.number_input("Mobile No", value=int(data.at[i, 'Mobile No']), key=f"mobile_{i}", format="%d")
            with cols[2]:  # DOJ column
                data.at[i, 'DOJ'] = st.date_input("DOJ", pd.to_datetime(data.at[i, 'DOJ']), key=f"doj_{i}")

        # Submit button to save changes
        submitted = st.form_submit_button("Save Changes")
        if submitted:
            save_employee_details(data)
            st.success("Employee details updated successfully!")

    data['Mobile No'] = data['Mobile No'].astype(str)
    # Display updated data
    displayhtml_data(data,"Employee Details")

def employee_details_tab():
    display_employee_details()
    