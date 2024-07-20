import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Drowsiness Detection Dashboard")

# Initialize session state for active button and view
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

# Sample data for the plots
data = pd.DataFrame({
    "Hour": list(range(1, 11)),
    "Drowsiness Level": [100, 200, 300, 400, 500, 600, 800, 900, 600, 300]
})

st.title('Hi, Supriyadi.')

st.header('You\'ve been drowsy 6 times today.')

today = datetime.today()

# Find the start of this week
start_of_week = today - timedelta(days=today.weekday())
# Generate dates for the week
week_dates = [(start_of_week + timedelta(days=i)).strftime('%d %b') for i in range(7)]

mobile_view = st.checkbox('Switch to Mobile View')

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
        for _ in range(6):
            st.info('Drowsiness detected at 10:03 a.m.')
        fig_day = px.line(data, x='Hour', y='Drowsiness Level', title='Drowsiness Trend Over the Day')
        st.plotly_chart(fig_day)
    elif view_selected == 'Week':
        week_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Drowsiness': [300, 400, 350, 500, 600, 700, 500]
        })
        fig_week = px.bar(week_data, x='Day', y='Drowsiness', title='Drowsiness Trend Over the Week')
        st.plotly_chart(fig_week)
    elif view_selected == 'Month':
        month_data = pd.DataFrame({
            'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'Drowsiness': [1500, 1600, 1700, 1800]
        })
        fig_month = px.bar(month_data, x='Week', y='Drowsiness', title='Drowsiness Trend Over the Month')
        st.plotly_chart(fig_month)
else:
    if st.session_state.view == 'Day':
        mon, tue, wed, thu, fri, sat, sun = st.columns(7)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, col in enumerate([mon, tue, wed, thu, fri, sat, sun]):
            col.button(week_dates[i], key=f'Day_{week_dates[i]}')

        for _ in range(6):
            st.info('Drowsiness detected at 10:03 a.m.')

        st.subheader('Daily Analytics')
        fig_day = px.line(data, x='Hour', y='Drowsiness Level', title='Drowsiness Trend Over the Day')
        st.plotly_chart(fig_day)
    elif st.session_state.view == 'Week':
        st.subheader('Weekly Analytics')
        week_data = pd.DataFrame({
            'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'Drowsiness': [300, 400, 350, 500, 600, 700, 500]
        })
        fig_week = px.bar(week_data, x='Day', y='Drowsiness', title='Drowsiness Trend Over the Week')
        st.plotly_chart(fig_week)
    elif st.session_state.view == 'Month':
        st.subheader('Monthly Analytics')
        month_data = pd.DataFrame({
            'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            'Drowsiness': [1500, 1600, 1700, 1800]
        })
        fig_month = px.bar(month_data, x='Week', y='Drowsiness', title='Drowsiness Trend Over the Month')
        st.plotly_chart(fig_month)


# General analytics applicable to all views
st.header('Overall Analytics')
st.subheader('You tend to feel most drowsy around 1:25 PM each day.')
fig_overall = px.line(data, x='Hour', y='Drowsiness Level', title='Overall Drowsiness Trend Over Time')
st.plotly_chart(fig_overall)

st.subheader("You've been 21% drowsier this week.")
week_data_overall = pd.DataFrame({
    'Week': ['Last Week', 'This Week'],
    'Drowsiness': [500, 600]
})
fig_week_overall = px.bar(week_data_overall, x='Week', y='Drowsiness', title='Weekly Drowsiness Comparison')
st.plotly_chart(fig_week_overall)
