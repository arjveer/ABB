# 🚀 Quick Start Guide

Get your YouTube Video Summarizer up and running in 5 minutes!

## ⚡ Super Quick Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. **Run the web app:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser and go to:** `http://localhost:8501`

5. **Paste a YouTube URL and click "Generate Summary"!**

## 🎯 Alternative: Command Line

Prefer the terminal? Use the CLI:

```bash
# Basic usage
python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get a detailed summary
python cli.py "https://youtu.be/example" --type detailed

# Save to file
python cli.py "video_url" --output summary.txt
```

## 🔑 Getting Your OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to "API Keys" section
4. Create a new API key
5. Copy and paste it in the web app or set as environment variable

## 📺 Example Videos to Try

- **Short:** `dQw4w9WgXcQ` (Rick Astley - Never Gonna Give You Up)
- **Educational:** `kJAsCz9hdJQ` (Machine Learning Basics)
- **Tutorial:** `8jLo02VtJmQ` (Python Tutorial)

## 🆘 Common Issues

- **"API key required"** → Set your OpenAI API key
- **"No transcript found"** → Try a different video or language
- **"Rate limit exceeded"** → Wait a few minutes and try again

## 🎉 You're Ready!

That's it! You now have a powerful YouTube video summarizer that can:
- Extract transcripts from any YouTube video
- Generate AI-powered summaries using GPT-4o
- Provide multiple summary lengths and types
- Export results as text or CSV files

Happy summarizing! 🎬✨
