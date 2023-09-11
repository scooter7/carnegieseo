import streamlit as st
import re
import plotly.graph_objects as go
from collections import Counter
from docx import Document
from docx.shared import Inches
import io
import matplotlib.pyplot as plt
import base64
import openai

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def draw_donut_chart(color_counts):
    labels = list(color_counts.keys())
    sizes = [color_counts.get(color, 0) for color in labels]
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, marker=dict(colors=labels))])
    return fig

def analyze_tone_with_gpt3(text, api_key):
    openai.api_key = api_key
    prompt = f"""
    Please provide a nuanced analysis of the following text, assigning a percentage score to indicate the extent to which the text embodies each of the following tones:
    - Relaxed
    - Assertive
    - Introverted
    - Extroverted
    - Conservative
    - Progressive
    - Emotive
    - Informative
    Text to Analyze:
    {text}
    """
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=100)
    gpt3_output = response.choices[0].text.strip().split('\n')
    tone_scores = {}
    for line in gpt3_output:
        if ":" in line:
            tone, score = line.split(":")
            tone_scores[tone.strip()] = float(score.strip().replace('%', ''))
    return tone_scores

def generate_word_doc(color_counts, user_content, tone_scores):
    doc = Document()
    doc.add_heading('Color Personality Analysis', 0)
    fig = draw_donut_chart(color_counts)
    image_stream = io.BytesIO(fig.to_image(format="png"))
    doc.add_picture(image_stream, width=Inches(4.0))
    image_stream.close()
    for tone, score in tone_scores.items():
        doc.add_paragraph(f"{tone}: {score}%")
    doc.add_heading('Original Text:', level=1)
    doc.add_paragraph(user_content)
    word_file_path = "Color_Personality_Analysis_Report.docx"
    doc.save(word_file_path)
    return word_file_path

def get_word_file_download_link(file_path, filename):
    with open(file_path, "rb") as f:
        file_data = f.read()
    b64_file = base64.b64encode(file_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_file}" download="{filename}">Download Word Report</a>'
    return href

def main():
    st.title('Color Personality Analysis')
    
    if 'sentence_to_colors' not in st.session_state:
        st.session_state.sentence_to_colors = {}
        
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
        return
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    
    color_keywords = {'Red': ['energetic', 'passionate'], 'Silver': ['bold', 'daring']}
    user_content = st.text_area('Paste your content here:')

    if st.button('Analyze'):
        st.session_state.sentence_to_colors = {}
        
        color_counts = analyze_text(user_content, color_keywords)
        initial_fig = draw_donut_chart(color_counts)
        st.subheader('Initial Donut Chart')
        st.plotly_chart(initial_fig)
        
        tone_scores = analyze_tone_with_gpt3(user_content, openai_api_key)
        st.subheader("Tone Analysis")
        
        tone_colors = [tone for tone in tone_scores.keys()]
        plt.bar(tone_scores.keys(), tone_scores.values(), color=tone_colors)
        plt.xticks(rotation=45)
        plt.xlabel('Tone')
        plt.ylabel('Percentage (%)')
        plt.title('Tone Analysis')
        st.pyplot()
        
        sentences = re.split(r'[.!?]', user_content)
        for sentence in sentences:
            if not sentence.strip():
                continue
            initial_colors = []
            for color, keywords in color_keywords.items():
                if any(keyword.lower() in sentence.lower() for keyword in keywords):
                    initial_colors.append(color)
            st.session_state.sentence_to_colors[sentence] = initial_colors
            
    if st.session_state.sentence_to_colors:
        updated_color_counts = Counter()
        for sentence, initial_colors in st.session_state.sentence_to_colors.items():
            selected_colors = st.multiselect(
                f"{sentence}. [{', '.join(initial_colors)}]",
                list(color_keywords.keys()),
                default=initial_colors
            )
            st.session_state.sentence_to_colors[sentence] = selected_colors
            for color in selected_colors:
                updated_color_counts[color] += 1
                
        updated_fig = draw_donut_chart(updated_color_counts)
        st.subheader('Updated Donut Chart based on User Reassignments')
        st.plotly_chart(updated_fig)
        
        word_file_path = generate_word_doc(updated_color_counts, user_content, tone_scores)
        download_link = get_word_file_download_link(word_file_path, "Color_Personality_Analysis_Report.docx")
        st.markdown(download_link, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
