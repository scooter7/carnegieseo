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
    words = re.findall(r'\\b\\w+\\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def draw_donut_chart(labels, sizes):
    colors = labels
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, marker=dict(colors=colors))])
    fig.write_image("donut_chart.png")
    return fig

def draw_quadrant_chart(tone_analysis, title):
    fig = go.Figure()
    for label, value in tone_analysis.items():
        fig.add_trace(go.Scatter(x=[label], y=[value], mode='markers', name=label))
            fig.add_shape(type='line', x0=5, x1=5, y0=0, y1=10, line=dict(color='Grey', width=1, dash='dash'))
    fig.add_shape(type='line', x0=0, x1=10, y0=5, y1=5, line=dict(color='Grey', width=1, dash='dash'))
    fig.update_xaxes(range=[0, 10], tickvals=list(range(0, 11)), ticktext=['Introverted', '', '', '', '', '', '', '', '', '', 'Extroverted'])
    fig.update_yaxes(range=[0, 10], tickvals=list(range(0, 11)), ticktext=['', '', '', '', '', 'Assertive', '', '', '', '', 'Relaxed'])
    fig.update_layout(title=title)
    fig.write_image(title + ".png")
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
    response = openai.Completion.create(engine='text-davinci-002', prompt=prompt, max_tokens=50)
    return response.choices[0].text.strip()

def generate_word_doc(top_colors, examples, user_content, general_analysis, tone_scores, new_tone_scores):
    doc = Document()
    doc.add_heading('Color Personality Analysis', 0)
    doc.add_picture('donut_chart.png', width=Inches(4.0))
    doc.add_heading('Top Colors', level=1)
    for color in top_colors:
        doc.add_paragraph(f'Top Color: {color}')
        for example in examples[color]:
            doc.add_paragraph(example, style='ListBullet')
    doc.add_heading('Original Content', level=1)
    doc.add_paragraph(user_content)
    doc.add_heading('GPT-3 Analysis', level=1)
    doc.add_paragraph(general_analysis)
    doc.add_heading('Tone Analysis', level=1)
    doc.add_paragraph(', '.join(f'{k}: {v}' for k, v in tone_scores.items()))
    doc.add_picture('Tone Quadrant Chart.png', width=Inches(4.0))
    doc.add_heading('Additional Tone Analysis', level=1)
    doc.add_paragraph(', '.join(f'{k}: {v}' for k, v in new_tone_scores.items()))
    doc.add_picture('Additional Tone Quadrant Chart.png', width=Inches(4.0))
    word_file_path = 'report.docx'
    doc.save(word_file_path)
    return word_file_path

def download_file(file_path):
    with open(file_path, 'rb') as f:
        file_data = f.read()
    b64_file = base64.b64encode(file_data).decode('utf-8')
    st.markdown(f'<a href="data:application/octet-stream;base64,{b64_file}" download="{file_path}">Download {file_path}</a>', unsafe_allow_html=True)

def main():
    st.title('Color Personality Analysis')
    if 'OPENAI_API_KEY' not in st.secrets:
        st.error('Please set the OPENAI_API_KEY secret on the Streamlit dashboard.')
        return

    openai_api_key = st.secrets['OPENAI_API_KEY']

    color_keywords = {'Red': ['Activate', 'Animate'], 'Blue': ['Accomplish', 'Achieve']}
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

        general_prompt = 'Who would find the following text compelling?\\n\\n' + user_content[:500]
        general_analysis = analyze_with_gpt3(user_content, openai_api_key, general_prompt)
        st.write('GPT-3 Analysis:')
        st.write(general_analysis)

        tone_scores = {'Extroverted': 7, 'Introverted': 3, 'Relaxed': 6, 'Assertive': 4}
        new_tone_scores = {'Emotive': 5, 'Informative': 5, 'Conservative': 3, 'Progressive': 7}

        fig1 = draw_quadrant_chart(tone_scores, 'Tone Quadrant Chart')
        fig2 = draw_quadrant_chart(new_tone_scores, 'Additional Tone Quadrant Chart')

        st.plotly_chart(fig1)
        st.plotly_chart(fig2)

        word_file_path = generate_word_doc(top_colors, examples, user_content, general_analysis, tone_scores, new_tone_scores)
        download_file(word_file_path)

if __name__ == '__main__':
    main()


