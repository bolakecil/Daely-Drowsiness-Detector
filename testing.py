import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
from PIL import Image
import base64
import io
import toml
import calendar

st.set_page_config(page_title="Drowsiness Detection Dashboard")

# Load secrets from TOML file
with open("secrets.toml", "r") as f:
    secrets = toml.load(f)

firebase_config = secrets["firebase"]

if not firebase_admin._apps:
    firebase_credentials = {
        "type": firebase_config["type"],
        "project_id": firebase_config["project_id"],
        "private_key_id": firebase_config["private_key_id"],
        "private_key": firebase_config["private_key"].replace("\\n", "\n"),
        "client_email": firebase_config["client_email"],
        "client_id": firebase_config["client_id"],
        "auth_uri": firebase_config["auth_uri"],
        "token_uri": firebase_config["token_uri"],
        "auth_provider_x509_cert_url": firebase_config["auth_provider_x509_cert_url"],
        "client_x509_cert_url": firebase_config["client_x509_cert_url"]
    }
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred, {'databaseURL': firebase_config["database_url"]})

ref = db.reference('/')

def preprocess_base64_image(base64_string):
    """
    Returns image from base64 encoded image
    """
    image_data = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_data))
    return image

def get_drowsiness_data():
    data = ref.get()
    if data is None:
        return []
    parsed_data = []
    for key, value in data.items():
        if value.get('prediction') == 'Fatigue Subjects': 
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
            # value['image'] = preprocess_base64_image(value['image'])
            parsed_data.append(value)
    return parsed_data

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
    div.stButton > button:focus:not(:active) {
        color: #FFFFFF;
    }
    .st-emotion-cache-uzeiqp img {
        max-width: none;
    }
</style>
""", unsafe_allow_html=True)

def calculate_today_drowsy_occurrences(data):
    today = datetime.today().date()
    today_data = [entry for entry in data if entry['timestamp'].date() == today]
    return len(today_data)

drowsiness_data = get_drowsiness_data()
drowsy_today = calculate_today_drowsy_occurrences(drowsiness_data)

st.title('Hi, Supriyadi.')
st.header(f'You\'ve been drowsy {drowsy_today} times today.')

today = datetime.today()
start_of_week = today - timedelta(days=today.weekday()) # Find the start of this week
week_dates = [(start_of_week + timedelta(days=i)).strftime('%d %b') for i in range(7)] # Generate dates for the week
mobile_view = st.checkbox('Switch to Mobile View')

def aggregate_weekly_data(data):
    df = pd.DataFrame(data)
    df['week'] = df['timestamp'].dt.isocalendar().week
    df['day'] = df['timestamp'].dt.day_name()
    weekly_data = df.groupby('day').size().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).reset_index(name='count')
    return weekly_data

def aggregate_monthly_data(data, selected_month):
    df = pd.DataFrame(data)
    df = df[df['timestamp'].dt.month == selected_month]
    df['day'] = df['timestamp'].dt.day
    daily_data = df.groupby('day').size().reset_index(name='count')

    max_day = pd.Timestamp(year=2024, month=selected_month, day=1).days_in_month
    all_days = pd.DataFrame({'day': range(1, max_day + 1)})
    daily_data = pd.merge(all_days, daily_data, on='day', how='left').fillna(0)
    return daily_data

if mobile_view:
    today_str = today.strftime('%d %b')
    default_day_index = week_dates.index(today_str)
    view_selected = st.selectbox('Select View', ['Day', 'Week', 'Month'])
    if view_selected == 'Day':
        day_selected = st.selectbox('Select Day', week_dates, index=default_day_index)
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
            
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = today.strftime('%d %b')  # Default to today's date

def handle_monthly_view(data, current_year):
    months = list(calendar.month_name)[1:]  # Get month names and skip the first empty entry
    current_month = datetime.now().month
    month_selected = st.selectbox('Select Month', months, index=current_month-1)  # Use month names instead of numbers
    month_index = months.index(month_selected) + 1  # Get the index of the selected month (1-based)
    monthly_day_data = aggregate_monthly_data(data, month_index)
    return monthly_day_data, month_selected

if mobile_view:
    if view_selected == 'Day':
        day_data = [entry for entry in drowsiness_data if entry['timestamp'].strftime('%d %b') == day_selected]
        day_data.sort(key=lambda x: x['timestamp'], reverse=True)

        if 'page' not in st.session_state:
            st.session_state.page = 0  

        items_per_page = 6  

        def next_page():
            st.session_state.page += 1

        def prev_page():
            st.session_state.page -= 1

        if not day_data:
            st.info(f"No drowsiness detected on {day_selected}")
        else:
            start_index = st.session_state.page * items_per_page
            end_index = start_index + items_per_page
            displayed_data = day_data[start_index:end_index]

            for entry in displayed_data:
                timestamp = entry['timestamp'].strftime('%I:%M %p')
                image_base64 = entry.get('image')
                if image_base64:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px; background-color: #e1f5fe; border-left: 5px solid #2196f3; padding: 8px; border-radius: 5px;">
                            <div style="flex: 1;">
                                <strong>Drowsiness detected at {timestamp}</strong>
                            </div>
                            <div style="flex: 0;">
                                <img src="data:image/png;base64,{image_base64}" alt="Drowsiness Image" style="height: 60px; object-fit: contain; margin-left: 10px;">
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px; background-color: #e1f5fe; border-left: 5px solid #2196f3; padding: 8px; border-radius: 5px;">
                            <div style="flex: 1;">
                                <strong>Drowsiness detected at {timestamp}</strong>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            total_pages = len(day_data) // items_per_page + (1 if len(day_data) % items_per_page != 0 else 0)
            st.write(f"Page {st.session_state.page + 1} of {total_pages}")

            col1, col2 = st.columns(2)
            if st.session_state.page > 0:
                with col1:
                    st.button("Previous", on_click=prev_page)
            if end_index < len(day_data):
                with col2:
                    st.button("Next", on_click=next_page)

        if day_data:
            fig_day = px.histogram(day_data, x='timestamp', title='Drowsiness Detections Over the Day', nbins=24)
            st.plotly_chart(fig_day)
    elif view_selected == 'Week':
        week_data = aggregate_weekly_data(drowsiness_data)
        fig_week = px.bar(week_data, x='day', y='count', title='Drowsiness Detections Over the Week')
        st.plotly_chart(fig_week)
    elif view_selected == 'Month':
        monthly_day_data, month_selected = handle_monthly_view(drowsiness_data)
        if monthly_day_data.empty:
            st.write("No drowsiness data available for this month.")
        else:
            fig_month_daily = px.bar(monthly_day_data, x='day', y='count', title=f'Drowsiness Detections for Month {month_selected}')
            st.plotly_chart(fig_month_daily)
else:
    if st.session_state.view == 'Day':
        mon, tue, wed, thu, fri, sat, sun = st.columns(7)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i, col in enumerate([mon, tue, wed, thu, fri, sat, sun]):
             if col.button(week_dates[i], key=f'Day_{week_dates[i]}'):
                st.session_state.selected_date = week_dates[i]
        day_data = [entry for entry in drowsiness_data if entry['timestamp'].strftime('%d %b') == st.session_state.selected_date]
        day_data.sort(key=lambda x: x['timestamp'], reverse=True)

        if 'page' not in st.session_state:
            st.session_state.page = 0  

        items_per_page = 8  

        def next_page():
            st.session_state.page += 1

        def prev_page():
            st.session_state.page -= 1

        if not day_data:
            st.info(f"No drowsiness detected on {st.session_state.selected_date}")
        else:
            start_index = st.session_state.page * items_per_page
            end_index = start_index + items_per_page
            displayed_data = day_data[start_index:end_index]

            for entry in displayed_data:
                timestamp = entry['timestamp'].strftime('%I:%M %p')
                image_base64 = entry.get('image')
                if image_base64:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px; background-color: #e1f5fe; border-left: 5px solid #2196f3; padding: 8px; border-radius: 5px;">
                            <div style="flex: 1;">
                                <strong>Drowsiness detected at {timestamp}</strong>
                            </div>
                            <div style="flex: 0;">
                                <img src="data:image/png;base64,{image_base64}" alt="Drowsiness Image" style="width: 80px; object-fit: contain; margin-left: 10px;">
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; margin-bottom: 10px; background-color: #e1f5fe; border-left: 5px solid #2196f3; padding: 8px; border-radius: 5px;">
                            <div style="flex: 1;">
                                <strong>Drowsiness detected at {timestamp}</strong>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            total_pages = len(day_data) // items_per_page + (1 if len(day_data) % items_per_page != 0 else 0)
            st.write(f"Page {st.session_state.page + 1} of {total_pages}")

            col1, col2 = st.columns(2)
            if st.session_state.page > 0:
                with col1:
                    st.button("Previous", on_click=prev_page)
            if end_index < len(day_data):
                with col2:
                    st.button("Next", on_click=next_page)
        if day_data:
            st.subheader('Daily Analytics')
            fig_day = px.histogram(day_data, x='timestamp', title='Drowsiness Detections Over the Day', nbins=24)
            st.plotly_chart(fig_day)
    elif st.session_state.view == 'Week':
        st.subheader('Weekly Analytics')
        week_data = aggregate_weekly_data(drowsiness_data)
        fig_week = px.bar(week_data, x='day', y='count', title='Drowsiness Detections Over the Week')
        st.plotly_chart(fig_week)
    elif st.session_state.view == 'Month':
        current_year = datetime.now().year
        monthly_day_data, month_selected = handle_monthly_view(drowsiness_data, current_year)
        if monthly_day_data.empty:
            st.write("No drowsiness data available for this month.")
        else:
            fig_month_daily = px.bar(monthly_day_data, x='day', y='count',
                                    title=f'Drowsiness Detections for {month_selected}',
                                    labels={'day': 'Day of the Month', 'count': 'Number of Drowsiness Events'})
            fig_month_daily.update_layout(xaxis_type='category')
            st.plotly_chart(fig_month_daily)
        
def calculate_weekly_change(data):
    df = pd.DataFrame(data)
    df['week'] = df['timestamp'].dt.isocalendar().week
    current_week = datetime.now().isocalendar()[1]
    current_week_data = df[df['week'] == current_week]
    last_week_data = df[df['week'] == current_week - 1]
    current_week_count = len(current_week_data)
    last_week_count = len(last_week_data)
    if last_week_count == 0:
        return 0
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
drowsy_period = get_highest_drowsiness_period(drowsiness_data)
st.header('Overall Analytics')
st.subheader(f"You tend to feel most drowsy around {drowsy_period} each day.")
fig_overall = px.histogram(drowsiness_data, x='timestamp', title='Overall Drowsiness Detections Over Time', nbins=24)
st.plotly_chart(fig_overall)

change_percentage = calculate_weekly_change(drowsiness_data)
if change_percentage == 0:
    st.subheader("No data from last week to compare.")
else:
    st.subheader(f"You've been {change_percentage}% drowsier this week.")
week_data_overall = aggregate_weekly_data(drowsiness_data)
fig_week_overall = px.bar(week_data_overall, x='day', y='count', title='Weekly Drowsiness Comparison')
st.plotly_chart(fig_week_overall)
