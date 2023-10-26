import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter
import openai
import base64

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
else:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    openai.api_key = openai_api_key

def scrape_content_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup.find_all(['header', 'footer', 'nav']):
        tag.decompose()
    content = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])])
    return content

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\\b\\w+\\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
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

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
    full_prompt = user_prompt if user_prompt else "Write an article with the following guidelines:"
    if keywords:
        full_prompt += f"\\nKeywords: {keywords}"
    if audience:
        full_prompt += f"\\nAudience: {audience}"
    if specific_facts_stats:
        full_prompt += f"\\nFacts/Stats: {specific_facts_stats}"
    messages = [{"role": "system", "content": full_prompt}]
    if content:
        messages.append({"role": "user", "content": content})
    if writing_styles and style_weights:
        for i, style in enumerate(writing_styles):
            weight = style_weights[i]
            messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"].strip()

url_input = st.text_area("Paste a list of comma-separated URLs:")

if st.button("Analyze"):
    urls = [url.strip() for url in url_input.split(",")]
    results = []
    for url in urls:
        try:
            content = scrape_content_from_url(url)
            top_colors = analyze_text(content, color_keywords)
            results.append((url, *top_colors))
        except:
            results.append((url, "Error", "", ""))
    st.session_state.results = results

if 'results' not in st.session_state:
    st.session_state.results = []

if st.session_state.results:
    for idx, (url, color1, color2, color3) in enumerate(st.session_state.results):
        if color1 != "Error":
            st.write(f"URL: {url}")
            st.write(f"Identified Colors: {color1}, {color2}, {color3}")
            selected_colors = st.multiselect(f"Select new color profiles for {url}:", list(color_keywords.keys()), default=[color1, color2, color3], key=f"color_{idx}")
            sliders = {}
            for color in selected_colors:
                sliders[color] = st.slider(f"Ratio for {color}:", 0, 100, 100 // len(selected_colors), key=f"slider_{color}_{idx}")
            seo_keywords = st.text_input(f"Additional SEO keywords for {url}:", key=f"keywords_{idx}")
            facts = st.text_area(f"Specific facts or stats for {url}:", key=f"facts_{idx}")
            if st.button("Revise", key=f"revise_{idx}"):
                original_content = scrape_content_from_url(url)
                revised_content = generate_article(original_content, selected_colors, [sliders[color] for color in selected_colors], None, seo_keywords, None, facts)
                st.write("Revised Content:")
                st.write(revised_content)
                b64 = base64.b64encode(revised_content.encode()).decode()
                dl_link = f'<a download="revised_content_{idx}.txt" href="data:text/plain;charset=UTF-8;base64,{b64}" >Download Revised Content for {url}</a><br></br>'
                st.markdown(dl_link, unsafe_allow_html=True)
