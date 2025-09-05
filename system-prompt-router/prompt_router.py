"""
System Prompt Router - Routes user queries to appropriate system prompts using semantic similarity.
"""

import os
import numpy as np
from typing import Dict, List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SystemPromptRouter:
    """
    A system that matches user queries to the best system prompt using semantic similarity.
    """
    
    def __init__(
        self, 
        embedding_model: str = "all-MiniLM-L6-v2",
        openai_model: str = "gpt-3.5-turbo",
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize the System Prompt Router.
        
        Args:
            embedding_model: Name of the sentence transformer model to use
            openai_model: OpenAI model to use for generating responses
            openai_api_key: OpenAI API key (if not provided, will use OPENAI_API_KEY env var)
        """
        self.embedding_model_name = embedding_model
        self.openai_model = openai_model
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.openai_client = OpenAI(api_key=api_key)
        
        # Initialize prompt library
        self.prompt_library: Dict[str, str] = {}
        self.prompt_embeddings: Optional[np.ndarray] = None
        self.prompt_names: List[str] = []
        
    def add_prompt(self, name: str, description: str, system_prompt: str) -> None:
        """
        Add a new prompt to the library.
        
        Args:
            name: Short descriptive name for the prompt
            description: Description that will be used for similarity matching
            system_prompt: The actual system prompt to use
        """
        self.prompt_library[name] = {
            "description": description,
            "system_prompt": system_prompt
        }
        
        # Recompute embeddings when new prompt is added
        self._compute_prompt_embeddings()
    
    def load_prompt_library(self, prompts: Dict[str, Dict[str, str]]) -> None:
        """
        Load a complete prompt library at once.
        
        Args:
            prompts: Dictionary where keys are prompt names and values contain
                    'description' and 'system_prompt' keys
        """
        self.prompt_library = prompts
        self._compute_prompt_embeddings()
    
    def _compute_prompt_embeddings(self) -> None:
        """Compute embeddings for all prompt descriptions."""
        if not self.prompt_library:
            return
            
        descriptions = []
        self.prompt_names = []
        
        for name, prompt_data in self.prompt_library.items():
            descriptions.append(prompt_data["description"])
            self.prompt_names.append(name)
        
        # Compute embeddings
        self.prompt_embeddings = self.embedding_model.encode(descriptions)
        print(f"Computed embeddings for {len(descriptions)} prompts")
    
    def find_best_prompt(self, user_query: str, top_k: int = 1) -> List[Tuple[str, float, str]]:
        """
        Find the best matching prompt(s) for a user query.
        
        Args:
            user_query: The user's input query
            top_k: Number of top matches to return
            
        Returns:
            List of tuples containing (prompt_name, similarity_score, system_prompt)
        """
        if not self.prompt_library or self.prompt_embeddings is None:
            raise ValueError("No prompts loaded. Please add prompts first.")
        
        # Embed the user query
        query_embedding = self.embedding_model.encode([user_query])
        
        # Compute cosine similarity
        similarities = np.dot(self.prompt_embeddings, query_embedding.T).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            prompt_name = self.prompt_names[idx]
            similarity_score = float(similarities[idx])
            system_prompt = self.prompt_library[prompt_name]["system_prompt"]
            results.append((prompt_name, similarity_score, system_prompt))
        
        return results
    
    def generate_response(
        self, 
        user_query: str, 
        use_best_prompt: bool = True,
        custom_system_prompt: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate a response using the best matching prompt or a custom prompt.
        
        Args:
            user_query: The user's input query
            use_best_prompt: Whether to use the best matching prompt
            custom_system_prompt: Custom system prompt to use (overrides use_best_prompt)
            
        Returns:
            Dictionary containing the response and metadata
        """
        if custom_system_prompt:
            system_prompt = custom_system_prompt
            matched_prompt = "custom"
            similarity_score = None
        elif use_best_prompt:
            best_matches = self.find_best_prompt(user_query, top_k=1)
            if not best_matches:
                raise ValueError("No prompts available for matching")
            
            matched_prompt, similarity_score, system_prompt = best_matches[0]
        else:
            raise ValueError("Either use_best_prompt must be True or custom_system_prompt must be provided")
        
        # Generate response using OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                "response": response.choices[0].message.content,
                "matched_prompt": matched_prompt,
                "similarity_score": similarity_score,
                "system_prompt_used": system_prompt,
                "model_used": self.openai_model,
                "usage": response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "matched_prompt": matched_prompt,
                "similarity_score": similarity_score,
                "system_prompt_used": system_prompt
            }
    
    def list_prompts(self) -> Dict[str, str]:
        """Return a list of all loaded prompts with their descriptions."""
        return {
            name: data["description"] 
            for name, data in self.prompt_library.items()
        }
    
    def get_prompt_details(self, prompt_name: str) -> Optional[Dict[str, str]]:
        """Get full details of a specific prompt."""
        return self.prompt_library.get(prompt_name)
