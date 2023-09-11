import streamlit as st
import re
import plotly.graph_objects as go
from collections import Counter
from docx import Document
from docx.shared import Inches
import io
import matplotlib.pyplot as plt
import base64

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def draw_donut_chart(color_counts, color_keywords):
    labels = list(color_keywords.keys())
    sizes = [color_counts.get(color, 0) for color in labels]
    colors = {label: label.lower() for label in labels}
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, marker=dict(colors=[colors[label] for label in labels]))])
    return fig

def plot_tone_analysis(tone_scores):
    fig, ax = plt.subplots()
    ax.bar(tone_scores.keys(), tone_scores.values())
    plt.xticks(rotation=45)
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf

def get_word_file_download_link(file_path, filename):
    with open(file_path, "rb") as f:
        file_data = f.read()
    b64_file = base64.b64encode(file_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{b64_file}" download="{filename}">Download Word Report</a>'
    return href

def generate_word_doc(color_counts, user_content, tone_scores, color_keywords):
    doc = Document()
    doc.add_heading('Color Personality Analysis', 0)
    fig = draw_donut_chart(color_counts, color_keywords)
    image_stream = io.BytesIO(fig.to_image(format="png"))
    doc.add_picture(image_stream, width=Inches(4.0))
    image_stream.close()
    tone_buf = plot_tone_analysis(tone_scores)
    doc.add_picture(tone_buf, width=Inches(4.0))
    tone_buf.close()
    doc.add_heading('Original Text:', level=1)
    doc.add_paragraph(user_content)
    word_file_path = "Color_Personality_Analysis_Report.docx"
    doc.save(word_file_path)
    return word_file_path

@st.cache(allow_output_mutation=True)
def main():
    st.title('Color Personality Analysis')
    
    if 'user_content' not in st.session_state:
        st.session_state.user_content = ""
    
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
    
    tone_keywords = {
        "Relaxed": ["calm", "peaceful", "easygoing", "informal"],
        "Assertive": ["confident", "aggressive", "self-assured", "dogmatic"],
        "Introverted": ["calm", "solitude", "introspective", "reserved"],
        "Extroverted": ["social", "energetic", "outgoing"],
        "Conservative": ["traditional", "status quo", "orthodox"],
        "Progressive": ["reform", "liberal", "innovative"],
        "Emotive": ["emotional", "passionate", "intense"],
        "Informative": ["inform", "disclose", "instructive"]
    }

    user_content = st.text_area('Paste your content here:', value=st.session_state.user_content)
    st.session_state.user_content = user_content

    if st.button('Analyze'):
        color_counts = analyze_text(user_content, color_keywords)
        fig = draw_donut_chart(color_counts, color_keywords)
        st.plotly_chart(fig)
        
        tone_scores = analyze_text(user_content, tone_keywords)
        tone_buf = plot_tone_analysis(tone_scores)
        st.image(tone_buf, caption='Tone Analysis', use_column_width=True)
        
        word_file_path = generate_word_doc(color_counts, user_content, tone_scores, color_keywords)
        download_link = get_word_file_download_link(word_file_path, "Color_Personality_Analysis_Report.docx")
        st.markdown(download_link, unsafe_allow_html=True)
        
        # Sentence Color Scoring
        sentences = re.split(r'[.!?]', user_content)
        st.subheader("Sentence Color Scoring")
        for sentence in sentences:
            if sentence.strip():
                sentence_color_counts = analyze_text(sentence, color_keywords)
                max_color = max(sentence_color_counts, key=sentence_color_counts.get, default="None")
                st.write(f"{sentence.strip()} ({max_color})")
                
        # Revision Section
        st.subheader("Revision Field")
        revision_input = st.text_area("Paste a sentence here for revision:")
        revised_color = st.selectbox("Select the revised color:", list(color_keywords.keys()))
        
        if st.button("Apply Revision"):
            if revision_input:
                pattern = re.escape(revision_input.strip()) + r'\s*\((\w+)\)'
                match = re.search(pattern, st.session_state.user_content)
                if match:
                    old_color = match.group(1)
                    revised_sentence = f"{revision_input.strip()} ({revised_color})"
                    st.session_state.user_content = re.sub(pattern, revised_sentence, st.session_state.user_content)
                    st.success(f"Sentence revised from '{old_color}' to '{revised_color}'.")
                    
                    # Recompute color counts and update the donut chart
                    color_counts = analyze_text(st.session_state.user_content, color_keywords)
                    fig = draw_donut_chart(color_counts, color_keywords)
                    st.plotly_chart(fig)
                    
                    # Recompute sentence color scores and display them
                    sentences = re.split(r'[.!?]', st.session_state.user_content)
                    st.subheader("Sentence Color Scoring")
                    for sentence in sentences:
                        if sentence.strip():
                            sentence_color_counts = analyze_text(sentence, color_keywords)
                            max_color = max(sentence_color_counts, key=sentence_color_counts.get, default="None")
                            st.write(f"{sentence.strip()} ({max_color})")

if __name__ == '__main__':
    main()
