"""
Core functionality for YouTube video summarizer.
Handles transcript extraction and OpenAI API integration.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

import openai
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeSummarizer:
    """Main class for summarizing YouTube videos."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the summarizer with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client with new API format
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.formatter = TextFormatter()
    
    def extract_video_id(self, url: str) -> str:
        """Extract YouTube video ID from various URL formats."""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume the input is already a video ID
        if len(url) == 11 and url.isalnum():
            return url
        
        raise ValueError("Invalid YouTube URL or video ID")
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> str:
        """Get transcript for a YouTube video."""
        if languages is None:
            languages = ['en', 'en-US', 'en-GB']
        
        try:
            # Create an instance of the API
            yt_api = YouTubeTranscriptApi()
            
            # Try to get transcript in preferred languages
            transcript_list = yt_api.fetch(video_id, languages=languages)
            
            # Format transcript to plain text
            transcript_text = self.formatter.format_transcript(transcript_list)
            return transcript_text
            
        except Exception as e:
            # Try to get available transcripts using the list method
            try:
                transcript_list = yt_api.list(video_id)
                
                if not transcript_list:
                    raise Exception("No transcripts available for this video")
                
                # Get the first available transcript
                transcript = transcript_list[0]
                transcript_data = transcript.fetch()
                
                # Format transcript to plain text
                transcript_text = self.formatter.format_transcript(transcript_data)
                return transcript_text
                
            except Exception as e2:
                raise Exception(f"Could not retrieve transcript: {str(e2)}")
    
    def get_video_info(self, video_id: str) -> Dict[str, str]:
        """Get basic video information."""
        try:
            # Create an instance of the API
            yt_api = YouTubeTranscriptApi()
            transcript_list = yt_api.list(video_id)
            transcript = transcript_list[0]
            
            # Get video metadata from transcript
            video_info = {
                'video_id': video_id,
                'language': transcript.language,
                'language_code': transcript.language_code,
                'is_generated': transcript.is_generated,
                'is_translatable': transcript.is_translatable,
            }
            
            return video_info
            
        except Exception as e:
            return {'video_id': video_id, 'error': str(e)}
    
    def summarize_transcript(self, transcript: str, summary_length: str = "medium") -> str:
        """Summarize transcript using OpenAI GPT-4o."""
        
        # Define summary length parameters
        length_params = {
            "short": {"max_tokens": 150, "description": "a concise 2-3 sentence summary"},
            "medium": {"max_tokens": 300, "description": "a comprehensive paragraph summary"},
            "long": {"max_tokens": 500, "description": "a detailed multi-paragraph summary"}
        }
        
        params = length_params.get(summary_length, length_params["medium"])
        
        # Prepare the prompt
        prompt = f"""Please provide {params['description']} of the following YouTube video transcript. 
        Focus on the main points, key insights, and important details. 
        Make it engaging and easy to understand.

        Transcript:
        {transcript}

        Summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates clear, engaging summaries of video content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=params["max_tokens"],
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def get_detailed_summary(self, transcript: str) -> Dict[str, str]:
        """Get a detailed summary with multiple aspects."""
        
        detailed_prompt = """Please analyze the following YouTube video transcript and provide:

1. **Main Topic**: What is the video about?
2. **Key Points**: What are the 3-5 most important points discussed?
3. **Key Insights**: What valuable insights or takeaways are provided?
4. **Summary**: A comprehensive summary of the content
5. **Action Items**: What should viewers do with this information?

Transcript:
{transcript}

Please format your response clearly with the above sections."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content analyst that provides structured, actionable summaries."},
                    {"role": "user", "content": detailed_prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return {
                "detailed_summary": response.choices[0].message.content.strip(),
                "transcript_length": len(transcript),
                "word_count": len(transcript.split())
            }
            
        except Exception as e:
            raise Exception(f"Error generating detailed summary: {str(e)}")
    
    def process_video(self, url: str, summary_type: str = "medium") -> Dict[str, any]:
        """Complete pipeline to process a YouTube video URL."""
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            
            # Get video info
            video_info = self.get_video_info(video_id)
            
            # Get transcript
            transcript = self.get_transcript(video_id)
            
            # Generate summary
            if summary_type == "detailed":
                summary_result = self.get_detailed_summary(transcript)
                summary = summary_result["detailed_summary"]
            else:
                summary = self.summarize_transcript(transcript, summary_type)
            
            return {
                "success": True,
                "video_id": video_id,
                "video_info": video_info,
                "transcript": transcript,
                "summary": summary,
                "summary_type": summary_type,
                "transcript_length": len(transcript),
                "word_count": len(transcript.split())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url
            }
