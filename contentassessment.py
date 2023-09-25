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
    'Blue': {'key_characteristics': ['growth', 'industry leader', 'stability', 'pride', 'strength', 'influence', 'accomplishment'], 'tone_and_style': ['bold', 'confident', 'self-assured', 'proud'], 'messaging_tips': ['bold', 'confident', 'self-assured', 'proud', 'powerful']},
    'Green': {'key_characteristics': ['Motivated by exploration and new knowledge', 'Driven by curiosity and the desire for progress', 'Discontent to sit still and accept present realities', 'Beckoning others to join the journey'], 'tone_and_style': ['Outgoing and energetic', 'Unpretentious', 'Honest, open, and invitational', 'Font and image treatment that suggests movement and that there is “more to see” beyond the page'], 'messaging_tips': ['Green is becoming a very popular brand expression in certain regions and markets. No longer can you limit Green expression to a plug-and-play of verbs and adjectives. Rather, Green messaging must be specific to the institution’s brand story. Tell of how and in what ways Green is uniquely encountered at the institution. Avoid being general by telling detailed stories.', 'Strive to move beyond cliché evidences offered by almost every institution into more genuine specificity. Green is not just a study abroad program, internships, or contextual education. These evidences may be a part of an institution’s Green identity, but they should always be framed in a broader narrative of continual openness and learning, curiosity and questioning, adventure and immersion.', 'Green is never finished. It’s driven by the seeking, questioning, and adventure and not by the destination or answer. Green is the state of constant curiosity. Promote this environment of ongoing inquiry and boundless opportunity.']},
    'Maroon': {'key_characteristics': ['Extremely hardworking', 'Strong, resilient, and determined to overcome, despite obstacles', 'Tenacious in their resolve to deliver', 'Highly competitive and intent on proving prowess'], 'tone_and_style': ['Strong but fully accessible', 'Unflinching in face of challenge', 'Realistic and transparent', 'Should feel human in its toil and exertion'], 'messaging_tips': ['Maroon messaging is immensely determined—leaning into the effort and process that lead to success. When messaging Maroon, tell the story of how you are dedicated to the end goal, whatever that may be.', 'Maroon is unapologetically realistic, tenacious, and transparent, telling stories of grit and overcoming obstacles.', 'Maroon messaging need not feel or sound sanitized. Use a variety of sentence lengths. Include language and stories that show you are true to life and unflagging. Maroon copy is resolute but honest, perhaps the most human of all archetypes.']}
}

color_to_hex = {
    'Silver': '#C0C0C0',
    'Purple': '#800080',
    'Pink': '#FFC0CB',
    'Yellow': '#FFFF00',
    'Red': '#FF0000',
    'Orange': '#FFA500',
    'Blue': '#0000FF',
    'Green': '#008000',
    'Maroon': '#800000'
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
        prompt=f"Carefully analyze the content provided and compare it with the detailed color guide below. Evaluate the content against each color’s key characteristics, tone & style, and messaging tips to determine the most fitting primary color and any supporting colors.\\n\\nContent:\\n{content}\\n\\nColor Guide:\\n{color_guide}\\n\\nBased on a detailed comparison of the content and every color profile in the color guide, identify the most aligned primary color and any supporting colors. Provide a thorough rationale explaining why each color was chosen, taking into account the key characteristics, tone & style, and messaging tips of each color before assigning the color values. Cite specific examples of the content analyzed when presenting your rationale for the color assignments.",
        temperature=0.5,
        max_tokens=400,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    output_text = response.choices[0].text.strip()
    primary_color = "Beige"
    supporting_colors = "Beige"
    rationale = "Not Provided"
    
    mentioned_colors = [color for color in color_profiles.keys() if color.lower() in output_text.lower()]

    if mentioned_colors:
        primary_color = mentioned_colors[0]
        if len(mentioned_colors) > 1:
            supporting_colors = ', '.join(mentioned_colors[1:])
    
    lines = output_text.split('\\n')
    if lines:
        rationale_line_start = 2 if "Supporting Colors:" in output_text else 1
        rationale = "\\n".join(lines[rationale_line_start:]).strip() if len(lines) > rationale_line_start else "Not Provided"

    return primary_color, supporting_colors, rationale

def main():
    st.title("Webpage Content Color Assessor")
    urls_input = st.text_area("Enter up to 20 URLs (separated by commas):")
    urls = [url.strip() for url in urls_input.split(",") if url.strip()]

    if st.button("Assess Content Colors"):
        if not urls or len(urls) > 20:
            st.error("Please enter up to 20 valid URLs.")
        else:
            color_count = {}
            for url in urls:
                content = scrape_text(url)
                primary_color, supporting_colors, rationale = assess_content(content)
                st.write(f"**URL:** {url}")
                st.write(f"**Primary Color:** {primary_color.split()[0] if ' ' in primary_color else primary_color}")
                st.write(f"**Supporting Colors:** {', '.join(supporting_colors.split()) if ' ' in supporting_colors else supporting_colors}")
                st.write(f"**Rationale:** {rationale}")
                st.write("---")
                color_count[primary_color] = color_count.get(primary_color, 0) + 1

            color_count_df = pd.DataFrame(list(color_count.items()), columns=['Color', 'Count'])
            fig = px.pie(color_count_df, names='Color', values='Count', color='Color', color_discrete_map=color_to_hex, hole=0.4, width=800, height=400)
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
