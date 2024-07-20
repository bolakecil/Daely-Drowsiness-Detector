import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #ccc;
        color: white;
        font-weight: bold;
        padding: 8px 0;
    }
    div.stButton > button:hover {
        color: black;
        border: 1px solid black;
    }
    #havent figured this active action out yet, udah coba2 pke active button
    # .css-1qb1u2v-ButtonContainer.e1tzin5v1 {
    #     background-color: #4caf50; /* Change color for the selected view */
    #     color: white; /* White text for selected button */
    # }
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

# Find the start of this week (adjust `start_of_week` for different start days, e.g., Monday vs. Sunday)
# This assumes the week starts on Monday
start_of_week = today - timedelta(days=today.weekday())

# Generate dates for the week
week_dates = [(start_of_week + timedelta(days=i)).strftime('%d %b') for i in range(7)]

# Use session state to track which view is active
if 'view' not in st.session_state:
    st.session_state.view = 'Day'  # Default view

col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Day'):
        st.session_state.view = 'Day'
with col2:
    if st.button('Week'):
        st.session_state.view = 'Week'
with col3:
    if st.button('Month'):
        st.session_state.view = 'Month'

mon, tue, wed, thu, fri, sat, sun = st.columns(7)
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for i, col in enumerate([mon, tue, wed, thu, fri, sat, sun]):
    col.button(week_dates[i])

# # Display current view
# st.write(f'Current View: {st.session_state.view}')
    
for _ in range(6):
    st.info('Drowsiness detected at 10:03 a.m.')

mon, tue, wed, thu, fri, sat, sun = st.columns(7)

# ANALYTICS
st.header('Analytics')
st.subheader('You tend to feel most drowsy around 1:25 PM each day.')
fig = px.line(data, x='Hour', y='Drowsiness Level', title='Drowsiness Trend Over Time')
st.plotly_chart(fig)

st.subheader("You've been 21% drowsier this week.")
week_data = pd.DataFrame({
    'Week': ['Last Week', 'This Week'],
    'Drowsiness': [500, 600]
})
fig_week = px.bar(week_data, x='Week', y='Drowsiness', title='Weekly Drowsiness Comparison')
st.plotly_chart(fig_week)
