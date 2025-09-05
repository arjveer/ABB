# System Prompt Router

A Python library that automatically routes user queries to the most appropriate system prompt using semantic similarity. Perfect for building multi-capability AI applications that need to switch between different prompting strategies based on user intent.

## 🚀 Features

- **Semantic Matching**: Uses sentence-transformers to find the best matching prompt based on query similarity
- **Pre-built Prompt Library**: Includes 10+ ready-to-use prompts for common AI capabilities
- **Custom Prompts**: Easy to add your own prompts and descriptions
- **OpenAI Integration**: Seamlessly integrates with OpenAI's API for response generation
- **Flexible Configuration**: Support for different embedding models and OpenAI models
- **CLI Interface**: Command-line tool for quick testing and batch processing
- **Performance Optimized**: Fast similarity matching with numpy operations

## 📦 Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:

```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=your_api_key_here
```

## 🎯 Quick Start

### Basic Usage

```python
from prompt_router import SystemPromptRouter
from prompt_library import get_prompt_library

# Initialize the router
router = SystemPromptRouter()

# Load the pre-built prompt library
router.load_prompt_library(get_prompt_library())

# Find the best prompt for a query
query = "Write a Python function to sort a list"
matches = router.find_best_prompt(query, top_k=3)

# Generate a response using the best prompt
response = router.generate_response(query)
print(response["response"])
```

### Command Line Interface

```bash
# Interactive mode
python cli.py

# Process a single query
python cli.py "Write a function to calculate fibonacci numbers"

# List all available prompts
python cli.py --list-prompts

# Show top 3 matches without generating response
python cli.py "Help me with legal advice" --top-k 3 --no-response
```

### Run Examples

```bash
# Run the main demo
python main.py

# Run automated demo with predefined queries
python main.py demo

# Run comprehensive examples
python example_usage.py
```

## 📚 Available Prompts

The library comes with 10 pre-built prompts for common AI capabilities:

| Prompt Name | Description | Use Case |
|-------------|-------------|----------|
| `code_writer` | Write, debug, and explain code | Programming help, code reviews |
| `video_summarizer` | Summarize videos and extract key points | Content analysis, video processing |
| `legal_assistant` | Answer legal questions and explain concepts | Legal guidance, compliance |
| `data_analyst` | Analyze data and create visualizations | Data science, statistics |
| `creative_writer` | Write creative content and marketing copy | Content creation, storytelling |
| `technical_documentation` | Create technical docs and user guides | Documentation, tutorials |
| `language_tutor` | Teach languages and explain grammar | Language learning, education |
| `business_consultant` | Provide business advice and strategy | Business planning, consulting |
| `scientific_researcher` | Explain scientific concepts and research | Science education, research |
| `personal_assistant` | Help with productivity and organization | Life management, productivity |

## 🛠️ Custom Prompts

Add your own prompts easily:

```python
# Add a custom prompt
router.add_prompt(
    name="recipe_helper",
    description="Help with cooking recipes and meal planning",
    system_prompt="""You are a cooking assistant. Help users with:
    - Recipe suggestions and modifications
    - Cooking techniques and tips
    - Meal planning and nutrition
    - Ingredient substitutions"""
)

# Or load multiple custom prompts at once
custom_prompts = {
    "my_prompt": {
        "description": "My custom prompt description",
        "system_prompt": "Your custom system prompt here"
    }
}
router.load_prompt_library(custom_prompts)
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Sentence transformer model
OPENAI_MODEL=gpt-3.5-turbo        # OpenAI model
```

### Model Options

**Embedding Models:**
- `all-MiniLM-L6-v2` (default) - Fast and efficient
- `all-mpnet-base-v2` - Higher quality, slower
- `all-distilroberta-v1` - Good balance

**OpenAI Models:**
- `gpt-3.5-turbo` (default) - Fast and cost-effective
- `gpt-4` - Higher quality, more expensive
- `gpt-4-turbo` - Latest GPT-4 with better performance

## 📊 How It Works

1. **Prompt Library**: Each prompt has a descriptive name and system prompt
2. **Embedding**: Descriptions are embedded using sentence-transformers
3. **Query Processing**: User queries are embedded with the same model
4. **Similarity Matching**: Cosine similarity finds the best matching prompt
5. **Response Generation**: The matched system prompt is used with OpenAI API

## 🔧 API Reference

### SystemPromptRouter

```python
router = SystemPromptRouter(
    embedding_model="all-MiniLM-L6-v2",
    openai_model="gpt-3.5-turbo",
    openai_api_key=None  # Uses OPENAI_API_KEY env var if None
)
```

### Key Methods

```python
# Add a single prompt
router.add_prompt(name, description, system_prompt)

# Load multiple prompts
router.load_prompt_library(prompts_dict)

# Find best matching prompts
matches = router.find_best_prompt(query, top_k=3)
# Returns: [(name, similarity_score, system_prompt), ...]

# Generate response
response = router.generate_response(query, use_best_prompt=True)
# Returns: {"response": "...", "matched_prompt": "...", ...}

# List all prompts
prompts = router.list_prompts()
# Returns: {"name": "description", ...}
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest test_prompt_router.py
```

Or run the example usage to see the system in action:

```bash
python example_usage.py
```

## 📈 Performance

- **Matching Speed**: ~1000 queries/second on modern hardware
- **Memory Usage**: ~50MB for the default embedding model
- **Accuracy**: High semantic matching accuracy with proper prompt descriptions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [sentence-transformers](https://www.sbert.net/)
- Powered by [OpenAI API](https://openai.com/api/)
- Inspired by the AI Builders Bootcamp community

## 📞 Support

For questions or issues:
1. Check the examples in `example_usage.py`
2. Review the CLI help: `python cli.py --help`
3. Open an issue on GitHub

---

**Happy Prompt Routing! 🎯**
