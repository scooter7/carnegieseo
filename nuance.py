import streamlit as st
from collections import Counter
import plotly.graph_objects as go
import re
import io
import base64
import openai

def analyze_text_with_openai(text, openai_api_key):
    openai.api_key = openai_api_key
    response = openai.Completion.create(engine="text-davinci-002", prompt=text, max_tokens=100)
    return response.choices[0].text.strip()

def analyze_text(text, color_profiles):
    color_scores = {}
    for color, profile in color_profiles.items():
        score = 0
        for keyword in profile['key_characteristics']:
            score += text.lower().count(keyword.lower())
        for tip in profile['messaging_tips']:
            score += text.lower().count(tip.lower())
        for tone in profile['tone_and_style']:
            score += text.lower().count(tone.lower())
        color_scores[color] = score
    return color_scores

def draw_donut_chart(color_scores, color_to_hex):
    labels = list(color_scores.keys())
    values = [color_scores[color] for color in labels]
    colors = [color_to_hex[color] for color in labels]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker=dict(colors=colors))])
    return fig

def main():
    st.title('Color Personality Analysis')
    
    if "OPENAI_API_KEY" not in st.secrets:
        st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
        return
    
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    
    user_content = st.text_area('Paste your content here:')
    
    color_profiles = {
        'Silver': {'key_characteristics': ['rebellious', 'rule-breaking', 'freedom', 'fearless', 'risks'], 'tone_and_style': ['intriguing', 'expressive', 'focused', 'intentional', 'unbound', 'bold', 'brash'], 'messaging_tips': ['spectrum', 'independence', 'freedom', 'unconventional', 'bold', 'dangerous', 'empower', 'embolden', 'free', 'fearless']},
        'Purple': {'key_characteristics': ['care', 'encourage', 'safe', 'supported', 'help', 'heal'], 'tone_and_style': ['warm', 'gentle', 'accessible', 'relatable', 'personable', 'genuine', 'intimate', 'invitational'], 'messaging_tips': ['personable', 'care', 'compassion', 'friendship', 'action', 'deep', 'specific', 'real', 'nurture', 'protect', 'guide']},
        'Pink': {'key_characteristics': ['elegant', 'sophisticated', 'experience', 'excellence', 'beauty', 'vitality'], 'tone_and_style': ['elevated', 'ethereal', 'thoughtful', 'meaningful', 'aspirational', 'dreamy'], 'messaging_tips': ['fine details', 'intentionality', 'unique experiences', 'elevated', 'ethereal', 'inspire', 'uplift', 'desired', 'important']},
        'Yellow': {'key_characteristics': ['new concepts', 'experimentation', 'newer', 'better', 'ambiguity', 'unknowns'], 'tone_and_style': ['eager', 'ambitious', 'bold', 'unafraid', 'bright', 'energetic', 'positive', 'optimistic'], 'messaging_tips': ['consistent', 'core intention', 'original', 'transformative', 'invention', 'transformation', 'advancement']},
        'Red': {'key_characteristics': ['cheerful', 'upbeat', 'entertain', 'uplift', 'fun', 'amusement'], 'tone_and_style': ['energetic', 'passionate', 'optimistic', 'extroverted', 'playful', 'humorous'], 'messaging_tips': ['upbeat', 'extroverted', 'positive energy', 'light', 'casual', 'invitational', 'surprise', 'unexpected', 'fun', 'energy', 'engaged community']},
        'Orange': {'key_characteristics': ['creative', 'original', 'self-expression', 'artistry', 'new ideas', 'modes of expression'], 'tone_and_style': ['exuberant', 'vivid', 'colorful', 'unrestrained', 'abstract', 'unconventional', 'interesting constructs', 'sentence structure'], 'messaging_tips': ['bold', 'transparent', 'art for art’s sake', 'original', 'creative', 'personable', 'inclusive', 'diversity']},
        'Blue': {'key_characteristics': ['growth', 'industry leader', 'stability', 'pride', 'strength', 'influence', 'accomplishment'], 'tone_and_style': ['bold', 'confident', 'self-assured', 'proud'], 'messaging_tips': ['bold', 'confident', 'self-assured', 'proud', 'no equivocation', 'words needed', 'powerful', 'not muddled']},
        'Maroon': {'key_characteristics': ['hardworking', 'strong', 'resilient', 'determined', 'overcome', 'obstacles', 'tenacious', 'competitive', 'proving prowess'], 'tone_and_style': ['strong', 'accessible', 'unflinching', 'realistic', 'transparent', 'human', 'toil', 'exertion'], 'messaging_tips': ['determined', 'effort', 'process', 'success', 'realistic', 'tenacious', 'transparent', 'grit', 'overcoming obstacles', 'true to life', 'unflagging', 'resolute', 'honest']},
        'Green': {'key_characteristics': ['exploration', 'new knowledge', 'curiosity', 'progress', 'discontent', 'sit still', 'accept present realities'], 'tone_and_style': ['outgoing', 'energetic', 'unpretentious', 'honest', 'open', 'invitational'], 'messaging_tips': ['specific', 'detailed stories', 'genuine specificity', 'openness', 'learning', 'curiosity', 'questioning', 'adventure', 'immersion', 'never finished', 'constant curiosity']}
    }
    
    color_to_hex = {
        'Silver': '#C0C0C0',
        'Purple': '#800080',
        'Pink': '#FFC0CB',
        'Yellow': '#FFFF00',
        'Red': '#FF0000',
        'Orange': '#FFA500',
        'Blue': '#0000FF',
        'Maroon': '#800000',
        'Green': '#008000'
    }
    
    analyzed_data_from_openai = analyze_text_with_openai(user_content, openai_api_key)
    color_scores = analyze_text(user_content, color_profiles)
    initial_fig = draw_donut_chart(color_scores, color_to_hex)
    st.subheader('Initial Donut Chart')
    st.plotly_chart(initial_fig)
    
    sentences = re.split(r'[.!?]', user_content)
    sentence_to_colors = {}
    
    for sentence in sentences:
        if sentence.strip():
            initial_colors = [color for color, profile in color_profiles.items() if any(keyword.lower() in sentence.lower() for keyword in profile['key_characteristics'])]
            sentence_to_colors[sentence] = initial_colors
    
    updated_color_scores = Counter()
    
    for sentence, initial_colors in sentence_to_colors.items():
        selected_colors = st.multiselect(f"{sentence}.", list(color_profiles.keys()), default=initial_colors)
        for color in selected_colors:
            updated_color_scores[color] += 1
    
    updated_fig = draw_donut_chart(updated_color_scores, color_to_hex)
    st.subheader('Updated Donut Chart')
    st.plotly_chart(updated_fig)
    
    dominant_color = updated_color_scores.most_common(1)[0][0] if updated_color_scores else 'None'
    supporting_colors = [color for color, count in updated_color_scores.items() if color != dominant_color]
    
    st.write(f"The dominant color in the content appears to be {dominant_color}.")
    st.write(f"The supporting colors are {', '.join(supporting_colors)}. They serve to complement the dominant tone by adding layers of complexity to the message.")
        
if __name__ == '__main__':
    main()
