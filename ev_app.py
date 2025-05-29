pip install plotly 
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load Forecast Data ---
@st.cache_data
def load_data():
    df_seattle = pd.read_csv("prophet_forecast_seattle.csv")
    df_sandiego = pd.read_csv("prophet_forecast_sandiego.csv")
    df_vancouver = pd.read_csv("prophet_forecast_vancouver.csv")
    optimized_schedule = pd.read_csv("optimized_charging_schedule.csv")
    return {
        "Seattle": df_seattle,
        "San Diego": df_sandiego,
        "Vancouver": df_vancouver,
        "Schedule": optimized_schedule
    }

data = load_data()

# --- UI Setup ---
st.set_page_config(page_title="EV Charging Demand Intelligence", layout="wide")
st.title("🚗💡 EV Charging Demand Intelligence Platform")
st.markdown("**Forecast | Optimize | Strategize**")
st.markdown("Empowering infrastructure planners, city authorities, and energy providers with demand forecasting and grid optimization insights.")

# --- Sidebar ---
city = st.sidebar.selectbox("Select a City", ["Seattle", "San Diego", "Vancouver"])
df_city = data[city]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Forecasts", "📊 Historical Trends", "⚡ Optimization", "📋 Executive Summary", "💰 ROI Estimator"])

# --- Forecasts ---
with tab1:
    st.header(f"{city} - Forecasted EV Charging Demand (2025–2027)")
    fig = px.line(df_city, x="ds", y="yhat", title="Forecasted Demand", labels={"ds": "Date", "yhat": "Forecasted Demand"})
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Note:** Forecasts generated using Prophet model based on weather, traffic, and EV data.")

# --- Historical Trends ---
with tab2:
    st.header(f"{city} - Historical EV Charging Demand")
    if "y" in df_city.columns:
        fig_hist = px.line(df_city, x="ds", y="y", title="Historical Demand", labels={"ds": "Date", "y": "Historical Demand"})
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("Historical data not available in this file.")

# --- Optimization ---
with tab3:
    st.header("Optimized Charging Schedule (Off-Peak Focus)")
    schedule_df = data["Schedule"]
    if city in schedule_df["City"].unique():
        city_schedule = schedule_df[schedule_df["City"] == city]
        fig_sched = px.line(city_schedule, x="Hour", y="Optimized_Demand", title=f"{city} - Off-Peak Charging Strategy")
        st.plotly_chart(fig_sched, use_container_width=True)
        st.markdown("**Strategy:** Shift charging demand to off-peak hours to lower energy costs and reduce grid load.")
    else:
        st.warning("No optimized schedule found for this city.")

# --- Executive Summary ---
with tab4:
    st.header("📋 Executive Summary")
    summary_text = f'''
- **City**: {city}
- **Forecast Period**: 2025–2027
- **Trend Insight**: Increasing EV demand projected in most regions.
- **Business Recommendation**: Prioritize charging station expansion in {city}, especially in high-demand zones during stable weather months.
- **Optimization Impact**: Potential peak load reduction of 20–30% using off-peak charging strategies.
    '''
    st.markdown(summary_text)

# --- ROI Estimator ---
with tab5:
    st.header("💰 ROI Estimator for Charging Station Deployment")
    st.markdown("Estimate profitability based on forecasted demand, installation costs, and energy rates.")

    install_cost = st.number_input("Cost per Station ($)", min_value=1000, value=15000)
    energy_cost = st.number_input("Energy Cost per kWh ($)", min_value=0.01, value=0.12)
    price_per_kwh = st.number_input("Selling Price per kWh ($)", min_value=0.01, value=0.30)
    total_kwh = st.number_input("Forecasted kWh Demand (2025–2027)", value=500000)

    revenue = total_kwh * price_per_kwh
    cost = total_kwh * energy_cost + install_cost
    profit = revenue - cost

    st.metric("📈 Estimated Revenue", f"${revenue:,.2f}")
    st.metric("💸 Estimated Cost", f"${cost:,.2f}")
    st.metric("🤑 Projected Profit", f"${profit:,.2f}")

# --- Footer ---
st.markdown("---")
st.markdown("Developed by Sherin Samuel | Powered by Prophet, ARIMA, Streamlit")
