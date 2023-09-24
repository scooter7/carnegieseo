import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import pandas as pd
import plotly.express as px

def extract_color_name(description: str) -> str:
    words = description.split()
    color_name = words[-1] if words else ""
    return color_name.rstrip(".")

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
        prompt=f"Carefully analyze the content provided and compare it with the detailed color guide below. Evaluate the content against each color’s key characteristics, tone & style, and messaging tips to determine the most fitting primary color and any supporting colors.\n\nContent:\n{content}\n\nColor Guide:\n{color_guide}\n\nBased on a detailed comparison of the content and every color profile in the color guide, identify the most aligned primary color and any supporting colors. Provide a thorough rationale explaining why each color was chosen, taking into account the key characteristics, tone & style, and messaging tips of each color before assigning the color values. Cite specific examples of the content analyzed when presenting your rationale for the color assignments.",
        temperature=0.5,
        max_tokens=400,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    output_text = response.choices[0].text.strip()
    primary_color = extract_color_name(primary_color_descriptive)
    supporting_colors = "Not Identified"
    rationale = "Not Provided"
    
    lines = output_text.split('\n')
    if lines:
        primary_color_line = lines[0].strip()
        primary_color = extract_color_name(primary_color_descriptive)
        if len(lines) > 1:
            supporting_colors_line = lines[1].strip()
            supporting_colors = supporting_colors_line.split(":")[1].strip() if ":" in supporting_colors_line else supporting_colors_line
            rationale = "\n".join(lines[2:]).strip() if len(lines) > 2 else "Not Provided"

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
                st.write(f"**Primary Color:** {primary_color}")
                if supporting_colors != "Not Identified":
                    st.write(f"**Supporting Colors:** {supporting_colors}")
                st.write(f"**Rationale:** {rationale if rationale != 'Not Provided' else 'No rationale provided.'}")
                st.write("---")
                color_names = list(color_profiles.keys())
                new_primary_color = extract_color_name(primary_color_descriptive)
                new_supporting_colors = st.multiselect("Reassign Supporting Colors (if needed):", list(color_profiles.keys()), default=[supporting_color for supporting_color in ([supporting_colors] if isinstance(supporting_colors, str) else supporting_colors) if supporting_color in color_profiles.keys()] if supporting_colors != "Not Identified" else [])
                new_rationale = st.text_area(f"Update Rationale for {url} (if needed):", value=rationale)
                if new_primary_color != primary_color or set(new_supporting_colors) != set([supporting_colors]) or new_rationale != rationale:
                    st.write("**Updated Assignments for this URL:**")
                    st.write(f"**Primary Color:** {new_primary_color}")
                    if new_supporting_colors:
                        st.write(f"**Supporting Colors:** {', '.join(new_supporting_colors)}")
                    st.write(f"**Rationale:** {new_rationale if new_rationale else 'No rationale provided.'}")
                    color_count[extract_color_name(new_primary_color)] = color_count.get(extract_color_name(new_primary_color), 0) + 1
                    color_count[extract_color_name(primary_color)] -= 1

                color_count[extract_color_name(primary_color)] = color_count.get(extract_color_name(primary_color), 0) + 1

            color_count_df = pd.DataFrame(list(color_count.items()), columns=['Color', 'Count'])
            
            color_count = {k: v for k, v in color_count.items() if v > 0}
            color_count_df = pd.DataFrame(list(color_count.items()), columns=['Color', 'Count'])
            fig = px.pie(color_count_df, names='Color', values='Count', color='Color', color_discrete_map=color_to_hex, hole=0.4, width=900, height=500)
            fig.update_traces(textinfo='none')  # Removing percentage labels
            fig.update_layout(showlegend=True, legend_title_text='')  # Showing only color names in the legend
            st.plotly_chart(fig)

            doc = Document()
            doc.add_heading('Webpage Content Color Assessor Analysis', level=1)
            
            for url in urls:
                content = scrape_text(url)
                primary_color, supporting_colors, rationale = assess_content(content)
                doc.add_heading(f'URL: {url}', level=2)
                doc.add_paragraph(f'Primary Color: {primary_color}')
                if supporting_colors != "Not Identified":
                    doc.add_paragraph(f'Supporting Colors: {supporting_colors}')
                doc.add_paragraph(f'Rationale: {rationale if rationale != 'Not Provided' else 'No rationale provided.'}')
                doc.add_paragraph('---')
            
            stream = BytesIO()
            doc.save(stream)
            
            b64 = base64.b64encode(stream.getvalue()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="analysis.docx">Download Analysis as Word Document</a>'
            st.markdown(href, unsafe_allow_html=True)



if __name__ == "__main__":
    main()
