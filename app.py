# Core pkgs
import streamlit as st
import streamlit.components.v1 as stc

# Import Mini Apps
#from stock_app import run_stock_app
#from stock_tsx import run_tsx_app
from inc import run_inc_app
from exp import run_exp_app
from reg import run_reg_app


HTML_BANNER = """
    <div style="background-color:#464e5f;padding:10px;border-radius:10px">
    <h1 style="color:white;text-align:center;">Chapter 5: National Income-Output</h1>
    </div>
    """
stc.html(HTML_BANNER)

def run_home_app():
    
    st.write("""
    Welcome to the Expenditure-Output Model and GDP Data Exploration!
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
