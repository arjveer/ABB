import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Set page config
st.set_page_config(
    page_title="AI Job Market Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Cache data loading
@st.cache_data
def load_data():
    """Load and clean the job data"""
    df = pd.read_csv('data/job_data.csv')
    return df

def standardize_salary(salary_text):
    """
    Parse salary text and convert to standardized annual min/max values
    """
    if pd.isna(salary_text) or salary_text == '':
        return None, None
    
    # Remove common prefixes and clean text
    salary_text = str(salary_text).replace('$', '').replace(',', '').strip()
    
    # Handle ranges like "70,000 - 250,001" or "10,000–15,000"
    range_patterns = [
        r'(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)',  # Standard ranges
        r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)',    # "X to Y" format
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, salary_text)
        if match:
            min_val = float(match.group(1))
            max_val = float(match.group(2))
            
            # Convert to annual if needed
            # Check for hourly indicators
            if any(word in salary_text.lower() for word in ['hour', 'hr', '/hour']):
                min_val *= 2080  # 40 hours * 52 weeks
                max_val *= 2080
            # Check for monthly indicators  
            elif any(word in salary_text.lower() for word in ['month', '/month', 'monthly']):
                min_val *= 12
                max_val *= 12
            
            return min_val, max_val
    
    # Handle single values
    single_match = re.search(r'(\d+(?:\.\d+)?)', salary_text)
    if single_match:
        val = float(single_match.group(1))
        
        # Convert to annual if needed
        if any(word in salary_text.lower() for word in ['hour', 'hr', '/hour']):
            val *= 2080
        elif any(word in salary_text.lower() for word in ['month', '/month', 'monthly']):
            val *= 12
            
        return val, val
    
    return None, None

def extract_ai_skills(job_description):
    """
    Extract AI/ML skills from job descriptions
    """
    if pd.isna(job_description):
        return []
    
    # Common AI/ML skills to look for
    skills_patterns = {
        'Python': r'\bpython\b',
        'PyTorch': r'\bpytorch\b',
        'TensorFlow': r'\btensorflow\b',
        'Machine Learning': r'\bmachine learning\b|\bml\b',
        'Deep Learning': r'\bdeep learning\b',
        'LLM': r'\bllm\b|\blarge language model\b',
        'NLP': r'\bnlp\b|\bnatural language processing\b',
        'Computer Vision': r'\bcomputer vision\b|\bcv\b',
        'AI': r'\bartificial intelligence\b|\bai\b',
        'Neural Networks': r'\bneural network\b',
        'Data Science': r'\bdata science\b',
        'Kubernetes': r'\bkubernetes\b',
        'Docker': r'\bdocker\b',
        'AWS': r'\baws\b|\bamazon web services\b',
        'GCP': r'\bgcp\b|\bgoogle cloud\b',
        'Azure': r'\bazure\b',
        'Transformers': r'\btransformer\b',
        'BERT': r'\bbert\b',
        'GPT': r'\bgpt\b',
        'LangChain': r'\blangchain\b',
        'Vector Database': r'\bvector database\b|\bpinecone\b|\bweaviate\b',
        'MLOps': r'\bmlops\b',
        'Reinforcement Learning': r'\breinforcement learning\b|\brl\b',
        'Scikit-learn': r'\bscikit-learn\b|\bsklearn\b',
        'Pandas': r'\bpandas\b',
        'NumPy': r'\bnumpy\b',
        'SQL': r'\bsql\b',
        'R': r'\b r \b|\br,|\br\.',
        'Java': r'\bjava\b',
        'C++': r'\bc\+\+\b',
        'Go': r'\bgolang\b|\bgo\b',
        'Rust': r'\brust\b',
        'React': r'\breact\b',
        'Node.js': r'\bnode\.js\b|\bnodejs\b',
        'TypeScript': r'\btypescript\b',
        'JavaScript': r'\bjavascript\b'
    }
    
    found_skills = []
    job_desc_lower = job_description.lower()
    
    for skill, pattern in skills_patterns.items():
        if re.search(pattern, job_desc_lower, re.IGNORECASE):
            found_skills.append(skill)
    
    return found_skills

@st.cache_data
def process_data(df):
    """Process the raw data for analysis"""
    # Standardize salaries
    salary_data = df['Salary Range:'].apply(standardize_salary)
    df['salary_min'] = [x[0] for x in salary_data]
    df['salary_max'] = [x[1] for x in salary_data]
    df['salary_avg'] = df[['salary_min', 'salary_max']].mean(axis=1)
    
    # Extract skills
    df['skills'] = df['Job Description'].apply(extract_ai_skills)
    
    # Filter out jobs without salary data for analysis
    df_with_salary = df.dropna(subset=['salary_min', 'salary_max'])
    
    return df, df_with_salary

def main():
    st.title("🤖 AI Job Market Dashboard")
    st.markdown("Analysis of AI and Machine Learning job opportunities")
    
    # Load and process data
    try:
        df = load_data()
        df_processed, df_with_salary = process_data(df)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # High-level stats
    st.header("📊 Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", len(df_processed))
    
    with col2:
        if len(df_with_salary) > 0:
            median_salary = df_with_salary['salary_avg'].median()
            st.metric("Median Salary", f"${median_salary:,.0f}")
        else:
            st.metric("Median Salary", "N/A")
    
    with col3:
        if len(df_with_salary) > 0:
            mean_salary = df_with_salary['salary_avg'].mean()
            st.metric("Mean Salary", f"${mean_salary:,.0f}")
        else:
            st.metric("Mean Salary", "N/A")
    
    with col4:
        jobs_with_salary = len(df_with_salary)
        st.metric("Jobs with Salary Data", jobs_with_salary)
    
    if len(df_with_salary) == 0:
        st.warning("No salary data available for analysis")
        return
    
    # Skills analysis
    st.header("💼 Top AI Skills in Demand")
    
    # Flatten all skills and count them
    all_skills = []
    for skills_list in df_processed['skills']:
        all_skills.extend(skills_list)
    
    if all_skills:
        skills_counter = Counter(all_skills)
        top_skills = skills_counter.most_common(15)
        
        if top_skills:
            skills_df = pd.DataFrame(top_skills, columns=['Skill', 'Count'])
            
            fig_skills = px.bar(
                skills_df, 
                x='Count', 
                y='Skill',
                orientation='h',
                title="Most Mentioned Skills in Job Descriptions",
                color='Count',
                color_continuous_scale='viridis'
            )
            fig_skills.update_layout(height=500, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_skills, use_container_width=True)
        else:
            st.info("No skills data extracted from job descriptions")
    
    # Pay analysis by skills
    st.header("💰 Average Salary by Top Skills")
    
    if all_skills and len(df_with_salary) > 0:
        # Calculate average salary for each skill
        skill_salaries = {}
        for skill in [s[0] for s in skills_counter.most_common(10)]:  # Top 10 skills
            jobs_with_skill = df_with_salary[df_with_salary['skills'].apply(lambda x: skill in x)]
            if len(jobs_with_skill) > 0:
                avg_salary = jobs_with_skill['salary_avg'].mean()
                skill_salaries[skill] = avg_salary
        
        if skill_salaries:
            skills_salary_df = pd.DataFrame(
                list(skill_salaries.items()), 
                columns=['Skill', 'Average Salary']
            ).sort_values('Average Salary', ascending=True)
            
            fig_skill_salary = px.bar(
                skills_salary_df,
                x='Average Salary',
                y='Skill',
                orientation='h',
                title="Average Salary by Skill",
                color='Average Salary',
                color_continuous_scale='plasma'
            )
            fig_skill_salary.update_layout(
                height=400,
                xaxis_title="Average Annual Salary ($)",
                yaxis={'categoryorder':'total ascending'}
            )
            fig_skill_salary.update_traces(
                texttemplate='$%{x:,.0f}', 
                textposition='outside'
            )
            st.plotly_chart(fig_skill_salary, use_container_width=True)
    
    # Salary distribution
    st.header("📈 Salary Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histogram of salaries
        fig_hist = px.histogram(
            df_with_salary,
            x='salary_avg',
            nbins=20,
            title="Salary Distribution",
            labels={'salary_avg': 'Average Salary ($)', 'count': 'Number of Jobs'}
        )
        fig_hist.update_layout(
            xaxis_title="Annual Salary ($)",
            yaxis_title="Number of Jobs"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Box plot of salaries
        fig_box = px.box(
            df_with_salary,
            y='salary_avg',
            title="Salary Range Distribution",
            labels={'salary_avg': 'Annual Salary ($)'}
        )
        fig_box.update_layout(
            yaxis_title="Annual Salary ($)"
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Salary ranges visualization
    st.header("💼 Salary Ranges by Job")
    
    # Create a scatter plot showing min and max salaries
    fig_range = go.Figure()
    
    for i, row in df_with_salary.iterrows():
        fig_range.add_trace(go.Scatter(
            x=[row['salary_min'], row['salary_max']],
            y=[i, i],
            mode='lines+markers',
            name=f"Job {i}",
            showlegend=False,
            line=dict(width=3),
            marker=dict(size=6)
        ))
    
    fig_range.update_layout(
        title="Salary Ranges for Each Job Position",
        xaxis_title="Annual Salary ($)",
        yaxis_title="Job Index",
        height=max(400, len(df_with_salary) * 20)
    )
    
    st.plotly_chart(fig_range, use_container_width=True)
    
    # Data table
    st.header("📋 Job Details")
    
    # Prepare display dataframe
    display_df = df_processed[['Job Title', 'salary_min', 'salary_max', 'salary_avg', 'skills']].copy()
    display_df['salary_min'] = display_df['salary_min'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    display_df['salary_max'] = display_df['salary_max'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    display_df['salary_avg'] = display_df['salary_avg'].apply(lambda x: f"${x:,.0f}" if pd.notna(x) else "N/A")
    display_df['skills'] = display_df['skills'].apply(lambda x: ', '.join(x[:5]) + ('...' if len(x) > 5 else ''))
    
    display_df.columns = ['Job Title', 'Min Salary', 'Max Salary', 'Avg Salary', 'Top Skills']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Summary insights
    st.header("🔍 Key Insights")
    
    if len(df_with_salary) > 0:
        insights = []
        
        # Salary insights
        highest_paying = df_with_salary.loc[df_with_salary['salary_avg'].idxmax()]
        lowest_paying = df_with_salary.loc[df_with_salary['salary_avg'].idxmin()]
        
        insights.append(f"**Highest paying role**: {highest_paying['Job Title']} (${highest_paying['salary_avg']:,.0f})")
        insights.append(f"**Lowest paying role**: {lowest_paying['Job Title']} (${lowest_paying['salary_avg']:,.0f})")
        
        # Skills insights
        if all_skills:
            most_common_skill = skills_counter.most_common(1)[0]
            insights.append(f"**Most in-demand skill**: {most_common_skill[0]} (mentioned in {most_common_skill[1]} jobs)")
        
        # Salary range insights
        salary_range = df_with_salary['salary_avg'].max() - df_with_salary['salary_avg'].min()
        insights.append(f"**Salary range span**: ${salary_range:,.0f}")
        
        for insight in insights:
            st.write(insight)

if __name__ == "__main__":
    main()
