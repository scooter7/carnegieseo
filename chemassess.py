import streamlit as st
import openai
import requests
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import io
import hashlib

# Load your API key from Streamlit's secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Define your color-based personas
placeholders = {
    "Purple - caring, encouraging": {"verbs": ["assist", "befriend", "care", "collaborate", "connect", "embrace", "empower", "encourage", "foster", "give", "help", "nourish", "nurture", "promote", "protect", "provide", "serve", "share", "shepherd", "steward", "tend", "uplift", "value", "welcome"], "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"], 
     "beliefs": ['Believe people should be cared for and encouraged', 'Desire to make others feel safe and supported', 'Have a strong desire to mend and heal', 'Become loyal teammates and trusted allies', 'Are put off by aggression and selfish motivations']},
    "Green - adventurous, curious": {"verbs": ["analyze", "discover", "examine", "expand", "explore", "extend", "inquire", "journey", "launch", "move", "pioneer", "pursue", "question", "reach", "search", "uncover", "venture", "wonder"], "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"], 
     "beliefs": ['The noblest pursuit is the quest for new knowledge', 'Continually inquiring and examining everything', 'Have an insatiable thirst for progress and discovery', 'Cannot sit still or accept present realities', 'Curiosity and possibility underpin their actions']},
    # Other color categories go here...
}

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def extract_words(text, words_list):
    words_counter = Counter()
    for word in words_list:
        words_counter[word] = text.lower().split().count(word.lower())
    return words_counter

def analyze_url_content(content):
    color_scores = defaultdict(int)
    color_analysis = defaultdict(dict)

    for color, traits in placeholders.items():
        verbs_count = extract_words(content, traits['verbs'])
        adjectives_count = extract_words(content, traits['adjectives'])
        total_count = sum(verbs_count.values()) + sum(adjectives_count.values())
        color_scores[color] = total_count
        color_analysis[color]['verbs'] = verbs_count
        color_analysis[color]['adjectives'] = adjectives_count

    return color_scores, color_analysis

def analyze_text_detailed(content, summarized_placeholders):
    prompt_base = f"Please analyze the following text and identify which verbs and adjectives from the following categories are present. Also, explain how these relate to the predefined beliefs of each category:\n\nCategories:\n" + "\n".join([f"{color}: Verbs({info['verbs']}), Adjectives({info['adjectives']})" for color, info in summarized_placeholders.items()]) + "\n\nText: "

    text_chunks = [content[i:i+3000] for i in range(0, len(content), 3000)]
    detailed_responses = []

    for chunk in text_chunks:
        prompt_text = prompt_base + chunk
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=500
        )
        detailed_responses.append(response.choices[0].message['content'])

    return "\n".join(detailed_responses)

st.title("Color Persona Text Analysis")

# Hide the toolbar using CSS
hide_toolbar_css = """
    <style>
        .css-14xtw13.e8zbici0 { display: none !important; }
    </style>
"""
st.markdown(hide_toolbar_css, unsafe_allow_html=True)

url_input = st.text_area("Paste comma-separated URLs here:", height=100)
urls = [url.strip() for url in url_input.split(',')]

results = st.session_state.get('results', [])
aggregate_scores = st.session_state.get('aggregate_scores', defaultdict(int))

if st.button("Analyze URLs"):
    results = []
    aggregate_scores = defaultdict(int)

    for url in urls:
        try:
            st.write(f"Analyzing URL: {url}")  # Debug statement
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.get_text()
            content_hash = get_content_hash(content)

            # Check if analysis for this content already exists
            if 'analysis_cache' not in st.session_state:
                st.session_state.analysis_cache = {}

            if content_hash in st.session_state.analysis_cache:
                color_scores, color_analysis = st.session_state.analysis_cache[content_hash]
            else:
                color_scores, color_analysis = analyze_url_content(content)
                st.session_state.analysis_cache[content_hash] = (color_scores, color_analysis)

            summarized_placeholders = {
                color: {
                    'verbs': ', '.join(info['verbs']),
                    'adjectives': ', '.join(info['adjectives'])
                } for color, info in placeholders.items()
            }

            detailed_analysis = analyze_text_detailed(content, summarized_placeholders)

            sorted_colors = sorted(color_scores.items(), key=lambda item: item[1], reverse=True)
            top_colors = sorted_colors[:3]

            url_result = {"URL": url}
            for i, (color, score) in enumerate(top_colors):
                url_result[f"Top Color {i + 1}"] = color
                aggregate_scores[color] += score
            results.append(url_result)

            st.write(f"Analysis for URL: {url}")
            for color, score in top_colors:
                st.write(f"**{color}** - Score: {score}")
                st.write("Reasons:")
                for belief in placeholders[color]['beliefs']:
                    st.write(f"- {belief}")
                st.write("Verbs found:")
                for verb, count in color_analysis[color]['verbs'].items():
                    if count > 0:
                        st.write(f"  {verb}: {count}")
                st.write("Adjectives found:")
                for adjective, count in color_analysis[color]['adjectives'].items():
                    if count > 0:
                        st.write(f"  {adjective}: {count}")
            st.write("Detailed Analysis:")
            st.write(detailed_analysis)
            st.write("---")
        except Exception as e:
            st.write(f"Error analyzing URL: {url}")
            st.write(f"Error message: {str(e)}")

    st.session_state.results = results
    st.session_state.aggregate_scores = aggregate_scores

if results:
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    # Downloadable table of results
    csv = df_results.to_csv(index=False)
    st.download_button(label="Download Table as CSV", data=csv, file_name="color_persona_analysis.csv", mime="text/csv")

    # Aggregate color scores chart
    st.subheader("Aggregate Color Scores")
    colors = list(aggregate_scores.keys())
    scores = [aggregate_scores[color] for color in colors]
    plt.figure(figsize=(12, 6))
    plt.bar(colors, scores, color='skyblue')
    plt.xlabel("Color Categories")
    plt.ylabel("Aggregate Scores")
    plt.title("Aggregate Color Scores for All URLs")
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # Downloadable chart
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.download_button(label="Download Chart as PNG", data=buf, file_name="aggregate_color_scores.png", mime="image/png")
