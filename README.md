# Narumi's Telegram Bot

A sophisticated Telegram bot powered by advanced language models that provides intelligent text processing, content analysis, and information retrieval capabilities. Built with Python and leveraging OpenAI's GPT models, this bot offers a comprehensive suite of natural language processing features.

## Key Features

### Text Processing
- **Text Polishing**: Enhance text quality while preserving meaning
  - Grammar and style improvements
  - Tone adjustment
  - Professional formatting
- **Summarization**: Generate concise summaries from various sources
  - Web page content
  - PDF documents
  - Long-form text
  - YouTube video transcripts
- **Translation**: Multilingual support
  - High-quality translations
  - Language detection
  - Context-aware translations

### Data & Analysis
- **Financial Data**: Real-time market information
  - Stock price tracking
  - Financial metrics
  - Market trends
- **Content Analysis**: Advanced processing capabilities
  - HTML content extraction
  - PDF text extraction
  - YouTube transcript processing
  - Semantic analysis

### System Features
- **Error Management**: Robust error handling
  - User-friendly error messages
  - Graceful failure recovery
  - Detailed logging
- **Security**: Advanced access control
  - User whitelisting
  - Request validation
  - Rate limiting

## Prerequisites

Before installation, ensure you have:

- Python 3.9 or higher
- pip (Python package installer)
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))
- An OpenAI API key
- (Optional) Qdrant instance for vector search capabilities

## Environment Setup

1. Create a `.env` file in the project root:

```plaintext
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
BOT_WHITELIST=user_id1,user_id2,user_id3

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Optional: Qdrant Configuration
QDRANT_URL=your_qdrant_url
QDRANT_COLLECTION_NAME=your_collection_name

# Optional: Development Settings
TEMPERATURE=0.0
DEBUG=true
```

## Installation

1. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev build-essential

# macOS
brew install python3
```

2. Install uv:
```bash
# Install pipx if not already installed
pip install --user pipx
pipx ensurepath

# Install uv using pipx
pipx install uv
```

3. Set up project:
```bash
# Clone the repository
git clone https://github.com/yourusername/narumi-telegram-bot.git
cd narumi-telegram-bot

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv sync
```

## Usage

### Running the Bot

Start the bot:
```bash
uv run bot
```

Start with development features (auto-reload):
```bash
make dev
```

### Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Show command list and usage | `/help` |
| `/polish` | Improve text quality | `/polish Your text here` |
| `/summarize` | Generate content summary | `/summarize https://example.com` |
| `/translate` | Translate text | `/translate en Hello World` |
| `/ticker` | Get stock information | `/ticker AAPL` |

## Project Structure

```
src/
├── bot/
│   ├── bot/           # Core bot functionality
│   │   ├── bot.py     # Main bot logic
│   │   ├── echo.py    # Echo command handler
│   │   └── ...        # Other command handlers
│   ├── loaders/       # Content processing
│   │   ├── html.py    # HTML content loader
│   │   ├── pdf.py     # PDF document loader
│   │   └── ...        # Other loaders
│   ├── tools/         # Feature implementations
│   │   ├── polish.py  # Text polishing logic
│   │   └── ...        # Other tools
│   ├── cli.py         # Command-line interface
│   ├── llm.py         # Language model integration
│   └── utils.py       # Utility functions
├── tests/             # Test suite
└── ...
```

## Development Guide

### Setting Up Development Environment

1. Install development tools:
```bash
# Install development dependencies
uv sync --dev

# Install pre-commit hooks
pre-commit install
```

2. Configure IDE:
- Enable type checking
- Set up autoformatting (black, isort)
- Enable linting (ruff)

### Best Practices

1. Code Style:
- Use type hints consistently
- Write comprehensive docstrings
- Follow PEP 8 guidelines
- Keep functions focused and small

2. Git Workflow:
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make commits with clear messages
git commit -m "feat: add new feature"

# Push changes
git push origin feature/your-feature-name
```

3. Testing:
- Write unit tests for new features
- Maintain test coverage
- Test edge cases
- Mock external services

### Dependency Management

1. Adding dependencies:
```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update lockfile after adding dependencies
uv lock
```

2. Updating dependencies:
```bash
# Update all dependencies
uv sync --upgrade
```

3. View dependency tree:
```bash
uv tree
```

## Testing

Run test suite:
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test file
uv run pytest tests/test_specific.py
```

## Troubleshooting

### Common Issues

1. **Bot Token Invalid**
   - Verify token with BotFather
   - Check .env file configuration
   - Ensure no whitespace in token

2. **OpenAI API Errors**
   - Verify API key
   - Check rate limits
   - Monitor API status

3. **Permission Errors**
   - Verify user is in whitelist
   - Check bot permissions
   - Ensure correct file permissions

4. **Dependency Issues**
   - Check virtual environment activation
   - Run `uv sync` to update dependencies
   - Run `uv lock` to update lockfile
   - Clear cache with `uv cache clean` if needed

### Getting Help

- Create an issue in the repository
- Check existing issues for solutions
- Review the bot's error logs
- Run `uv help <command>` for command-specific help

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please ensure your PR:
- Includes tests
- Updates documentation
- Follows code style guidelines
- Passes all checks
