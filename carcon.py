import streamlit as st
import re
import plotly.graph_objects as go
from collections import Counter
import base64
from docx import Document
from docx.shared import Inches
import openai
import io
import matplotlib.pyplot as plt

def analyze_text(text, color_keywords):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    color_counts = Counter()
    for color, keywords in color_keywords.items():
        color_counts[color] = sum(words.count(k.lower()) for k in keywords)
    return color_counts

def analyze_sentences_by_color(text, color_keywords):
    text = text.lower()
    sentences = re.split(r'[.!?]', text)
    scored_sentences = []
    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence)
        color_counts = Counter()
        for color, keywords in color_keywords.items():
            color_counts[color] = sum(words.count(k.lower()) for k in keywords)
        most_common_color = color_counts.most_common(1)
        if most_common_color:
            scored_sentences.append((sentence.strip(), most_common_color[0][0]))
    return scored_sentences

def draw_donut_chart(color_counts, color_keywords):
    labels = list(color_keywords.keys())
    sizes = [color_counts.get(color, 0) for color in labels]
    colors = [label.lower() for label in labels]
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.3, marker=dict(colors=colors))])
    return fig

def main():
    if 'OPENAI_API_KEY' not in st.secrets:
        st.error('Please set the OPENAI_API_KEY secret on the Streamlit dashboard.')
        return
    openai_api_key = st.secrets['OPENAI_API_KEY']
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
    
    def analyze_tone(text):
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
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        tone_counts = Counter()
        for tone, keywords in tone_keywords.items():
            tone_counts[tone] = sum(words.count(k.lower()) for k in keywords)
        total_count = sum(tone_counts.values())
        tone_scores = {tone: (count / total_count) * 100 for tone, count in tone_counts.items()}
        return tone_scores

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

    def analyze_with_gpt3(text, api_key):
        openai.api_key = api_key
        prompt = f"Please evaluate the following text and score it based on these tonal definitions: Relaxed, Assertive, Introverted, Extroverted, Conservative, Progressive, Emotive, Informative.\n\nText:\n{text}"
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=50)
        return response.choices[0].text.strip()

    st.title("Content Analysis and Revision Tool")
    
    st.sidebar.title("Instructions")
    st.sidebar.markdown(
        "1. Paste your text in the text box below."
        "\n2. Click the 'Analyze' button to analyze the text and visualize the tone distribution."
        "\n3. To revise the color of a sentence, paste the sentence with the desired color in parentheses and click 'Submit Revision'."
    )

    user_content = st.text_area("Paste your text here:")
    
    if not user_content:
        st.warning("Please paste some text for analysis.")
        return

    st.sidebar.header("Analyze Tone")
    if st.sidebar.button("Analyze"):
        tone_scores = analyze_tone(user_content)
        st.subheader("Tone Analysis")
        for tone, score in tone_scores.items():
            st.write(f"{tone}: {score}%")
    
    st.sidebar.header("Revisions")
    
    if st.sidebar.button("Submit Revision"):
        revision_text = st.sidebar.text_area("Enter the revised sentence:")
        if not revision_text:
            st.warning("Please enter the revised sentence.")
        else:
            user_content = user_content.replace(revision_text.split("(")[0].strip(), revision_text)
            st.text_area("Revised Text:", value=user_content)
            st.success("Revision submitted successfully!")

    st.sidebar.subheader("Color Keywords")
    st.sidebar.write(color_keywords)
    
    color_counts = analyze_text(user_content, color_keywords)
    top_colors = [color for color, count in color_counts.most_common(3)]
    
    st.subheader("Tone Visualization")
    tone_scores = analyze_tone(user_content)
    st.write(tone_scores)
    
    st.subheader("Top Colors in Text")
    st.write(top_colors)
    
    st.subheader("Examples of Top Colors")
    examples = extract_examples(user_content, color_keywords, top_colors)
    for color, color_examples in examples.items():
        st.write(f"**{color}**:")
        for example in color_examples:
            st.write(f"- {example}")

    st.subheader("Donut Chart of Color Distribution")
    fig = draw_donut_chart(color_counts, color_keywords)
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
