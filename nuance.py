import streamlit as st
from collections import Counter
import plotly.graph_objects as go
import re
import io
import base64
import openai

if 'updated_color_scores' not in st.session_state:
    st.session_state['updated_color_scores'] = Counter()

def analyze_text(text, color_profiles):
    color_scores = Counter()
    for color, profile in color_profiles.items():
        for characteristic in profile['key_characteristics']:
            color_scores[color] += text.lower().count(characteristic.lower())
        for tip in profile['messaging_tips']:
            color_scores[color] += text.lower().count(tip.lower())
        for tone in profile['tone_and_style']:
            color_scores[color] += text.lower().count(tone.lower())
    return color_scores

def draw_donut_chart(color_scores, color_to_hex):
    labels = list(color_scores.keys())
    values = [color_scores[color] for color in labels]
    colors = [color_to_hex[color] for color in labels]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker=dict(colors=colors))])
    return fig

def main():
    st.title('Color Personality Analysis')
    
    color_profiles = {
        'Silver': {'key_characteristics': ['rebellious', 'rule-breaking', 'freedom', 'fearless', 'risks'], 'tone_and_style': ['intriguing', 'expressive', 'focused', 'intentional', 'unbound', 'bold', 'brash'], 'messaging_tips': ['spectrum', 'independence', 'freedom', 'unconventional', 'bold', 'dangerous', 'empower', 'embolden', 'free', 'fearless']},
        'Purple': {'key_characteristics': ['care', 'encourage', 'safe', 'supported', 'help', 'heal'], 'tone_and_style': ['warm', 'gentle', 'accessible', 'relatable', 'personable', 'genuine', 'intimate', 'invitational'], 'messaging_tips': ['personable', 'care', 'compassion', 'friendship', 'deep', 'nurtures', 'protects', 'guides', 'comes alongside']},
        'Pink': {'key_characteristics': ['elegant', 'sophisticated', 'experience', 'excellence', 'beauty', 'vitality'], 'tone_and_style': ['elevated', 'ethereal', 'thoughtful', 'meaningful', 'aspirational', 'dreamy'], 'messaging_tips': ['fine details', 'intentionality', 'unique experiences', 'elevated language', 'excellence', 'refinement', 'inspire', 'uplift', 'desired', 'important']},
        'Yellow': {'key_characteristics': ['new concepts', 'experimentation', 'newer', 'better', 'ambiguity', 'unknowns', 'possibilities', 'imagine', 'invent'], 'tone_and_style': ['eager', 'ambitious', 'bold', 'unafraid', 'bright', 'energetic', 'positive', 'optimistic'], 'messaging_tips': ['core intention', 'original', 'transformative', 'invention', 'transformation', 'advancement']},
        'Red': {'key_characteristics': ['cheerful', 'upbeat', 'entertain', 'uplift', 'fun', 'amusement', 'energized', 'happy'], 'tone_and_style': ['energetic', 'passionate', 'optimistic', 'extroverted', 'playful', 'humorous'], 'messaging_tips': ['upbeat', 'extroverted', 'positive energy', 'light', 'casual', 'invitational', 'surprise', 'unexpected', 'fun', 'energy', 'engaged community']},
        'Orange': {'key_characteristics': ['creative', 'original', 'self-expression', 'artistry', 'new ideas', 'modes of expression'], 'tone_and_style': ['exuberant', 'vivid', 'colorful', 'unrestrained', 'abstract', 'unconventional', 'interesting constructs', 'sentence structure'], 'messaging_tips': ['expressive freedom', 'art for art’s sake', 'original', 'creative', 'diversity', 'imagination', 'ideation']},
        'Blue': {'key_characteristics': ['growth', 'industry leader', 'stability', 'pride', 'strength', 'influence', 'accomplishment'], 'tone_and_style': ['bold', 'confident', 'self-assured', 'proud'], 'messaging_tips': ['bold', 'confident', 'self-assured', 'proud', 'powerful']}
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
    
    user_content = st.text_area('Paste your content here:')
    analyze_button = st.button('Analyze')
    
    if analyze_button or st.session_state['updated_color_scores']:
        color_scores = analyze_text(user_content, color_profiles)
        initial_fig = draw_donut_chart(color_scores, color_to_hex)
        st.subheader('Initial Donut Chart')
        st.plotly_chart(initial_fig)
        
        sentences = re.split(r'[.!?]', user_content)
        sentence_to_colors = {}
        
        for sentence in sentences:
            if sentence.strip():
                sentence_to_colors[sentence] = st.multiselect(f"{sentence}.", list(color_profiles.keys()), key=sentence)
        
        for sentence, selected_colors in sentence_to_colors.items():
            for color in selected_colors:
                st.session_state['updated_color_scores'][color] += 1
        
        if st.session_state['updated_color_scores']:
            updated_fig = draw_donut_chart(st.session_state['updated_color_scores'], color_to_hex)
            st.subheader('Updated Donut Chart')
            st.plotly_chart(updated_fig)
        
        dominant_color = st.session_state['updated_color_scores'].most_common(1)[0][0] if st.session_state['updated_color_scores'] else None
        supporting_colors = [color for color, count in st.session_state['updated_color_scores'].items() if color != dominant_color]
        
        if dominant_color:
            st.write(f"The dominant color in the content appears to be {dominant_color}.")
        else:
            st.write(f"No dominant color could be determined from the content.")
            
        if supporting_colors:
            st.write(f"The supporting colors are {', '.join(supporting_colors)}. They serve to complement the dominant color by adding layers of complexity to the message.")
        else:
            st.write(f"No supporting colors could be determined.")
        
if __name__ == '__main__':
    main()