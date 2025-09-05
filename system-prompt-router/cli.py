#!/usr/bin/env python3
"""
Command-line interface for the System Prompt Router.
"""

import argparse
import sys
from prompt_router import SystemPromptRouter
from prompt_library import get_prompt_library


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="System Prompt Router - Route queries to appropriate system prompts"
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="The query to process"
    )
    
    parser.add_argument(
        "--list-prompts",
        action="store_true",
        help="List all available prompts"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=1,
        help="Number of top matches to return (default: 1)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="OpenAI model to use (default: gpt-3.5-turbo)"
    )
    
    parser.add_argument(
        "--embedding-model",
        default="all-MiniLM-L6-v2",
        help="Embedding model to use (default: all-MiniLM-L6-v2)"
    )
    
    parser.add_argument(
        "--no-response",
        action="store_true",
        help="Only show prompt matching, don't generate response"
    )
    
    args = parser.parse_args()
    
    # Initialize router
    try:
        router = SystemPromptRouter(
            embedding_model=args.embedding_model,
            openai_model=args.model
        )
        router.load_prompt_library(get_prompt_library())
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # List prompts if requested
    if args.list_prompts:
        print("Available prompts:")
        for name, desc in router.list_prompts().items():
            print(f"  {name}: {desc}")
        return
    
    # Process query if provided
    if args.query:
        try:
            # Find best matches
            matches = router.find_best_prompt(args.query, top_k=args.top_k)
            
            print(f"Query: {args.query}")
            print(f"Top {len(matches)} matches:")
            print("-" * 50)
            
            for i, (name, score, system_prompt) in enumerate(matches, 1):
                prompt_details = router.get_prompt_details(name)
                print(f"{i}. {name}")
                print(f"   Similarity: {score:.3f}")
                print(f"   Description: {prompt_details['description']}")
                print()
            
            # Generate response if requested
            if not args.no_response:
                print("Generating response...")
                response = router.generate_response(args.query)
                
                if "error" in response:
                    print(f"Error: {response['error']}", file=sys.stderr)
                else:
                    print("Response:")
                    print("-" * 50)
                    print(response["response"])
                    print("-" * 50)
                    print(f"Matched prompt: {response['matched_prompt']}")
                    print(f"Similarity score: {response['similarity_score']:.3f}")
        
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Interactive mode
        print("System Prompt Router - Interactive Mode")
        print("Enter queries (or 'quit' to exit):")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                if not query:
                    continue
                
                matches = router.find_best_prompt(query, top_k=args.top_k)
                print(f"\nTop {len(matches)} matches:")
                for i, (name, score, _) in enumerate(matches, 1):
                    prompt_details = router.get_prompt_details(name)
                    print(f"{i}. {name} (similarity: {score:.3f})")
                    print(f"   {prompt_details['description']}")
                
                if not args.no_response:
                    response = router.generate_response(query)
                    if "error" not in response:
                        print(f"\nResponse: {response['response']}")
                    else:
                        print(f"\nError: {response['error']}")
            
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
