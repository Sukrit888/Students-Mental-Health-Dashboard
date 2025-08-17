import streamlit as st
import pandas as pd
import plotly.express as px
import warnings

warnings.filterwarnings('ignore')

# Set Streamlit page configuration
st.set_page_config(
    page_title="Student Mental Health Dashboard",
    page_icon="🧠",
    layout="wide",
)

# --- Load the data ---
@st.cache_data
def load_data():
    """Load the dataset from the CSV file."""
    try:
        # Use a relative file path, which works on Streamlit Community Cloud
        df = pd.read_csv('MentalHealthSurvey.csv')
        return df
    except FileNotFoundError:
        st.error("Error: The 'MentalHealthSurvey.csv' file was not found. Please make sure it's in the same directory as the app.py file in your GitHub repository.")
        return None

df = load_data()
if df is None:
    st.stop()

# --- Data Cleaning and Preprocessing ---
# Standardize column names and drop 'university'
df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_').str.strip()
if 'university' in df.columns:
    df = df.drop(columns=['university'])

# Check for required columns for analysis
required_cols = ['gender', 'age', 'academic_year', 'depression', 'anxiety', 'stress_relief_activities', 'average_sleep']
if not all(col in df.columns for col in required_cols):
    st.error("Error: The dataset is missing some required columns. Please check your data.")
    st.stop()

# Rename the 'mental_health' column to 'stress_level_score' for clarity
if 'mental_health' in df.columns:
    df.rename(columns={'mental_health': 'stress_level_score'}, inplace=True)
else:
    st.warning("The 'mental_health' column was not found. Some visualizations may be unavailable.")

# Convert relevant columns to numeric, coercing errors
for col in ['depression', 'anxiety', 'stress_level_score']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# --- Dashboard Title and Introduction ---
st.title("🧠 Student Mental Health Insights Dashboard")
st.write("This interactive dashboard visualizes key factors influencing student mental health")
st.markdown("---")

# --- Filters in Sidebar ---
with st.sidebar:
    st.header("⚙️ Filter Data")

    # Age slider
    age_range = st.slider(
        "Select Age Range",
        min_value=int(df['age'].min()),
        max_value=int(df['age'].max()),
        value=(int(df['age'].min()), int(df['age'].max()))
    )

    # Gender multiselect
    genders = st.multiselect(
        "Select Gender",
        options=df['gender'].unique(),
        default=df['gender'].unique()
    )

    # Apply filters
    filtered_df = df[(df['age'] >= age_range[0]) & (df['age'] <= age_range[1]) & (df['gender'].isin(genders))]

    if filtered_df.empty:
        st.warning("No data matches the selected filters. Please adjust your selections.")
        st.stop()

# --- Key Metrics Section ---
st.header("📊 Key Metrics")
mental_health_metrics = [col for col in ['depression', 'anxiety', 'stress_level_score'] if col in filtered_df.columns]
cols = st.columns(len(mental_health_metrics))

for i, metric in enumerate(mental_health_metrics):
    avg_score = filtered_df[metric].mean()
    with cols[i]:
        st.metric(label=f"Average {metric.replace('_', ' ').title()}", value=f"{avg_score:.2f}")

st.markdown("---")

# --- Visualizations ---

st.header("📈 Data Visualizations")

# Chart 1: Average Scores by Academic Year
st.subheader("Mental Health Scores by Academic Year")
if 'academic_year' in filtered_df.columns and mental_health_metrics:
    avg_by_year = filtered_df.groupby('academic_year')[mental_health_metrics].mean().reset_index()
    # Ensure correct order of academic years
    year_order = ['1st year', '2nd year', '3rd year', '4th year', '5th year', 'Postgraduate']
    avg_by_year['academic_year'] = pd.Categorical(avg_by_year['academic_year'], categories=year_order, ordered=True)
    avg_by_year = avg_by_year.sort_values('academic_year')

    fig_year = px.bar(
        avg_by_year,
        x="academic_year",
        y=mental_health_metrics,
        barmode='group',
        title="Average Mental Health Scores by Academic Year",
        labels={'value': 'Average Score', 'variable': 'Metric'}
    )
    st.plotly_chart(fig_year, use_container_width=True)
else:
    st.warning("Academic year data is not available for visualization.")

st.markdown("---")

# Chart 2: Average Scores by Sleep Quality
st.subheader("Mental Health Scores by Sleep Quality")
if 'average_sleep' in filtered_df.columns and mental_health_metrics:
    avg_by_sleep = filtered_df.groupby('average_sleep')[mental_health_metrics].mean().reset_index()
    # Order the bars
    sleep_order = ['2-4 hrs', '4-6 hrs', '7-8 hrs', '9-10 hrs']
    avg_by_sleep['average_sleep'] = pd.Categorical(avg_by_sleep['average_sleep'], categories=sleep_order, ordered=True)
    avg_by_sleep = avg_by_sleep.sort_values('average_sleep')

    fig_sleep = px.bar(
        avg_by_sleep,
        x="average_sleep",
        y=mental_health_metrics,
        barmode='group',
        title="Average Mental Health Scores by Sleep Quality",
        labels={'value': 'Average Score', 'variable': 'Metric'}
    )
    st.plotly_chart(fig_sleep, use_container_width=True)
else:
    st.warning("Sleep quality data is not available for visualization.")

st.markdown("---")

# Chart 3: Top Stress Relief Activities
st.subheader("Most Common Stress Relief Activities")
if 'stress_relief_activities' in filtered_df.columns:
    all_activities = filtered_df['stress_relief_activities'].str.split(',').explode().str.strip().dropna()
    top_activities = all_activities.value_counts().reset_index()
    top_activities.columns = ['Activity', 'Count']

    fig_activities = px.bar(
        top_activities.head(10),
        x='Count',
        y='Activity',
        orientation='h',
        title="Top 10 Most Common Stress Relief Activities",
        color='Count',
        color_continuous_scale=px.colors.sequential.Bluyl
    )
    st.plotly_chart(fig_activities, use_container_width=True)
else:
    st.warning("Stress relief activities data is not available for visualization.")

# --- Insights and Conclusion Section ---
st.markdown("---")
st.header("🧠 Insights from the Data")
st.write("""
Based on the dashboard visualizations, here are some key insights from your dataset:

- **Academic Year and Mental Health**: As students advance through their academic years, their average **depression, anxiety, and stress levels** appear to increase. This could reflect the mounting pressures of higher education.
- **The Role of Sleep**: The data highlights a strong connection between **sleep quality** and mental well-being, suggesting that adequate sleep is a crucial factor.
- **Coping Mechanisms**: The most popular stress relief methods for this group of students are **Religious Activities, Online Entertainment, and Social Connections**. This shows a blend of personal, digital, and social coping strategies.

This dashboard provides a starting point for understanding the complex relationship between lifestyle factors and mental health in a student population. Feel free to use the filters on the left to explore different age groups and genders!
""")
