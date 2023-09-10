import streamlit as st
import re
from collections import Counter
import base64
from docx import Document
from docx.shared import Inches
import plotly.graph_objects as go
import openai

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def draw_donut_chart(labels, sizes):
    colors = labels  # Assign the color name to the corresponding data
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, marker=dict(colors=colors))])
    return fig

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

def analyze_with_gpt3(text, api_key, prompt):
    openai.api_key = api_key
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=50)
    return response.choices[0].text.strip()

def generate_word_doc(top_colors, examples, user_content, general_analysis, tone_analysis, new_tone_analysis):
    doc = Document()
    doc.add_heading('Color Personality Analysis', 0)
    doc.add_picture('donut_chart.png', width=Inches(4.0))
    for color in top_colors:
        doc.add_heading(f'Top Color: {color}', level=1)
        for example in examples[color]:
            doc.add_paragraph(example)
    doc.add_heading('Original Text:', level=1)
    doc.add_paragraph(user_content)
    doc.add_heading('GPT-3 General Analysis:', level=1)
    doc.add_paragraph(general_analysis)
    doc.add_heading('Tone Analysis:', level=1)
    doc.add_paragraph(f"Extroverted: {tone_analysis['Extroverted']}, Introverted: {tone_analysis['Introverted']}, Relaxed: {tone_analysis['Relaxed']}, Assertive: {tone_analysis['Assertive']}")
    doc.add_heading('Additional Tone Analysis:', level=1)
    doc.add_paragraph(f"Emotive: {new_tone_analysis['Emotive']}, Informative: {new_tone_analysis['Informative']}, Conservative: {new_tone_analysis['Conservative']}, Progressive: {new_tone_analysis['Progressive']}")
    word_file_path = "report.docx"
    doc.save(word_file_path)
    return word_file_path

def download_file(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
    b64_file = base64.b64encode(file_data).decode("utf-8")
    href = f'<a href="data:application/octet-stream;base64,{b64_file}" download="report.docx">Download Word Report</a>'
    st.markdown(href, unsafe_allow_html=True)

def main():
    st.title("Color Personality Analysis")
    color_keywords = {
        'Red': ['Activate', 'Animate'],
        'Silver': ['Activate', 'Campaign'],
        'Blue': ['Accomplish', 'Achieve'],
        'Yellow': ['Accelerate', 'Advance'],
        'Green': ['Analyze', 'Discover'],
        'Purple': ['Accommodate', 'Assist'],
        'Maroon': ['Accomplish', 'Achieve'],
        'Orange': ['Compose', 'Conceptualize'],
        'Pink': ['Arise', 'Aspire']
    }
    user_content = st.text_area("Paste your content here:")
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
        return
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    if st.button('Analyze'):
        st.write("Original Text:")
        st.write(user_content)
        color_counts = analyze_text(user_content, color_keywords)
        total_counts = sum(color_counts.values())
        if total_counts == 0:
            st.write("No relevant keywords found.")
            return
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        top_colors = [color for color, _ in sorted_colors[:3]]
        labels = [k for k, v in color_counts.items() if v > 0]
        sizes = [v for v in color_counts.values() if v > 0]
        fig1 = draw_donut_chart(labels, sizes)
        fig1.write_image("donut_chart.png")
        st.plotly_chart(fig1)
        examples = extract_examples(user_content, color_keywords, top_colors)
        for color in top_colors:
            st.write(f"Examples for {color}:")
            st.write(", ".join(examples[color]))
        general_prompt = f"Please analyze the following text and identify who would likely find it compelling:\n\n{user_content}"
        general_analysis = analyze_with_gpt3(user_content, openai_api_key, general_prompt)
        st.write("GPT-3 General Analysis:")
        st.write(general_analysis)
        tone_prompts = {
            'Extroverted': f"How extroverted is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:",
            'Introverted': f"How introverted is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:",
            'Relaxed': f"How relaxed is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:",
            'Assertive': f"How assertive is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:"
        }
        tone_analysis = {}
        for tone, prompt in tone_prompts.items():
            tone_analysis[tone] = analyze_with_gpt3(user_content, openai_api_key, prompt)
        new_tone_prompts = {
            'Emotive': f"How emotive is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:",
            'Informative': f"How informative is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:",
            'Conservative': f"How conservative is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:",
            'Progressive': f"How progressive is the tone of the following text?\n\n{user_content}\n\nRate from 0 to 10:"
        }
        new_tone_analysis = {}
        for tone, prompt in new_tone_prompts.items():
            new_tone_analysis[tone] = analyze_with_gpt3(user_content, openai_api_key, prompt)
        
        word_file_path = generate_word_doc(top_colors, examples, user_content, general_analysis, tone_analysis, new_tone_analysis)
        download_file(word_file_path)

if __name__ == "__main__":
    main()
