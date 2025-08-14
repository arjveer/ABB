import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter

# Page config
st.set_page_config(
    page_title="AI Jobs Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stMetric > label {
        font-size: 1.2rem !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data():
    """Load and process the AI job data"""
    
    # Load the data
    df = pd.read_csv('data/ai_job_data.csv')
    
    # Remove duplicates based on company_name, job_title, and location
    df_clean = df.drop_duplicates(subset=['company_name', 'job_title', 'location'])
    
    # Handle salary data
    df_clean = df_clean.copy()
    df_clean['salary_min'] = pd.to_numeric(df_clean['salary_min'], errors='coerce')
    df_clean['salary_max'] = pd.to_numeric(df_clean['salary_max'], errors='coerce')
    
    # Convert hourly rates (< $100) to annual salary (assuming 40 hours/week, 52 weeks/year)
    hourly_mask_min = (df_clean['salary_min'] < 100) & (df_clean['salary_min'] > 0)
    hourly_mask_max = (df_clean['salary_max'] < 100) & (df_clean['salary_max'] > 0)
    
    df_clean.loc[hourly_mask_min, 'salary_min'] = df_clean.loc[hourly_mask_min, 'salary_min'] * 40 * 52
    df_clean.loc[hourly_mask_max, 'salary_max'] = df_clean.loc[hourly_mask_max, 'salary_max'] * 40 * 52
    
    # Calculate average salary
    df_clean['avg_salary'] = (df_clean['salary_min'] + df_clean['salary_max']) / 2
    
    # Handle cases where only one salary value exists
    df_clean['avg_salary'] = df_clean['avg_salary'].fillna(df_clean['salary_min']).fillna(df_clean['salary_max'])
    
    # Remove rows with no salary data
    df_clean = df_clean.dropna(subset=['avg_salary'])
    df_clean = df_clean[df_clean['avg_salary'] > 0]
    
    # Clean location data
    df_clean['location'] = df_clean['location'].fillna('Not Specified')
    df_clean['location'] = df_clean['location'].replace('N/A', 'Not Specified')
    
    return df_clean

def extract_skills(job_descriptions):
    """Extract common data science, ML, and AI skills from job descriptions"""
    
    # Define skill keywords
    skills_keywords = {
        'Python': r'\bpython\b',
        'R': r'\bR\b',
        'SQL': r'\bSQL\b',
        'Machine Learning': r'\bmachine learning\b|\bML\b',
        'Deep Learning': r'\bdeep learning\b|\bDL\b',
        'TensorFlow': r'\btensorflow\b',
        'PyTorch': r'\bpytorch\b',
        'Scikit-learn': r'\bscikit.?learn\b|\bsklearn\b',
        'Pandas': r'\bpandas\b',
        'NumPy': r'\bnumpy\b',
        'Matplotlib': r'\bmatplotlib\b',
        'Seaborn': r'\bseaborn\b',
        'Plotly': r'\bplotly\b',
        'Tableau': r'\btableau\b',
        'Power BI': r'\bpower.?bi\b',
        'AWS': r'\baws\b|\bamazon web services\b',
        'Azure': r'\bazure\b',
        'GCP': r'\bgcp\b|\bgoogle cloud\b',
        'Docker': r'\bdocker\b',
        'Kubernetes': r'\bkubernetes\b',
        'Spark': r'\bspark\b|\bpyspark\b',
        'Hadoop': r'\bhadoop\b',
        'Statistics': r'\bstatistics\b|\bstatistical\b',
        'NLP': r'\bnlp\b|\bnatural language processing\b',
        'Computer Vision': r'\bcomputer vision\b|\bcv\b',
        'LLM': r'\bllm\b|\blarge language model\b',
        'GPT': r'\bgpt\b',
        'Transformers': r'\btransformers\b',
        'BERT': r'\bbert\b',
        'API': r'\bapi\b',
        'REST': r'\brest\b|\brestful\b',
        'Git': r'\bgit\b|\bgithub\b',
        'Linux': r'\blinux\b',
        'Java': r'\bjava\b',
        'JavaScript': r'\bjavascript\b|\bjs\b',
        'React': r'\breact\b',
        'Node.js': r'\bnode\.?js\b',
        'MongoDB': r'\bmongodb\b',
        'PostgreSQL': r'\bpostgresql\b|\bpostgres\b',
        'MySQL': r'\bmysql\b'
    }
    
    skill_counts = Counter()
    
    for description in job_descriptions:
        if pd.isna(description):
            continue
        description_lower = str(description).lower()
        for skill, pattern in skills_keywords.items():
            if re.search(pattern, description_lower, re.IGNORECASE):
                skill_counts[skill] += 1
    
    return skill_counts

def create_top_companies_chart(df, top_n=10):
    """Create bar chart of top paying companies"""
    company_avg_salary = df.groupby('company_name')['avg_salary'].agg(['mean', 'count']).reset_index()
    company_avg_salary = company_avg_salary[company_avg_salary['count'] >= 1]  # At least 1 job
    company_avg_salary = company_avg_salary.sort_values('mean', ascending=False).head(top_n)
    
    fig = px.bar(
        company_avg_salary, 
        x='mean', 
        y='company_name',
        orientation='h',
        title=f'Top {top_n} Highest Paying Companies',
        labels={'mean': 'Average Salary ($)', 'company_name': 'Company'},
        color='mean',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
    return fig

def create_top_skills_chart(skill_counts, df, top_n=15):
    """Create bar chart of top paying skills"""
    # Get top skills by frequency
    top_skills = dict(skill_counts.most_common(top_n))
    
    # Calculate average salary for jobs mentioning each skill
    skill_salaries = {}
    
    for skill in top_skills.keys():
        skill_pattern = {
            'Python': r'\bpython\b',
            'R': r'\bR\b',
            'SQL': r'\bSQL\b',
            'Machine Learning': r'\bmachine learning\b|\bML\b',
            'Deep Learning': r'\bdeep learning\b|\bDL\b',
            'TensorFlow': r'\btensorflow\b',
            'PyTorch': r'\bpytorch\b',
            'Scikit-learn': r'\bscikit.?learn\b|\bsklearn\b',
            'Pandas': r'\bpandas\b',
            'NumPy': r'\bnumpy\b',
            'Matplotlib': r'\bmatplotlib\b',
            'Seaborn': r'\bseaborn\b',
            'Plotly': r'\bplotly\b',
            'Tableau': r'\btableau\b',
            'Power BI': r'\bpower.?bi\b',
            'AWS': r'\baws\b|\bamazon web services\b',
            'Azure': r'\bazure\b',
            'GCP': r'\bgcp\b|\bgoogle cloud\b',
            'Docker': r'\bdocker\b',
            'Kubernetes': r'\bkubernetes\b',
            'Spark': r'\bspark\b|\bpyspark\b',
            'Hadoop': r'\bhadoop\b',
            'Statistics': r'\bstatistics\b|\bstatistical\b',
            'NLP': r'\bnlp\b|\bnatural language processing\b',
            'Computer Vision': r'\bcomputer vision\b|\bcv\b',
            'LLM': r'\bllm\b|\blarge language model\b',
            'GPT': r'\bgpt\b',
            'Transformers': r'\btransformers\b',
            'BERT': r'\bbert\b',
            'API': r'\bapi\b',
            'REST': r'\brest\b|\brestful\b',
            'Git': r'\bgit\b|\bgithub\b',
            'Linux': r'\blinux\b',
            'Java': r'\bjava\b',
            'JavaScript': r'\bjavascript\b|\bjs\b',
            'React': r'\breact\b',
            'Node.js': r'\bnode\.?js\b',
            'MongoDB': r'\bmongodb\b',
            'PostgreSQL': r'\bpostgresql\b|\bpostgres\b',
            'MySQL': r'\bmysql\b'
        }.get(skill, skill.lower())
        
        mask = df['job_description'].str.contains(skill_pattern, case=False, na=False, regex=True)
        if mask.any():
            skill_salaries[skill] = df[mask]['avg_salary'].mean()
        else:
            skill_salaries[skill] = 0
    
    # Create DataFrame for plotting
    skills_df = pd.DataFrame([
        {'skill': skill, 'avg_salary': salary, 'job_count': top_skills[skill]}
        for skill, salary in skill_salaries.items()
    ]).sort_values('avg_salary', ascending=False)
    
    fig = px.bar(
        skills_df,
        x='avg_salary',
        y='skill',
        orientation='h',
        title=f'Top {top_n} Highest Paying Skills',
        labels={'avg_salary': 'Average Salary ($)', 'skill': 'Skill'},
        color='avg_salary',
        color_continuous_scale='plasma',
        hover_data=['job_count']
    )
    fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
    return fig

# Main app
def main():
    st.markdown('<h1 class="main-header">🤖 AI Jobs Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner('Loading and processing data...'):
        df = load_and_process_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Salary range filter
    min_salary = int(df['avg_salary'].min())
    max_salary = int(df['avg_salary'].max())
    salary_range = st.sidebar.slider(
        "Salary Range ($)",
        min_value=min_salary,
        max_value=max_salary,
        value=(min_salary, max_salary),
        step=10000
    )
    
    # Location filter
    locations = ['All'] + sorted(df['location'].unique().tolist())
    selected_location = st.sidebar.selectbox("Location", locations)
    
    # Company filter
    companies = ['All'] + sorted(df['company_name'].unique().tolist())
    selected_company = st.sidebar.selectbox("Company", companies)
    
    # Apply filters
    filtered_df = df[
        (df['avg_salary'] >= salary_range[0]) & 
        (df['avg_salary'] <= salary_range[1])
    ]
    
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['company_name'] == selected_company]
    
    # High-level statistics
    st.header("📊 Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Jobs",
            value=f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df):,}" if len(filtered_df) != len(df) else None
        )
    
    with col2:
        median_pay = filtered_df['avg_salary'].median()
        st.metric(
            label="Median Salary",
            value=f"${median_pay:,.0f}",
            delta=f"${median_pay - df['avg_salary'].median():,.0f}" if len(filtered_df) != len(df) else None
        )
    
    with col3:
        mean_pay = filtered_df['avg_salary'].mean()
        st.metric(
            label="Mean Salary",
            value=f"${mean_pay:,.0f}",
            delta=f"${mean_pay - df['avg_salary'].mean():,.0f}" if len(filtered_df) != len(df) else None
        )
    
    with col4:
        unique_companies = filtered_df['company_name'].nunique()
        st.metric(
            label="Companies",
            value=f"{unique_companies:,}",
            delta=f"{unique_companies - df['company_name'].nunique():,}" if len(filtered_df) != len(df) else None
        )
    
    # Charts section
    st.header("📈 Analysis")
    
    # Create tabs for different analyses
    tab1, tab2, tab4 = st.tabs(["Companies", "Skills", "Salary Distribution"])
    
    with tab1:
        st.subheader("Top Paying Organizations")
        if len(filtered_df) > 0:
            companies_chart = create_top_companies_chart(filtered_df)
            st.plotly_chart(companies_chart, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")
    
    with tab2:
        st.subheader("Top Paying Skills")
        if len(filtered_df) > 0:
            with st.spinner('Analyzing job descriptions for skills...'):
                skill_counts = extract_skills(filtered_df['job_description'])
            
            if skill_counts:
                skills_chart = create_top_skills_chart(skill_counts, filtered_df)
                st.plotly_chart(skills_chart, use_container_width=True)
                
                # Show skill frequency table
                with st.expander("View Skill Frequencies"):
                    skills_df = pd.DataFrame([
                        {'Skill': skill, 'Job Count': count, 'Percentage': f"{count/len(filtered_df)*100:.1f}%"}
                        for skill, count in skill_counts.most_common(20)
                    ])
                    st.dataframe(skills_df, use_container_width=True)
            else:
                st.warning("No skills data available for the selected filters.")
        else:
            st.warning("No data available for the selected filters.")
    
    with tab4:
        st.subheader("Salary Distribution")
        if len(filtered_df) > 0:
            # Histogram
            fig_hist = px.histogram(
                filtered_df, 
                x='avg_salary',
                nbins=30,
                title='Salary Distribution',
                labels={'avg_salary': 'Average Salary ($)', 'count': 'Number of Jobs'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.add_vline(
                x=filtered_df['avg_salary'].median(), 
                line_dash="dash", 
                line_color="red",
                annotation_text=f"Median: ${filtered_df['avg_salary'].median():,.0f}"
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Box plot by company (top 10)
            top_companies = filtered_df.groupby('company_name')['avg_salary'].count().nlargest(10).index
            company_salary_df = filtered_df[filtered_df['company_name'].isin(top_companies)]
            
            if len(company_salary_df) > 0:
                fig_box = px.box(
                    company_salary_df,
                    x='company_name',
                    y='avg_salary',
                    title='Salary Distribution by Top Companies',
                    labels={'avg_salary': 'Average Salary ($)', 'company_name': 'Company'}
                )
                fig_box.update_xaxes(tickangle=45)
                st.plotly_chart(fig_box, use_container_width=True)
        else:
            st.warning("No data available for the selected filters.")
    
    # Data table
    st.header("📋 Job Listings")
    
    # Show filtered data
    display_df = filtered_df[['company_name', 'job_title', 'location', 'avg_salary']].copy()
    display_df['avg_salary'] = display_df['avg_salary'].apply(lambda x: f"${x:,.0f}")
    display_df.columns = ['Company', 'Job Title', 'Location', 'Average Salary']
    
    st.dataframe(
        display_df.sort_values('Average Salary', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="ai_jobs_filtered.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
