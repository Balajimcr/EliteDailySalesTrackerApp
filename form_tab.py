import streamlit as st
import pandas as pd
import random
from data_management import load_data, load_employee_names
from ui_helpers import Text, tabs_font_css,display_text
from datetime import date, datetime, timedelta
from data_management import csv_file
from accounts_db_tab import sync_all_csv_files
from config import SHOP_NAME

def form_tab():
    # Initialize data, last closing cash, and employee names
    data, last_closing_cash = load_data()
    employee_names = load_employee_names()
    
    # Ensure last_closing_cash is an integer
    if last_closing_cash is None:
        last_closing_cash = 0
    else:
        try:
            last_closing_cash = int(last_closing_cash)  # Convert to integer if it's not
        except ValueError:
            last_closing_cash = 0  # Default to 0 if conversion fails

    # When retrieving from session_state, also convert to integer to ensure type safety
    opening_cash_value = st.session_state.get('opening_cash', last_closing_cash)
    if opening_cash_value is not None:
        try:
            opening_cash_value = int(opening_cash_value)  # Convert to int to avoid type issues
        except ValueError:
            opening_cash_value = last_closing_cash  # Fallback to last_closing_cash if conversion fails

    st.title(SHOP_NAME)

    st.write(tabs_font_css, unsafe_allow_html=True)

    # Create a two-column layout
    left_col, right_col = st.columns(2)

    # Data input fields in the left column
    with left_col:
        st.subheader("Sales")
        date_input = st.date_input(Text("Date (தேதி)"), value=st.session_state.get('date_input', date.today()), format="DD-MM-YYYY")
        opening_cash = st.number_input(Text("Opening Cash (ஆரம்ப இருப்பு)"), value=st.session_state.get('opening_cash', last_closing_cash), min_value=0, step=100)
        total_sales_pos = st.number_input(Text("Total Sales POS ( சேல்ஸ் )"), value=st.session_state.get('total_sales_pos', 0), min_value=0, step=100)
        paytm = st.number_input(Text("Paytm (பேடிஎம்)"), value=st.session_state.get('paytm', 0), min_value=0, step=100)

        # Expenses fields
        st.subheader("Expenses")
        # Generate number inputs for employee advances using list comprehension
        employee_advances = [st.number_input(Text(name), value=st.session_state.get(name, 0), min_value=0, step=100) for name in employee_names]

        # Generate number input for cleaning expenses
        cleaning = st.number_input(Text("Cleaning"), value=st.session_state.get('cleaning', 0), min_value=0, step=100)

       # Unified list of other expenses options
        other_expenses_options = ["Tea or Snacks", "Others", "Flower", "Corporation", "Paper"]

        # Initialize a list to collect the amounts of other expenses
        other_expenses_names = []
        other_expenses = []

        # Loop through a range to create multiple expense inputs using an offset
        number_of_expense_inputs = 2  # Adjust the number as needed
        for idx in range(number_of_expense_inputs):
            offset = idx + 1  # Start indexing from 1
            name_label = f"Other Expenses Name {offset}"
            amount_label = f"Other Expenses Amount {offset}"
            expense_name = st.selectbox(Text(name_label), other_expenses_options,index=idx, label_visibility="collapsed")
            expense_amount = st.number_input(amount_label, value=st.session_state.get(amount_label, 0), min_value=0, step=100, label_visibility="collapsed")
            other_expenses.append(expense_amount)
            other_expenses_names.append(expense_name)

        # Calculate and display total expenses
        expenses_shop_total = sum(employee_advances) + cleaning + sum(other_expenses)

        display_text(f"Total Expenses: ₹{expenses_shop_total}")


    # Denominations in the right column
    with right_col:
        st.subheader("Denominations")
        # Define denominations and their corresponding values
        denominations = [500, 200, 100, 50, 20, 10, 5]

        # Create a dictionary to store user input for each denomination
        denomination_counts = {denom: st.number_input(Text(f"{denom} x"), value=st.session_state.get(f"{denom} x", 0), min_value=0, step=1) for denom in denominations}

        # Calculate the denomination total using list comprehension
        denomination_total = sum(count * value for count, value in denomination_counts.items())

        display_text(f"Total: ₹{denomination_total}")
        cash_withdrawn = st.number_input(Text("Cash Withdrawn (பணம் எடுத்தது)"), value=st.session_state.get('cash_withdrawn', 0), min_value=0, step=100)

        # Calculate closing cash and display
        closing_cash = denomination_total - cash_withdrawn
        
        display_text(f"Closing Cash: ₹{closing_cash}")

        # Adjust for small cash amounts
        offset = 0
        
        # Calculate total cash and cash difference
        total_cash = opening_cash + (total_sales_pos - paytm) - expenses_shop_total + offset
        cash_difference = total_cash - denomination_total
        
        cash_difference_masked = cash_difference

        # Display data with dynamic styling based on cash difference
        text_color = "red" if cash_difference > 100 else "blue" if cash_difference > 0 else "green"
            
        # Limit negative cash difference to -100
        if cash_difference < -100:
            cash_difference_masked = random.randint(1, 10) * 10
        
        display_text(f"Total Sales: ₹{total_sales_pos}")
        display_text(f"Cash: ₹{total_sales_pos - paytm}")
        display_text(f"Paytm: ₹{paytm}")
        display_text(f"Expenses: ₹{expenses_shop_total}")
        display_text(f"Total Cash: ₹{total_cash}")
        display_text(f"Closing Cash: ₹{closing_cash}")
        # Display cash difference with custom font size and color
        display_text(f"Difference: ₹{cash_difference_masked}",color=text_color,font_size ="28px")

    # Submit button to handle form submission
    submit_button = st.button("Submit")

    if submit_button:
        new_row = {
            "Date": date_input.strftime('%d-%b-%y'), 
            "Opening Cash": int(opening_cash),
            "Expenses Shop": int(expenses_shop_total),
            "Denomination Total": int(denomination_total),
            "Total Cash": int(total_cash),
            "Total Sales POS": int(total_sales_pos),
            "Paytm": int(paytm),  
            "Cash Withdrawn": int(cash_withdrawn),  
            "Employee 1": int(employee_advances[0]),
            "Employee 2": int(employee_advances[1]),
            "Employee 3": int(employee_advances[2]),
            "Employee 4": int(employee_advances[3]),
            "Cleaning": int(cleaning),
            "Other Expenses Name": other_expenses_names[0],
            "Other Expenses Amount": int(other_expenses[0]),
            "Other Expenses Name_1": other_expenses_names[1],
            "Other Expenses Amount_1": int(other_expenses[1]),
            "500": int(denomination_counts[500]),
            "200": int(denomination_counts[200]),
            "100": int(denomination_counts[100]),
            "50": int(denomination_counts[50]),
            "20": int(denomination_counts[20]),
            "10": int(denomination_counts[10]),
            "5": int(denomination_counts[5]),
            "Cash Difference": int(cash_difference),
            "Closing Cash": int(closing_cash),
        }
        
        # Default to True indicating data is valid to submit
        Pass = True

        # Check if cash_withdrawn is greater than the available cash in denominations
        if cash_withdrawn > denomination_total:
            Pass = False
            display_text(f"[Error] Cash Withdrawn is wrong! {cash_withdrawn} > {denomination_total}",color="red",font_size ="28px")
            
        if abs(cash_difference) > 1000:
            Pass = False
            display_text(f"[Error] High Cash Difference : {cash_difference}! Call Owner",color="red",font_size ="28px")
            
        # If the checks passed, proceed to add new data and save it
        if Pass:
            # Use pd.concat() to add the new row to the existing data
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

            # Append the new data to the CSV file without overwriting, with proper line terminators
            with open(csv_file, 'a', encoding='utf-8', newline='') as f:
                # Write the data to CSV without header if appending
                data.tail(1).to_csv(f, header=f.tell() == 0, index=False, lineterminator='\n')

            st.success("Data submitted successfully!")
            st.balloons()
            sync_all_csv_files()
            st.success("Data synchronized successfully!")   

