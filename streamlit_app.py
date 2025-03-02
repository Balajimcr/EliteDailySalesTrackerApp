import streamlit as st
from employee_salary_tab import employee_salary_tab
from form_tab import form_tab
from ui_helpers import Text
from accounts_db_tab import accounts_db_tab
from shop_purchase_tab import shop_purchase_tab
from employee_details import employee_details_tab
from user_authentication import is_logged_in, login
from config import BRANCH_NAME

def main_app():
    st.sidebar.title(BRANCH_NAME)
    # Initialize session state for the current tab if it's not already set
    if 'current_tab' not in st.session_state:
        st.session_state['current_tab'] = "Login"

    # Dropdown for navigating between tabs
    tabs = ["Login", Text("Form"), "Daily Accounts Database", "Shop Purchase Account", "Employee Details", "Employee Salary Account"]
    # Dynamically update the 'current_tab' on user interaction
    st.session_state['current_tab'] = st.sidebar.radio("Go to", tabs, index=tabs.index(st.session_state['current_tab']))

    if st.session_state['current_tab'] == "Login" and not is_logged_in():
        user_logged_in = login()
        if user_logged_in:
            st.session_state['current_tab'] = Text("Form")
            st.rerun()
        else:
            st.warning("Please log in to continue.")
    elif is_logged_in():
        if st.session_state['current_tab'] == Text("Form"):
            form_tab()
        elif st.session_state['current_tab'] == "Daily Accounts Database":
            accounts_db_tab()
        elif st.session_state['current_tab'] == "Shop Purchase Account":
            shop_purchase_tab()
        elif st.session_state['current_tab'] == "Employee Salary Account":
            employee_salary_tab()
        elif st.session_state['current_tab'] == "Employee Details":
            employee_details_tab()
    else:
        st.warning("You need to login to access this tab.")

if __name__ == "__main__":
    main_app()
