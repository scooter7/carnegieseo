import streamlit as st
from bs4 import BeautifulSoup
import requests
from collections import Counter
import openai
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
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

color_keywords = {
    "Purple - caring, encouraging": {"verbs": ["care", "encourage"], "adjectives": ["caring", "encouraging"]},
    "Green - adventurous, curious": {"verbs": ["explore", "discover"], "adjectives": ["adventurous", "curious"]},
    # ... [other color keywords] ...
}

def insert_facts_based_on_context(content_sentences, facts):
    vectorizer = TfidfVectorizer().fit(content_sentences)
    content_vectors = vectorizer.transform(content_sentences)
    for fact in facts:
        fact_vector = vectorizer.transform([fact])
        cosine_similarities = (content_vectors * fact_vector.T).toarray()
        best_sentence_index = np.argmax(cosine_similarities)
        content_sentences[best_sentence_index] += f" {fact}"
    return ' '.join(content_sentences)

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
    full_prompt = user_prompt if user_prompt else "Modify the article with the following guidelines:"
    messages = [{"role": "system", "content": full_prompt}]
    if content:
        messages.append({"role": "user", "content": content})
    if writing_styles and style_weights:
        for i, style in enumerate(writing_styles):
            weight = style_weights[i]
            messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    revised_content = response.choices[0].message["content"].strip()
    revised_sentences = revised_content.split('. ')
    revised_content = insert_facts_based_on_context(revised_sentences, specific_facts_stats.split('\n'))
    return revised_content

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
