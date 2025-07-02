import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
import os

# 🔁 Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="datarefresh")

st.set_page_config(page_title="Live Weather Dashboard", layout="wide")
st.title("🌤️ Live Weather Dashboard")
st.caption("Streaming from Arduino MKR + IoT Carrier")

# Path to your data file
csv_path = "deviceCALE_2025-06-30.csv"

# Clear any cached data to ensure fresh reads
if 'last_mod_time' not in st.session_state:
    st.session_state.last_mod_time = 0

if os.path.exists(csv_path):
    try:
        # Read CSV with timestamp parsing
        df = pd.read_csv(csv_path, parse_dates=["timestamp"])
        current_mod_time = os.path.getmtime(csv_path)

        # Debug info
        st.sidebar.write(f"📄 File size: {len(df)} rows")
        st.sidebar.write(f"🕐 Last modified: {datetime.fromtimestamp(current_mod_time).strftime('%H:%M:%S')}")
        st.sidebar.write(f"🔄 Current time: {datetime.now().strftime('%H:%M:%S')}")

        if len(df) == 0:
            st.warning("CSV file is empty. Waiting for data...")
        else:
            # Sort and clean data
            df = df.sort_values('timestamp').reset_index(drop=True)
            df = df.dropna(subset=['timestamp'])

            # Detect pressure unit
            avg_pressure = df['pressure'].mean()
            if avg_pressure > 500:
                pressure_unit = "hPa"
                pressure_label = "Pressure (hPa)"
            else:
                pressure_unit = "kPa"
                pressure_label = "Pressure (kPa)"

            # Show latest readings
            latest = df.iloc[-1]
            st.subheader("🔎 Latest Readings")
            col1, col2, col3 = st.columns(3)
            col1.metric("🌡️ Temperature (°C)", f"{latest['temperature']:.2f}")
            col2.metric("💧 Humidity (%)", f"{latest['humidity']:.2f}")
            col3.metric(f"🌬️ {pressure_label}", f"{latest['pressure']:.2f}")

            st.divider()

            # Show last 24 hours (at 5s intervals = 17280 points)
            df_recent = df.tail(17280)

            # 📊 Temperature graph
            st.subheader("🌡️ Temperature Over Time")
            fig_temp = px.line(df_recent, x="timestamp", y="temperature", 
                               labels={"timestamp": "Time", "temperature": "Temperature (°C)"})
            fig_temp.update_layout(
                showlegend=False,
                xaxis=dict(tickformat="%m/%d %H:%M", tickmode='auto', nticks=10),
            )
            fig_temp.update_xaxes(tickangle=45, title_text="Time")
            st.plotly_chart(fig_temp, use_container_width=True)

            # 📊 Humidity graph
            st.subheader("💧 Humidity Over Time")
            fig_hum = px.line(df_recent, x="timestamp", y="humidity", 
                              labels={"timestamp": "Time", "humidity": "Humidity (%)"})
            fig_hum.update_layout(
                showlegend=False,
                xaxis=dict(tickformat="%m/%d %H:%M", tickmode='auto', nticks=10),
            )
            fig_hum.update_xaxes(tickangle=45, title_text="Time")
            st.plotly_chart(fig_hum, use_container_width=True)

            # 📊 Pressure graph
            st.subheader(f"🌬️ {pressure_label} Over Time")
            fig_press = px.line(df_recent, x="timestamp", y="pressure", 
                                labels={"timestamp": "Time", "pressure": pressure_label})
            fig_press.update_layout(
                showlegend=False,
                xaxis=dict(tickformat="%m/%d %H:%M", tickmode='auto', nticks=10),
                yaxis=dict(
                    range=[
                        df_recent['pressure'].min() - 2,
                        df_recent['pressure'].max() + 2
                    ] if pressure_unit == "hPa" else [
                        max(0, df_recent['pressure'].min() - 0.2),
                        df_recent['pressure'].max() + 0.2
                    ]
                )
            )
            fig_press.update_xaxes(tickangle=45, title_text="Time")
            st.plotly_chart(fig_press, use_container_width=True)

            # Additional sidebar info
            st.sidebar.write(f"📊 Pressure unit detected: {pressure_unit}")
            st.sidebar.write(f"📊 Pressure range: {df_recent['pressure'].min():.1f} - {df_recent['pressure'].max():.1f}")
            st.sidebar.write(f"📊 Data points: {len(df_recent)}")
            if len(df_recent) > 0:
                st.sidebar.write(f"🕐 Data time span: {df_recent['timestamp'].min().strftime('%H:%M:%S')} to {df_recent['timestamp'].max().strftime('%H:%M:%S')}")
                st.sidebar.write(f"🕐 Duration: {(df_recent['timestamp'].max() - df_recent['timestamp'].min()).total_seconds()/3600:.1f} hours")

            # Update session state
            st.session_state.last_mod_time = current_mod_time

    except Exception as e:
        st.error(f"❌ Error reading CSV file:\n\n{e}")
        st.write("**Debug info:**")
        st.write(f"- File exists: {os.path.exists(csv_path)}")
        st.write(f"- File size: {os.path.getsize(csv_path) if os.path.exists(csv_path) else 'N/A'} bytes")
else:
    st.warning(f"CSV file not found at `{csv_path}`")
