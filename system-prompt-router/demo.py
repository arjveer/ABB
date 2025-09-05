#!/usr/bin/env python3
"""
Quick demo of the System Prompt Router.
Shows the system in action without requiring OpenAI API calls.
"""

from prompt_router import SystemPromptRouter
from prompt_library import get_prompt_library


def demo_without_openai():
    """Demo that shows prompt matching without OpenAI API calls."""
    print("🎯 System Prompt Router Demo (No OpenAI Required)")
    print("=" * 60)
    
    # Initialize router (without OpenAI for this demo)
    try:
        router = SystemPromptRouter()
        router.load_prompt_library(get_prompt_library())
        print("✅ Router initialized successfully!")
    except ValueError:
        print("⚠️  OpenAI API key not found, but we can still demo prompt matching!")
        # Create a mock router for demo purposes
        router = SystemPromptRouter.__new__(SystemPromptRouter)
        router.embedding_model = None
        router.prompt_library = {}
        router.prompt_embeddings = None
        router.prompt_names = []
        
        # Load library manually for demo
        from sentence_transformers import SentenceTransformer
        router.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        router.load_prompt_library(get_prompt_library())
    
    print(f"📚 Loaded {len(router.prompt_library)} prompts from library")
    
    # Show available prompts
    print("\n📋 Available Prompts:")
    print("-" * 40)
    for name, data in router.list_prompts().items():
        print(f"• {name}: {data}")
    
    # Demo queries
    demo_queries = [
        "Write a Python function to sort a list",
        "Summarize this video about machine learning",
        "What are the legal requirements for starting a business?",
        "Analyze this sales data and create a chart",
        "Write a creative story about a robot",
        "Create documentation for this API endpoint",
        "Explain the difference between 'affect' and 'effect'",
        "Help me create a business plan for my startup",
        "Explain how photosynthesis works",
        "Help me organize my daily tasks and improve productivity"
    ]
    
    print(f"\n🔍 Testing {len(demo_queries)} demo queries:")
    print("=" * 60)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 50)
        
        try:
            # Find best matches
            matches = router.find_best_prompt(query, top_k=3)
            
            print("Top 3 matches:")
            for j, (name, score, _) in enumerate(matches, 1):
                prompt_details = router.get_prompt_details(name)
                print(f"  {j}. {name} (similarity: {score:.3f})")
                print(f"     {prompt_details['description']}")
            
            # Show the best match's system prompt (truncated)
            best_name, best_score, best_prompt = matches[0]
            print(f"\n🎯 Best match: {best_name}")
            print(f"📝 System prompt preview:")
            print(f"   {best_prompt[:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n✅ Demo completed! The system successfully matched queries to appropriate prompts.")
    print(f"\n💡 To generate actual responses, set your OPENAI_API_KEY and run:")
    print(f"   python main.py")
    print(f"   python cli.py 'your query here'")


if __name__ == "__main__":
    demo_without_openai()
