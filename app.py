import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(page_title="Currency Dashboard", page_icon="💱", layout="wide")

st.title("💱 Currency Exchange Rate Analysis Dashboard")
st.markdown("*Built by Pradnya Bapat - Real-time currency exchange rate trends and analysis*")
st.markdown("---")

# Generate sample data (simulating real currency data)
@st.cache_data
def load_data():
    # Create 1 year of daily data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    
    # Currency pairs with realistic base rates
    pairs = {
        'USD/EUR': {'base': 0.85, 'volatility': 0.01},
        'USD/GBP': {'base': 0.75, 'volatility': 0.012},
        'USD/JPY': {'base': 110.0, 'volatility': 1.5},
        'USD/INR': {'base': 83.0, 'volatility': 0.8},
        'EUR/GBP': {'base': 0.88, 'volatility': 0.008},
        'GBP/INR': {'base': 110.0, 'volatility': 1.2}
    }
    
    data = []
    for i, date in enumerate(dates):
        for pair_name, config in pairs.items():
            # Create realistic fluctuations
            trend = np.sin(i * 0.02) * 0.05  # Seasonal trend
            random_change = np.random.normal(0, config['volatility'])
            rate = config['base'] * (1 + trend + random_change)
            
            data.append({
                'Date': date,
                'Currency_Pair': pair_name,
                'Exchange_Rate': round(rate, 4),
                'Volume': np.random.randint(1000000, 8000000)
            })
    
    return pd.DataFrame(data)

# Load data
df = load_data()

# Sidebar filters
st.sidebar.header("🔧 Dashboard Controls")
st.sidebar.markdown("*Filter and customize your analysis*")

# Currency selection
currencies = st.sidebar.multiselect(
    "Select Currency Pairs:",
    options=df['Currency_Pair'].unique(),
    default=['USD/EUR', 'USD/GBP', 'USD/INR'],
    help="Choose one or more currency pairs to analyze"
)

# Time period
period = st.sidebar.selectbox(
    "Time Period:",
    ['Last 30 Days', 'Last 90 Days', 'Last 6 Months', 'Last Year'],
    help="Select the time range for analysis"
)

# Calculate date range
today = df['Date'].max()
if period == 'Last 30 Days':
    start_date = today - timedelta(days=30)
elif period == 'Last 90 Days':
    start_date = today - timedelta(days=90)
elif period == 'Last 6 Months':
    start_date = today - timedelta(days=180)
else:
    start_date = df['Date'].min()

# Filter data
filtered_data = df[
    (df['Currency_Pair'].isin(currencies)) & 
    (df['Date'] >= start_date)
]

if filtered_data.empty:
    st.warning("⚠️ No data available for selected filters. Please adjust your selection.")
    st.stop()

# Key Metrics Row
st.subheader("📊 Key Metrics Dashboard")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📈 Currency Pairs",
        value=len(currencies),
        help="Number of selected currency pairs"
    )

with col2:
    avg_rate = filtered_data['Exchange_Rate'].mean()
    st.metric(
        label="📊 Average Rate",
        value=f"{avg_rate:.3f}",
        help="Mean exchange rate across all selected pairs"
    )

with col3:
    total_volume = filtered_data['Volume'].sum() / 1000000
    st.metric(
        label="💰 Total Volume",
        value=f"{total_volume:.1f}M",
        help="Total trading volume in millions"
    )

with col4:
    volatility = filtered_data['Exchange_Rate'].std()
    risk = "High" if volatility > 5 else "Medium" if volatility > 1 else "Low"
    color = "normal" if risk == "Low" else "inverse"
    st.metric(
        label="⚠️ Risk Level",
        value=risk,
        help="Based on exchange rate volatility"
    )

st.markdown("---")

# Main trend chart
st.subheader("📈 Exchange Rate Trends")
st.markdown(f"*Showing trends for {period.lower()} across selected currency pairs*")

fig_line = px.line(
    filtered_data,
    x='Date',
    y='Exchange_Rate',
    color='Currency_Pair',
    title=f"Currency Exchange Rate Trends - {period}",
    height=500,
    labels={'Exchange_Rate': 'Exchange Rate', 'Date': 'Date'}
)

fig_line.update_layout(
    xaxis_title="Date",
    yaxis_title="Exchange Rate",
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig_line, use_container_width=True)

# Two column layout for additional analysis
col1, col2 = st.columns(2)

# Peak vs Low rates
with col1:
    st.subheader("📊 Peak vs Lowest Rates")
    st.markdown("*Compare highest and lowest exchange rates*")
    
    stats = filtered_data.groupby('Currency_Pair')['Exchange_Rate'].agg(['min', 'max']).reset_index()
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name='Lowest Rate',
        x=stats['Currency_Pair'],
        y=stats['min'],
        marker_color='#ff6b6b',
        text=stats['min'].round(4),
        textposition='auto'
    ))
    fig_bar.add_trace(go.Bar(
        name='Peak Rate',
        x=stats['Currency_Pair'],
        y=stats['max'],
        marker_color='#4ecdc4',
        text=stats['max'].round(4),
        textposition='auto'
    ))
    
    fig_bar.update_layout(
        title="Peak vs Lowest Exchange Rates",
        barmode='group',
        height=400,
        xaxis_title="Currency Pair",
        yaxis_title="Exchange Rate"
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

# Currency basket
with col2:
    st.subheader("🎯 Currency Basket Analysis")
    st.markdown("*Equal-weighted portfolio performance*")
    
    # Equal weight basket calculation
    basket_data = filtered_data.groupby('Date')['Exchange_Rate'].mean().reset_index()
    basket_data.columns = ['Date', 'Basket_Value']
    
    fig_area = px.area(
        basket_data,
        x='Date',
        y='Basket_Value',
        title="Weighted Currency Basket Value",
        height=400,
        labels={'Basket_Value': 'Basket Value', 'Date': 'Date'}
    )
    
    fig_area.update_traces(fill='tonexty', fillcolor='rgba(74, 144, 226, 0.3)')
    st.plotly_chart(fig_area, use_container_width=True)

# Statistics table
st.subheader("📋 Detailed Currency Statistics")
st.markdown("*Comprehensive analysis of selected currency pairs*")

stats_data = []
for currency in currencies:
    curr_data = filtered_data[filtered_data['Currency_Pair'] == currency]['Exchange_Rate']
    if len(curr_data) > 0:
        vol = curr_data.std()
        risk_level = "🔴 High" if vol > 5 else "🟡 Medium" if vol > 1 else "🟢 Low"
        
        stats_data.append({
            'Currency Pair': currency,
            'Current Rate': f"{curr_data.iloc[-1]:.4f}",
            'Peak Rate': f"{curr_data.max():.4f}",
            'Lowest Rate': f"{curr_data.min():.4f}",
            'Average Rate': f"{curr_data.mean():.4f}",
            'Volatility': f"{vol:.3f}",
            'Risk Level': risk_level
        })

stats_df = pd.DataFrame(stats_data)
st.dataframe(stats_df, use_container_width=True, hide_index=True)

# Risk Assessment Section
st.subheader("⚠️ Volatility-Based Risk Assessment System")
st.markdown("*Categorization based on exchange rate standard deviation*")

risk_col1, risk_col2, risk_col3 = st.columns(3)

with risk_col1:
    st.success("**🟢 Low Risk Portfolio**")
    st.markdown("*Volatility < 1.0 - Stable currencies*")
    low_risk = [curr for curr in currencies if filtered_data[filtered_data['Currency_Pair'] == curr]['Exchange_Rate'].std() < 1.0]
    if low_risk:
        for curr in low_risk:
            vol = filtered_data[filtered_data['Currency_Pair'] == curr]['Exchange_Rate'].std()
            st.write(f"• {curr} (σ: {vol:.3f})")
    else:
        st.write("• No currencies in this category")

with risk_col2:
    st.warning("**🟡 Medium Risk Portfolio**")
    st.markdown("*1.0 ≤ Volatility < 5.0 - Moderate risk*")
    med_risk = [curr for curr in currencies if 1.0 <= filtered_data[filtered_data['Currency_Pair'] == curr]['Exchange_Rate'].std() < 5.0]
    if med_risk:
        for curr in med_risk:
            vol = filtered_data[filtered_data['Currency_Pair'] == curr]['Exchange_Rate'].std()
            st.write(f"• {curr} (σ: {vol:.3f})")
    else:
        st.write("• No currencies in this category")

with risk_col3:
    st.error("**🔴 High Risk Portfolio**")
    st.markdown("*Volatility ≥ 5.0 - High volatility*")
    high_risk = [curr for curr in currencies if filtered_data[filtered_data['Currency_Pair'] == curr]['Exchange_Rate'].std() >= 5.0]
    if high_risk:
        for curr in high_risk:
            vol = filtered_data[filtered_data['Currency_Pair'] == curr]['Exchange_Rate'].std()
            st.write(f"• {curr} (σ: {vol:.3f})")
    else:
        st.write("• No currencies in this category")

# Footer with additional information
st.markdown("---")
st.markdown("### 📖 About This Dashboard")

footer_col1, footer_col2 = st.columns(2)

with footer_col1:
    st.markdown("""
    **🔧 Technical Implementation:**
    - Built with Python, Streamlit & Plotly
    - Real-time data simulation
    - Interactive filtering system
    - Responsive design
    """)

with footer_col2:
    st.markdown("""
    **📊 Key Features:**
    - Dynamic currency pair selection
    - Multiple time period analysis
    - Peak/lowest rate comparison
    - Volatility-based risk assessment
    """)

st.markdown("---")
st.markdown("**💼 Built by Pradnya Bapat** | *Currency Exchange Rate Analysis Dashboard*")
st.markdown("*Demonstration project with simulated exchange rate data*")
