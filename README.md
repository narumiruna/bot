# Narumi's Telegram Bot

A Telegram bot that leverages advanced language models to provide various functionalities.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Installation](#installation)
- [Usage](#usage)

## Environment Variables

Create a `.env` file in the root directory of your project and add the following variables:

```plaintext
BOT_TOKEN=
BOT_WHITELIST=

# Choose one of the models
MODEL=gpt-4o-mini
OPENAI_API_KEY=
# or
MODEL=gemini-1.5-flash
GOOGLE_API_KEY=
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

```bash
poetry run bot
```
