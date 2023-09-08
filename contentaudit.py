import streamlit as st
import re
import matplotlib.pyplot as plt
from collections import Counter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
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
                    break  # Only add one example per keyword
    return examples

def generate_pdf(fig, top_colors, examples, user_content):
    pdf_file_path = "report.pdf"
    
    c = canvas.Canvas(pdf_file_path, pagesize=letter)
    width, height = letter
    c.drawString(100, height - 50, "Color Personality Analysis")
    
    y_position = height - 100
    
    for color in top_colors:
        c.drawString(100, y_position, f"Top Color: {color}")
        y_position -= 20
        for example in examples[color][:3]:
            c.drawString(100, y_position, example)
            y_position -= 15
    
    c.drawString(100, y_position, "Original Text:")
    y_position -= 20
    user_content = user_content.encode('latin-1', 'replace').decode('latin-1')
    c.drawString(100, y_position, user_content)
    
    # Add the pie chart to the PDF
    fig.savefig("chart.png")
    c.drawImage("chart.png", 100, 100, width=400, height=300)
    
    c.showPage()
    c.save()
    
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
        return

    openai_api_key = st.secrets["OPENAI_API_KEY"]

    color_keywords = {
        # Color keyword definitions
    }

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

        pdf_file_path = generate_pdf(fig, top_colors, examples, user_content)
        download_file(pdf_file_path)

if __name__ == "__main__":
    main()
