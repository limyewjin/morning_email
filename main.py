import api
import re
import pytz
from datetime import datetime
from pytrends.request import TrendReq

import os
from dotenv import load_dotenv
load_dotenv()

INTERESTED_TOPICS = [ "bitcoin", "ethereum" ]
TOP_TRENDING_QUERIES = 3

def get_pacific_time():
    pacific_tz = pytz.timezone('US/Pacific')
    pacific_now = datetime.now(pacific_tz)
    is_dst = bool(pacific_now.dst())
    time_type = "PDT" if is_dst else "PST"
    
    print(f"Current Pacific time: {pacific_now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}")
    print(f"Time Type: {time_type}")
    
    return is_dst, pacific_now

def extract_email_content(email_text):
    # Pattern to match subject and body
    pattern = r'<subject>(.*?)</subject>.*?<body>(.*?)</body>'
    
    # Use re.DOTALL flag to make . match newlines as well
    match = re.search(pattern, email_text, re.DOTALL)
    
    if match:
        subject = match.group(1).strip()
        body = match.group(2).strip()
        return subject, body
    else:
        return None, None

def main():
    is_dst, current_time = get_pacific_time()
    tz = 420 if is_dst else 480
    
    pytrends = TrendReq(hl='en-US', tz=tz)
    trending_queries = pytrends.trending_searches(pn='united_states')
    print(trending_queries)
    
    formatted_datetime = current_time.strftime("%A, %B %d, %Y %H:%M")
    formatted_date = current_time.strftime("%Y%m%d")
    print(f"Formatted datetime: {formatted_datetime}")
    print(f"Formatted date: {formatted_date}")

    trending_results = {}
    for query in trending_queries[0][:TOP_TRENDING_QUERIES]:
      print(query)
      trending_results[query] = api.news_serper(query)
    
    weather_results = api.search_serper("weather", os.environ["USER_LOCATION"]) 

    interested_results = {}
    for query in INTERESTED_TOPICS:
      interested_results = api.news_serper(query)

    prompt = f"""You are an AI assistant tasked with writing a brief email summary for a user, focusing on weather and potentially including relevant news. Follow these steps:

Current datetime: {formatted_datetime}

1. Weather data will be provided in the following format:
<weather_data>
{weather_results}
</weather_data>

2. News results for top trending queries will be provided in the following format:
<news_results>
{trending_queries}
</news_results>

3. News results for User interests will be provided in the following format:
<user_interests>
{interested_results}
</user_interests>

4. Compose a brief email summary following these guidelines:
   a. Start with a greeting appropriate for the time of day (morning/afternoon/evening).
   b. Provide a quick note about today's weather.
   c. Mention any interesting weather events in the next few days, if applicable.
   d. Include relevant news only if there is new information (published within the last 24 hours) related to the top trending queries or user interests. Provide links to news if mentioning.
   e. If multiple news items are available, prioritize trending topics over user interests.
   f. If no relevant news is available, omit the news section entirely.
   g. Keep the email concise and informative.
   h. Use a friendly, conversational tone.
   i. End with a brief, friendly sign-off.

5. Format your response as follows:
   - Use <subject> tags for the email subject line.
   - Use <body> tags for the email body.
   - Ensure the entire email (subject and body) is no more than 5-7 sentences long.
   - Use the following HTML tags for formatting within the <body> tags:
     * <h2> for section headers
     * <p> for paragraphs
     * <strong> for bold text
     * <em> for italicized text
     * <ul> and <li> for unordered lists
     * <a href="URL">link text</a> for hyperlinks
   - Use line breaks (<br>) sparingly for better readability.

6. If any required data is missing, note this briefly in the email body.

Here's an example of how your output should be structured:

<subject>Daily Update: Sunny Today, Chance of Rain Tomorrow</subject>

<body>
It's a beautiful sunny day today with a high of 75°F. Heads up for tomorrow - there's a 60% chance of rain, so don't forget your umbrella. In other news, [insert brief mention of relevant news if applicable].

Have a great day!
</body>

Remember, it's okay to omit news results if there's no new relevant information. Focus on providing a quick, useful summary for the user.
""".strip()

    response = api.generate_anthropic_response([{"role":"user", "content":prompt}])
    print(response)
    subject, body = extract_email_content(response[0].text)

    print(f"subject: {subject}\nbody: {body}")
    api.send_email(subject, body)

if __name__ == "__main__":
    main()
