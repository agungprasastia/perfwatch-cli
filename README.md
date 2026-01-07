# 🚀 Perfwatch

**AI-Powered Website Performance Testing CLI Tool**

Perfwatch is a CLI tool for website performance testing with AI-powered analysis using Google Gemini.

Inspired by [Guardian CLI](https://github.com/zakirkun/guardian-cli).

## ✨ Features

### 🔍 Performance Analysis
- **PageSpeed Insights** - Core Web Vitals, Lighthouse scores
- **Load Testing** - Concurrent HTTP stress testing
- **SEO Analysis** - Meta tags, headings, technical SEO
- **AI Recommendations** - Smart suggestions powered by Gemini

### 📊 Reporting
- Multiple formats: HTML, JSON, Markdown
- Beautiful styled HTML reports
- Session management

### 🤖 AI-Powered
- Performance recommendations
- Issue prioritization
- Smart analysis

## 📋 Prerequisites

- Python 3.10+
- Google Gemini API Key (for AI features)
- Google PageSpeed API Key (for Lighthouse analysis, avoids rate limits)

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/agungprasastia/perfwatch-cli.git
cd perfwatch-cli

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/macOS)
source venv/bin/activate

# Install dependencies
pip install -e .
```

## ⚙️ Configuration

### API Keys (.env)

```bash
# Initialize configuration
python -m cli init
```

Or create `.env` file manually:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
PAGESPEED_API_KEY=your_pagespeed_api_key_here
```

### Settings (config/settings.yaml)

Edit `config/settings.yaml` to customize default values:

```yaml
ai:
  model: gemini-2.5-flash    # AI model
  temperature: 0.3

loadtest:
  requests: 100              # Default request count
  concurrent: 10             # Concurrent connections
  timeout: 30                # Request timeout

pagespeed:
  strategy: mobile           # mobile or desktop
  categories:
    - performance
    - accessibility
    - best-practices
    - seo

reports:
  output_dir: reports
  default_format: html
```

## 🎯 Usage

### Full Website Audit
```bash
python -m cli audit --url https://example.com
```

### Lighthouse Analysis
```bash
python -m cli lighthouse --url https://example.com --device mobile
```

### Load Testing
```bash
python -m cli loadtest --url https://example.com --requests 100 --concurrent 10
```

### SEO Analysis
```bash
python -m cli seo --url https://example.com
```

### View Reports
```bash
python -m cli report list
python -m cli report show report_20250107.json
```

## 📁 Project Structure

```
perfwatch/
├── ai/                 # AI integration (Gemini)
│   ├── gemini.py       # Gemini client
│   └── prompts.py      # AI prompts
├── cli/                # CLI layer
│   ├── __init__.py     # Main CLI app
│   └── commands/       # CLI commands
│       ├── audit.py
│       ├── lighthouse.py
│       ├── loadtest.py
│       ├── seo.py
│       └── report.py
├── core/               # Agent system
│   ├── agent.py        # Base agent
│   ├── planner.py      # Planner agent
│   ├── analyzer.py     # Analyzer agent
│   └── reporter.py     # Reporter agent
├── tools/              # Performance tools
│   ├── pagespeed.py    # PageSpeed API
│   ├── seo.py          # SEO checker
│   └── loadtest.py     # Load tester
├── utils/              # Utilities
│   ├── config.py       # Config loader
│   ├── logger.py       # Rich logging
│   └── validator.py    # URL validation
├── config/             # Configuration
│   └── settings.yaml   # Default settings
└── reports/            # Generated reports
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- [Guardian CLI](https://github.com/zakirkun/guardian-cli) - Inspiration
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal output
- [Google Gemini](https://ai.google.dev/) - AI recommendations