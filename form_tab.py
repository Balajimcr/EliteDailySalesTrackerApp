"""
Streamlit Database Management UI

This module implements the Streamlit app for managing the database operations.
It includes data input, computations, and saving data to a CSV file.
"""

# Standard library imports
from datetime import date, datetime, timedelta
import random

# Third-party imports
import streamlit as st
import pandas as pd

# Local application imports
from data_management import load_data, load_employee_names, csv_file
from ui_helpers import Text, tabs_font_css, display_text
from accounts_db_tab import sync_all_csv_files
from config import SHOP_NAME


def safe_int(value, default=0):
    """
    Safely convert a value to an integer. Returns a default value if conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def form_tab():
    """
    Render the main form for sales, expenses, and cash handling.

    This function initializes the necessary data, displays input fields for sales and expenses,
    computes totals (including denominations), performs validations, and saves the updated data.
    """
    # Initialize data, last closing cash, and employee names
    data, last_closing_cash = load_data()
    employee_names = load_employee_names()

    # Ensure last_closing_cash is an integer
    last_closing_cash = safe_int(last_closing_cash, default=0)

    # Retrieve opening cash value from session_state and ensure type safety
    opening_cash_value = safe_int(st.session_state.get('opening_cash', last_closing_cash), default=last_closing_cash)

    st.title(SHOP_NAME)
    st.write(tabs_font_css, unsafe_allow_html=True)

    # Create a two-column layout
    left_col, right_col = st.columns(2)

    # --------------------- Left Column: Sales and Expenses ---------------------
    with left_col:
        st.subheader("Sales")
        date_input = st.date_input(
            Text("Date (தேதி)"),
            value=st.session_state.get('date_input', date.today()),
            format="DD-MM-YYYY"
        )
        opening_cash = st.number_input(
            Text("Opening Cash (ஆரம்ப இருப்பு)"),
            value=st.session_state.get('opening_cash', last_closing_cash),
            min_value=0,
            step=100
        )
        total_sales_pos = st.number_input(
            Text("Total Sales POS ( சேல்ஸ் )"),
            value=st.session_state.get('total_sales_pos', 0),
            min_value=0,
            step=100
        )
        paytm = st.number_input(
            Text("Paytm (பேடிஎம்)"),
            value=st.session_state.get('paytm', 0),
            min_value=0,
            step=100
        )

        # --------------------- Expenses Fields ---------------------
        st.subheader("Expenses")
        # Generate number inputs for employee advances using list comprehension
        employee_advances = [
            st.number_input(
                Text(name),
                value=st.session_state.get(name, 0),
                min_value=0,
                step=100
            )
            for name in employee_names
        ]

        # Number input for cleaning expenses
        cleaning = st.number_input(
            Text("Cleaning"),
            value=st.session_state.get('cleaning', 0),
            min_value=0,
            step=100
        )

        # Unified list of other expenses options
        other_expenses_options = ["Tea or Snacks", "Others", "Flower", "Corporation", "Paper"]

        # Initialize lists to collect names and amounts for other expenses
        other_expenses_names = []
        other_expenses = []

        # Create multiple expense inputs (adjust number_of_expense_inputs as needed)
        number_of_expense_inputs = 2
        for idx in range(number_of_expense_inputs):
            offset = idx + 1  # Start indexing from 1
            name_label = f"Other Expenses Name {offset}"
            amount_label = f"Other Expenses Amount {offset}"
            expense_name = st.selectbox(
                Text(name_label),
                other_expenses_options,
                index=idx,
                label_visibility="collapsed"
            )
            expense_amount = st.number_input(
                amount_label,
                value=st.session_state.get(amount_label, 0),
                min_value=0,
                step=100,
                label_visibility="collapsed"
            )
            other_expenses.append(expense_amount)
            other_expenses_names.append(expense_name)

        # Calculate and display total shop expenses
        expenses_shop_total = sum(employee_advances) + cleaning + sum(other_expenses)
        display_text(f"Total Expenses: ₹{expenses_shop_total}")

    # --------------------- Right Column: Denominations and Cash Calculations ---------------------
    with right_col:
        st.subheader("Denominations")
        # Define available denominations
        denominations = [500, 200, 100, 50, 20, 10, 5]

        # Create a dictionary to store user inputs for each denomination
        denomination_counts = {
            denom: st.number_input(
                Text(f"{denom} x"),
                value=st.session_state.get(f"{denom} x", 0),
                min_value=0,
                step=1
            )
            for denom in denominations
        }

        # Calculate the total cash from denominations
        denomination_total = sum(count * value for value, count in denomination_counts.items())
        display_text(f"Total: ₹{denomination_total}")

        cash_withdrawn = st.number_input(
            Text("Cash Withdrawn (பணம் எடுத்தது)"),
            value=st.session_state.get('cash_withdrawn', 0),
            min_value=0,
            step=100
        )

        # Calculate closing cash and display
        closing_cash = denomination_total - cash_withdrawn
        display_text(f"Closing Cash: ₹{closing_cash}")

        # Optional offset for small cash amounts
        offset = 50

        # Calculate overall total cash and cash difference
        total_cash = opening_cash + (total_sales_pos - paytm) - expenses_shop_total + offset
        cash_difference = total_cash - denomination_total
        cash_difference_masked = cash_difference

        # Dynamic styling: color the difference text based on its value
        text_color = "red" if cash_difference > 50 else "blue" if cash_difference > 0 else "green"

        # If negative cash difference is too large, mask it with a random value
        if cash_difference < -100:
            cash_difference_masked = random.randint(1, 10) * 10

        display_text(f"Total Sales: ₹{total_sales_pos}")
        display_text(f"Cash: ₹{total_sales_pos - paytm}")
        display_text(f"Paytm: ₹{paytm}")
        display_text(f"Expenses: ₹{expenses_shop_total}")
        display_text(f"Total Cash: ₹{total_cash}")
        display_text(f"Closing Cash: ₹{closing_cash}")
        display_text(f"Difference: ₹{cash_difference_masked}", color=text_color, font_size="28px")

    # --------------------- Form Submission ---------------------
    submit_button = st.button("Submit")

    if submit_button:
        # Prepare the new data row to be appended
        new_row = {
            "Date": date_input.strftime('%d-%b-%y'),
            "Opening Cash": safe_int(opening_cash),
            "Expenses Shop": safe_int(expenses_shop_total),
            "Denomination Total": safe_int(denomination_total),
            "Total Cash": safe_int(total_cash),
            "Total Sales POS": safe_int(total_sales_pos),
            "Paytm": safe_int(paytm),
            "Cash Withdrawn": safe_int(cash_withdrawn),
            "Employee 1": safe_int(employee_advances[0]),
            "Employee 2": safe_int(employee_advances[1]),
            "Employee 3": safe_int(employee_advances[2]),
            "Employee 4": safe_int(employee_advances[3]),
            "Cleaning": safe_int(cleaning),
            "Other Expenses Name": other_expenses_names[0],
            "Other Expenses Amount": safe_int(other_expenses[0]),
            "Other Expenses Name_1": other_expenses_names[1],
            "Other Expenses Amount_1": safe_int(other_expenses[1]),
            "500": safe_int(denomination_counts[500]),
            "200": safe_int(denomination_counts[200]),
            "100": safe_int(denomination_counts[100]),
            "50": safe_int(denomination_counts[50]),
            "20": safe_int(denomination_counts[20]),
            "10": safe_int(denomination_counts[10]),
            "5": safe_int(denomination_counts[5]),
            "Cash Difference": safe_int(cash_difference),
            "Closing Cash": safe_int(closing_cash),
        }

        # Validate the new data before submission
        is_valid = True

        # Validation: cash withdrawn should not exceed collected denomination total
        if cash_withdrawn > denomination_total:
            is_valid = False
            display_text(f"[Error] Cash Withdrawn is wrong! {cash_withdrawn} > {denomination_total}", color="red", font_size="28px")

        # Validation: if the cash difference is high, flag an error
        if abs(cash_difference) > 1000:
            is_valid = False
            display_text(f"[Error] High Cash Difference: {cash_difference}! Call Owner", color="red", font_size="28px")

        # If the data passes validation, update the CSV file and synchronize data
        if is_valid:
            # Append the new row to the existing data using pd.concat
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

            # Append new data to CSV without overwriting, ensuring proper line termination
            with open(csv_file, 'a', encoding='utf-8', newline='') as f:
                data.tail(1).to_csv(f, header=f.tell() == 0, index=False, lineterminator='\n')

            st.success("Data submitted successfully!")
            st.balloons()

            sync_all_csv_files()
            st.success("Data synchronized successfully!")