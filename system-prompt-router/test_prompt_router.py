"""
Test suite for the System Prompt Router.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from prompt_router import SystemPromptRouter
from prompt_library import get_prompt_library


class TestSystemPromptRouter:
    """Test cases for SystemPromptRouter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
            self.router = SystemPromptRouter()
    
    def test_initialization(self):
        """Test router initialization."""
        assert self.router.embedding_model is not None
        assert self.router.openai_client is not None
        assert self.router.prompt_library == {}
        assert self.router.prompt_embeddings is None
    
    def test_add_prompt(self):
        """Test adding a single prompt."""
        self.router.add_prompt(
            name="test_prompt",
            description="A test prompt for testing",
            system_prompt="You are a test assistant."
        )
        
        assert "test_prompt" in self.router.prompt_library
        assert self.router.prompt_library["test_prompt"]["description"] == "A test prompt for testing"
        assert self.router.prompt_library["test_prompt"]["system_prompt"] == "You are a test assistant."
        assert self.router.prompt_embeddings is not None
        assert len(self.router.prompt_names) == 1
    
    def test_load_prompt_library(self):
        """Test loading a complete prompt library."""
        test_prompts = {
            "prompt1": {
                "description": "First test prompt",
                "system_prompt": "You are the first assistant."
            },
            "prompt2": {
                "description": "Second test prompt", 
                "system_prompt": "You are the second assistant."
            }
        }
        
        self.router.load_prompt_library(test_prompts)
        
        assert len(self.router.prompt_library) == 2
        assert self.router.prompt_embeddings is not None
        assert self.router.prompt_embeddings.shape[0] == 2
        assert len(self.router.prompt_names) == 2
    
    def test_find_best_prompt(self):
        """Test finding the best matching prompt."""
        # Add test prompts
        self.router.add_prompt(
            name="code_prompt",
            description="Help with programming and coding",
            system_prompt="You are a coding assistant."
        )
        self.router.add_prompt(
            name="cooking_prompt",
            description="Help with cooking and recipes",
            system_prompt="You are a cooking assistant."
        )
        
        # Test query
        query = "How do I write a Python function?"
        matches = self.router.find_best_prompt(query, top_k=2)
        
        assert len(matches) == 2
        assert all(isinstance(match, tuple) and len(match) == 3 for match in matches)
        assert all(isinstance(score, (int, float)) for _, score, _ in matches)
        
        # Code prompt should rank higher for programming query
        assert matches[0][0] == "code_prompt"
        assert matches[0][1] > matches[1][1]  # Higher similarity score
    
    def test_find_best_prompt_no_prompts(self):
        """Test finding best prompt when no prompts are loaded."""
        with pytest.raises(ValueError, match="No prompts loaded"):
            self.router.find_best_prompt("test query")
    
    @patch('prompt_router.OpenAI')
    def test_generate_response_success(self, mock_openai):
        """Test successful response generation."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.usage = Mock()
        mock_response.usage.dict.return_value = {"total_tokens": 100}
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        self.router.openai_client = mock_client
        
        # Add test prompt
        self.router.add_prompt(
            name="test_prompt",
            description="Test prompt",
            system_prompt="You are a test assistant."
        )
        
        # Generate response
        response = self.router.generate_response("test query")
        
        assert "response" in response
        assert response["response"] == "Test response"
        assert response["matched_prompt"] == "test_prompt"
        assert response["similarity_score"] is not None
        assert response["model_used"] == "gpt-3.5-turbo"
    
    @patch('prompt_router.OpenAI')
    def test_generate_response_error(self, mock_openai):
        """Test response generation with error."""
        # Mock OpenAI error
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        self.router.openai_client = mock_client
        
        # Add test prompt
        self.router.add_prompt(
            name="test_prompt",
            description="Test prompt",
            system_prompt="You are a test assistant."
        )
        
        # Generate response
        response = self.router.generate_response("test query")
        
        assert "error" in response
        assert response["error"] == "API Error"
    
    def test_generate_response_custom_prompt(self):
        """Test response generation with custom system prompt."""
        with patch('prompt_router.OpenAI') as mock_openai:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Custom response"
            mock_response.usage = Mock()
            mock_response.usage.dict.return_value = {"total_tokens": 50}
            
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = mock_response
            self.router.openai_client = mock_client
            
            response = self.router.generate_response(
                "test query",
                custom_system_prompt="You are a custom assistant."
            )
            
            assert response["response"] == "Custom response"
            assert response["matched_prompt"] == "custom"
            assert response["similarity_score"] is None
    
    def test_list_prompts(self):
        """Test listing all prompts."""
        self.router.add_prompt(
            name="prompt1",
            description="First prompt",
            system_prompt="System prompt 1"
        )
        self.router.add_prompt(
            name="prompt2", 
            description="Second prompt",
            system_prompt="System prompt 2"
        )
        
        prompts = self.router.list_prompts()
        
        assert len(prompts) == 2
        assert prompts["prompt1"] == "First prompt"
        assert prompts["prompt2"] == "Second prompt"
    
    def test_get_prompt_details(self):
        """Test getting prompt details."""
        self.router.add_prompt(
            name="test_prompt",
            description="Test description",
            system_prompt="Test system prompt"
        )
        
        details = self.router.get_prompt_details("test_prompt")
        assert details["description"] == "Test description"
        assert details["system_prompt"] == "Test system prompt"
        
        # Test non-existent prompt
        assert self.router.get_prompt_details("nonexistent") is None


class TestPromptLibrary:
    """Test cases for the prompt library."""
    
    def test_get_prompt_library(self):
        """Test getting the prompt library."""
        library = get_prompt_library()
        
        assert isinstance(library, dict)
        assert len(library) > 0
        
        # Check structure
        for name, data in library.items():
            assert "description" in data
            assert "system_prompt" in data
            assert isinstance(data["description"], str)
            assert isinstance(data["system_prompt"], str)
    
    def test_get_prompt_by_name(self):
        """Test getting a specific prompt by name."""
        from prompt_library import get_prompt_by_name
        
        # Test existing prompt
        prompt = get_prompt_by_name("code_writer")
        assert prompt is not None
        assert "description" in prompt
        assert "system_prompt" in prompt
        
        # Test non-existent prompt
        assert get_prompt_by_name("nonexistent") is None
    
    def test_list_prompt_names(self):
        """Test listing prompt names."""
        from prompt_library import list_prompt_names
        
        names = list_prompt_names()
        assert isinstance(names, list)
        assert len(names) > 0
        assert "code_writer" in names
    
    def test_search_prompts_by_keyword(self):
        """Test searching prompts by keyword."""
        from prompt_library import search_prompts_by_keyword
        
        # Search for code-related prompts
        code_prompts = search_prompts_by_keyword("code")
        assert len(code_prompts) > 0
        assert "code_writer" in code_prompts
        
        # Search for non-existent keyword
        empty_prompts = search_prompts_by_keyword("nonexistent")
        assert len(empty_prompts) == 0


if __name__ == "__main__":
    pytest.main([__file__])
