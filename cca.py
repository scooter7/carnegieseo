import streamlit as st
import re
from collections import Counter
import base64
from docx import Document
from docx.shared import Inches
import plotly.graph_objects as go
import openai

# Define GPT-3 API key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

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

# Modify the main() function
def main():
    st.title('Color Personality Analysis')
    
    # Check if the API key is set
    if not OPENAI_API_KEY:
        st.error('Please set the OPENAI_API_KEY variable with your OpenAI API key.')
        return

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
    
    user_content = st.text_area('Paste your content here:')
    
    if st.button('Analyze'):
        # Analyze text for color keywords and create donut chart
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
        
        # Extract examples for top colors
        examples = extract_examples(user_content, color_keywords, top_colors)
        for color in top_colors:
            st.write(f'Examples for {color}:')
            st.write(', '.join(examples[color]))
        
        # Analyze tone with GPT-3
        tone_analysis_prompt = 'Assess the text for tone based on the definitions: relaxed (calm, laid-back), assertive (confident, self-assured), introverted (reserved, solitary), and extroverted (sociable, outgoing). Provide scores from 1 to 10 for each trait.'
        tone_analysis_response = analyze_with_gpt3(user_content, tone_analysis_prompt)
        
        if tone_analysis_response:
            # Parse and display GPT-3 analysis of tone
            tone_scores = parse_tone_scores(tone_analysis_response)
            st.write('Tone Analysis:')
            st.write(', '.join(f'{k}: {v}' for k, v in tone_scores.items()))
            
            # Create and display the tone quadrant chart
            fig1 = draw_quadrant_chart(tone_scores, 'Tone Quadrant Chart', ['Relaxed', 'Assertive'], ['Extroverted', 'Introverted'])
            st.plotly_chart(fig1)
        
        # Analyze additional tone with GPT-3
        additional_tone_prompt = 'Assess the text for additional tone based on the definitions: conservative (traditional, resistant to change), progressive (forward-thinking, open to change), emotive (expressing emotion), and informative (providing information). Provide scores from 1 to 10 for each trait.'
        additional_tone_response = analyze_with_gpt3(user_content, additional_tone_prompt)
        
        if additional_tone_response:
            # Parse and display GPT-3 analysis of additional tone
            new_tone_scores = parse_tone_scores(additional_tone_response)
            st.write('Additional Tone Analysis:')
            st.write(', '.join(f'{k}: {v}' for k, v in new_tone_scores.items()))
            
            # Create and display the additional tone quadrant chart
            fig2 = draw_quadrant_chart(new_tone_scores, 'Additional Tone Quadrant Chart', ['Conservative', 'Progressive'], ['Emotive', 'Informative'])
            st.plotly_chart(fig2)
        
        # Generate Word document and provide download link
        general_analysis = 'Your text was analyzed by GPT-3 to determine the following traits based on your tone: ' + ', '.join([f"{k}: {v}" for k, v in {**tone_scores, **new_tone_scores}.items()])
        word_file_path = generate_word_doc(top_colors, examples, user_content, general_analysis, tone_scores, new_tone_scores)
        download_file(word_file_path)

if __name__ == '__main__':
    main()
