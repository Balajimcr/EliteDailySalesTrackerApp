from numpy import PINF
import streamlit as st
import hashlib
from streamlit.runtime.scriptrunner import get_script_run_ctx
from data_management import UserDirectoryPath

# Simulated user database with hashed passwords
USER_DATA = {
    "balajimcr@gmail.com":"f20732a590b9312ee8282a5962cc5b90e4c1bbb31e5c537d51857c5a3fab5a41",
    "elitesalonlalgudi@gmail.com":"9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0",
    "elitesalonmcr@gmail.com":"9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0",
    "Pin_No":"9af15b336e6a9619928537df30b2e6a2376569fcf9d7e773eccede65606529a0",
}
# Check user session to determine if they're logged in
def is_logged_in():
    ctx = get_script_run_ctx()
    if ctx.session_id in st.session_state:
        return st.session_state[ctx.session_id].get("logged_in", False)
    return False

# Set user session to mark login status
def set_logged_in(logged_in):
    ctx = get_script_run_ctx()
    if ctx.session_id not in st.session_state:
        st.session_state[ctx.session_id] = {}
    st.session_state[ctx.session_id]["logged_in"] = logged_in

# Login form that returns the login status
def login():
    st.header("Elite Salon Manachanallur")
    st.header("Login")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    pin_no   = st.text_input("Pin No", type="password", key="pin_no")
    pin_no_hash = hashlib.sha256(pin_no.encode()).hexdigest()
    login_button = st.button("Login")
    
    if login_button and pin_no:
        pin_no_hash = hashlib.sha256(pin_no.encode()).hexdigest()
        if pin_no_hash == USER_DATA['Pin_No']:  # Corrected the key here
            set_logged_in(True)
            st.success("Login successful!")
            return True
        else:
            st.error("Invalid PIN. Please try again.")
            return False

    if login_button:
        if username in USER_DATA:
            # Hash the entered password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if USER_DATA[username] == hashed_password:
                set_logged_in(True)
                st.success("Login successful!")
                return True
            else:
                st.error("Invalid password. Please try again.")
                return False
        else:
            st.error(f"Invalid username {username} Please try again.")
            return False
    return False
