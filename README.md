
# Instagram Bot with OpenAI Integration

This Python-based bot logs into Instagram, checks for new messages, waits for a specified time, reads the message, generates a reply using OpenAI's API (like ChatGPT), and types out the response to mimic human behavior.

## Features


- **Check for new messages** in your Instagram inbox.
- **Wait 5 minutes** before opening the message.
- **Send the message to OpenAI** to generate a reply.
- **Type the reply out** as if a human is typing (no copy-pasting).

## Prerequisites

- Python 3.x
- `openai` Python package for AI-generated replies.
- `playwright` for browser automation.

## Setup Instructions

### 1. Clone the Repository or Download Files

If you haven’t already, download or clone the repository to your local machine:

```bash
git clone https://github.com/LeilaSchooley/instagram-openai-bot.git
cd instagram-openai-bot

```

or sign in to github desktop, go to https://github.com/LeilaSchooley/instagram-openai-bot, login and click Open with Github desktop 
### 2. Create a Virtual Environment

It's a good practice to use a virtual environment to keep your dependencies isolated. To create a virtual environment:

```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment

Activate the virtual environment to start using it.

- **On Windows**:

  ```bash
  venv\Scripts\activate
  ```

- **On macOS/Linux**:

  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies

Install all necessary packages using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

Next, install Playwright's browser dependencies:

```bash
playwright install
```

### 5. Configure Credentials

You need to set up a configuration file (`config.ini`) to store your credentials and API keys.

Create a file named `config.ini` in the root directory of your project and add the following:

```ini
[DEFAULT]
OPENAI = your-openai-api-key
DOLPHIN_TOKEN = your-dolphin-api-key

```

- Replace `your-openai-api-key` with your actual OpenAI API key.
`generate_response()` contains the prompt used. Feel free to change this.

Log in to the instagram account, set the profile ID by copying it from dolphin anty, and then change the profile id in the function : 
`check_inbox_and_reply()`

### 6. Run the Bot

Once everything is set up, run the bot by executing the following command:

```bash
python bot.py
```

### 7. What the Bot Does

- **Inbox Monitoring**: It will check the Instagram inbox for any messages that are 5 minutes old.
- **Read and Generate Reply**: After reading the message, it sends the content to OpenAI, which generates a reply.
- **Human-like Typing**: The bot types out the reply as if a person were doing it, then sends the message.

## Files Overview

- **`bot.py`**: The main script that runs the bot.
- **`config.ini`**: The file where you store sensitive information like your OpenAI API key and Instagram credentials (make sure not to share this).
- **`requirements.txt`**: Contains the list of Python packages required to run the bot.
- **`README.md`**: This file, which provides setup instructions and usage information.

## Notes

- **Security**: Ensure your Instagram account is secure, and be cautious with automation to avoid account restrictions or bans.
- **OpenAI Usage**: Make sure your OpenAI account is active and you are aware of any token or usage limits. 
- **Bot Limitations**: The bot currently waits for 5-minute-old messages to respond. You can modify the waiting time in the script.

