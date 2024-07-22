import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import db, credentials
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not firebase_admin._apps:
    cred = credentials.Certificate('credentials.json')
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
ref = db.reference('/')

def get_drowsiness_data():
    data = ref.get()

    if data is None:
        return []

    parsed_data = []
    for key, value in data.items():
        if value.get('prediction') == 'Active Subjects': #harusnya Fatigue Subjects
            time_data = value['time']
            timestamp = datetime(
                int(time_data['year']),
                int(time_data['month']),
                int(time_data['date']),
                int(time_data['hour']),
                int(time_data['minute']),
                int(time_data['second'])
            )
            value['timestamp'] = timestamp
            parsed_data.append(value)
    return parsed_data


st.set_page_config(page_title="Drowsiness Detection Dashboard")

if 'active_button' not in st.session_state:
    st.session_state.active_button = 'Day'  # Default active button and view
if 'view' not in st.session_state:
    st.session_state.view = 'Day'  # Default view

def set_active_button(button_name):
    st.session_state.active_button = button_name
    st.session_state.view = button_name

st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #68C4FF;
        background-color: #68C4FF;
        color: #FFFFFF;
        font-weight: bold;
        padding: 8px 0;
    }
    div.stButton > button:hover {
        color: #68C4FF;
        background-color: #FFFFFF;
        border: 1px solid #68C4FF;
    }
</style>
""", unsafe_allow_html=True)

st.title('Hi, Supriyadi.')

st.header('You\'ve been drowsy 6 times today.')

today = datetime.today()

# Find the start of this week
start_of_week = today - timedelta(days=today.weekday())
# Generate dates for the week
week_dates = [(start_of_week + timedelta(days=i)).strftime('%d %b') for i in range(7)]

mobile_view = st.checkbox('Switch to Mobile View')

drowsiness_data = get_drowsiness_data()

def aggregate_weekly_data(data):
    df = pd.DataFrame(data)
    df['week'] = df['timestamp'].dt.isocalendar().week
    df['day'] = df['timestamp'].dt.day_name()
    weekly_data = df.groupby('day').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')
    return weekly_data

def aggregate_monthly_data(data):
    df = pd.DataFrame(data)
    df['month'] = df['timestamp'].dt.month
    df['week'] = df['timestamp'].dt.isocalendar().week
    monthly_data = df.groupby('week').size().reset_index(name='count')
    return monthly_data

if mobile_view:
    view_selected = st.selectbox('Select View', ['Day', 'Week', 'Month'])
    day_selected = st.selectbox('Select Day', week_dates)
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button('Day', key='Day_btn'):
            set_active_button('Day')
    with col2:
        if st.button('Week', key='Week_btn'):
            set_active_button('Week')
    with col3:
        if st.button('Month', key='Month_btn'):
            set_active_button('Month')

if mobile_view:
    if view_selected == 'Day':
        st.write(f'Selected Day: {day_selected}')
        for entry in drowsiness_data:
            if entry['timestamp'].strftime('%d %b') == day_selected:
                st.info(f"Drowsiness detected at {entry['timestamp'].strftime('%I:%M %p')}")
        fig_day = px.histogram(drowsiness_data, x='timestamp', title='Drowsiness Detections Over the Day', nbins=24)
        st.plotly_chart(fig_day)
    elif view_selected == 'Week':
        week_data = aggregate_weekly_data(drowsiness_data)
        fig_week = px.bar(week_data, x='day', y='count', title='Drowsiness Detections Over the Week')
        st.plotly_chart(fig_week)
    elif view_selected == 'Month':
        month_data = aggregate_monthly_data(drowsiness_data)
        fig_month = px.bar(month_data, x='week', y='count', title='Drowsiness Detections Over the Month')
        st.plotly_chart(fig_month)
else:
    if st.session_state.view == 'Day':
        mon, tue, wed, thu, fri, sat, sun = st.columns(7)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, col in enumerate([mon, tue, wed, thu, fri, sat, sun]):
            col.button(week_dates[i], key=f'Day_{week_dates[i]}')

        for entry in drowsiness_data:
            if entry['timestamp'].strftime('%d %b') in week_dates:
                st.info(f"Drowsiness detected at {entry['timestamp'].strftime('%I:%M %p')}")
        
        st.subheader('Daily Analytics')
        fig_day = px.histogram(drowsiness_data, x='timestamp', title='Drowsiness Detections Over the Day', nbins=24)
        st.plotly_chart(fig_day)
    elif st.session_state.view == 'Week':
        st.subheader('Weekly Analytics')
        week_data = aggregate_weekly_data(drowsiness_data)
        fig_week = px.bar(week_data, x='day', y='count', title='Drowsiness Detections Over the Week')
        st.plotly_chart(fig_week)
    elif st.session_state.view == 'Month':
        st.subheader('Monthly Analytics')
        month_data = aggregate_monthly_data(drowsiness_data)
        fig_month = px.bar(month_data, x='week', y='count', title='Drowsiness Detections Over the Month')
        st.plotly_chart(fig_month)
        
def calculate_weekly_change(data):
    df = pd.DataFrame(data)
    df['week'] = df['timestamp'].dt.isocalendar().week
    current_week = datetime.now().isocalendar()[1]
    
    current_week_data = df[df['week'] == current_week]
    last_week_data = df[df['week'] == current_week - 1]
    
    current_week_count = len(current_week_data)
    last_week_count = len(last_week_data)
    
    if last_week_count == 0:
        return "No data from last week to compare."
    
    change_percentage = ((current_week_count - last_week_count) / last_week_count) * 100
    return change_percentage

def get_highest_drowsiness_period(data):
    df = pd.DataFrame(data)
    df['time_period'] = pd.cut(df['timestamp'].dt.hour, #edit as needed, interval 1h or 2h
                               bins=[0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
                               labels=['22:00-00:00', '00:00-02:00', '02:00-04:00', 
                                       '04:00-06:00', '06:00-08:00', '08:00-10:00', 
                                       '10:00-12:00', '12:00-14:00', '14:00-16:00', 
                                       '16:00-18:00', '18:00-20:00', '20:00-22:00'], 
                               right=False)
    highest_period = df['time_period'].value_counts().idxmax()
    max_count = df['time_period'].value_counts().max()
    return highest_period

# General analytics applicable to all views
drowsy_period=get_highest_drowsiness_period(drowsiness_data)
st.header('Overall Analytics')
st.subheader(f"You tend to feel most drowsy around {drowsy_period} each day." )
fig_overall = px.histogram(drowsiness_data, x='timestamp', title='Overall Drowsiness Detections Over Time', nbins=24)
st.plotly_chart(fig_overall)

change_percentage=calculate_weekly_change(drowsiness_data)
st.subheader(f"You've been {change_percentage}% drowsier this week.")
week_data_overall = aggregate_weekly_data(drowsiness_data)
fig_week_overall = px.bar(week_data_overall, x='day', y='count', title='Weekly Drowsiness Comparison')
st.plotly_chart(fig_week_overall)
