import streamlit as st
import requests
import base64
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(page_title="Lab Attendance System", page_icon="📋")
st.title("Attendance - Fuels and Clean Energy Laboratory")

# Dán Web app URL MỚI CỦA ÔNG vào đây
GAS_URL = "https://script.google.com/macros/s/AKfycbxUj2TdhNlfr_DhpOxknZlATJhwbH_6bztS6uF26mpM1SJ88i_NKSdbN4bH0nhEs0J5/exec"

with st.form(key="attendance_form"):
    st.subheader("1. Information")
    name = st.text_input("Full Name")
    role = st.selectbox("Role", ["PhD / Master Student", "Undergraduate Student", "Lecturer / Professor", "Guest"])
    status = st.radio("Status", ["Present", "Late", "Excused Absence", "Unexcused Absence"])

    st.subheader("2. Face Verification")
    st.info("Please allow camera access and take a clear photo of your face.")
    photo = st.camera_input("Take a photo")

    st.subheader("3. Location")
    st.info("Click the target icon below to capture your current location (allow location access in browser).")
    location_data = streamlit_geolocation()

    st.write("---")
    submit_button = st.form_submit_button(label="Submit Attendance")

    if submit_button:
        # Validate inputs
        if not name.strip():
            st.warning("Please enter your Full Name!")
        elif not photo:
            st.warning("Please take a photo for verification!")
        else:
            # Process Location
            location_str = "No location captured"
            if location_data and location_data.get('latitude') and location_data.get('longitude'):
                lat = location_data['latitude']
                lon = location_data['longitude']
                location_str = f"Lat: {lat}, Lon: {lon}"
            
            # Process Image (Encode to Base64)
            image_bytes = photo.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Prepare data payload
            data = {
                "name": name.strip(),
                "role": role,
                "status": status,
                "location": location_str,
                "image": image_base64
            }
            
            # Send to Google Apps Script
            try:
                with st.spinner('Uploading data and photo... Please wait!'):
                    response = requests.post(GAS_URL, data=data)
                    
                if response.text == "Success":
                    st.success(f"Attendance recorded successfully for {name}!")
                else:
                    st.error(f"Failed to save. Server response: {response.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")
