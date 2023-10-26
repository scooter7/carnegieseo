import streamlit as st
from bs4 import BeautifulSoup
import requests
from collections import Counter
import openai
import base64

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
else:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    openai.api_key = openai_api_key

def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = " ".join([para.text for para in paragraphs])
    return text

def analyze_text(text, color_keywords):
    text = text.lower()
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        for keyword in keywords['verbs'] + keywords['adjectives']:
            color_counts[color] += text.count(keyword.lower())
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    return [color for color, _ in sorted_colors[:3]]

color_keywords = {
    "Purple - caring, encouraging": {"verbs": ["care", "encourage"], "adjectives": ["caring", "encouraging"]},
    "Green - adventurous, curious": {"verbs": ["explore", "discover"], "adjectives": ["adventurous", "curious"]},
    "Maroon - gritty, determined": {"verbs": ["persevere", "strive"], "adjectives": ["gritty", "determined"]},
    "Orange - artistic, creative": {"verbs": ["create", "express"], "adjectives": ["artistic", "creative"]},
    "Yellow - innovative, intelligent": {"verbs": ["innovate", "intellect"], "adjectives": ["innovative", "intelligent"]},
    "Red - entertaining, humorous": {"verbs": ["entertain", "amuse"], "adjectives": ["entertaining", "humorous"]},
    "Blue - confident, influential": {"verbs": ["inspire", "influence"], "adjectives": ["confident", "influential"]},
    "Pink - charming, elegant": {"verbs": ["charm", "grace"], "adjectives": ["charming", "elegant"]},
    "Silver - rebellious, daring": {"verbs": ["rebel", "dare"], "adjectives": ["rebellious", "daring"]},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble"], "adjectives": ["dedicated", "humble"]}
}

url_input = st.text_area("Paste a list of comma-separated URLs:")

if st.button("Analyze"):
    urls = [url.strip() for url in url_input.split(",")]
    results = []
    for url in urls:
        try:
            content = scrape_text(url)
            top_colors = analyze_text(content, color_keywords)
            results.append((url, content, *top_colors))
        except:
            results.append((url, "Error", "", ""))
    st.session_state.results = results

if 'results' not in st.session_state:
    st.session_state.results = []

for idx, (url, content, color1, color2, color3) in enumerate(st.session_state.results):
    st.write(f"URL: {url}")
    st.write(content)
    st.write(f"Identified Colors: {color1}, {color2}, {color3}")
        selected_colors = st.multiselect(f"Select new color profiles for {url}:", list(color_keywords.keys()), default=[color1, color2, color3], key=f"color_{idx}")
        sliders = {}
        for color in selected_colors:
            sliders[color] = st.slider(f"Ratio for {color}:", 0, 100, 100 // len(selected_colors), key=f"slider_{color}_{idx}")
        seo_keywords = st.text_input(f"Additional SEO keywords for {url}:", key=f"keywords_{idx}")
        facts = st.text_area(f"Specific facts or stats for {url}:", key=f"facts_{idx}")
        if st.button("Revise", key=f"revise_{idx}"):
            original_content = scrape_text(url)
            revised_content = generate_article(original_content, selected_colors, [sliders[color] for color in selected_colors], None, seo_keywords, None, facts)
            st.write("Revised Content:")
            st.write(revised_content)
            b64 = base64.b64encode(revised_content.encode()).decode()
            dl_button = st.download_button(label="Download Revised Content", data=b64, file_name=f'revised_content_{idx}.txt', mime='text/plain')
