"""
Tests for the core YouTube summarizer functionality.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from core import YouTubeSummarizer


class TestYouTubeSummarizer:
    """Test cases for YouTubeSummarizer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock API key for testing
        self.mock_api_key = "test_api_key_12345"
        
        # Sample transcript data
        self.sample_transcript = [
            {"text": "Hello world", "start": 0.0, "duration": 1.0},
            {"text": "This is a test video", "start": 1.0, "duration": 2.0},
            {"text": "Thank you for watching", "start": 3.0, "duration": 1.5}
        ]
        
        # Sample video info
        self.sample_video_info = {
            'video_id': 'test12345678',
            'language': 'English',
            'language_code': 'en',
            'is_generated': False,
            'is_translatable': True
        }
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        with patch.dict(os.environ, {}, clear=True):
            summarizer = YouTubeSummarizer(self.mock_api_key)
            assert summarizer.api_key == self.mock_api_key
    
    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="OpenAI API key is required"):
                YouTubeSummarizer()
    
    def test_init_with_env_api_key(self):
        """Test initialization with environment variable API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': self.mock_api_key}):
            summarizer = YouTubeSummarizer()
            assert summarizer.api_key == self.mock_api_key
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL."""
        summarizer = YouTubeSummarizer(self.mock_api_key)
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = summarizer.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_short_url(self):
        """Test extracting video ID from short YouTube URL."""
        summarizer = YouTubeSummarizer(self.mock_api_key)
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = summarizer.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_embed_url(self):
        """Test extracting video ID from embed URL."""
        summarizer = YouTubeSummarizer(self.mock_api_key)
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = summarizer.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_direct_id(self):
        """Test extracting video ID when input is already an ID."""
        summarizer = YouTubeSummarizer(self.mock_api_key)
        video_id = summarizer.extract_video_id("dQw4w9WgXcQ")
        assert video_id == "dQw4w9WgXcQ"
    
    def test_extract_video_id_invalid_url(self):
        """Test extracting video ID from invalid URL raises error."""
        summarizer = YouTubeSummarizer(self.mock_api_key)
        with pytest.raises(ValueError, match="Invalid YouTube URL or video ID"):
            summarizer.extract_video_id("https://invalid.com/video")
    
    @patch('core.YouTubeTranscriptApi')
    def test_get_transcript_success(self, mock_api):
        """Test successful transcript retrieval."""
        # Mock the API response
        mock_api.get_transcript.return_value = self.sample_transcript
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        transcript = summarizer.get_transcript("test12345678")
        
        assert "Hello world" in transcript
        assert "This is a test video" in transcript
        assert "Thank you for watching" in transcript
    
    @patch('core.YouTubeTranscriptApi')
    def test_get_transcript_fallback(self, mock_api):
        """Test transcript retrieval with fallback to available transcripts."""
        # Mock first attempt failure
        mock_api.get_transcript.side_effect = Exception("Language not available")
        
        # Mock fallback attempt
        mock_transcript = Mock()
        mock_transcript.fetch.return_value = self.sample_transcript
        
        mock_list = Mock()
        mock_list.__getitem__.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_list
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        transcript = summarizer.get_transcript("test12345678")
        
        assert "Hello world" in transcript
    
    @patch('core.YouTubeTranscriptApi')
    def test_get_transcript_failure(self, mock_api):
        """Test transcript retrieval failure."""
        # Mock both attempts to fail
        mock_api.get_transcript.side_effect = Exception("First error")
        mock_api.list_transcripts.side_effect = Exception("Second error")
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        
        with pytest.raises(Exception, match="Could not retrieve transcript"):
            summarizer.get_transcript("test12345678")
    
    @patch('core.YouTubeTranscriptApi')
    def test_get_video_info_success(self, mock_api):
        """Test successful video info retrieval."""
        # Mock the API response
        mock_transcript = Mock()
        mock_transcript.language = 'English'
        mock_transcript.language_code = 'en'
        mock_transcript.is_generated = False
        mock_transcript.is_translatable = True
        
        mock_list = Mock()
        mock_list.__getitem__.return_value = mock_transcript
        mock_api.list_transcripts.return_value = mock_list
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        video_info = summarizer.get_video_info("test12345678")
        
        assert video_info['language'] == 'English'
        assert video_info['language_code'] == 'en'
        assert video_info['is_generated'] is False
        assert video_info['is_translatable'] is True
    
    @patch('core.YouTubeTranscriptApi')
    def test_get_video_info_failure(self, mock_api):
        """Test video info retrieval failure."""
        # Mock API to fail
        mock_api.list_transcripts.side_effect = Exception("API error")
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        video_info = summarizer.get_video_info("test12345678")
        
        assert 'error' in video_info
        assert video_info['video_id'] == 'test12345678'
    
    @patch('core.openai.ChatCompletion.create')
    def test_summarize_transcript_success(self, mock_openai):
        """Test successful transcript summarization."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test summary."
        mock_openai.return_value = mock_response
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        summary = summarizer.summarize_transcript("Test transcript content", "short")
        
        assert summary == "This is a test summary."
        mock_openai.assert_called_once()
    
    @patch('core.openai.ChatCompletion.create')
    def test_summarize_transcript_failure(self, mock_openai):
        """Test transcript summarization failure."""
        # Mock OpenAI to fail
        mock_openai.side_effect = Exception("OpenAI API error")
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        
        with pytest.raises(Exception, match="Error generating summary"):
            summarizer.summarize_transcript("Test transcript content", "short")
    
    @patch('core.openai.ChatCompletion.create')
    def test_get_detailed_summary_success(self, mock_openai):
        """Test successful detailed summary generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Detailed analysis content"
        mock_openai.return_value = mock_response
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        result = summarizer.get_detailed_summary("Test transcript content")
        
        assert result['detailed_summary'] == "Detailed analysis content"
        assert 'transcript_length' in result
        assert 'word_count' in result
    
    @patch('core.openai.ChatCompletion.create')
    def test_get_detailed_summary_failure(self, mock_openai):
        """Test detailed summary generation failure."""
        # Mock OpenAI to fail
        mock_openai.side_effect = Exception("OpenAI API error")
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        
        with pytest.raises(Exception, match="Error generating detailed summary"):
            summarizer.get_detailed_summary("Test transcript content")
    
    @patch.object(YouTubeSummarizer, 'extract_video_id')
    @patch.object(YouTubeSummarizer, 'get_video_info')
    @patch.object(YouTubeSummarizer, 'get_transcript')
    @patch.object(YouTubeSummarizer, 'summarize_transcript')
    def test_process_video_success(self, mock_summarize, mock_transcript, mock_info, mock_extract):
        """Test successful video processing pipeline."""
        # Mock all the method calls
        mock_extract.return_value = "test12345678"
        mock_info.return_value = self.sample_video_info
        mock_transcript.return_value = "Test transcript content"
        mock_summarize.return_value = "Test summary"
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        result = summarizer.process_video("https://youtube.com/watch?v=test12345678", "medium")
        
        assert result['success'] is True
        assert result['video_id'] == "test12345678"
        assert result['summary'] == "Test summary"
        assert result['summary_type'] == "medium"
    
    @patch.object(YouTubeSummarizer, 'extract_video_id')
    def test_process_video_failure(self, mock_extract):
        """Test video processing pipeline failure."""
        # Mock extraction to fail
        mock_extract.side_effect = Exception("Invalid URL")
        
        summarizer = YouTubeSummarizer(self.mock_api_key)
        result = summarizer.process_video("invalid_url", "medium")
        
        assert result['success'] is False
        assert 'error' in result
        assert result['url'] == "invalid_url"


if __name__ == "__main__":
    pytest.main([__file__])
