#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#NOTES ON USING STREAMLIT!:
#region CLICK HERE TO EXPAND SECTION



#======================================================
#CACHING
# > You will likely want to cache your sql database connection. Luckily, streamlit has a database connection function that handles caching for you: 
#conn = st.connection("my_database")
#df = conn.query("select * from my_table")
#st.dataframe(df)

# > I'm thinking that I'll likely want to have a section at the top of my main app home page file where the database connection is made/cached

# > FOR EACH TIME YOU MAKE A REFERENCE TO A DATABASE TABLE AND PULL DATA, GO AHEAD AND CACHE IT SO THAT YOU DON'T HAVE TO PULL ALL OF THIS DATA MULTIPLE TIMES! 

# > BE CAREFUL WITH CACHING THO, BECAUSE IF YOU CHANGE THE DATA SOURCE IT COULD CAUSE ERRORS? KEEP THIS IN MIND WHEN YOU START BUILDING THIS APP! DOESN'T SOUND LIKE IT WILL BE A PROBLEM THO

# > For the future, you will likely want to use "secrets" to setup a username/password for accessing your database! This is explained at the end of the "Advanced Concepts" section





#======================================================
#SESSIONS: 
# > You already understand this concept from your web dev days!
# > Because streamlit works by re-running your python file every time you interact with a component, you will want to strategically save data to sessions after each component is interacted with to save time/processing power. This will also prevent users having to re-specify data when using components











#======================================================
#PAGES: 
# > You will likley want to create seperate "pages" for each of the different modules that you'll want to program into the application (i.e. Performance Tracking, Paperwork Tracking, Equipment Tracking, etc.)
# > You will need to setup the app where different pages will be available based on user type, and 





#======================================================
#COLUMNS: 
# > You will want to use the column fuction shown in the "basic concepts" section to add widgets side by side on the web app page. 


#======================================================
#CUSTOM COMPONENTS: 
# > If you want to use a component that Streamlit doesn't offer, there is a large community of additional components created by the community at streamlit.io/components
# > You can also create your own components with streamlit's components API


#======================================================
#DEPLOYING YOUR APP: 
# > Go to the "Share Your App" section of the "Create an App" tutorial for a quick guide here



#======================================================
#GENERAL IDEAS:
# > You may want to use a "Sidebar" instead of a navbar at the top of the page? At least at first maybe, because it is a built in component to streamlit









#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#SECTION #1 | IMPORTING LIBRARIES:
#region CLICK HERE TO EXPAND SECTION

import streamlit as st
import datetime



#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#SECTION #2 | SETTING UP THE PAGE CONFIGURATIONS: 
#region CLICK HERE TO EXPAND SECTION

st.set_page_config(
    #============================================================================================================================================================
    #Web browser tab title and logo:
    page_title="Pyramid Construction Analytics",
    page_icon="static/Main_Logo.jpg",

    #============================================================================================================================================================
    #App page layout:
    layout="wide",  # Choose "centered" or "wide"
    initial_sidebar_state="expanded"  # Sidebar default state
)

#For some reason, it looks like streamlit wants me to import the cookie manager library after the page configuration setting
from streamlit_cookies_manager import EncryptedCookieManager
#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#SECTION #3 | SETTING UP THE SIDEBAR:
#region CLICK HERE TO EXPAND SECTION

# Add the custom logo to the sidebar
#st.sidebar.image("static/Main_Logo_With_Name.jpg", width=275)


#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#SECTION #4 | DEFINING FUNCTIONS/VARIABLES FOR USE THROUGHOUT SCRIPT:
#region CLICK HERE TO EXPAND SECTION

#===================================================================================================================================================================
#Creating a cookie manager for creating/storing cookies in our script
cookies = EncryptedCookieManager(
    prefix="my_app",  # Optional: adds a prefix to all cookies for namespacing
    password="my_secret_password"  # Change this to a strong password
)

# Initialize the cookie manager
if not cookies.ready():
    st.stop()


#===================================================================================================================================================================
#Creating a dictinoary of user credentials to use for validating login info: 
USER_CREDENTIALS = {
    "admin": "password123",
    "user1": "password1",
    "user2": "password2"
}


#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#<>
#<>
#USER PAGES: 
#<>
#<>
#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#LOGIN FORM SECTION:
#region CLICK HERE TO EXPAND SECTION

#===================================================================================================================================================================
#Adding a title to our login form: 
st.title("Login Below to Get Started!")

#===================================================================================================================================================================
#If the user has logged in in the past week, then their credentials will be saved in a cookie already and we want to disply a success message:
if cookies['userName']!=None: 
    username=cookies['userName']
    password=cookies['password']
    userPosition=cookies['userPosition']

    st.success(f"You are already logged in from your previous session. Welcome back, {username}!")

#===================================================================================================================================================================
#Creating our login form: 
with st.form("login_form"):
    #If the user's credentials are already saved in a cookie, then we will want their username to already be populated in the 
    if cookies['userName']!=None: 
        username = st.text_input("Username", value=username)
        password = st.text_input("Password", type="password", value=password)
        submit_button = st.form_submit_button("Login")

    else: 
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")

#===================================================================================================================================================================
#Checking credentials
if submit_button:
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        st.success(f"Login Successful. Welcome, {username}!")
        st.session_state.userName = username
        st.session_state.userPosition = 'Operations Manager'

        #Saving our user credentials as cookies in the browser: 
        cookies['userName'] = username
        cookies['password'] = password
        cookies['userPosition'] = 'Operations Manager'
        
    else:
        st.error("Invalid username or password, please try again!")


#===================================================================================================================================================================
#Adding a note at the bottom of the login box:
st.markdown(
    """
    *If you have not been provided with a login/password, contact your system administrator to get an account setup. Click on the "Help" module in the sidebar to learn more.
""")


#endregion


#========================================================================================================================================================================================================================================
#========================================================================================================================================================================================================================================
#Writing up our "What is Pyramid Analytics" section:
#region CLICK HERE TO EXPAND SECTION

#===================================================================================================================================================================
#Adding some spacing and a divider:
st.write("")
st.write("")
st.write("")
st.write("")
st.divider()


#===================================================================================================================================================================
#Adding our writeup:
st.title("What is Pyramid Analytics?")
st.markdown(
    """
    Pyarmid Analytics is a data management platform that helps contractors in the heavy civil space to manage and analyze their data.
    **👈 Select "Learn More" from the sidebar** to learn more about what Pyarmid Analytics can do!
    ### Pyramid Analytics Features
    - Tracks key performance indicatiors (KPIs) for various departments of your company, including: operations, project management, estimating, and equipment
    - Includes a customizable KPI based incentive system for your company's employees
    - Manages your company's historical data, and provides insights on areas where each department can improve
    - Utilizes customized AI tools to help employees navigate and act on their data
    
"""
)

#endregion













