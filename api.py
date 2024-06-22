import anthropic
import http.client
import html2text
import requests
import re
import json
import os
from retrying import retry
from playwright.sync_api import sync_playwright

from pytrends.request import TrendReq

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
load_dotenv()
anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

@retry(stop_max_attempt_number=3, wait_exponential_multiplier=100, wait_exponential_max=1000)
# Define a decorator to handle retrying on specific exceptions
def generate_anthropic_response(messages, temperature=0.0, max_tokens=4096, model="claude-3-5-sonnet-20240620"):
  try:
    response = anthropic_client.messages.create(
      model=model,
      max_tokens=max_tokens,
      temperature=temperature,
      messages=messages)
    return response.content
  except Exception as e:
    print(f"Unexpected error: {e}")
    raise


def search_serper(query, location=None, api_key=os.environ["SERPER_API_KEY"]):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
      "q": query
    })
    if location:
      payload = json.dumps({
        "q": query,
        "location": location
      })
    headers = {
      'X-API-KEY': api_key,
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

def news_serper(query, api_key=os.environ["SERPER_API_KEY"]):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
      "q": query
    })
    headers = {
      'X-API-KEY': api_key,
      'Content-Type': 'application/json'
    }
    conn.request("POST", "/news", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def navigate(url):
    try:
      with sync_playwright() as p:
          browser = p.firefox.launch()
          page = browser.new_page()
          page.goto(url)
          page.wait_for_load_state()
          page.wait_for_timeout(5000)
          text = page.content()
          return text.replace("<|endoftext|>", "<endoftext>")
      return None
    except Exception as e:
      return str(e)

def get_url(url):
    html = navigate(url)
    if html is None: return None
    h = html2text.HTML2Text()
    return h.handle(html)

def send_email(subject, body):
    # Email configuration
    sender_email = os.environ["SENDER_EMAIL"]
    receiver_email = os.environ["RECEIVER_EMAIL"]
    password = os.environ["SMTP_PASSWORD"]
    smtp_server = os.environ["SMTP_SERVER"]
    smtp_port = os.environ["SMTP_PORT"]

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to the email
    message.attach(MIMEText(body, "html"))

    # Create a secure SSL/TLS connection and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)

def fetch_crypto_data(crypto_ids):
    base_url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(crypto_ids),
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
