import streamlit as st
import re
import matplotlib.pyplot as plt
import openai
import sys
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def analyze_text(text, color_keywords):
    color_counts = {color: 0 for color in color_keywords}
    
    for color, keywords in color_keywords.items():
        for keyword in keywords:
            count = len(re.findall(fr'\b{re.escape(keyword)}\b', text, flags=re.IGNORECASE))
            color_counts[color] += count
            
    return color_counts

def draw_pie_chart(labels, sizes):
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    return fig

def extract_examples(text, color_keywords, top_colors):
    examples = {color: [] for color in top_colors}
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    for sentence in sentences:
        for color, keywords in color_keywords.items():
            for keyword in keywords:
                if re.search(fr'\b{re.escape(keyword)}\b', sentence, flags=re.IGNORECASE):
                    if len(examples[color]) < 3 and sentence not in examples[color]:
                        examples[color].append(sentence)
    
    return examples

def generate_pdf(text, fig, top_colors, examples):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Title
    title = "Color Personality Analysis"
    title_style = styles['Title']
    title_paragraph = Paragraph(title, title_style)
    
    # Original Text
    original_text_text = "Original Text:"
    original_text_style = styles['Heading2']
    original_text_paragraph = Paragraph(original_text_text, original_text_style)
    
    original_text = Paragraph(text, styles['Normal'])
    
    # Top Colors
    top_colors_text = "Top Colors in the Text:"
    top_colors_style = styles['Heading2']
    top_colors_paragraph = Paragraph(top_colors_text, top_colors_style)
    
    top_colors_list = ", ".join(top_colors)
    
    # Pie Chart
    img = Image(fig, width=400, height=400)
    
    # Color Examples
    color_examples_text = "Examples:"
    color_examples_style = styles['Heading2']
    color_examples_paragraph = Paragraph(color_examples_text, color_examples_style)
    
    examples_text = []
    for color, color_examples in examples.items():
        color_examples_text = f"{color} Examples:"
        examples_text.append(Paragraph(color_examples_text, color_examples_style))
        for example in color_examples:
            examples_text.append(Paragraph(f"- {example}", styles['Normal']))
    
    # Build PDF content
    content = [title_paragraph, Spacer(1, 12)]
    content.extend([original_text_paragraph, original_text, Spacer(1, 12)])
    content.extend([top_colors_paragraph, Paragraph(top_colors_list, styles['Normal']), Spacer(1, 12)])
    content.extend([Paragraph("Color Distribution:", styles['Heading2']), img, Spacer(1, 12)])
    content.append(color_examples_paragraph)
    content.extend(examples_text)
    
    doc.build(content)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def download_file(pdf_data):
    st.download_button(
        "Download PDF Report",
        pdf_data,
        file_name="report.pdf",
        key="pdf-download"
    )

def main():
    st.title("Color Personality Analysis")

    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
        sys.exit(1)

    openai_api_key = st.secrets["OPENAI_API_KEY"]

    color_keywords = {
        'Red': ['Activate', 'Animate', 'Amuse', 'Captivate', 'Cheer', 'Delight', 'Encourage', 'Energize', 'Engage', 'Enjoy', 'Enliven', 'Entertain', 'Excite', 'Express', 'Inspire', 'Joke', 'Motivate', 'Play', 'Stir', 'Uplift', 'Amusing', 'Clever', 'Comedic', 'Dynamic', 'Energetic', 'Engaging', 'Enjoyable', 'Entertaining', 'Enthusiastic', 'Exciting', 'Expressive', 'Extroverted', 'Fun', 'Humorous', 'Interesting', 'Lively', 'Motivational', 'Passionate', 'Playful', 'Spirited'],
        'Silver': ['Activate', 'Campaign', 'Challenge', 'Commit', 'Confront', 'Dare', 'Defy', 'Disrupting', 'Drive', 'Excite', 'Face', 'Ignite', 'Incite', 'Influence', 'Inspire', 'Inspirit', 'Motivate', 'Move', 'Push', 'Rebel', 'Reimagine', 'Revolutionize', 'Rise', 'Spark', 'Stir', 'Fight', 'Free', 'Aggressive', 'Bold', 'Brazen', 'Committed', 'Courageous', 'Daring', 'Disruptive', 'Driven', 'Fearless', 'Free', 'Gutsy', 'Independent', 'Inspired', 'Motivated', 'Rebellious', 'Revolutionary', 'Unafraid', 'Unconventional'],
        'Blue': ['Accomplish', 'Achieve', 'Affect', 'Assert', 'Cause', 'Command', 'Determine', 'Direct', 'Dominate', 'Drive', 'Empower', 'Establish', 'Guide', 'Impact', 'Impress', 'Influence', 'Inspire', 'Lead', 'Outpace', 'Outshine', 'Realize', 'Shape', 'Succeed', 'Transform', 'Win', 'Accomplished', 'Assertive', 'Authoritative', 'Commanding', 'Confident', 'Decisive', 'Distinguished', 'Dominant', 'Elite', 'Eminent', 'Established', 'Exceptional', 'Expert', 'First-class', 'First-rate', 'Impressive', 'Influential', 'Leading', 'Magnetic', 'Managerial', 'Masterful', 'Noble', 'Premier', 'Prestigious', 'Prominent', 'Proud', 'Strong'],
        'Yellow': ['Accelerate', 'Advance', 'Change', 'Conceive', 'Create', 'Engineer', 'Envision', 'Experiment', 'Dream', 'Ignite', 'Illuminate', 'Imagine', 'Innovate', 'Inspire', 'Invent', 'Pioneer', 'Progress', 'Shape', 'Spark', 'Solve', 'Transform', 'Unleash', 'Unlock', 'Advanced', 'Brilliant', 'Conceptual', 'Enterprising', 'Expert', 'Extraordinary', 'Forward-looking', 'Forward-thinking', 'Fresh', 'Future-minded', 'Future-thinking', 'Ingenious', 'Intelligent', 'Inventive', 'Leading-edge', 'Luminous', 'New', 'Pioneering', 'Reforming', 'Rising', 'Transformative', 'Visionary', 'World-changing', 'World-class'],
        'Green': ['Analyze', 'Discover', 'Examine', 'Expand', 'Explore', 'Extend', 'Inquire', 'Journey', 'Launch', 'Move', 'Pioneer', 'Pursue', 'Question', 'Reach', 'Search', 'Uncover', 'Venture', 'Wonder', 'Adventurous', 'Analytical', 'Curious', 'Discerning', 'Experiential', 'Exploratory', 'Fearless', 'Inquisitive', 'Intriguing', 'Investigative', 'Journeying', 'Mysterious', 'Philosophical', 'Pioneering', 'Questioning', 'Unbound', 'Unexpected'],
        'Purple': ['Accommodate', 'Assist', 'Befriend', 'Care', 'Collaborate', 'Connect', 'Embrace', 'Empower', 'Encourage', 'Foster', 'Give', 'Help', 'Nourish', 'Nurture', 'Promote', 'Protect', 'Provide', 'Serve', 'Share', 'Shepherd', 'Steward', 'Tend', 'Uplift', 'Value', 'Welcome', 'Affectionate', 'Attentive', 'Beneficial', 'Benevolent', 'Big-hearted', 'Caring', 'Charitable', 'Compassionate', 'Considerate', 'Encouraging', 'Friendly', 'Generous', 'Gentle', 'Helpful', 'Hospitable', 'Inclusive', 'Kind-hearted', 'Merciful', 'Missional', 'Neighborly', 'Nurturing', 'Protective', 'Responsible', 'Selfless', 'Supportive', 'Sympathetic', 'Thoughtful', 'Uplifting', 'Vocational', 'Warm'],
        'Maroon': ['Accomplish', 'Achieve', 'Build', 'Challenge', 'Commit', 'Compete', 'Contend', 'Dedicate', 'Defend', 'Devote', 'Drive', 'Endeavor', 'Entrust', 'Endure', 'Fight', 'Grapple', 'Grow', 'Improve', 'Increase', 'Overcome', 'Persevere', 'Persist', 'Press on', 'Pursue', 'Resolve', 'Tackle', 'Ambitious', 'Brave', 'Committed', 'Competitive', 'Consistent', 'Constant', 'Continuous', 'Courageous', 'Dedicated', 'Determined', 'Earnest', 'Industrious', 'Loyal', 'Persevering', 'Persistent', 'Proud', 'Purposeful', 'Relentless', 'Reliable', 'Resilient', 'Resolute', 'Steadfast', 'Strong', 'Tenacious', 'Tireless', 'Tough'],
        'Orange': ['Compose', 'Conceptualize', 'Conceive', 'Craft', 'Create', 'Design', 'Dream', 'Envision', 'Express', 'Fashion', 'Form', 'Imagine', 'Interpret', 'Make', 'Originate', 'Paint', 'Perform', 'Portray', 'Realize', 'Shape', 'Abstract', 'Artistic', 'Avant-garde', 'Colorful', 'Conceptual', 'Contemporary', 'Creative', 'Decorative', 'Eccentric', 'Eclectic', 'Evocative', 'Expressive', 'Imaginative', 'Interpretive', 'Offbeat', 'One-of-a-kind', 'Original', 'Uncommon', 'Unconventional', 'Unexpected', 'Unique', 'Vibrant', 'Whimsical'],
        'Pink': ['Arise', 'Aspire', 'Detail', 'Dream', 'Elevate', 'Enchant', 'Enrich', 'Envision', 'Exceed', 'Excel', 'Experience', 'Improve', 'Idealize', 'Imagine', 'Inspire', 'Perfect', 'Poise', 'Polish', 'Prepare', 'Refine', 'Uplift', 'Affectionate', 'Admirable', 'Age-less', 'Beautiful', 'Classic', 'Desirable', 'Detailed', 'Dreamy', 'Elegant', 'Enchanting', 'Enriching', 'Ethereal', 'Excellent', 'Exceptional', 'Experiential', 'Exquisite', 'Glamorous', 'Graceful', 'Idealistic', 'Inspiring', 'Lofty', 'Mysterious', 'Ordered', 'Perfect', 'Poised', 'Polished', 'Pristine', 'Pure', 'Refined', 'Romantic', 'Sophisticated', 'Spiritual', 'Timeless', 'Traditional', 'Virtuous', 'Visionary']
    }

    user_content = st.text_area("Paste or type the text you want to analyze:", height=200)
    if not user_content:
        st.warning("Please enter text to analyze.")
        st.stop()
    
    if st.button("Analyze"):
        st.write("Analyzing the provided text...")
        try:
            top_colors = []
            color_counts = analyze_text(user_content, color_keywords)
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            for color, _ in sorted_colors[:3]:
                top_colors.append(color)

            st.write("Top Colors in the Text:")
            st.write(", ".join(top_colors))

            color_sizes = [color_counts[color] for color in top_colors]
            color_labels = [f"{color} ({count})" for color, count in zip(top_colors, color_sizes)]

            st.write("Creating a pie chart to visualize color distribution...")
            pie_chart = draw_pie_chart(color_labels, color_sizes)
            st.pyplot(pie_chart)

            st.write("Extracting examples of text related to the top colors...")
            color_examples = extract_examples(user_content, color_keywords, top_colors)
            st.write("Examples:")

            for color, examples in color_examples.items():
                st.subheader(f"{color} Examples:")
                for example in examples:
                    st.write(f"- {example}")

            st.write("Generating a PDF report...")
            pdf_data = generate_pdf(user_content, pie_chart, top_colors, color_examples)
            st.success("PDF report generated successfully!")

            download_file(pdf_data)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
