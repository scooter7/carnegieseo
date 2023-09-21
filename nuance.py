import streamlit as st
from collections import Counter
import plotly.graph_objects as go
import re
import io
import base64
import openai

# Initialize session state
if 'updated_color_scores' not in st.session_state:
    st.session_state['updated_color_scores'] = Counter()

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
        st.error("Please set the OPENAI_API_KEY secret.")
        return
    
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    
    user_content = st.text_area('Paste your content here:')
    analyze_button = st.button('Analyze')
    
    if analyze_button or st.session_state['updated_color_scores']:
        color_profiles = {'Silver': {'key_characteristics': ['rebellious', 'rule-breaking', 'freedom', 'fearless', 'risks'], 'tone_and_style': ['intriguing', 'expressive', 'focused', 'intentional', 'unbound', 'bold', 'brash'], 'messaging_tips': ['spectrum', 'independence', 'freedom', 'unconventional', 'bold', 'dangerous', 'empower', 'embolden', 'free', 'fearless']}, 'Purple': {'key_characteristics': ['care', 'encourage', 'safe', 'supported', 'help', 'heal'], 'tone_and_style': ['warm', 'gentle', 'accessible', 'relatable', 'personable', 'genuine', 'intimate', 'invitational'], 'messaging_tips': ['personable', 'care', 'compassion', 'friendship', 'action', 'deep', 'specific', 'real', 'nurture', 'protect', 'guide']}}
        color_to_hex = {'Silver': '#C0C0C0', 'Purple': '#800080'}
        
        color_scores = analyze_text(user_content, color_profiles)
        initial_fig = draw_donut_chart(color_scores, color_to_hex)
        st.subheader('Initial Donut Chart')
        st.plotly_chart(initial_fig)
        
        sentences = re.split(r'[.!?]', user_content)
        sentence_to_colors = {}
        
        for sentence in sentences:
            if sentence.strip():
                sentence_to_colors[sentence] = st.multiselect(f"{sentence}.", list(color_profiles.keys()), default=[])
        
        if analyze_button:
            for sentence, selected_colors in sentence_to_colors.items():
                for color in selected_colors:
                    st.session_state['updated_color_scores'][color] += 1
        
        updated_fig = draw_donut_chart(st.session_state['updated_color_scores'], color_to_hex)
        st.subheader('Updated Donut Chart')
        st.plotly_chart(updated_fig)
        
        dominant_color = st.session_state['updated_color_scores'].most_common(1)[0][0] if st.session_state['updated_color_scores'] else 'None'
        supporting_colors = [color for color, count in st.session_state['updated_color_scores'].items() if color != dominant_color]
        
        if dominant_color != 'None':
            st.write(f"The dominant color in the content appears to be {dominant_color}.")
        else:
            st.write(f"No dominant color could be determined from the content.")
            
        if supporting_colors:
            st.write(f"The supporting colors are {', '.join(supporting_colors)}.")
        else:
            st.write(f"No supporting colors could be determined.")
        
if __name__ == '__main__':
    main()
