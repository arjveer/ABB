#!/usr/bin/env python3
"""
Simple example usage of the YouTube Video Summarizer.
This script demonstrates the basic functionality.
"""

import os
from core import YouTubeSummarizer


def main():
    """Simple example of using the YouTube summarizer."""
    
    # You need to set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        return
    
    # Initialize the summarizer
    summarizer = YouTubeSummarizer(api_key)
    
    # Example video URL (change this to any YouTube video you want to summarize)
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"🎬 Processing: {video_url}")
    
    try:
        # Process the video and get a medium-length summary
        result = summarizer.process_video(video_url, "medium")
        
        if result["success"]:
            print(f"✅ Success! Video ID: {result['video_id']}")
            print(f"📊 Transcript: {result['word_count']:,} words")
            print(f"📝 Summary: {result['summary']}")
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
