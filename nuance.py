import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

color_profiles = {
    'Silver': {'key_characteristics': ['rebellious', 'rule-breaking', 'freedom', 'fearless', 'risks'],
               'tone_and_style': ['intriguing', 'expressive', 'focused', 'intentional', 'unbound', 'bold', 'brash'],
               'messaging_tips': ['spectrum', 'independence', 'freedom', 'unconventional', 'bold', 'dangerous', 'empower', 'embolden', 'free', 'fearless']},
    'Purple': {'key_characteristics': ['care', 'encourage', 'safe', 'supported', 'help', 'heal'],
               'tone_and_style': ['warm', 'gentle', 'accessible', 'relatable', 'personable', 'genuine', 'intimate', 'invitational'],
               'messaging_tips': ['personable', 'care', 'compassion', 'friendship', 'deep', 'nurtures', 'protects', 'guides', 'comes alongside']},
    'Pink': {'key_characteristics': ['elegant', 'sophisticated', 'experience', 'excellence', 'beauty', 'vitality'],
             'tone_and_style': ['elevated', 'ethereal', 'thoughtful', 'meaningful', 'aspirational', 'dreamy'],
             'messaging_tips': ['fine details', 'intentionality', 'unique experiences', 'elevated language', 'excellence', 'refinement', 'inspire', 'uplift', 'desired', 'important']},
    'Yellow': {'key_characteristics': ['new concepts', 'experimentation', 'newer', 'better', 'ambiguity', 'unknowns', 'possibilities', 'imagine', 'invent'],
               'tone_and_style': ['eager', 'ambitious', 'bold', 'unafraid', 'bright', 'energetic', 'positive', 'optimistic'],
               'messaging_tips': ['core intention', 'original', 'transformative', 'invention', 'transformation', 'advancement']},
    'Red': {'key_characteristics': ['cheerful', 'upbeat', 'entertain', 'uplift', 'fun', 'amusement', 'energized', 'happy'],
            'tone_and_style': ['energetic', 'passionate', 'optimistic', 'extroverted', 'playful', 'humorous'],
            'messaging_tips': ['upbeat', 'extroverted', 'positive energy', 'light', 'casual', 'invitational', 'surprise', 'unexpected', 'fun', 'energy', 'engaged community']},
    'Orange': {'key_characteristics': ['creative', 'original', 'self-expression', 'artistry', 'new ideas', 'modes of expression'],
               'tone_and_style': ['exuberant', 'vivid', 'colorful', 'unrestrained', 'abstract', 'unconventional', 'interesting constructs', 'sentence structure'],
               'messaging_tips': ['expressive freedom', 'art for art’s sake', 'original', 'creative', 'diversity', 'imagination', 'ideation']},
    'Blue': {'key_characteristics': ['growth', 'industry leader', 'stability', 'pride', 'strength', 'influence', 'accomplishment'],
             'tone_and_style': ['bold', 'confident', 'self-assured', 'proud'],
             'messaging_tips': ['bold', 'confident', 'self-assured', 'proud', 'powerful']}
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
        prompt=f"{color_guide}\n\n{content}\n\nPrimary Color: ",
        temperature=0,
        max_tokens=100,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    primary_color = response.choices[0].text.strip()
    return primary_color, "Supporting colors and rationale will also be obtained from OpenAI"

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
                if content:
                    primary_color, rationale = assess_content(content)
                    results.append({
                        "URL": url,
                        "Primary Color": primary_color,
                        "Supporting Colors and Rationale": rationale
                    })
            
            df = pd.DataFrame(results)
            st.table(df)
            
            colors_df = df["Primary Color"].value_counts().reset_index()
            colors_df.columns = ["Color", "Count"]
            fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
            wedges, texts = ax.pie(colors_df["Count"], wedgeprops=dict(width=0.4), startangle=-40, colors=[color_to_hex.get(color, "#FFFFFF") for color in colors_df["Color"]])
            bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
            kw = dict(arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center")
            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1)/2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                connectionstyle = "angle,angleA=0,angleB={}".format(ang)
                kw["arrowprops"].update({"connectionstyle": connectionstyle})
                ax.annotate(colors_df["Color"].iloc[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                             horizontalalignment=horizontalalignment, **kw)
            st.pyplot(fig)

if __name__ == "__main__":
    main()
