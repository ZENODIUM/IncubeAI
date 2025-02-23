import requests
import json
import os
import re
from crewai_tools import ScrapeWebsiteTool
from youtube_transcript_api import YouTubeTranscriptApi

os.environ["SERPER_API_KEY"] = "80cbe6bcf3ecf30eeef6effaa1ec09eb9d631d7f"
os.environ["YOUTUBE_API_KEY"] = "AIzaSyA1yN2irDyHuUXTOGPGzskqEjsw5vwDUxU"  # Replace with your YouTube API key



def send_to_granite(prompt,granite_key):
    """ Sends the structured prompt to the Granite LLM and returns the response. """
    url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
    body = {
        "input": prompt,
        "parameters": {
            "decoding_method": "greedy",
            "max_new_tokens": 1500,
            "min_new_tokens": 0,
            "repetition_penalty": 1
        },
        "model_id": "ibm/granite-3-8b-instruct",
        "project_id": "58e29d0a-b08d-4b3a-9e10-d41d5adb23fd",
        "moderations": {
            "hap": {"input": {"enabled": False, "threshold": 0.5}, "output": {"enabled": False, "threshold": 0.5}},
            "pii": {"input": {"enabled": False, "threshold": 0.5}, "output": {"enabled": False, "threshold": 0.5}}
        }
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {granite_key}"  # Replace with actual API key
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    if data.get("results"):
        return data["results"][0].get("generated_text", "No analysis available.")
    else:
        return "No analysis available."
    
def search_service_items(product_name,country_code):
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": product_name,
        "gl": country_code,  # Country code (optional)
        "hl": "en"   # Language code (optional)
    })
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch shopping results: {response.text}")

    search_results = response.json()
    return search_results.get("organic", [])



def search_shopping_items(product_name,country_code):
    url = "https://google.serper.dev/shopping"
    payload = json.dumps({
        "q": product_name,
        "gl": country_code,  # Country code (optional)
        "hl": "en"   # Language code (optional)
    })
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch shopping results: {response.text}")

    search_results = response.json()
    return search_results.get("shopping", [])



def scrape_website_content(url):
    scrape_tool = ScrapeWebsiteTool(website_url=url)
    scraped_content = scrape_tool.run()
    return scraped_content

# Step 3: Search for YouTube Videos
def search_youtube_videos(product_name,number_of_video_search):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": f"{product_name} review",
        "type": "video",
        "maxResults": number_of_video_search,  # Fetch only the top video
        "key": os.getenv("YOUTUBE_API_KEY")
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch YouTube videos: {response.text}")

    search_results = response.json()
    return search_results.get("items", [])

# Step 4: Fetch YouTube Video Transcript
def fetch_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        print(f"Error fetching transcript for video {video_id}: {e}")
        return None

# Step 5: Fetch Top 10 YouTube Video Comments
def fetch_youtube_comments(video_id,comment_count):
    url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        "part": "snippet",
        "videoId": video_id,
        "maxResults": comment_count,  # Fetch top 10 comments
        "key": os.getenv("YOUTUBE_API_KEY")
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch YouTube comments: {response.text}")

    comments = response.json().get("items", [])
    comment_texts = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in comments]
    return comment_texts





def extract_details(analysis):
    details = {}

    # Extracting Product Overview
    product_overview = re.search(r"\*\*Product Overview\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Product Overview"] = product_overview.group(1).strip() if product_overview else "Not available"

    # Extracting Key Features
    key_features = re.search(r"\*\*Key Features\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Key Features"] = [feat.strip("- ") for feat in key_features.group(1).strip().split("\n") if feat.strip()] if key_features else []

    # Extracting Pros
    pros = re.search(r"\*\*Pros\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Pros"] = [p.strip("- ") for p in pros.group(1).strip().split("\n") if p.strip()] if pros else []

    # Extracting Cons
    cons = re.search(r"\*\*Cons\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Cons"] = [c.strip("- ") for c in cons.group(1).strip().split("\n") if c.strip()] if cons else []

    # Extracting Price Analysis
    price_analysis = re.search(r"\*\*Price Analysis\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Price Analysis"] = price_analysis.group(1).strip() if price_analysis else "Not available"

    # Extracting Rating Analysis
    rating_analysis = re.search(r"\*\*Rating Analysis\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Rating Analysis"] = rating_analysis.group(1).strip() if rating_analysis else "Not available"

    # Extracting YouTube Insights
    youtube_insights = re.search(r"\*\*YouTube Insights\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["YouTube Insights"] = [insight.strip("- ") for insight in youtube_insights.group(1).strip().split("\n") if insight.strip()] if youtube_insights else []

    # Extracting Additional Details
    additional_details = re.search(r"\*\*Additional Details\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Additional Details"] = [detail.strip("- ") for detail in additional_details.group(1).strip().split("\n") if detail.strip()] if additional_details else []

    # Extracting Strengths
    strengths = re.search(r"\*\*Strengths \(Best features\)\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Strengths"] = [s.strip("- ") for s in strengths.group(1).strip().split("\n") if s.strip()] if strengths else []

    # Extracting Weaknesses
    weaknesses = re.search(r"\*\*Weaknesses \(Negative feedback\)\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Weaknesses"] = [w.strip("- ") for w in weaknesses.group(1).strip().split("\n") if w.strip()] if weaknesses else []

    # Extracting Opportunities
    opportunities = re.search(r"\*\*Opportunities \(Unexplored features\)\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Opportunities"] = [o.strip("- ") for o in opportunities.group(1).strip().split("\n") if o.strip()] if opportunities else []

    # Extracting Threats
    threats = re.search(r"\*\*Threats \(Strong competitors\)\*\*:(.*?)\n\n", analysis, re.DOTALL)
    details["Threats"] = threats.group(1).strip() if threats else "Not available"

    # Extracting Seller Name
    seller_name = re.search(r"\*\*Seller Name\*\*:(.*?)$", analysis, re.DOTALL)
    details["Seller Name"] = seller_name.group(1).strip() if seller_name else "Not available"

    # Extracting Negative Comments
    negative_comments = re.search(r"\*\*Negative Comments\*\*:\s*(\d+)", analysis)
    details["Negative Comments"] = int(negative_comments.group(1)) if negative_comments else 0

    # Extracting Positive Comments
    positive_comments = re.search(r"\*\*Positive Comments\*\*:\s*(\d+)", analysis)
    details["Positive Comments"] = int(positive_comments.group(1)) if positive_comments else 0


    return details

