# Core pkgs
import streamlit as st
import streamlit.components.v1 as stc
import numpy as np


from inc import run_inc_app
from exp import run_exp_app
from reg import run_reg_app


HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">Chapter 6: National Income and Product Accounts</h1>
    </div>
    """
stc.html(HTML_BANNER)

def run_home_app():
    
    st.write("""
    Welcome to the Exploration of National Income and Product Accounts Data!
    """)
    
    st.markdown("""
    **Instructions:**
    
    1. Use the **Menu** on the left sidebar to navigate through the application.
    2. Choose from the following options:
        - **Home**: You're currently on the home page which provides a brief overview.
        - **Expenditure**: Dive deep into expenditure data and analytics.
        - **Income**: Explore data related to income statistics.
        - **Regions**: Discover insights by region.
    3. Depending on your selection, the main content area will update to display relevant information and visualizations.
    4. Navigate back to **Home** anytime to see these instructions again.
    """)



def main():
    menu = ["Home","Expenditure","Income","Regions"]
    choice = st.sidebar.selectbox("Menu",menu)

    if choice == "Home":
        run_home_app()
    elif choice == "Expenditure":
        run_exp_app()
    elif choice == "Income":
        run_inc_app()
    elif choice == "Regions":
        run_reg_app()
    else:
        run_home_app()


if __name__ == '__main__':
    main() 
