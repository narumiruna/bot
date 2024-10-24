# Narumi's Telegram Bot

A sophisticated Telegram bot powered by advanced language models (GPT-4 or Gemini) that provides intelligent text processing, content analysis, and information retrieval capabilities. The bot supports multiple features including text polishing, summarization, translation, and financial data retrieval.

## Features

- **Text Polishing**: Enhance and refine text while maintaining its original meaning
- **Summarization**: Generate concise summaries of text content and web pages
- **Translation**: Translate text between different languages
- **Financial Data**: Retrieve stock market information and financial data
- **Content Processing**: Handle various content types including HTML, PDF, and YouTube transcripts
- **Error Handling**: Robust error management and user-friendly feedback
- **Access Control**: Whitelist-based user authentication for security

## Table of Contents

- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

## Environment Variables

Create a `.env` file in the root directory of your project and add the following variables:

```plaintext
BOT_TOKEN=your_telegram_bot_token
BOT_WHITELIST=comma_separated_user_ids

# Choose one of the models
MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_api_key
```

## Installation

```bash
# Install pipx if not already installed
pip install pipx

# Use pipx to install poetry
pipx install poetry

# Install project dependencies
poetry install
```

## Usage

Start the bot using Poetry:

```bash
poetry run bot
```

For development with auto-reload:

```bash
make dev
```

## Commands

- `/help` - Display available commands and usage information
- `/polish` - Improve and refine text while preserving its meaning
- `/summarize` - Generate a concise summary of provided text or URL content
- `/translate` - Translate text to a specified language
- `/ticker` - Retrieve financial data for a given stock symbol

## Project Structure

```
src/
├── bot/
│   ├── bot/          # Core bot functionality
│   ├── loaders/      # Content loaders (HTML, PDF, YouTube)
│   ├── tools/        # Feature implementations
│   ├── cli.py        # Command-line interface
│   ├── llm.py        # Language model integration
│   └── utils.py      # Utility functions
tests/               # Test suite
```

## Development

1. Install pre-commit hooks:

```bash
pre-commit install
```

2. Follow code style guidelines:

- Use type hints
- Write docstrings for functions and classes
- Follow PEP 8 guidelines

3. Create feature branches for new development:

```bash
git checkout -b feature/your-feature-name
```

## Testing

Run the test suite:

```bash
poetry run pytest
```

Run tests with coverage:

```bash
poetry run pytest --cov
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
