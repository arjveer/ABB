#!/usr/bin/env python3
"""
Command-line interface for YouTube video summarizer.
Provides a simple way to summarize YouTube videos from the terminal.
"""

import argparse
import sys
import os
from pathlib import Path
from core import YouTubeSummarizer

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="YouTube Video Summarizer - Extract transcripts and generate AI-powered summaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s dQw4w9WgXcQ --type detailed --output summary.txt
  %(prog)s "https://youtu.be/kJAsCz9hdJQ" --type short --model gpt-4o-mini
        """
    )
    
    parser.add_argument(
        "url_or_id",
        help="YouTube video URL or video ID"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["short", "medium", "long", "detailed"],
        default="medium",
        help="Summary type (default: medium)"
    )
    
    parser.add_argument(
        "--model", "-m",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: print to stdout)"
    )
    
    parser.add_argument(
        "--transcript-only",
        action="store_true",
        help="Only extract and display transcript, no summary"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (can also use OPENAI_API_KEY environment variable)"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize summarizer
        summarizer = YouTubeSummarizer(api_key=args.api_key)
        summarizer.model = args.model
        
        if args.verbose:
            print(f"🔧 Using model: {summarizer.model}")
            print(f"🎯 Summary type: {args.type}")
            print(f"📺 Processing: {args.url_or_id}")
            print()
        
        # Process video
        if args.transcript_only:
            # Extract transcript only
            video_id = summarizer.extract_video_id(args.url_or_id)
            transcript = summarizer.get_transcript(video_id)
            
            if args.verbose:
                print(f"✅ Transcript extracted successfully!")
                print(f"📊 Length: {len(transcript):,} characters, {len(transcript.split()):,} words")
                print()
            
            output_content = transcript
            
        else:
            # Full processing with summary
            result = summarizer.process_video(args.url_or_id, args.type)
            
            if not result["success"]:
                print(f"❌ Error: {result['error']}", file=sys.stderr)
                sys.exit(1)
            
            if args.verbose:
                print(f"✅ Video processed successfully!")
                print(f"🎬 Video ID: {result['video_id']}")
                print(f"📊 Transcript: {result['word_count']:,} words, {result['transcript_length']:,} characters")
                print()
            
            # Format output
            output_content = format_output(result, args.type)
        
        # Output results
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output_content, encoding='utf-8')
            print(f"💾 Results saved to: {output_path}")
        else:
            print(output_content)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def format_output(result: dict, summary_type: str) -> str:
    """Format the output content based on summary type."""
    
    if summary_type == "detailed":
        return format_detailed_output(result)
    else:
        return format_simple_output(result)

def format_simple_output(result: dict) -> str:
    """Format simple summary output."""
    
    output = f"""YouTube Video Summary
{'=' * 50}

🎬 Video ID: {result['video_id']}
📊 Statistics: {result['word_count']:,} words, {result['transcript_length']:,} characters
🎯 Summary Type: {result['summary_type'].title()}

📝 SUMMARY:
{result['summary']}

📄 TRANSCRIPT:
{result['transcript']}
"""
    return output

def format_detailed_output(result: dict) -> str:
    """Format detailed summary output."""
    
    # For detailed summaries, the summary already contains structured information
    output = f"""YouTube Video Summary (Detailed)
{'=' * 50}

🎬 Video ID: {result['video_id']}
📊 Statistics: {result['word_count']:,} words, {result['transcript_length']:,} characters
🎯 Summary Type: {result['summary_type'].title()}

📝 DETAILED ANALYSIS:
{result['summary']}

📄 TRANSCRIPT:
{result['transcript']}
"""
    return output

if __name__ == "__main__":
    main()
