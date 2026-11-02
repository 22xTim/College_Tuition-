import streamlit as st
import pandas as pd
import plotly.express as px
import gzip

# Set Page Config
st.set_page_config(
    page_title="US College Tuition & Affordability Dashboard",
    page_icon="🎓",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('college_scorecard_dashboard_optimized.csv.gz', compression='gzip')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Title and Description
st.title("🎓 US College Tuition & Affordability")
st.markdown("""
An interactive exploration of tuition costs, student debt, and median earnings 10 years after entry.
Using the optimized US College Scorecard dataset.
""")

# Sidebar Filters
st.sidebar.header("Filter Options")

selected_states = st.sidebar.multiselect(
    "Select States",
    options=sorted(df['STABBR'].unique()),
    default=[]
)

selected_control = st.sidebar.multiselect(
    "Select School Sector",
    options=sorted(df['CONTROL'].unique()),
    default=df['CONTROL'].unique()
)

selected_degree = st.sidebar.multiselect(
    "Select Predominant Degree",
    options=sorted(df['PREDDEG'].unique()),
    default=df['PREDDEG'].unique()
)

# Apply Filters
filtered_df = df.copy()
if selected_states:
    filtered_df = filtered_df[filtered_df['STABBR'].isin(selected_states)]
if selected_control:
    filtered_df = filtered_df[filtered_df['CONTROL'].isin(selected_control)]
if selected_degree:
    filtered_df = filtered_df[filtered_df['PREDDEG'].isin(selected_degree)]

# Main KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Colleges", f"{len(filtered_df):,}")
with col2:
    st.metric("Avg In-State Tuition", f"${filtered_df['TUITIONFEE_IN'].mean():,.0f}")
with col3:
    st.metric("Median 10-Yr Earnings", f"${filtered_df['MD_EARN_WNE_P10'].median():,.0f}")
with col4:
    st.metric("Median Student Debt", f"${filtered_df['GRAD_DEBT_MDN_SUPP'].median():,.0f}")

st.markdown("--- ")

# Plots Row 1
plot_col1, plot_col2 = st.columns(2)

with plot_col1:
    st.subheader("Tuition vs. 10-Year Post-Graduate Earnings")
    fig1 = px.scatter(
        filtered_df,
        x='TUITIONFEE_IN',
        y='MD_EARN_WNE_P10',
        color='CONTROL',
        hover_name='INSTNM',
        labels={'TUITIONFEE_IN': 'In-State Tuition ($)', 'MD_EARN_WNE_P10': '10-Year Median Earnings ($)'},
        opacity=0.7,
        template='plotly_white'
    )
    st.plotly_chart(fig1, use_container_width=True)

with plot_col2:
    st.subheader("Earnings Distribution by School Sector")
    fig2 = px.box(
        filtered_df,
        x='CONTROL',
        y='MD_EARN_WNE_P10',
        color='CONTROL',
        labels={'CONTROL': 'Sector', 'MD_EARN_WNE_P10': '10-Year Median Earnings ($)'},
        template='plotly_white'
    )
    st.plotly_chart(fig2, use_container_width=True)

# Plots Row 2
plot_col3, plot_col4 = st.columns(2)

with plot_col3:
    st.subheader("Median Earnings vs. Median Student Debt by Degree")
    degree_summary = filtered_df.groupby('PREDDEG')[['MD_EARN_WNE_P10', 'GRAD_DEBT_MDN_SUPP']].median().reset_index()
    degree_melted = degree_summary.melt(id_vars='PREDDEG', var_name='Metric', value_name='Amount')
    degree_melted['Metric'] = degree_melted['Metric'].map({'MD_EARN_WNE_P10': 'Median Earnings', 'GRAD_DEBT_MDN_SUPP': 'Median Debt'})

    fig3 = px.bar(
        degree_melted,
        x='PREDDEG',
        y='Amount',
        color='Metric',
        barmode='group',
        labels={'PREDDEG': 'Degree Type', 'Amount': 'Value ($)'},
        template='plotly_white'
    )
    st.plotly_chart(fig3, use_container_width=True)

with plot_col4:
    st.subheader("Data Explorer Table")
    st.dataframe(
        filtered_df[['INSTNM', 'STABBR', 'CONTROL', 'PREDDEG', 'TUITIONFEE_IN', 'MD_EARN_WNE_P10', 'GRAD_DEBT_MDN_SUPP']],
        use_container_width=True,
        height=400
    )
