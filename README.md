# 🤖 Research Bot

**Intelligent Research Assistant — Built with Google Gemini**

---

## Overview

Research Bot is an AI-powered research assistant that helps users find reliable information from multiple sources and presents it in clear, organized summaries. The bot automatically detects the language of your question and responds in the same language (Arabic, English, or any other language).

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 Interactive Chat | Modern chat interface with real-time responses |
| 🌐 Auto Language Detection | Responds in the same language as the question |
| ⚙️ Settings Panel | Users can enter their own Google API key directly in the UI |
| 🌓 Light/Dark Mode | Toggle between themes, preference saved in browser |
| 📄 Export Markdown | Download conversation as `.md` file |
| 📑 Export PDF | Download conversation as `.pdf` with Arabic RTL support |
| 🎨 Google Design System | Professional UI with Google brand colors |
| 📱 Fully Responsive | Works on mobile, tablet, and desktop |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|--------|
| Python 3.11+ | Backend logic |
| Flask | Web framework |
| Google Gemini API | AI model (gemini-3.8-flash) |
| fpdf2 | PDF generation |
| arabic-reshaper + python-bidi | Arabic RTL text processing |
| Vercel | Hosting & deployment |

---

## 📁 Project Structure

```
research-bot/
├── api/
│   └── index.py              # Vercel serverless handler
├── fonts/
│   └── arial.ttf             # Arabic-supporting font
├── static/
│   └── style.css             # CSS styles (Google design system)
├── templates/
│   └── index.html            # Web interface
├── .gitignore                # Git ignore rules
├── app.py                    # Local development server
├── requirements.txt          # Python dependencies
└── vercel.json               # Vercel configuration
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites

- Python 3.11 or higher
- A Google AI Studio API key (free at https://aistudio.google.com/apikey)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/research-bot.git
cd research-bot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the local server
python app.py
```

Open your browser and go to: **http://localhost:5000**

---

## 🌍 Deploy to Vercel

### Option 1: Via Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository `research-bot`
4. Vercel auto-detects Python — leave defaults
5. Add Environment Variable:
   - Name: `GOOGLE_API_KEY`
   - Value: Your actual API key
6. Click **"Deploy"**

### Option 2: Via Vercel CLI

```bash
npm i -g vercel
cd research-bot
vercel login
vercel env add GOOGLE_API_KEY
vercel --prod
```

After deployment, you'll get a URL like:
```
https://research-bot.vercel.app
```

---

## 🔐 Security

- API keys are stored in browser `localStorage` per device (not on server)
- Server-side fallback uses environment variables (never hardcoded)
- `.env` files are excluded from version control via `.gitignore`

---

## 💰 Cost

| Service | Monthly Cost |
|---------|-------------|
| Vercel Hobby Plan | Free |
| Gemini API (Flash) | ~$0.75 per 1M tokens |
| Total (personal use) | Under $5/month |

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 👤 Author

**Ali Moojid**

Built with ❤️ using Google Gemini & Vercel

---

## 🙏 Acknowledgments

- Google Gemini API for the AI model
- Vercel for hosting
- fpdf2 for PDF generation
- arabic-reshaper & python-bidi for Arabic text support
