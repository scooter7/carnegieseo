import streamlit as st
import openai
import sys
import logging
import random

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]

logging.info(f"OPENAI_API_KEY: {openai_api_key}")

st.title("Carnegie Content Creator")

style_guides = ["None", "MLA", "APA", "Chicago"]  # List of available style guides

placeholders = {
    "Purple - caring, encouraging": {
        "verbs": ["care", "encourage"],
        "adjectives": ["caring", "encouraging"],
    },
    "Green - adventurous, curious": {
        "verbs": ["explore", "discover"],
        "adjectives": ["adventurous", "curious"],
    },
    "Maroon - gritty, determined": {
        "verbs": ["persevere", "strive"],
        "adjectives": ["gritty", "determined"],
    },
    "Orange - artistic, creative": {
        "verbs": ["create", "express"],
        "adjectives": ["artistic", "creative"],
    },
    "Yellow - innovative, intelligent": {
        "verbs": ["innovate", "intellect"],
        "adjectives": ["innovative", "intelligent"],
    },
    "Red - entertaining, humorous": {
        "verbs": ["entertain", "amuse"],
        "adjectives": ["entertaining", "humorous"],
    },
    "Blue - confident, influential": {
        "verbs": ["inspire", "influence"],
        "adjectives": ["confident", "influential"],
    },
    "Pink - charming, elegant": {
        "verbs": ["charm", "grace"],
        "adjectives": ["charming", "elegant"],
    },
    "Silver - rebellious, daring": {
        "verbs": ["rebel", "dare"],
        "adjectives": ["rebellious", "daring"],
    },
    "Beige - dedicated, humble": {
        "verbs": ["dedicate", "humble"],
        "adjectives": ["dedicated", "humble"],
    },
    # Add more color and adjective placeholders as needed
}

def generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate_text, word_count, stats_facts, title, placeholders, style_guide, include_h1, include_subheadings):
    if not title:
        return "Error: Title is required."

    messages = [
        {"role": "system", "content": "You are a content creator."},
        {"role": "user", "content": "Generate SEO-optimized content."},
        {"role": "assistant", "content": f"Sure! What type of content would you like to generate?"},
        {"role": "user", "content": content_type},
        {"role": "assistant", "content": "Great! Please provide me with some keywords related to the content."},
        {"role": "user", "content": keywords},
        {"role": "assistant", "content": "Alright. Now, let's select the writing styles for the content."},
        {"role": "user", "content": f"H1 should be included: {include_h1}"},
        {"role": "user", "content": f"Subheadings should be included: {include_subheadings}"},
    ]

    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "assistant", "content": f"The content should have {style} style with a weight of {weight * 100:.1f}%"})

        # Include placeholder verbs and adjectives in user instructions
        if style in placeholders:
            style_verbs = placeholders[style]["verbs"]
            style_adjectives = placeholders[style]["adjectives"]
            verb = random.choice(style_verbs)
            adjective = random.choice(style_adjectives)
            verb_instruction = f"The content must include {verb}"
            adjective_instruction = f"The content must include {adjective}"
            messages.append({"role": "user", "content": verb_instruction})
            messages.append({"role": "user", "content": adjective_instruction})

    messages.extend([
        {"role": "assistant", "content": f"The content should have {', '.join(writing_styles)} styles"},
        {"role": "assistant", "content": "Please specify the target audience for the content (optional)."},
        {"role": "user", "content": audience},
        {"role": "assistant", "content": "Do you want the content to include references to any specific institution or organization? If yes, please provide the name; otherwise, you can skip this step."},
        {"role": "user", "content": institution},
        {"role": "assistant", "content": "Please provide any specific statistics or facts that you would like to include in the content (optional)."},
        {"role": "user", "content": stats_facts},
        {"role": "assistant", "content": "Lastly, let me know the desired word count for the content."},
        {"role": "user", "content": str(word_count)},
        {"role": "assistant", "content": "Lastly, could you please provide a title for the content?"},
        {"role": "user", "content": title},
        {"role": "assistant", "content": "Alright, generating the content..."},
    ])

with st.beta_container():
    content_type = st.selectbox("Content Type", ["Blog post", "Article", "News report", "Product description"])
    keywords = st.text_input("Keywords (comma-separated)")
    writing_styles = st.multiselect("Writing Styles", ["Purple - caring, encouraging", "Green - adventurous, curious", "Maroon - gritty, determined", "Orange - artistic, creative", "Yellow - innovative, intelligent", "Red - entertaining, humorous", "Blue - confident, influential", "Pink - charming, elegant", "Silver - rebellious, daring", "Beige - dedicated, humble"])
    style_weights = st.slider("Style Weights", min_value=0.0, max_value=1.0, value=(0.5, 0.5), step=0.1)
    audience = st.text_input("Target Audience")
    institution = st.text_input("Institution/Organization")
    emulate_text = st.text_input("Emulate Text (optional)")
    word_count = st.number_input("Word Count", min_value=1, step=1)
    stats_facts = st.text_area("Statistics/Facts (optional)")
    title = st.text_input("Title")
    style_guide = st.selectbox("Style Guide", style_guides)
    include_h1 = st.checkbox("Include H1")
    include_subheadings = st.checkbox("Include Subheadings")

    if st.button("Generate"):
        if not title:
            st.error("Please enter a title.")
        else:
            result = generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate_text, word_count, stats_facts, title, placeholders, style_guide, include_h1, include_subheadings)
            st.markdown(result)
            st.download_button(
                label="Download content",
                data=result,
                file_name='Content.txt',
                mime='text/txt',
            )