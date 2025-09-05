"""
Main application demonstrating the System Prompt Router.
"""

import os
from prompt_router import SystemPromptRouter
from prompt_library import get_prompt_library


def main():
    """Main function to demonstrate the System Prompt Router."""
    
    print("🚀 System Prompt Router Demo")
    print("=" * 50)
    
    # Initialize the router
    try:
        router = SystemPromptRouter(
            embedding_model="all-MiniLM-L6-v2",
            openai_model="gpt-3.5-turbo"
        )
        print("✅ Router initialized successfully!")
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set your OPENAI_API_KEY environment variable.")
        return
    
    # Load the prompt library
    prompt_library = get_prompt_library()
    router.load_prompt_library(prompt_library)
    print(f"✅ Loaded {len(prompt_library)} prompts from library")
    
    # Display available prompts
    print("\n📚 Available Prompts:")
    print("-" * 30)
    for name, data in router.list_prompts().items():
        print(f"• {name}: {data}")
    
    # Interactive demo
    print("\n🎯 Interactive Demo")
    print("=" * 50)
    print("Enter your query (or 'quit' to exit, 'list' to see prompts):")
    
    while True:
        user_input = input("\n💬 Your query: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        elif user_input.lower() == 'list':
            print("\n📚 Available Prompts:")
            for name, desc in router.list_prompts().items():
                print(f"• {name}: {desc}")
            continue
        elif not user_input:
            continue
        
        # Find the best matching prompt
        print("\n🔍 Finding best prompt...")
        try:
            best_matches = router.find_best_prompt(user_input, top_k=3)
            
            print(f"\n🎯 Best matches:")
            for i, (name, score, system_prompt) in enumerate(best_matches, 1):
                print(f"{i}. {name} (similarity: {score:.3f})")
                print(f"   Description: {router.get_prompt_details(name)['description']}")
            
            # Generate response using the best prompt
            print(f"\n🤖 Generating response using '{best_matches[0][0]}' prompt...")
            response = router.generate_response(user_input)
            
            if "error" in response:
                print(f"❌ Error: {response['error']}")
            else:
                print(f"\n📝 Response:")
                print("-" * 40)
                print(response["response"])
                print("-" * 40)
                print(f"\n📊 Details:")
                print(f"• Matched prompt: {response['matched_prompt']}")
                print(f"• Similarity score: {response['similarity_score']:.3f}")
                print(f"• Model used: {response['model_used']}")
                if response.get('usage'):
                    print(f"• Tokens used: {response['usage']['total_tokens']}")
        
        except Exception as e:
            print(f"❌ Error: {e}")


def demo_queries():
    """Run a demo with predefined queries."""
    print("🎬 Running Demo Queries")
    print("=" * 50)
    
    # Initialize router
    try:
        router = SystemPromptRouter()
        router.load_prompt_library(get_prompt_library())
    except ValueError as e:
        print(f"❌ Error: {e}")
        return
    
    # Demo queries
    demo_queries = [
        "Write a Python function to sort a list",
        "Summarize the key points from this video about machine learning",
        "What are the legal requirements for starting a business?",
        "Analyze this sales data and create a chart",
        "Write a creative story about a robot",
        "Create documentation for this API endpoint",
        "Explain the difference between 'affect' and 'effect'",
        "Help me create a business plan for my startup",
        "Explain how photosynthesis works",
        "Help me organize my daily tasks and improve productivity"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 60)
        
        try:
            # Find best match
            best_matches = router.find_best_prompt(query, top_k=1)
            best_name, best_score, _ = best_matches[0]
            
            print(f"🎯 Best match: {best_name} (similarity: {best_score:.3f})")
            
            # Generate response
            response = router.generate_response(query)
            
            if "error" not in response:
                print(f"✅ Response generated successfully")
                print(f"📊 Tokens used: {response.get('usage', {}).get('total_tokens', 'N/A')}")
            else:
                print(f"❌ Error: {response['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_queries()
    else:
        main()
