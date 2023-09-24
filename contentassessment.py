import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import pandas as pd
import plotly.express as px
from docx import Document

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
    'Blue': '#0000FF'
}

def create_word_document(urls_analysis):
    document = Document()
    document.add_heading('Webpage Content Color Assessor Analysis', level=1)
    for url, analysis in urls_analysis.items():
        document.add_heading(f'URL: {url}', level=2)
        document.add_heading('Primary Color:', level=3)
        document.add_paragraph(analysis['primary_color'])
        document.add_heading('Supporting Colors:', level=3)
        document.add_paragraph(', '.join(analysis['supporting_colors']))
        document.add_heading('Rationale:', level=3)
        document.add_paragraph(analysis['rationale'])
    file_path = "/mnt/data/analysis.docx"
    document.save(file_path)
    return file_path

def main():
    st.title("Webpage Content Color Assessor")
    urls_input = st.text_area("Enter up to 20 URLs (separated by commas):")
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]

    if st.button("Assess Content Colors"):
        if not urls or len(urls) > 20:
            st.error("Please enter up to 20 valid URLs.")
        else:
            urls_analysis = {}
            color_count = {}
            for url in urls:
                content = scrape_text(url)
                primary_color, supporting_colors, rationale = assess_content(content)
                st.write(f"**URL:** {url}")
                st.write(f"**Primary Color:** {primary_color}")
                st.write(f"**Supporting Colors:** {supporting_colors if supporting_colors != 'Not Identified' else ''}")
                st.write(f"**Rationale:** {rationale}")
                
                reassign_primary = st.selectbox(f'Reassign Primary Color for {url}', list(color_profiles.keys()), key=f'primary_{url}')
                reassign_supporting = st.multiselect(f'Reassign Supporting Colors for {url}', list(color_profiles.keys()), key=f'supporting_{url}')
                retype_rationale = st.text_area(f'Retype Rationale for {url}', value=rationale, key=f'rationale_{url}')
                
                if st.button('Update Analysis', key=f'update_{url}'):
                    primary_color = reassign_primary
                    supporting_colors = ', '.join(reassign_supporting)
                    rationale = retype_rationale
                    st.write(f"Updated Primary Color for {url}: {primary_color}")
                    st.write(f"Updated Supporting Colors for {url}: {supporting_colors}")
                    st.write(f"Updated Rationale for {url}: {rationale}")
                    st.write("---")
                
                urls_analysis[url] = {
                    'primary_color': primary_color,
                    'supporting_colors': supporting_colors.split(', '),
                    'rationale': rationale
                }
                color_count[primary_color] = color_count.get(primary_color, 0) + 1

            color_count_df = pd.DataFrame(list(color_count.items()), columns=['Color', 'Count'])
            fig = px.pie(color_count_df, names='Color', values='Count', color='Color', color_discrete_map=color_to_hex, hole=0.4, width=1000, height=500)
            st.plotly_chart(fig)
            
            if st.button('Download Analysis'):
                file_path = create_word_document(urls_analysis)
                st.markdown(f'[Download Analysis]({file_path})')

if __name__ == "__main__":
    main()
