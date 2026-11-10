import streamlit as st
import requests
import base64
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="FCELab Attendance", page_icon="📋")

# Paste your NEW Web app URL here
GAS_URL = "https://script.google.com/macros/s/AKfycbzmeJRoUS9nNfzxrkaP21__LdzCg4f_EG8Z4JRVfczZ78OYaeW36MJIbYHvvSOOx41K/exec"

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.title("🔐 FCELab Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if not username or not password:
                st.warning("Please enter both username and password!")
            else:
                with st.spinner("Authenticating..."):
                    try:
                        res = requests.post(GAS_URL, data={
                            "action": "login", 
                            "username": username, 
                            "password": password
                        })
                        data = res.json()
                        if data.get("status") == "success":
                            st.session_state.logged_in = True
                            st.session_state.name = data.get("name")
                            st.session_state.role = data.get("role")
                            st.rerun()
                        else:
                            st.error(data.get("message", "Invalid username or password!"))
                    except Exception as e:
                        st.error(f"Server connection error: {e}")

def attendance_page():
    col1, col2 = st.columns([8, 2])
    with col1:
        st.subheader(f"Hello, {st.session_state.name} 👋")
    with col2:
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()
            
    st.write(f"**Role:** {st.session_state.role}")

    with st.form(key="attendance_form"):
        st.subheader("1. Action")
        att_type = st.radio("What would you like to do?", ["Check In", "Check Out"])

        st.subheader("2. Face Verification")
        photo = st.camera_input("Take a photo")

        st.subheader("3. Location")
        location_data = streamlit_geolocation()

        st.write("---")
        submit_button = st.form_submit_button(label="Submit")

        if submit_button:
            if not photo:
                st.warning("Please take a photo for verification!")
            else:
                # Process Location
                location_str = "Location not found"
                if location_data and location_data.get('latitude') and location_data.get('longitude'):
                    lat = location_data['latitude']
                    lon = location_data['longitude']
                    location_str = f"https://www.google.com/maps?q={lat},{lon}"
                
                # Process Image
                image_base64 = base64.b64encode(photo.getvalue()).decode('utf-8')

                payload = {
                    "action": "attendance",
                    "name": st.session_state.name,
                    "role": st.session_state.role,
                    "type": att_type,
                    "location": location_str,
                    "image": image_base64
                }
                
                try:
                    with st.spinner(f'Recording {att_type}... Please wait!'):
                        res = requests.post(GAS_URL, data=payload)
                        data = res.json()
                        
                    if data.get("status") == "success":
                        st.success(f"{att_type} recorded successfully for {st.session_state.name}!")
                    else:
                        st.error(f"Storage error: {data.get('message')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

# Navigation
if not st.session_state.logged_in:
    login_page()
else:
    attendance_page()
