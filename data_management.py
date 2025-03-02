import pandas as pd
from datetime import datetime
from config import UserDirectoryPath,employee_names_def
import hashlib
import pandas as pd

csv_file = UserDirectoryPath +"database_collection.csv"
employee_csv = UserDirectoryPath +"Employee_data.csv"
employee_salary_Advance_bankTransfer_csv = UserDirectoryPath +"employee_salary_Advance_bankTransfer_data.csv"
employee_salary_data_csv = UserDirectoryPath +"employee_salary_data.csv"
employee_salary_csv = UserDirectoryPath +"employee_salary.csv"
credentials_path = "/.streamlit/secrets.toml"

def load_employee_names():
    try:
        employee_data = pd.read_csv(employee_csv)
        employee_names = employee_data["Name"].tolist()
    except (FileNotFoundError, IndexError):
        st.error("Employee names file not found! Please ensure the file exists.")
        employee_names = employee_names_def
    return employee_names


def load_data():
    try:                
        data = pd.read_csv(csv_file, parse_dates=['Date'], dayfirst=True)
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce', dayfirst=True)
        
        data["Closing Cash"] = pd.to_numeric(data["Closing Cash"], errors='coerce', downcast="integer")
        # Exclude 'Date' from conversion (assuming it's already a datetime)
        numeric_cols = [col for col in data.columns if col != 'Date']

        # Attempt conversion to numeric (integers) with error handling
        for col in numeric_cols:
            try:
                data[col] = pd.to_numeric(data[col], errors='coerce', downcast="integer")
            except:
                print(f"Warning: Error converting column {col} to numeric (integers).")
        
        # Remove duplicates in the 'Date' column, keeping the last entry
        data = data.sort_values('Date').drop_duplicates(subset='Date', keep='last')
        
        data.sort_values(by='Date', inplace=True)
        today_date = datetime.combine(datetime.today().date(), datetime.min.time())
        filtered_data = data[data['Date'] < today_date].copy()
        if not filtered_data.empty:
            last_closing_cash = filtered_data["Closing Cash"].iloc[-1]
        else:
            last_closing_cash = 0
    except (FileNotFoundError, IndexError):
        data = pd.DataFrame(columns=[
            "Date", "Opening Cash", "Expenses Shop", "Denomination Total","Total Cash",
            "Total Sales POS", "Paytm", "Cash Withdrawn", "Employee 1", 
            "Employee 2", "Employee 3", "Employee 4", "Cleaning", 
            "Other Expenses Name", "Other Expenses Amount", 
            "Other Expenses Name_1", "Other Expenses Amount_1", 
            "500", "200","100", "50", "20", "10", "5","Cash Difference",
            "Closing Cash"
        ])
        last_closing_cash = 0
    return data, last_closing_cash


def save_data(data):
    data.to_csv(csv_file, index=False)

