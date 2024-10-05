import streamlit as st
import pandas as pd
import hashlib
import datetime
from ui_helpers import display_text
from data_management import load_employee_names,UserDirectoryPath,credentials_path,csv_file
from data_management import load_data, save_data # Assuming save_data is a function you will define to save data back to CSV

import base64
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Updated the sync_all_csv_files function to include a unique identifier for each file

def sync_csv_to_google_sheet(csv_path, sheet_name, unique_identifier):
    # Read the CSV file
    df_local = pd.read_csv(csv_path)

    # Get existing data from Google Sheet
    df_sheet = conn.read(worksheet=sheet_name)

    # Ensure unique_identifier is in both DataFrames
    if unique_identifier not in df_local.columns or unique_identifier not in df_sheet.columns:
        raise ValueError(f"Unique identifier '{unique_identifier}' not found in both local CSV and Google Sheets data.")

    # Merge the local data with the existing sheet data based on the unique identifier
    df_merged = pd.concat([df_sheet, df_local]).drop_duplicates(subset=unique_identifier, keep='last')

    # Update the Google Sheet with the merged data
    conn.update(worksheet=sheet_name, data=df_merged)

    print(f"Successfully synced new rows from {csv_path} to Google Sheet: {sheet_name}")


# Updated sync_all_csv_files function with unique identifiers
def sync_all_csv_files():
    csv_files_and_sheets = {
        'database_collection.csv': {'sheet_name': 'Database', 'unique_identifier': 'Date'},
        'employee_salary_Advance_bankTransfer_data.csv': {'sheet_name': 'EmployeeSalaryAdvance', 'unique_identifier': 'Date'},
        'employee_salary_data.csv': {'sheet_name': 'EmployeeSalaryData', 'unique_identifier': 'Month'}
    }

    directory = os.path.join(UserDirectoryPath)  # Corrected directory path

    for csv_file, sheet_info in csv_files_and_sheets.items():
        csv_path = os.path.join(directory, csv_file)
        sheet_name = sheet_info['sheet_name']
        unique_identifier = sheet_info['unique_identifier']

        # Check if the file exists
        if os.path.isfile(csv_path):
            sync_csv_to_google_sheet(csv_path, sheet_name, unique_identifier)
        else:
            print(f"Warning: CSV file '{csv_file}' not found in '{directory}'. Skipping.")



def save_data(data):
    # Your logic to save data to CSV
    data.to_csv(csv_file, index=False)
    
    # Call sync_all_csv_files after saving data
    sync_all_csv_files()
    
    st.success("Data synchronized successfully to Google Sheets!")
    
def get_file_path(directory, filename):
    return os.path.join(directory, filename)

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.
    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)
    
    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def DownloadFiles():
    # Directory containing the CSV files
    directory = UserDirectoryPath
    
    # List all CSV files in the directory
    files = [file for file in os.listdir(directory) if file.endswith('.csv')]
    
    # Create a select box to choose a file
    file_to_download = st.selectbox('Select a CSV file to download:', files)
    
    # Create a button to download the selected file
    if st.button('Sync CSV file'):
        sync_all_csv_files()
        file_path = get_file_path(directory, file_to_download)
        df = pd.read_csv(file_path)
        tmp_download_link = download_link(df, file_to_download, 'Click here to download your CSV!')
        st.markdown(tmp_download_link, unsafe_allow_html=True)

def display_data(data):
    def highlight_difference(val):
        color = 'red' if val > 0 else ('green' if val < 0 else 'none')
        return f'background-color: {color}; color: black;'

    styled_data = data.style.applymap(highlight_difference, subset=['Cash Difference'])
    html = styled_data.to_html(escape=False)
    st.write(html, unsafe_allow_html=True)

def delete_row(data, index):
    """ Removes a row from the dataframe based on the given index. """
    if index in data.index:
        return data.drop(index)
    else:
        st.error("Row index not found in the database.")
        return data
    
def display_last_entry(data,index, employees):
    """
    Display the most recent entry of the dataset in a two-column formatted table.
    
    Args:
        data (DataFrame): The dataframe containing the data.
        employees (list): A list of employee names.
        
    Returns:
        None
    """
    if not data.empty:
        # Get the first row of the DataFrame (most recent entry)
        
        numeric_cols = [col for col in data.columns if col != 'Date']

        # Attempt conversion to numeric (integers) with error handling
        for col in numeric_cols:
            try:
                data[col] = pd.to_numeric(data[col], errors='coerce', downcast="integer")
            except:
                print(f"Warning: Error converting column {col} to numeric (integers).")
        
        data["Closing Cash"] = pd.to_numeric(data["Closing Cash"], errors='coerce', downcast="integer")
        
        top_entry = data.iloc[index]
        top_entry['Date'] = pd.to_datetime(top_entry['Date'], dayfirst=True).strftime('%d-%b-%Y (%A)')
        
        employees = [employeeName.split("-")[0].strip() for employeeName in employees]

        # Define entries for column 0 and column 1
        col0_entries = [
            f"Date: {top_entry['Date']}",
            f"Sales",
            f"Opening Cash: ₹{top_entry['Opening Cash']}",
            f"Total Sales POS: ₹{top_entry['Total Sales POS']}",
            f"Paytm: ₹{top_entry['Paytm']}",
            f"Expenses",
            f"{employees[0]}: ₹{top_entry['Employee 1']}",
            f"{employees[1]}: ₹{top_entry['Employee 2']}",
            f"{employees[2]}: ₹{top_entry['Employee 3']}",
            f"{employees[3]}: ₹{top_entry['Employee 4']}",
            f"Cleaning: ₹{top_entry['Cleaning']}",
            f"Total Expenses: ₹{top_entry['Expenses Shop']}",
        ]

        col1_entries = [
            f"Denominations:",
            f"₹500 x {top_entry['500']} = ₹{500*top_entry['500']}",
            f"₹200 x {top_entry['200']} = ₹{200*top_entry['200']}",
            f"₹100 x {top_entry['100']} = ₹{100*top_entry['100']}",
            f"₹50  x {top_entry['50']}  = ₹{50*top_entry['50']}",
            f"₹20  x {top_entry['20']}  = ₹{20*top_entry['20']}",
            f"₹10  x {top_entry['10']}  = ₹{10*top_entry['10']}",
            f"₹5   x {top_entry['5']}   = ₹{5*top_entry['5']}",
            f"Total: ₹{top_entry['Denomination Total']}",
            f"Cash Withdrawn: ₹{top_entry['Cash Withdrawn']}",
            f"Closing Cash: ₹{top_entry['Closing Cash']}",
            f"Total Cash: ₹{top_entry['Total Cash']}",
        ]

        # Display using Streamlit columns
        col1, col2 = st.columns(2)
        with col1:
            for entry in col0_entries:
                display_text(entry)
        with col2:
            for entry in col1_entries:
                display_text(entry)
                
        Cash_diff = f"Cash Difference: ₹{top_entry['Cash Difference']}"
        text_color = "red" if top_entry['Cash Difference'] > 100 else "blue" if top_entry['Cash Difference'] > 0 else "green"
        display_text(Cash_diff,color=text_color,font_size ="28px")
        
    else:
        st.error("No data available to display.")


    
def accounts_db_tab():
    st.title("Elite Unisex Salon Daily Accounts Database")

    try:
        data, last_closing_cash = load_data()
        employees = load_employee_names()  # Load names or define list
    except FileNotFoundError:
        st.error("The database file is missing. Please ensure it exists in the correct location.")
        return
    except pd.errors.ParserError:
        st.error("Error parsing the CSV file. Please check the file format.")
        return

    if not data.empty:
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'])
            data = data.sort_values(by='Date', ascending=False)  # Sort by date in ascending order
            data['Date'] = data['Date'].dt.strftime('%d-%m-%Y')  # Format the date for display after sorting

        expected_columns = ["Date", "Opening Cash", "Closing Cash", "Cash Difference", "Total Sales POS", "Paytm", "Total Cash", "Denomination Total", "Cash Withdrawn"]
        
        if not all(col in data.columns for col in expected_columns):
            st.error("The data structure has changed or some columns are missing.")
            return
        
        selected_row = st.number_input("Entry:", min_value=0,max_value=len(data), step=1)
        display_last_entry(data,selected_row,employees)

        # Layout for row selection, password input, and delete button
        col1, col2, col3 = st.columns(3)
        
        with col1:
            row_to_delete = st.selectbox("Select Row", options=data.index)
        with col2:
            password = st.text_input("Enter password to delete entry", type="password")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
        with col3:
            delete_button_clicked = st.button("Delete Row")
            
        
        
        if delete_button_clicked and hashed_password == "f20732a590b9312ee8282a5962cc5b90e4c1bbb31e5c537d51857c5a3fab5a41":  # Replace 'password' with the actual password
            data = delete_row(data, row_to_delete)
            data.sort_index(inplace=True)  # Sort back by original index before saving
            save_data(data)  # Save the restored order data back to CSV
            st.success(f"Row {row_to_delete} deleted successfully.")
            
        elif delete_button_clicked:
            st.error("Incorrect password.")
            
        DownloadFiles()

        display_data(data[expected_columns])
    else:
        st.warning("No data found. The database might be empty or filtered out.")
