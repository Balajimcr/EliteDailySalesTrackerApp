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
    """
    Main Streamlit application entry point. It sets up the sidebar navigation,
    manages user authentication, and routes to the appropriate tab based on
    the user's selection.
    """
    st.sidebar.title(BRANCH_NAME)
    
    # Ensure the current tab is stored in session_state; default to "Login".
    if 'current_tab' not in st.session_state:
        st.session_state['current_tab'] = "Login"

    # List available tabs for navigation.
    tabs = [
        "Login",
        Text("Form"),
        "Daily Accounts Database",
        "Shop Purchase Account",
        "Employee Details",
        "Employee Salary Account"
    ]

    # Update current_tab based on user selection from the sidebar radio button.
    st.session_state['current_tab'] = st.sidebar.radio(
        "Go to",
        tabs,
        index=tabs.index(st.session_state['current_tab'])
    )

    # Handle authentication and tab routing.
    if st.session_state['current_tab'] == "Login" and not is_logged_in():
        # If the user is on the login tab and not logged in, display the login screen.
        user_logged_in = login()
        if user_logged_in:
            # After successful login, switch to the Form tab and rerun the page.
            st.session_state['current_tab'] = Text("Form")
            st.rerun()
        else:
            st.warning("Please log in to continue.")
    elif is_logged_in():
        # If the user is authenticated, route to the selected tab.
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
        st.warning("You need to log in to access this tab.")


if __name__ == "__main__":
    main_app()