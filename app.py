import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Travel Data Analyst", layout="wide")

st.title("📊 Travel & Logistics Analysis Dashboard")
st.markdown("Upload your *Excel (.xlsx)* booking dataset to generate instant insights.")

# --- File Upload Section ---
uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type=['xlsx', 'xls'])

@st.cache_data
def process_data(file):
    # Read Excel file
    df = pd.read_excel(file)
    
    # Date Conversions (Crucial for Q9 and Q16)
    date_cols = ['Journey Date', 'Booked On', 'Issued On']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate Lead Time (Q9)
    if 'Journey Date' in df.columns and 'Booked On' in df.columns:
        df['Advance Days'] = (df['Journey Date'] - df['Booked On']).dt.days
        
    return df

if uploaded_file is not None:
    df = process_data(uploaded_file)
    
    # --- Sidebar Filters ---
    st.sidebar.header("Data Filters")
    if 'Status' in df.columns:
        status_list = df['Status'].unique().tolist()
        selected_status = st.sidebar.multiselect("Filter by Status", status_list, default=status_list)
        df = df[df['Status'].isin(selected_status)]

    # --- Metrics (Q1, Q3, Q4) ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Bookings", len(df))
    
    if 'Net Amount' in df.columns:
        m2.metric("Total Revenue", f"₹{df['Net Amount'].sum():,.2f}")
    
    if 'Status' in df.columns:
        m3.metric("Confirmed Bookings", len(df[df['Status'] == 'Booked']))
        m4.metric("Cancellations", len(df[df['Status'] == 'Cancel']))

    # --- Visual Analysis ---
    col1, col2 = st.columns(2)

    with col1:
        # Q2: Channel Check
        if 'Booked By' in df.columns:
            st.subheader("Top Booking Channels")
            top_channels = df['Booked By'].value_counts().head(10)
            fig1 = px.bar(top_channels, orientation='h', color=top_channels.values, 
                          labels={'value': 'Transactions', 'index': 'Channel'})
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Q16: Weekly Demand
        if 'Journey Date' in df.columns:
            st.subheader("Demand by Day of Week")
            df['Weekday'] = df['Journey Date'].dt.day_name()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            week_data = df['Weekday'].value_counts().reindex(day_order)
            fig2 = px.line(x=week_data.index, y=week_data.values, markers=True, 
                           labels={'x': 'Day', 'y': 'Number of Bookings'})
            st.plotly_chart(fig2, use_container_width=True)

    # --- Deep Dive Tabs ---
    tab1, tab2, tab3 = st.tabs(["Route Analysis", "Financials", "Operational Efficiency"])

    with tab1:
        # Q7 & Q5
        st.subheader("Route Performance")
        if 'Route' in df.columns and 'Net Amount' in df.columns:
            route_rev = df.groupby('Route')['Net Amount'].sum().sort_values(ascending=False).head(10).reset_index()
            st.write("Top 10 Routes by Revenue")
            st.dataframe(route_rev, use_container_width=True)

    with tab2:
        # Q12: OTA vs Local
        if 'Category' in df.columns:
            st.subheader("Revenue by Category (OTA vs Online Agent)")
            cat_rev = df.groupby('Category')['Net Amount'].sum().reset_index()
            fig3 = px.pie(cat_rev, values='Net Amount', names='Category', hole=0.4)
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        # Q15: Driver Analysis
        if 'Drivers' in df.columns:
            st.subheader("Top Performing Drivers (by Rev…
