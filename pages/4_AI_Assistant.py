import streamlit as st

# Set the page configuration with the custom logo as the page icon
st.set_page_config(
    page_title="Your App Title",
    page_icon="static/Main_Logo.jpg",  # Path to your .jpg file
    layout="centered",  # Choose "centered" or "wide"
    initial_sidebar_state="expanded"  # Sidebar default state
)

# Add the custom logo at the top of the sidebar with a smaller size
st.sidebar.image("static/Main_Logo.jpg", width=100)  # Set the width in pixels

# Add navigation links or widgets below the logo
st.sidebar.title("Navigation")
selected_page = st.sidebar.radio("Go to", ["Page 1", "Page 2", "Page 3"])

# Main content based on selection
if selected_page == "Page 1":
    st.title("Welcome to Page 1")
    st.write("Content for Page 1 goes here.")
elif selected_page == "Page 2":
    st.title("Welcome to Page 2")
    st.write("Content for Page 2 goes here.")
elif selected_page == "Page 3":
    st.title("Welcome to Page 3")
    st.write("Content for Page 3 goes here.")