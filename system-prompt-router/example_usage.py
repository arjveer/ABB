"""
Example usage of the System Prompt Router.
Demonstrates various features and use cases.
"""

import os
from prompt_router import SystemPromptRouter
from prompt_library import get_prompt_library


def basic_example():
    """Basic example of using the System Prompt Router."""
    print("🔧 Basic Example")
    print("=" * 50)
    
    # Initialize router
    router = SystemPromptRouter()
    
    # Load prompt library
    router.load_prompt_library(get_prompt_library())
    
    # Example query
    query = "Write a Python function to calculate fibonacci numbers"
    
    print(f"Query: {query}")
    
    # Find best prompt
    matches = router.find_best_prompt(query, top_k=3)
    print(f"\nTop 3 matches:")
    for i, (name, score, _) in enumerate(matches, 1):
        print(f"{i}. {name} (similarity: {score:.3f})")
    
    # Generate response
    response = router.generate_response(query)
    print(f"\nResponse: {response['response']}")
    print(f"Matched prompt: {response['matched_prompt']}")


def custom_prompts_example():
    """Example of adding custom prompts."""
    print("\n🎨 Custom Prompts Example")
    print("=" * 50)
    
    router = SystemPromptRouter()
    
    # Add custom prompts
    router.add_prompt(
        name="recipe_helper",
        description="Help with cooking recipes, meal planning, and food preparation",
        system_prompt="""You are a helpful cooking assistant and recipe expert. Your role is to:
- Provide detailed cooking instructions and recipes
- Suggest ingredient substitutions and modifications
- Help with meal planning and nutrition
- Answer cooking technique questions
- Provide tips for food preparation and storage

Always consider dietary restrictions and preferences when making suggestions."""
    )
    
    router.add_prompt(
        name="travel_planner",
        description="Plan trips, suggest destinations, and provide travel advice",
        system_prompt="""You are a travel planning expert and destination guide. Your role is to:
- Suggest travel destinations and itineraries
- Provide information about attractions, activities, and local culture
- Help with travel logistics and planning
- Recommend accommodations and transportation options
- Share travel tips and safety advice

Consider budget, interests, and travel preferences in your recommendations."""
    )
    
    # Test with custom prompts
    queries = [
        "How do I make a perfect chocolate cake?",
        "Plan a 5-day trip to Japan",
        "What's the best way to cook pasta?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        matches = router.find_best_prompt(query, top_k=2)
        for i, (name, score, _) in enumerate(matches, 1):
            print(f"{i}. {name} (similarity: {score:.3f})")


def similarity_analysis_example():
    """Example showing similarity analysis for different query types."""
    print("\n📊 Similarity Analysis Example")
    print("=" * 50)
    
    router = SystemPromptRouter()
    router.load_prompt_library(get_prompt_library())
    
    # Test queries with different intents
    test_queries = [
        "Write a function to sort an array",
        "Summarize this video about AI",
        "What are my legal rights as a tenant?",
        "Create a bar chart from this data",
        "Write a poem about nature",
        "Document this API endpoint",
        "Explain English grammar rules",
        "Help me start a business",
        "How does DNA replication work?",
        "Organize my daily schedule"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        matches = router.find_best_prompt(query, top_k=3)
        
        print("Top 3 matches:")
        for i, (name, score, _) in enumerate(matches, 1):
            prompt_details = router.get_prompt_details(name)
            print(f"  {i}. {name} (similarity: {score:.3f}) - {prompt_details['description']}")


def batch_processing_example():
    """Example of processing multiple queries in batch."""
    print("\n⚡ Batch Processing Example")
    print("=" * 50)
    
    router = SystemPromptRouter()
    router.load_prompt_library(get_prompt_library())
    
    # Batch of queries
    queries = [
        "Debug this Python code",
        "Summarize the meeting notes",
        "Create a business proposal",
        "Explain quantum physics",
        "Help me learn Spanish"
    ]
    
    results = []
    
    for query in queries:
        print(f"Processing: {query}")
        
        # Find best prompt
        matches = router.find_best_prompt(query, top_k=1)
        best_match = matches[0]
        
        # Generate response
        response = router.generate_response(query)
        
        results.append({
            "query": query,
            "matched_prompt": best_match[0],
            "similarity_score": best_match[1],
            "response_length": len(response.get("response", "")),
            "success": "error" not in response
        })
    
    # Summary
    print(f"\n📈 Batch Processing Summary:")
    print(f"Total queries: {len(queries)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    
    print(f"\nPrompt distribution:")
    prompt_counts = {}
    for result in results:
        prompt = result["matched_prompt"]
        prompt_counts[prompt] = prompt_counts.get(prompt, 0) + 1
    
    for prompt, count in sorted(prompt_counts.items()):
        print(f"  {prompt}: {count} queries")


def performance_test():
    """Test the performance of the router."""
    print("\n🚀 Performance Test")
    print("=" * 50)
    
    import time
    
    router = SystemPromptRouter()
    router.load_prompt_library(get_prompt_library())
    
    # Test queries
    test_queries = [
        "Write a sorting algorithm",
        "Summarize this document",
        "Explain legal concepts",
        "Analyze this data",
        "Create marketing content"
    ] * 10  # 50 total queries
    
    # Time the matching process
    start_time = time.time()
    
    for query in test_queries:
        router.find_best_prompt(query)
    
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / len(test_queries)
    
    print(f"Processed {len(test_queries)} queries")
    print(f"Total time: {total_time:.3f} seconds")
    print(f"Average time per query: {avg_time:.3f} seconds")
    print(f"Queries per second: {len(test_queries) / total_time:.1f}")


def main():
    """Run all examples."""
    print("🎯 System Prompt Router Examples")
    print("=" * 60)
    
    try:
        basic_example()
        custom_prompts_example()
        similarity_analysis_example()
        batch_processing_example()
        performance_test()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable.")


if __name__ == "__main__":
    main()
