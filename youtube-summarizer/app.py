"""
Streamlit web application for YouTube video summarizer.
Provides a user-friendly interface for summarizing YouTube videos.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
from core import YouTubeSummarizer

# Page configuration
st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1.5rem;
        text-align: center;
        margin: 1rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 1rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📺 YouTube Video Summarizer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Extract transcripts and generate AI-powered summaries using GPT-4o</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. You can also set it as an environment variable OPENAI_API_KEY."
        )
        
        # Summary type selection
        summary_type = st.selectbox(
            "Summary Type",
            ["medium", "short", "long", "detailed"],
            help="Choose the length and detail level of your summary"
        )
        
        # Language preference
        languages = st.multiselect(
            "Preferred Languages",
            ["en", "en-US", "en-GB", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
            default=["en", "en-US", "en-GB"],
            help="Select preferred languages for transcript extraction"
        )
        
        # Model selection
        model = st.selectbox(
            "OpenAI Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            help="Choose the OpenAI model for summarization"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Statistics")
        
        # Session state for statistics
        if 'total_videos' not in st.session_state:
            st.session_state.total_videos = 0
        if 'total_words' not in st.session_state:
            st.session_state.total_words = 0
        if 'total_summaries' not in st.session_state:
            st.session_state.total_summaries = 0
        
        st.metric("Videos Processed", st.session_state.total_videos)
        st.metric("Words Summarized", st.session_state.total_words)
        st.metric("Summaries Generated", st.session_state.total_summaries)
        
        st.markdown("---")
        st.markdown("### 📚 About")
        st.markdown("""
        This tool extracts YouTube video transcripts and uses OpenAI's GPT-4o to generate intelligent summaries.
        
        **Features:**
        - 🎯 Multiple summary lengths
        - 🌍 Multi-language support
        - 📝 Detailed analysis option
        - 💾 Export results
        """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎬 Video Input")
        
        # URL input
        video_url = st.text_input(
            "YouTube Video URL or ID",
            placeholder="https://www.youtube.com/watch?v=... or just the video ID",
            help="Paste a YouTube URL or enter the video ID directly"
        )
        
        # Process button
        if st.button("🚀 Generate Summary", type="primary", use_container_width=True):
            if not video_url.strip():
                st.error("Please enter a YouTube video URL or ID.")
            elif not api_key and not os.getenv("OPENAI_API_KEY"):
                st.error("Please enter your OpenAI API key.")
            else:
                process_video(video_url, summary_type, model, languages)
    
    with col2:
        st.header("📋 Quick Examples")
        st.markdown("""
        Try these video IDs:
        
        **Short Video:**
        `dQw4w9WgXcQ`
        
        **Educational:**
        `kJAsCz9hdJQ`
        
        **Tutorial:**
        `8jLo02VtJmQ`
        """)
    
    # Results section
    if 'last_result' in st.session_state and st.session_state.last_result:
        display_results(st.session_state.last_result)
    
    # History section
    if 'history' in st.session_state and st.session_state.history:
        display_history()

def process_video(url: str, summary_type: str, model: str, languages: list):
    """Process a YouTube video and generate summary."""
    
    try:
        with st.spinner("🔄 Processing video..."):
            # Initialize summarizer
            summarizer = YouTubeSummarizer()
            
            # Override model if specified
            if model:
                summarizer.model = model
            
            # Process video
            result = summarizer.process_video(url, summary_type)
            
            if result["success"]:
                # Store result in session state
                st.session_state.last_result = result
                
                # Update statistics
                st.session_state.total_videos += 1
                st.session_state.total_words += result.get("word_count", 0)
                st.session_state.total_summaries += 1
                
                # Add to history
                if 'history' not in st.session_state:
                    st.session_state.history = []
                
                history_entry = {
                    'timestamp': datetime.now(),
                    'video_id': result['video_id'],
                    'summary_type': summary_type,
                    'word_count': result.get('word_count', 0),
                    'url': url
                }
                st.session_state.history.append(history_entry)
                
                st.success("✅ Summary generated successfully!")
                
            else:
                st.error(f"❌ Error: {result['error']}")
                
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

def display_results(result: dict):
    """Display the results of video processing."""
    
    st.markdown("---")
    st.header("📊 Results")
    
    # Video information
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["video_id"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Video ID</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["word_count"]:,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Words</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["transcript_length"]:,}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Characters</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-value">{result["summary_type"].title()}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Summary Type</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Video info
    if "video_info" in result and result["video_info"]:
        st.subheader("🎥 Video Information")
        video_info = result["video_info"]
        
        if "error" not in video_info:
            info_cols = st.columns(3)
            with info_cols[0]:
                st.info(f"**Language:** {video_info.get('language', 'Unknown')}")
            with info_cols[1]:
                st.info(f"**Generated:** {'Yes' if video_info.get('is_generated') else 'No'}")
            with info_cols[2]:
                st.info(f"**Translatable:** {'Yes' if video_info.get('is_translatable') else 'No'}")
    
    # Summary
    st.subheader("📝 AI-Generated Summary")
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown(result["summary"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Transcript preview
    with st.expander("📄 View Full Transcript"):
        st.text_area("Transcript", result["transcript"], height=300, disabled=True)
    
    # Export options
    st.subheader("💾 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export as Text", use_container_width=True):
            export_text(result)
    
    with col2:
        if st.button("📊 Export as CSV", use_container_width=True):
            export_csv(result)

def display_history():
    """Display processing history."""
    
    st.markdown("---")
    st.header("📚 Processing History")
    
    if st.session_state.history:
        # Convert to DataFrame for better display
        df = pd.DataFrame(st.session_state.history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        # Display history table
        st.dataframe(
            df,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Timestamp"),
                "video_id": st.column_config.TextColumn("Video ID"),
                "summary_type": st.column_config.TextColumn("Summary Type"),
                "word_count": st.column_config.NumberColumn("Word Count"),
                "url": st.column_config.TextColumn("URL")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("No processing history yet.")

def export_text(result: dict):
    """Export results as text file."""
    
    text_content = f"""YouTube Video Summary
====================

Video ID: {result['video_id']}
Summary Type: {result['summary_type']}
Word Count: {result['word_count']:,}
Character Count: {result['transcript_length']:,}

SUMMARY:
{result['summary']}

TRANSCRIPT:
{result['transcript']}

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    st.download_button(
        label="📥 Download Text File",
        data=text_content,
        file_name=f"youtube_summary_{result['video_id']}.txt",
        mime="text/plain"
    )

def export_csv(result: dict):
    """Export results as CSV file."""
    
    # Create DataFrame for export
    export_data = {
        'video_id': [result['video_id']],
        'summary_type': [result['summary_type']],
        'word_count': [result['word_count']],
        'character_count': [result['transcript_length']],
        'summary': [result['summary']],
        'transcript': [result['transcript']],
        'timestamp': [datetime.now().isoformat()]
    }
    
    df = pd.DataFrame(export_data)
    
    # Convert to CSV
    csv = df.to_csv(index=False)
    
    st.download_button(
        label="📥 Download CSV File",
        data=csv,
        file_name=f"youtube_summary_{result['video_id']}.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()
