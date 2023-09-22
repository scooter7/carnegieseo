import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import pandas as pd
import plotly.express as px

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

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
else:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    openai.api_key = openai_api_key

def scrape_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = " ".join([para.text for para in paragraphs])
    return text

def assess_content(content):
    color_guide = ""
    for color, attributes in color_profiles.items():
        color_guide += f"{color}:\n"
        for attribute, values in attributes.items():
            color_guide += f"  {attribute}: {' '.join(values)}\n"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"{color_guide}\n\n{content}\n\nBased on the content and the color guide above, identify the primary color and the supporting colors, and provide a detailed rationale for the choices made.",
        temperature=0.5,
        max_tokens=300,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    output_text = response.choices[0].text.strip()
    primary_color = "Not Identified"
    supporting_colors = "Not Identified"
    rationale = "Not Provided"
    
    lines = output_text.split('\n')
    if lines:
        primary_color = lines[0].strip()
        if len(lines) > 1:
            supporting_line = lines[1].strip()
            if "Supporting Colors:" in supporting_line:
                supporting_colors = ", ".join([word for word in supporting_line.replace("Supporting Colors:", "").strip().split() if word in color_profiles.keys()])
                rationale = "\n".join(lines[2:]).strip() if len(lines) > 2 else "Not Provided"
            else:
                rationale = "\n".join(lines[1:]).strip()
                
    return primary_color, supporting_colors, rationale

def main():
    st.title("Webpage Content Color Assessor")
    urls_input = st.text_area("Enter up to 20 URLs (separated by commas):")
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]

    if st.button("Assess Content Colors"):
        if not urls or len(urls) > 20:
            st.error("Please enter up to 20 valid URLs.")
        else:
            results = []
            for url in urls:
                content = scrape_text(url)
                primary_color, supporting_colors, rationale = assess_content(content)
                results.append({
                    "URL": url,
                    "Primary Color": primary_color,
                    "Supporting Colors": supporting_colors,
                    "Rationale": rationale
                })

            df = pd.DataFrame(results)
            st.table(df)

            colors_df = df["Primary Color"].value_counts().reset_index()
            colors_df.columns = ["Color", "Count"]
            fig = px.pie(colors_df, names='Color', values='Count', color='Color', color_discrete_map=color_to_hex, hole=0.4, width=800, height=400)
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
