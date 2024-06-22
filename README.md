# Daily Weather and News Email Summary

This project generates and sends a daily email containing a brief weather forecast and relevant news updates. It uses various APIs to gather information and Claude AI to generate a concise, human-friendly email summary.

## Features

- Retrieves current weather information based on the user's location
- Fetches trending search queries and related news
- Gathers news on user-specified topics of interest
- Uses Claude AI to generate a brief, personalized email summary
- Sends the email summary to the specified recipient

## Requirements

- Python 3.7+
- Required Python packages (install via `pip install -r requirements.txt`):
  - anthropic
  - pytrends
  - pytz
  - requests
  - python-dotenv

## Setup

1. Clone this repository
2. Install the required packages: `pip install -r requirements.txt`
3. Set up a `.env` file in the project root with the following variables:
```
ANTHROPIC_API_KEY=your_anthropic_api_key
SERPER_API_KEY=your_serper_api_key
SENDER_EMAIL=your_sender_email
RECEIVER_EMAIL=your_receiver_email
SMTP_PASSWORD=your_smtp_password
SMTP_SERVER=your_smtp_server
SMTP_PORT=your_smtp_port
USER_LOCATION=your_location
INTERESTED_TOPICS=topic1,topic2,topic3
```

## Usage

Run the script daily (e.g., via a cron job) using:
```
python main.py
```

