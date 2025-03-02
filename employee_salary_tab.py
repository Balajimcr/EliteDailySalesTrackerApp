import os
import pandas as pd

import datetime
from datetime import date, datetime, timedelta
from ui_helpers import displayhtml_data
from data_management import csv_file, employee_csv, employee_salary_Advance_bankTransfer_csv,employee_salary_data_csv,employee_salary_csv
from config import start_month
import streamlit as st
from data_management import load_data, load_employee_names

def display_data(dataframe, title):
    """Display a dataframe with a title."""
    st.markdown(f'<div style="color: black; font-size: 24px; font-weight: bold;">{title}:</div>', unsafe_allow_html=True)
    st.dataframe(dataframe)
        
def save_data_to_csv(new_data, file_name=employee_salary_Advance_bankTransfer_csv):
    # Check if file exists
    if not os.path.isfile(file_name):
        # Create a new DataFrame and save it
        pd.DataFrame([new_data]).to_csv(file_name, index=False)
    else:
        # Load existing data and append new data
        existing_data = pd.read_csv(file_name, parse_dates=['Date'], dayfirst=True)
        new_frame = pd.DataFrame([new_data])
        updated_data = pd.concat([existing_data, new_frame], ignore_index=True)
        updated_data.to_csv(file_name, index=False,encoding="utf-8")
    return pd.read_csv(file_name, parse_dates=['Date'], dayfirst=True)  # Return updated data

def load_salary_data():
    """Load salary data from CSV, handling potential errors."""
    if not os.path.exists(employee_salary_data_csv):
        st.error("Salary data file is missing. Please ensure it exists in the correct location.")
        return None
    try:
        salary_data = pd.read_csv(employee_salary_data_csv, parse_dates=['Month'], dayfirst=True, encoding='utf-8')
        salary_data['Month'] = pd.to_datetime(salary_data['Month'], format='%d-%b-%y', errors='coerce')
        # Format Month as DD-Mmm-YY for consistency
        salary_data['Month'] = salary_data['Month'].dt.strftime('%d-%b-%y')
        return salary_data.sort_values(by='Month', ascending=False)
    except Exception as e:
        st.error(f"An error occurred while loading the salary data: {str(e)}")
        return None

def update_salary_data():
    salary_data = load_salary_data()
    if salary_data is None:
        st.error("Failed to load salary data. Please check the data source.")
        return None  # Exit if the data couldn't be loaded
    
    st.write("### Update Employee Salary")

    # Format 'Month' for display and use in selection
    salary_data['Month'] = pd.to_datetime(salary_data['Month'])
    months = salary_data['Month'].dt.strftime('%b-%y').unique()
    selected_month = st.selectbox("Select Month", options=months)

    # Convert selected month back to datetime for comparison
    selected_month_datetime = pd.to_datetime(selected_month, format='%b-%y')

    # Create a list to collect updated salary data
    updates = []
    
    salary_data['Month'] = salary_data['Month'].dt.strftime('%b-%y')

    for employee in salary_data['Employee Name'].unique():
        # Filter data for the selected month and employee
        filtered_data = salary_data[(salary_data['Month'] == selected_month_datetime) & 
                                    (salary_data['Employee Name'] == employee)]
        
        current_salary = filtered_data.iloc[0]['Salary'] if not filtered_data.empty else 0

        # Use Streamlit columns to display employee name, current salary, and input for new salary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"{employee}")
        with col2:
            st.write(f"{current_salary}")
        with col3:
            new_salary = st.number_input(f"New Salary for {employee}", key=f"salary_{employee}", value=int(current_salary))
        
        # Collect data for updates
        updates.append((employee, new_salary, filtered_data.index))

    if st.button("Update Salary"):
        new_entries = []
        for employee, new_salary, idx in updates:
            if idx.empty:
                new_entries.append({
                    'Month': selected_month_datetime,
                    'Employee Name': employee,
                    'Monthly Bank Transfers': 0,
                    'Monthly Cash Withdrawn': 0,
                    'Total Salary Advance': 0,
                    'Total Sales': new_salary * 2,  # Assuming sales are double the salary
                    'Salary': new_salary,
                    'Balance': 0,
                    'Balance Till date': 0
                })
            else:
                salary_data.loc[idx, 'Salary'] = new_salary
                salary_data.loc[idx, 'Total Sales'] = new_salary * 2  # Assuming sales are double the salary

        if new_entries:
            new_entries_df = pd.DataFrame(new_entries)
            salary_data = pd.concat([salary_data, new_entries_df], ignore_index=True)

        try:
            salary_data.to_csv(employee_salary_data_csv, index=False)
            st.success("Salary data updated successfully.")
        except Exception as e:
            st.error(f"An error occurred while saving the salary data: {str(e)}")
            return None  # Return None if saving fails
    
    display_data(salary_data, "Employee Salary")
    
    return salary_data


    
def aggregate_financials(bank_transfer_df, cash_withdrawn_df):
    """
    Aggregate financial data month-wise for bank transfers and cash withdrawals.
    """
    # Convert date strings to datetime objects for easier manipulation
    bank_transfer_df['Date'] = pd.to_datetime(bank_transfer_df['Date'], dayfirst=True)
    cash_withdrawn_df['Date'] = pd.to_datetime(cash_withdrawn_df['Date'], dayfirst=True)

    # Group and resample bank transfer data by month
    monthly_bank_transfers = bank_transfer_df.groupby(['Employee', pd.Grouper(key='Date', freq='M')]).sum().reset_index()
    monthly_bank_transfers['Month'] = monthly_bank_transfers['Date'].dt.strftime('%b-%y')
    monthly_bank_transfers.rename(columns={'Amount': 'Monthly Bank Transfers', 'Employee': 'Employee Name'}, inplace=True)
    monthly_bank_transfers.drop(columns=['Date','Comments'], inplace=True, errors='ignore')

    # Melt cash_withdrawn_df to make it long format, preparing it for grouping
    melted_cash_withdrawn = pd.melt(cash_withdrawn_df, id_vars=['Date'], var_name='Employee Name', value_name='Amount')
    melted_cash_withdrawn['Month'] = melted_cash_withdrawn['Date'].dt.to_period('M')
    
    # Aggregate the melted data by month and employee for the 'Amount' column only
    monthly_cash_withdrawn = melted_cash_withdrawn.groupby(['Month', 'Employee Name']).agg({'Amount': 'sum'}).reset_index()
    monthly_cash_withdrawn['Month'] = monthly_cash_withdrawn['Month'].dt.strftime('%b-%y')
    monthly_cash_withdrawn.rename(columns={'Amount': 'Monthly Cash Withdrawn'}, inplace=True)

    # Merge the DataFrames on 'Month' and 'Employee Name'
    financial_summary = pd.merge(monthly_cash_withdrawn, monthly_bank_transfers, on=['Month', 'Employee Name'], how='left')

    # Fill NaN values with 0 for the Monthly Bank Transfers column
    financial_summary['Monthly Bank Transfers'].fillna(0, inplace=True)
    
    # Calculate Total Salary Advance
    financial_summary['Total Salary Advance'] = financial_summary['Monthly Bank Transfers'] + financial_summary['Monthly Cash Withdrawn']
    
    # Display intermediate results for debugging
    display_data(monthly_bank_transfers, "Monthly Bank Transfers")
    display_data(monthly_cash_withdrawn, "Monthly Cash Withdrawn")
    display_data(financial_summary, "Monthly Financial Summary")

    return financial_summary

def update_employee_salary_csv(Employee_Salary_data, csv_file_path):
    st.write("### Update Employee Salary Data CSV")

    # Ensure the DataFrame has the correct column names
    required_columns = ['Month', 'Employee Name', 'Monthly Bank Transfers', 'Monthly Cash Withdrawn', 
                        'Total Salary Advance', 'Total Sales', 'Salary', 'Balance', 'Balance Till date']
    
    # Rename columns if necessary
    column_mapping = {
        'Employee': 'Employee Name',
        'Balance Current': 'Balance',
        'Balance Till Date': 'Balance Till date'
    }
    Employee_Salary_data = Employee_Salary_data.rename(columns=column_mapping)

    # Ensure all required columns are present
    for col in required_columns:
        if col not in Employee_Salary_data.columns:
            Employee_Salary_data[col] = 0  # Add missing columns with default value 0

    # Reorder columns to match the required format
    Employee_Salary_data = Employee_Salary_data[required_columns]

    # Convert 'Month' to datetime for proper chronological sorting
    Employee_Salary_data['Month_dt'] = pd.to_datetime(Employee_Salary_data['Month'], format='%b-%y', errors='coerce')

    # Sort by 'Month_dt' (ascending) and then 'Employee Name'
    Employee_Salary_data = Employee_Salary_data.sort_values(['Month_dt'], ascending=[True])

    # Convert 'Month' back to string format 'Mmm-YY' for display and saving
    Employee_Salary_data['Month'] = Employee_Salary_data['Month_dt'].dt.strftime('%b-%y')    
    # Drop the temporary datetime column
    Employee_Salary_data = Employee_Salary_data.drop(columns=['Month_dt'])
    
    # Convert all numeric columns to integers
    numeric_columns = ['Monthly Bank Transfers', 'Monthly Cash Withdrawn', 'Total Salary Advance', 
                      'Total Sales', 'Salary', 'Balance', 'Balance Till date']
    
    for col in numeric_columns:
        Employee_Salary_data[col] = Employee_Salary_data[col].round().astype(int)

    # Compute 'Total Sales' based on 'Salary' (Total Sales = Salary / 0.45) and convert to integer
    Employee_Salary_data['Total Sales'] = (Employee_Salary_data['Salary'] / 0.45).round().astype(int)

    # Display the data that will be saved
    st.dataframe(Employee_Salary_data)
    
    # Save to CSV without index
    try:
        Employee_Salary_data.to_csv(employee_salary_csv, index=False)
        st.success(f"Data successfully saved to {employee_salary_csv}")
    except Exception as e:
        st.error(f"An error occurred while saving the data: {str(e)}")

    return Employee_Salary_data

  
def calculate_financials(month, employee, financial_summary, employee_salary_data, previous_balances):
    """
    Compute financial details for each employee for a given month, updating the previous balance.

    Args:
    - month (str): The month in 'Mon-YYYY' format.
    - employee (str): The name of the employee.
    - financial_summary (pd.DataFrame): DataFrame containing financial summaries.
    - employee_salary_data (pd.DataFrame): DataFrame containing employee salary data.
    - previous_balances (dict): Dictionary holding previous balance till date for each employee.

    Returns:
    - dict: A dictionary with calculated financial details for the employee.
    """
    # Filter the data for the specific month and employee
    financials = financial_summary[(financial_summary['Employee Name'] == employee) &
                                   (financial_summary['Month'] == month)]
    salary_info = employee_salary_data[(employee_salary_data['Employee Name'] == employee) &
                                       (employee_salary_data['Month'] == month)]

    # Compute financial metrics
    monthly_cash_withdrawn = financials['Monthly Cash Withdrawn'].sum()
    monthly_bank_transfers = financials['Monthly Bank Transfers'].sum()
    total_salary_advance = financials['Total Salary Advance'].sum()
    monthly_sales = salary_info['Total Sales'].sum()
    salary = salary_info['Salary'].sum()
    
    # Get the previous balance if it exists, otherwise start from 0
    previous_balance = previous_balances.get(f"{month}-{employee}", 0)

    # Calculate the current balance and update for this month
    balance = total_salary_advance - salary
    balance_till_date = previous_balance + balance

    # Update the previous balances dictionary for the next month
    next_month = (pd.to_datetime(month, format='%b-%y') + pd.DateOffset(months=1)).strftime('%b-%y')
    previous_balances[f"{next_month}-{employee}"] = balance_till_date

    return {
        "Month": month,
        "Employee": employee,
        "Monthly Cash Withdrawn": monthly_cash_withdrawn,
        "Monthly Bank Transfers": monthly_bank_transfers,
        "Total Salary Advance": total_salary_advance,
        "Monthly Sales": monthly_sales,
        "Salary": salary,
        "Balance Current": balance,
        "Balance Till Date": balance_till_date
    }

def update_financial_records_over_time(start_month, end_month, employees, financial_summary, employee_salary_data):
    """
    Update financial records over a specified range of months for all employees.

    Args:
    - start_month (str): Start month in 'Mon-YY' format.
    - end_month (str): End month in 'Mon-YY' format.
    - employees (list): List of employee names.
    - financial_summary (pd.DataFrame): DataFrame containing financial summaries.
    - employee_salary_data (pd.DataFrame): DataFrame containing employee salary data.

    Returns:
    - pd.DataFrame: DataFrame with computed financial details over the specified months.
    """
    # Parse start and end months explicitly with %b-%y
    start_dt = pd.to_datetime(start_month, format='%b-%y')
    end_dt = pd.to_datetime(end_month, format='%b-%y')
    
    month_range = pd.date_range(start=start_dt, end=end_dt, freq='MS').strftime('%b-%y')
    results = []
    previous_balances = {}

    for month in month_range:
        for employee in employees:
            financial_details = calculate_financials(month, employee, financial_summary, employee_salary_data, previous_balances)
            results.append(financial_details)

    return pd.DataFrame(results)

def employee_salary_tab():
    st.title("Employee Salary Accounts")

    # Check if the CSV file exists
    try:
        data, last_closing_cash = load_data()
        employee_names_list = load_employee_names()  # Load employee names as a list
    except FileNotFoundError:
        st.error("The database file is missing. Please ensure it exists in the correct location.")
        return
    except pd.errors.ParserError:
        st.error("Error parsing the CSV file. Please check the file format.")
        return
    
    # Create a copy of the data for modification
    employee_sa_cash_withdrawn = data.copy()

    # Assuming employee_names_list is correctly ordered to replace "Employee 1", "Employee 2", etc.
    # Create a dictionary mapping old column names to new names based on the loaded list
    column_name_mapping = {
        "Employee 1": employee_names_list[0],
        "Employee 2": employee_names_list[1],
        "Employee 3": employee_names_list[2],
        "Employee 4": employee_names_list[3]
    }

    # Rename columns in the copy of the DataFrame
    employee_sa_cash_withdrawn.rename(columns=column_name_mapping, inplace=True)

    if employee_sa_cash_withdrawn.empty:
        st.warning("No data found. The database might be empty or filtered out.")
        return

    if 'Date' in employee_sa_cash_withdrawn.columns:
        employee_sa_cash_withdrawn['Date'] = pd.to_datetime(employee_sa_cash_withdrawn['Date']).dt.strftime('%d-%b-%y')
        employee_sa_cash_withdrawn = employee_sa_cash_withdrawn.sort_values(by='Date', ascending=False)
        
    # User Inputs
    input_date = st.date_input("Date", value=date.today(), format="DD-MM-YYYY")
    input_amount = st.number_input("Amount", min_value=0, step=1000) 
    input_employee = st.selectbox("Employee", options=employee_names_list)
    input_comments = st.text_input("Comments")

    if st.button("Save Entry"):
        new_entry = {
            "Date": input_date.strftime('%d-%b-%y'),
            "Amount": input_amount,
            "Employee": input_employee,
            "Comments": input_comments
        }
        save_data_to_csv(new_entry)
    
    if os.path.isfile(employee_salary_Advance_bankTransfer_csv):
        data = pd.read_csv(employee_salary_Advance_bankTransfer_csv, parse_dates=['Date'], dayfirst=True)
        data['Date'] = pd.to_datetime(data['Date'],format='%d-%b-%y', errors='coerce', dayfirst=True)
        data = data.sort_values(by='Date', ascending=False)
        data['Date'] = data['Date'].dt.strftime('%d-%b-%y')
        display_data(data, "Employee Advance Bank Transfer")
    else:
        st.error(f"File {employee_salary_Advance_bankTransfer_csv} is missing! Please check the CSV file path.")

    expected_columns = ["Date", employee_names_list[0], employee_names_list[1], employee_names_list[2], employee_names_list[3]]
    
    employee_cash_withdrawn_data = []
    
    if not all(col in employee_sa_cash_withdrawn.columns for col in expected_columns):
        st.error("The data structure has changed or some columns are missing. Please check the CSV file.")
    else:
        employee_cash_withdrawn_data = employee_sa_cash_withdrawn[expected_columns].copy()
        employee_cash_withdrawn_data['Date'] = pd.to_datetime(employee_cash_withdrawn_data['Date'], format='%d-%b-%y', errors='coerce')
        employee_cash_withdrawn_data = employee_cash_withdrawn_data.sort_values(by='Date', ascending=False)
        employee_cash_withdrawn_data['Date'] = employee_cash_withdrawn_data['Date'].dt.strftime('%d-%b-%y')
        display_data(employee_cash_withdrawn_data, "Employee Cash Advance")
        
    employee_Salary_data = update_salary_data()
    
    if employee_Salary_data is None:
        st.error("Failed to update sales data. Please check the data source and processing logic.")
        return

    # Sort by Employee and then by Month
    try:
        employee_Salary_data.sort_values(by=['Employee Name', 'Month'], inplace=True)
    except Exception as e:
        st.error(f"An error occurred while sorting the data: {str(e)}")
        return
    
    end_month = datetime.now().strftime('%b-%y')

    adv_bank_transfer_df = pd.read_csv(employee_salary_Advance_bankTransfer_csv, parse_dates=['Date'], dayfirst=True)
    cash_withdrawn_df = employee_cash_withdrawn_data

    # Assuming you have a way to fetch or define a list of employees
    employees = load_employee_names()  # Load names or define list
    
    financial_summary = aggregate_financials(adv_bank_transfer_df, cash_withdrawn_df)
    
    # Assuming financial_summary and employee_salary_data are loaded and prepared
    Employee_Salary_data = update_financial_records_over_time(start_month, end_month, employees, financial_summary, employee_Salary_data)
    
    # Add a select box to choose an employee
    selected_employee = st.selectbox("Select an Employee", options=Employee_Salary_data['Employee'].unique())
    
    # Filter the DataFrame to show only the selected employee's data
    employee_specific_salary_data = Employee_Salary_data[Employee_Salary_data['Employee'] == selected_employee]
    
    display_data(employee_specific_salary_data, "Employee Salary Data")
    
    Employee_Salary_data = update_employee_salary_csv(Employee_Salary_data, employee_salary_data_csv)
    
    
    
