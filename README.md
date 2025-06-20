# CarBot

CarBot parses car listings from OLX and Facebook Marketplace and notifies users via a Telegram bot. Listings are analyzed with a simple NLP pipeline.

## Setup

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Provide credentials using environment variables or a `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_token
   FB_EMAIL=your_facebook_email
   FB_PASSWORD=your_facebook_password
   ```

## Running

Initialize the database and start scraping:

```bash
python main.py
```

## Tests and linting

Run flake8 and the unit tests with pytest:

```bash
flake8
pytest
```
