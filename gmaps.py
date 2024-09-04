import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from datetime import date
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import linear_model
import sqlite3 as sql
from matplotlib import pyplot as plt
import re

st.set_page_config()
RegisterSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()

# # Get Model Accuracy
# def linearRegression(X_train, X_test, Y_train, Y_test):  
#     from sklearn.linear_model import LinearRegression 
#     regressor = LinearRegression() 
#     regressor.fit(X_train,Y_train)         
#     score = regressor.score(X_test, Y_test) 
#     return score 


# On Successful Login
def maps_page():
    # Optimal path mapping section
    st.header("Select delivery locations")
    HtmlFile = open("optimal_path_mapping.html", 'r', encoding='utf-8')
    source_code = HtmlFile.read() 
    components.html(source_code, height=540)

    # Intializing Road ID for following roads
    roads = {
        'Padil-RailwayGate': 1, 'Padil-Alape': 2, 'Alape-Nagori': 3, 
        'Nagori-RailwayStation': 4, 'Alape-RailwayStation': 5, 'RailwayGate-RailwayStation': 6
    }
    travel_time_without_traffic = { 1: 40, 2: 20, 3: 100, 4: 110, 5: 150, 6: 180 } 

    # Traffic Congestion Prediction Section
    st.header("Check Traffic Congestion")
    data = pd.read_csv("data//traffic_data.csv")
    x = data.drop(["Road","TravelTime"],axis=1)
    y = data['TravelTime'] 
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=101)
    lm = linear_model.LinearRegression()
    lm.fit(x_train,y_train)
    # print(linearRegression(x_train, x_test, y_train, y_test))     # To check Model Accuracy

    # Retrieving necessary variables for prediction
    selected_locs = st.multiselect('Select locations to check traffic',(roads.keys()))
    day_number = datetime.today().isoweekday()
    todays_date = date.today()
    month_number = todays_date.month
    today = datetime.today()
    now = datetime.now()
    current_time = now.strftime("%H.%M")
    time_for_dataset = float(current_time)
    prediction_list = []
    without_traffic_list = []

    # Predicting traffic for selected roads
    for i in range(len(selected_locs)):
        dictionary_data  = {'Road_ID':[roads.get(selected_locs[i])],'Day':[day_number],'Month':[month_number],'Time':[time_for_dataset]}
        predicting_data = pd.DataFrame(dictionary_data)
        prediction = lm.predict(predicting_data)
        if prediction <= travel_time_without_traffic.get(roads.get(selected_locs[i])):
            st.write(selected_locs[i], ": No traffic")
        elif prediction > travel_time_without_traffic.get(roads.get(selected_locs[i]))+20:
            st.write(selected_locs[i], ": Heavy traffic")
        else:
            st.write(selected_locs[i], ": Mild traffic")
        prediction_list.append(int(prediction))
        without_traffic_list.append(travel_time_without_traffic.get(roads.get(selected_locs[i])))

    # Plotting bar graph for Travel time without traffic vs Predicted Travel time for current time for selected roads
    plt.style.use("fivethirtyeight")
    fig = plt.figure(figsize = (14, 8))
    x_indexes = np.arange(len(selected_locs))
    width = 0.25
    plt.bar(x_indexes-width,without_traffic_list,width=width,color="#008fd5",label="Travel time without traffic")
    plt.bar(x_indexes,prediction_list,width=width,color="#e5ae38",label="Predicted travel time for current time")
    plt.xticks(ticks=x_indexes, labels=selected_locs)
    plt.title("Travel Time for selected roads")
    plt.xlabel("Roads")
    plt.ylabel("Travel Time in seconds")
    plt.legend()
    plt.tight_layout()
    st.pyplot(fig)

    # Data contribution for Dataset
    st.header("Contribute to improve traffic prediction")
    contributing_loc = st.selectbox('Select location',(roads.keys()))
    road_id = roads.get(contributing_loc)
    st.text("Click Start to begin the timer")
    but1,but2 = st.columns([1,1])
    start = but1.button("Start")
    stop = but2.button("Stop")
    watch = 0
    time_id = 1
    ph = st.empty()
    # Store travel time in database
    if start:
        while True:
            ph.metric("Timer", f"{watch} seconds")
            time.sleep(1)
            with sql.connect("gmapsdb.db") as conn:
                c = conn.cursor()
                time_id = 1
                c.execute(""" UPDATE travel_time 
                        SET time = ?
                        WHERE time_id = ?
                        """,(watch,time_id))
                conn.commit()
                watch+=1
            if stop:
                break

    # Updating the dataset
    with sql.connect("gmapsdb.db") as conn:
        c = conn.cursor()
        travel_time = c.execute("""
            SELECT time FROM travel_time WHERE time_id=?
            """,[time_id]).fetchall()
    st.text("Click submit to contribute travelling time for selected location")
    if st.button("Submit"):
        contribute_data = {
            "Road_ID":[road_id], "Road":[contributing_loc], "Day":[day_number], 
            "Month":[month_number], "Time":[time_for_dataset], "TravelTime":[travel_time[0][0]]
        }
        contribute_data = pd.DataFrame(contribute_data)
        contribute_data.to_csv("data//traffic_data.csv", mode='a', header = False, index= False)
        st.success("Successfully Submitted")
    # Logout
    if st.button ("Log Out", key="logout", on_click=LoggedOut_Clicked):
        show_login_page()


# Ending Session
def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False


# Validate user credentials in database
def login(username, password):
    with sql.connect("gmapsdb.db") as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM EMPLOYEE WHERE emp_name=? and emp_password=?
            """,(username, password))
        check = c.fetchall()
        if len(check) > 0:
            return True

# Creating session
def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        st.session_state['loggedIn'] = True
    else:
        st.session_state['loggedIn'] = False
        st.error("Invalid user name or password")


# Startup page
def show_login_page():
    # Login Section
    with loginSection:
        if st.session_state['loggedIn'] == False:
            st.title("Login")
            userName = st.text_input (label="", value="", placeholder="Enter your username")
            password = st.text_input (label="", value="",placeholder="Enter password", type="password")
            st.button ("Login", on_click=LoggedIn_Clicked, args= (userName, password))

            # Registration Section
            st.title("Employee Registration")
            with st.form("Employee form"):
                regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                col1, col2 = st.columns(2)
                name = col1.text_input(placeholder="Username", label="")
                phone = col2.text_input(placeholder="Mobile No.", label="")
                address = st.text_area(label="", placeholder="Address")
                email = st.text_input(placeholder="Email ID", label="")
                password = st.text_input (label="", value="",placeholder="Password", type="password")
                register = st.form_submit_button("Register")
                if register == True:
                    if len(phone) != 10:
                        st.error("Invalid Mobile Number")
                    elif not re.fullmatch(regex, email):
                        st.error("Invalid  Email ID")
                    else:
                        with sql.connect("gmapsdb.db") as conn:
                            c = conn.cursor()
                            c.execute("""
                                SELECT * FROM EMPLOYEE WHERE emp_name=?
                                """,[name])
                            check = c.fetchall()
                            if len(check) > 0:
                                st.warning("Username already taken")
                            else:
                                c.execute("""
                                    INSERT INTO EMPLOYEE(emp_name, emp_address, emp_phone, emp_email, emp_password) VALUES(?,?,?,?,?)
                                    """, (name, address, phone, email, password))
                                conn.commit()
                                st.success("Registered sucessfully..")
                            

# first run will have nothing in session_state
def main():
    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False
        
        show_login_page() 
    else:
        if st.session_state['loggedIn']: 
            maps_page()
        else:
            show_login_page()

if __name__ == '__main__':
    main()