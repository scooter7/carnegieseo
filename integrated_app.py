import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter
import openai

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
else:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    openai.api_key = openai_api_key

def scrape_content_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup.find_all(['header', 'footer', 'nav']):
        tag.decompose()
    content = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    return content

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    return [color for color, _ in sorted_colors[:3]]

color_keywords = {'Red': ['Activate', 'Animate', 'Amuse', 'Captivate', 'Cheer', 'Delight', 'Encourage', 'Energize', 'Engage', 'Enjoy', 'Enliven', 'Entertain', 'Excite', 'Express', 'Inspire', 'Joke', 'Motivate', 'Play', 'Stir', 'Uplift', 'Amusing', 'Clever', 'Comedic', 'Dynamic', 'Energetic', 'Engaging', 'Enjoyable', 'Entertaining', 'Enthusiastic', 'Exciting', 'Expressive', 'Extroverted', 'Fun', 'Humorous', 'Interesting', 'Lively', 'Motivational', 'Passionate', 'Playful', 'Spirited'], 'Purple': ['Care', 'Encourage', 'Support', 'Help', 'Assist', 'Guide', 'Caring', 'Encouraging', 'Supportive', 'Helpful', 'Assisting', 'Guiding']}
    'Red': ['Activate', 'Animate', 'Amuse', 'Captivate', 'Cheer', 'Delight', 'Encourage', 'Energize', 'Engage', 'Enjoy', 'Enliven', 'Entertain', 'Excite', 'Express', 'Inspire', 'Joke', 'Motivate', 'Play', 'Stir', 'Uplift', 'Amusing', 'Clever', 'Comedic', 'Dynamic', 'Energetic', 'Engaging', 'Enjoyable', 'Entertaining', 'Enthusiastic', 'Exciting', 'Expressive', 'Extroverted', 'Fun', 'Humorous', 'Interesting', 'Lively', 'Motivational', 'Passionate', 'Playful', 'Spirited'],
}

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
    full_prompt = user_prompt
    if keywords:
        full_prompt += f"\nKeywords: {keywords}"
    if audience:
        full_prompt += f"\nAudience: {audience}"
    if specific_facts_stats:
        full_prompt += f"\nFacts: {specific_facts_stats}"
    response = openai.Completion.create(prompt=full_prompt, max_tokens=150)
    return response.choices[0].text.strip()

placeholders = {'Red': {'verbs': ['Activate', 'Animate', 'Amuse', 'Captivate', 'Cheer', 'Delight', 'Encourage', 'Energize', 'Engage', 'Enjoy', 'Enliven', 'Entertain', 'Excite', 'Express', 'Inspire', 'Joke', 'Motivate', 'Play', 'Stir', 'Uplift'], 'adjectives': ['Amusing', 'Clever', 'Comedic', 'Dynamic', 'Energetic', 'Engaging', 'Enjoyable', 'Entertaining', 'Enthusiastic', 'Exciting', 'Expressive', 'Extroverted', 'Fun', 'Humorous', 'Interesting', 'Lively', 'Motivational', 'Passionate', 'Playful', 'Spirited']}, 'Purple': {'verbs': ['Care', 'Encourage', 'Support', 'Help', 'Assist', 'Guide'], 'adjectives': ['Caring', 'Encouraging', 'Supportive', 'Helpful', 'Assisting', 'Guiding']}}
    "Purple - caring, encouraging": {"verbs": ["care", "encourage"], "adjectives": ["caring", "encouraging"]},
}

url_input = st.text_area("Paste a list of comma-separated URLs:")

if url_input:
    urls = [url.strip() for url in url_input.split(",")]
    results = []

    for url in urls:
        try:
            content = scrape_content_from_url(url)
            top_colors = analyze_text(content, color_keywords)
            results.append((url, *top_colors))
        except:
            results.append((url, "Error", "", ""))

    for idx, (url, color1, color2, color3) in enumerate(results):
        if color1 != "Error":
            st.write(f"URL: {url}")
            st.write(f"Identified Colors: {color1}, {color2}, {color3}")
            color_profile = st.selectbox(f"Select a new color profile for {url}:", list(placeholders.keys()), key=f"color_{idx}")
            seo_keywords = st.text_input(f"Additional SEO keywords for {url}:", key=f"keywords_{idx}")
            facts = st.text_area(f"Specific facts or stats for {url}:", key=f"facts_{idx}")
            original_content = scrape_content_from_url(url)
            revised_content = generate_article(original_content, None, None, None, seo_keywords, None, facts)
            st.write("Revised Content:")
            st.write(revised_content)
