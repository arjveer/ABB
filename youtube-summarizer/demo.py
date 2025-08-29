#!/usr/bin/env python3
"""
Demo script for YouTube Video Summarizer.
Shows how to use the summarizer programmatically.
"""

import os
import sys
from core import YouTubeSummarizer


def demo_basic_usage():
    """Demonstrate basic usage of the YouTube summarizer."""
    print("🎬 YouTube Video Summarizer Demo")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your_api_key_here'")
        return False
    
    try:
        # Initialize the summarizer
        print("🔧 Initializing summarizer...")
        summarizer = YouTubeSummarizer(api_key)
        print(f"✅ Using model: {summarizer.model}")
        
        # Example video ID (you can change this)
        video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
        
        print(f"\n📺 Processing video: {video_id}")
        
        # Get video information
        print("📊 Getting video information...")
        video_info = summarizer.get_video_info(video_id)
        
        if "error" in video_info:
            print(f"⚠️  Warning: Could not get video info: {video_info['error']}")
        else:
            print(f"✅ Language: {video_info.get('language', 'Unknown')}")
            print(f"✅ Generated: {'Yes' if video_info.get('is_generated') else 'No'}")
            print(f"✅ Translatable: {'Yes' if video_info.get('is_translatable') else 'No'}")
        
        # Get transcript
        print("\n📝 Extracting transcript...")
        transcript = summarizer.get_transcript(video_id)
        print(f"✅ Transcript extracted: {len(transcript):,} characters, {len(transcript.split()):,} words")
        
        # Show transcript preview
        preview_length = 200
        if len(transcript) > preview_length:
            print(f"📄 Transcript preview: {transcript[:preview_length]}...")
        else:
            print(f"📄 Full transcript: {transcript}")
        
        # Generate different types of summaries
        summary_types = ["short", "medium", "long"]
        
        for summary_type in summary_types:
            print(f"\n🤖 Generating {summary_type} summary...")
            try:
                summary = summarizer.summarize_transcript(transcript, summary_type)
                print(f"✅ {summary_type.title()} Summary:")
                print(f"   {summary}")
            except Exception as e:
                print(f"❌ Error generating {summary_type} summary: {e}")
        
        # Generate detailed summary
        print(f"\n🔍 Generating detailed analysis...")
        try:
            detailed_result = summarizer.get_detailed_summary(transcript)
            print("✅ Detailed Analysis:")
            print(detailed_result['detailed_summary'])
        except Exception as e:
            print(f"❌ Error generating detailed analysis: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        return False


def demo_url_parsing():
    """Demonstrate URL parsing capabilities."""
    print("\n🔗 URL Parsing Demo")
    print("=" * 30)
    
    summarizer = YouTubeSummarizer("dummy_key")  # We only need this for URL parsing
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/embed/dQw4w9WgXcQ",
        "https://www.youtube.com/v/dQw4w9WgXcQ",
        "dQw4w9WgXcQ"  # Direct video ID
    ]
    
    for url in test_urls:
        try:
            video_id = summarizer.extract_video_id(url)
            print(f"✅ {url} → {video_id}")
        except Exception as e:
            print(f"❌ {url} → Error: {e}")


def demo_batch_processing():
    """Demonstrate batch processing capabilities."""
    print("\n📚 Batch Processing Demo")
    print("=" * 30)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Skipping batch demo - no API key available")
        return
    
    # Example video IDs (you can change these)
    video_ids = [
        "dQw4w9WgXcQ",  # Rick Astley
        "kJAsCz9hdJQ",  # Another example
    ]
    
    try:
        summarizer = YouTubeSummarizer(api_key)
        
        for i, video_id in enumerate(video_ids, 1):
            print(f"\n🎬 Processing video {i}/{len(video_ids)}: {video_id}")
            
            try:
                # Process the video
                result = summarizer.process_video(video_id, "medium")
                
                if result["success"]:
                    print(f"✅ Success! {result['word_count']:,} words processed")
                    print(f"📝 Summary preview: {result['summary'][:100]}...")
                else:
                    print(f"❌ Failed: {result['error']}")
                    
            except Exception as e:
                print(f"❌ Error processing {video_id}: {e}")
                
    except Exception as e:
        print(f"❌ Error during batch demo: {e}")


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n⚠️  Error Handling Demo")
    print("=" * 30)
    
    # Test with invalid video ID
    invalid_id = "invalid_video_id_123"
    
    try:
        summarizer = YouTubeSummarizer("dummy_key")
        
        print(f"🔍 Testing with invalid video ID: {invalid_id}")
        
        # This should fail gracefully
        result = summarizer.process_video(invalid_id, "medium")
        
        if not result["success"]:
            print(f"✅ Error handled gracefully: {result['error']}")
        else:
            print("⚠️  Unexpected success with invalid ID")
            
    except Exception as e:
        print(f"✅ Exception caught and handled: {e}")


def main():
    """Main demo function."""
    print("🚀 Starting YouTube Video Summarizer Demo")
    print("=" * 60)
    
    # Run demos
    success = demo_basic_usage()
    
    if success:
        demo_url_parsing()
        demo_batch_processing()
        demo_error_handling()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Try the web interface: streamlit run app.py")
        print("   2. Use the CLI: python cli.py <video_url>")
        print("   3. Integrate into your own code")
        
    else:
        print("\n❌ Demo failed. Please check your setup and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
