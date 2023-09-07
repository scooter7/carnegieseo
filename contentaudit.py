import streamlit as st
import re
import matplotlib.pyplot as plt
from collections import Counter
import openai
import sys
import logging
import pandas as pd
from fpdf import FPDF
import base64

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def draw_pie_chart(labels, sizes):
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    return fig1

def extract_examples(text, color_keywords, top_colors):
    text = text.lower()
    examples = {}
    sentences = re.split(r'[.!?]', text)
    for color in top_colors:
        examples[color] = []
        for keyword in color_keywords[color]:
            keyword = keyword.lower()
            for sentence in sentences:
                if keyword in sentence:
                    examples[color].append(sentence.strip() + '.')
    return examples

def generate_pdf(text, fig, top_colors, examples):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Color Personality Analysis", ln=1, align='C')
    pdf.cell(200, 10, "Original Text:", ln=1)
    pdf.multi_cell(0, 10, text)
    pdf.add_page()
    pdf.image("chart.png", x=10, y=10, w=190)
    pdf.ln(65)
    for color in top_colors:
        pdf.cell(200, 10, f"Top Color: {color}", ln=1)
        pdf.multi_cell(0, 10, "\n".join(examples[color]))
    pdf_file_path = "report.pdf"
    pdf.output(name=pdf_file_path, dest='F').encode('latin1')
    return pdf_file_path

def download_file(file_path):
    with open(file_path, "rb") as f:
        pdf_file = f.read()
    b64_pdf = base64.b64encode(pdf_file).decode("utf-8")
    href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="report.pdf">Download PDF Report</a>'
    st.markdown(href, unsafe_allow_html=True)

def main():
    st.title("Color Personality Analysis")
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
        sys.exit(1)
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    color_keywords = {'Red': ['Activate', 'Animate'], 'Silver': ['Campaign', 'Challenge'], 'Blue': ['Accomplish', 'Achieve']}
    user_content = st.text_area("Paste your content here:")
    if st.button('Analyze'):
        color_counts = analyze_text(user_content, color_keywords)
        total_counts = sum(color_counts.values())
        if total_counts == 0:
            st.write("No relevant keywords found.")
            return
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        top_colors = [color for color, _ in sorted_colors[:3]]
        labels = [k for k, v in color_counts.items() if v > 0]
        sizes = [v for v in color_counts.values() if v > 0]
        fig = draw_pie_chart(labels, sizes)
        st.pyplot(fig)
        examples = extract_examples(user_content, color_keywords, top_colors)
        for color in top_colors:
            st.write(f"Examples for {color}:")
            st.write(", ".join(examples[color]))
        fig.savefig("chart.png")
        pdf_file_path = generate_pdf(user_content, fig, top_colors, examples)
        download_file(pdf_file_path)

main()
