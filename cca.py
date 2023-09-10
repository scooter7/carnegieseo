import streamlit as st
import re
from collections import Counter
import base64
from docx import Document
from docx.shared import Inches
import plotly.graph_objects as go
import openai

# Define GPT-3 API key
OPENAI_API_KEY = "OPENAI_API_KEY"

# Rest of your code remains the same...

def analyze_with_gpt3(text, prompt):
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.Completion.create(
            engine='text-davinci-002',
            prompt=f"{prompt}\n\n{text}",
            max_tokens=50,
            temperature=0.5
        )
        return response.choices[0].text.strip()
    except Exception as e:
        st.error(f"GPT-3 API Error: {e}")
        return ""

def draw_donut_chart(labels, sizes):
    colors = labels
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, marker=dict(colors=colors))])
    fig.write_image("donut_chart.png")
    return fig

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def extract_examples(text, color_keywords, top_colors):
    text = text.lower()
    examples = {}
    sentences = list(set(re.split(r'[.!?]', text)))
    for color in top_colors:
        examples[color] = set()
        for keyword in color_keywords[color]:
            keyword = keyword.lower()
            for sentence in sentences:
                if keyword in sentence:
                    examples[color].add(sentence.strip() + '.')
        examples[color] = list(examples[color])[:3]
    return examples

# Modify the main() function
def main():
    st.title('Color Personality Analysis')
    if 'OPENAI_API_KEY' not in st.secrets:
        st.error('Please set the OPENAI_API_KEY secret on the Streamlit dashboard.')
        return
    openai_api_key = st.secrets['OPENAI_API_KEY']
    color_keywords = {...}
    user_content = st.text_area('Paste your content here:')
    if st.button('Analyze'):
        color_counts = analyze_text(user_content, color_keywords)
        total_counts = sum(color_counts.values())
        if total_counts == 0:
            st.write('No relevant keywords found.')
            return
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        top_colors = [color for color, _ in sorted_colors[:3]]
        labels = [k for k, v in color_counts.items() if v > 0]
        sizes = [v for v in color_counts.values() if v > 0]
        fig = draw_donut_chart(labels, sizes)
        st.plotly_chart(fig)
        examples = extract_examples(user_content, color_keywords, top_colors)
        for color in top_colors:
            st.write(f'Examples for {color}:')
            st.write(', '.join(examples[color]))
        try:
            tone_analysis_prompt = """Based on the following text, please provide scores between 1 to 10 for the following traits: - relaxed: calm, laid-back, stress-free - assertive: confident, self-assured - introverted: reserved, quiet - extroverted: outgoing, social"""
            tone_scores = analyze_with_gpt3(user_content, openai_api_key, tone_analysis_prompt)
            additional_tone_prompt = """Based on the following text, please provide scores between 1 to 10 for the following additional traits: - conservative: traditional, resistant to change - progressive: open to new ideas, forward-thinking - emotive: expressing emotion - informative: providing useful or interesting information"""
            new_tone_scores = analyze_with_gpt3(user_content, openai_api_key, additional_tone_prompt)
            combined_tone_scores = {**tone_scores, **new_tone_scores}
            general_analysis = 'Your text was analyzed by GPT-3 to determine the following traits based on your tone: ' + ', '.join([f"{k}: {v}" for k, v in combined_tone_scores.items()])
            st.write('GPT-3 Analysis:')
            st.write(general_analysis)
            fig1 = draw_quadrant_chart(tone_scores, 'Tone Quadrant Chart', ['Relaxed', 'Assertive'], ['Extroverted', 'Introverted'])
            fig2 = draw_quadrant_chart(new_tone_scores, 'Additional Tone Quadrant Chart', ['Conservative', 'Progressive'], ['Emotive', 'Informative'])
            st.plotly_chart(fig1)
            st.plotly_chart(fig2)
            word_file_path = generate_word_doc(top_colors, examples, user_content, general_analysis, tone_scores, new_tone_scores)
            download_file(word_file_path)
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
