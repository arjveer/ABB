# 📺 YouTube Video Summarizer

A powerful tool that extracts YouTube video transcripts and generates intelligent summaries using OpenAI's GPT-4o. Perfect for content creators, researchers, students, and anyone who wants to quickly understand video content without watching the entire video.

## ✨ Features

- 🎯 **Multiple Summary Types**: Short, medium, long, and detailed summaries
- 🌍 **Multi-language Support**: Extract transcripts in various languages
- 🤖 **AI-Powered**: Uses OpenAI's latest GPT-4o model for intelligent summarization
- 💻 **Multiple Interfaces**: Web app (Streamlit) and command-line interface
- 📊 **Rich Analytics**: Word counts, character counts, and processing statistics
- 💾 **Export Options**: Save results as text or CSV files
- 📱 **Modern UI**: Beautiful, responsive web interface
- 🔧 **Flexible Configuration**: Customize models, languages, and summary parameters

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- YouTube video URL or ID

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd youtube-summarizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key:**
   ```bash
   # Option 1: Environment variable
   export OPENAI_API_KEY="your_api_key_here"
   
   # Option 2: Create .env file
   cp env_example.txt .env
   # Edit .env and add your API key
   ```

### Usage

#### 🌐 Web Interface (Recommended)

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`

#### 💻 Command Line Interface

Basic usage:
```bash
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Advanced options:
```bash
# Generate detailed summary
python cli.py "https://youtu.be/kJAsCz9hdJQ" --type detailed

# Use specific model and save to file
python cli.py dQw4w9WgXcQ --type long --model gpt-4o --output summary.txt

# Extract transcript only
python cli.py "https://youtu.be/example" --transcript-only --verbose
```

## 📖 Detailed Usage

### Summary Types

- **Short**: 2-3 sentence concise summary (~150 tokens)
- **Medium**: Comprehensive paragraph summary (~300 tokens)
- **Long**: Detailed multi-paragraph summary (~500 tokens)
- **Detailed**: Structured analysis with key points, insights, and action items (~600 tokens)

### Supported URL Formats

The tool automatically detects and extracts video IDs from:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/embed/VIDEO_ID`
- `https://youtube.com/v/VIDEO_ID`
- Direct video ID (11 characters)

### Language Support

The tool supports multiple languages for transcript extraction:
- English (en, en-US, en-GB)
- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o
SUMMARY_LENGTH=medium
```

### API Key Security

- Never commit your API key to version control
- Use environment variables or `.env` files
- The `.env` file is already in `.gitignore`

## 📊 Example Output

### Simple Summary
```
YouTube Video Summary
==================================================

🎬 Video ID: dQw4w9WgXcQ
📊 Statistics: 1,234 words, 6,789 characters
🎯 Summary Type: Medium

📝 SUMMARY:
This video discusses the fundamentals of machine learning algorithms...
```

### Detailed Summary
```
📝 DETAILED ANALYSIS:

1. **Main Topic**: Introduction to Machine Learning Fundamentals
2. **Key Points**: 
   - Supervised vs. unsupervised learning
   - Common algorithms and their applications
   - Data preprocessing techniques
3. **Key Insights**: Understanding the bias-variance tradeoff is crucial...
4. **Summary**: This comprehensive tutorial covers...
5. **Action Items**: Practice with the provided datasets...
```

## 🛠️ Development

### Project Structure

```
youtube-summarizer/
├── core.py              # Core functionality and API integration
├── app.py               # Streamlit web application
├── cli.py               # Command-line interface
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Project configuration
├── README.md           # This file
└── env_example.txt     # Environment variables template
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black .

# Linting
flake8 .
```

### Adding New Features

1. **Core Functionality**: Add methods to `YouTubeSummarizer` class in `core.py`
2. **Web Interface**: Extend `app.py` with new UI components
3. **CLI Options**: Add new arguments to `cli.py`
4. **Testing**: Write tests for new functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for providing the GPT-4o API
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api) for transcript extraction
- [Streamlit](https://streamlit.io/) for the web interface framework

## 🆘 Troubleshooting

### Common Issues

1. **"OpenAI API key is required"**
   - Set your API key as an environment variable or in the web interface
   - Ensure the `.env` file is in the correct location

2. **"Could not retrieve transcript"**
   - Video may not have captions/transcripts enabled
   - Try different language preferences
   - Check if the video is publicly accessible

3. **"Rate limit exceeded"**
   - OpenAI API has rate limits
   - Wait a few minutes before making more requests
   - Consider upgrading your OpenAI plan

4. **"Invalid YouTube URL or video ID"**
   - Ensure the URL is a valid YouTube video
   - Check if the video ID is exactly 11 characters

### Getting Help

- Check the [Issues](https://github.com/your-repo/issues) page
- Create a new issue with detailed error information
- Include the video URL/ID and error message

## 🔮 Future Enhancements

- [ ] Batch processing for multiple videos
- [ ] Custom summary prompts
- [ ] Translation support
- [ ] Audio file processing
- [ ] Integration with other AI models
- [ ] Mobile app version
- [ ] API endpoint for external integrations

---

**Happy summarizing! 🎉**

If you find this tool useful, please give it a ⭐ and share with others!
