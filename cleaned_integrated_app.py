import streamlit as st
from bs4 import BeautifulSoup
import requests
from collections import Counter
import openai
import base64
import pandas as pd  # Add this line to import pandas
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
    full_prompt = user_prompt if user_prompt else "Modify the content based on the following guidelines:"
    if keywords:
        full_prompt += f"\nInclude these keywords: {keywords}"
    messages = [{"role": "system", "content": full_prompt}]
    messages.append({"role": "user", "content": content})
    if writing_styles and style_weights:
        for i, style in enumerate(writing_styles):
            weight = style_weights[i]
            messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    revised_content = response.choices[0].message["content"].strip()
    revised_sentences = revised_content.split('. ')
    vectorizer = TfidfVectorizer().fit(revised_sentences)
    for fact in specific_facts_stats.split('\n'):
        fact_vector = vectorizer.transform([fact]).toarray()
        similarities = cosine_similarity(fact_vector, vectorizer.transform(revised_sentences).toarray())
        index = np.argmax(similarities)
        revised_sentences[index] = f"{revised_sentences[index]}. {fact}"
    revised_content = ". ".join(revised_sentences)
    if keywords:
        revised_content += f"\nKeywords: {keywords}"
    st.text(revised_content)
    st.download_button("Download Revised Content", revised_content, "revised_content.txt")
    return revised_content

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
    results = process_urls(url_list, openai_api_key)
    df = pd.DataFrame(results, columns=["URL", "Top Color", "Top Supporting Color", "Additional Supporting Color"])
    st.write(df)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="color_analysis.csv">Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)
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
        revised_colors = (url, *top_colors)  # Assuming top_colors contains the revised colors
        results[idx] = revised_colors

df = pd.DataFrame(results, columns=["URL", "Top Color", "Top Supporting Color", "Additional Supporting Color"])
st.write(df)
csv = df.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()
href = f'<a href="data:file/csv;base64,{b64}" download="color_analysis.csv">Download CSV File</a>'
st.markdown(href, unsafe_allow_html=True)
revised_content = generate_article(content, selected_colors, [sliders[color] for color in selected_colors], None, seo_keywords, None, facts)

def process_urls(url_list, openai_api_key, rate_limit=60, delay_time=60):
    results = []
    for idx, url in enumerate(url_list):
        try:
            content = scrape_text(url)
            top_colors = analyze_text(content, color_keywords)
            results.append((url, *top_colors))
            if (idx + 1) % rate_limit == 0:
                time.sleep(delay_time)
        except:
            results.append((url, "Error", "", ""))
    return results
