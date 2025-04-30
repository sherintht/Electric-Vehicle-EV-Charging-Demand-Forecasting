import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# Set page configuration
st.set_page_config(page_title="EV Charging Demand Dashboard", layout="wide")

# Title and description
st.title("EV Charging Demand Forecasting Dashboard")
st.markdown("""
This dashboard visualizes electric vehicle (EV) charging demand trends and forecasts based on weather, time, and traffic data.
Select a city and model to explore historical data, forecasts, weather impacts, and optimized charging schedules.
""")

# Load data
DATA_PATH = "D:/Internship/DataSet/Electrical_vehicle_"
timeseries_df = pd.read_csv(os.path.join(DATA_PATH, "ev_demand_timeseries.csv"))
summary_df = pd.read_csv(os.path.join(DATA_PATH, "ev_summary_tableau.csv"))
# Load the optimized charging schedule
schedule_path = os.path.join(DATA_PATH, "optimized_charging_schedule.csv")
if os.path.exists(schedule_path):
    schedule_df = pd.read_csv(schedule_path)
else:
    schedule_df = pd.DataFrame()  # Empty DataFrame if file not found
    st.warning(f"Optimized charging schedule not found at {schedule_path}")

# Sidebar filters
st.sidebar.header("Filters")
cities = ["Seattle", "Vancouver", "San Diego"]
city = st.sidebar.selectbox("Select City", cities)
model = st.sidebar.radio("Select Model", ["Prophet", "ARIMA"])

# Create tabs for organization
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Historical Trends", "Forecasts", "Weather Impact", "Summary Statistics", "Optimized Charging Schedule"])

# Tab 1: Historical Trends
with tab1:
    st.header(f"Historical EV Demand in {city}")
    city_data = timeseries_df[timeseries_df['City'] == city]
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(data=city_data, x='Year', y='Weighted_Demand', marker='o', ax=ax)
    ax.set_title(f"EV Charging Demand in {city} (2015-2024)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Weighted Demand (EV Count × Electric Range)")
    ax.grid(True)
    st.pyplot(fig)

    # Show data table
    st.subheader("Historical Data")
    st.dataframe(city_data[['Year', 'EV_Count', 'Electric Range', 'Weighted_Demand', 'temperature', 'humidity', 'traffic_volume']])

# Tab 2: Forecasts
with tab2:
    st.header(f"EV Demand Forecast for {city} (2025-2027)")
    model_lower = model.lower()
    city_lower = city.lower().replace(" ", "_")
    forecast_png = os.path.join(DATA_PATH, f"{model_lower}_forecast_{city_lower}.png")
    
    if os.path.exists(forecast_png):
        st.image(forecast_png, caption=f"{model} Forecast for {city}")
    else:
        st.warning(f"Forecast plot for {city} ({model}) not found at {forecast_png}")

    # Load and display forecast table
    forecast_csv = os.path.join(DATA_PATH, f"{model_lower}_forecast_{city_lower}.csv")
    if os.path.exists(forecast_csv):
        forecast_df = pd.read_csv(forecast_csv)
        st.subheader("Forecast Values")
        if model == "Prophet":
            forecast_df = forecast_df[forecast_df['ds'] >= 2025][['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
            forecast_df.columns = ['Year', 'Forecast', 'Lower Bound', 'Upper Bound']
        else:
            forecast_df = forecast_df[forecast_df['Year'] >= 2025][['Year', 'Forecast']]
        st.dataframe(forecast_df)
    else:
        st.warning(f"Forecast data for {city} ({model}) not found at {forecast_csv}")

# Tab 3: Weather Impact
with tab3:
    st.header(f"Weather vs. EV Demand in {city}")
    city_data = timeseries_df[timeseries_df['City'] == city]
    fig = px.scatter(city_data, x='temperature', y='Weighted_Demand', 
                     size='EV_Count', color='humidity', 
                     hover_data=['Year'], 
                     title=f"Temperature vs. Demand in {city}")
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Summary Statistics
with tab4:
    st.header("Summary Statistics")
    city_summary = summary_df[summary_df['City'] == city]
    if not city_summary.empty:
        st.dataframe(city_summary[['City', 'State', 'EV_Count', 'temperature', 'humidity', 'Electric Range']])
    else:
        st.warning(f"No summary data available for {city}")

    # Download button for summary CSV
    st.subheader("Download Summary Data")
    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Summary CSV",
        data=csv,
        file_name="ev_summary_tableau.csv",
        mime="text/csv"
    )

# Tab 5: Optimized Charging Schedule
with tab5:
    st.header(f"Optimized Charging Schedule for {city}")
    if not schedule_df.empty:
        # Filter schedule for the selected city
        city_schedule = schedule_df[schedule_df["city"] == city].copy()
        city_schedule['date'] = pd.to_datetime(city_schedule['date'])  # Ensure date format
        
        if not city_schedule.empty:
            # Highlight recommended (off-peak) charging hours
            optimal_hours = city_schedule[city_schedule["is_optimal"]]
            st.subheader("Recommended Charging Hours (Off-Peak)")
            st.dataframe(optimal_hours[["date", "hour", "demand_kwh"]].style.format({"date": "{:%Y-%m-%d}", "demand_kwh": "{:.2f}"}))

            # Plot the optimized hourly demand
            fig = px.line(city_schedule, x="hour", y="demand_kwh", color="date",
                          title=f"Optimized Hourly Charging Demand in {city}",
                          labels={"hour": "Hour of Day", "demand_kwh": "Demand (kWh)", "date": "Date"})
            fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
            st.plotly_chart(fig, use_container_width=True)

            # Download button for the schedule
            st.subheader("Download Optimized Schedule")
            csv = city_schedule.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Schedule CSV",
                data=csv,
                file_name=f"{city}_optimized_schedule.csv",
                mime="text/csv"
            )
        else:
            st.warning(f"No optimized schedule data available for {city}")
    else:
        st.error("Optimized charging schedule data not found. Ensure the optimization step has been run in the main program.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Data Source: EV, Weather, and Traffic Datasets | Forecast Models: Prophet, ARIMA")