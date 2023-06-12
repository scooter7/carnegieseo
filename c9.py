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

style_guides = ["MLA", "APA", "Chicago", "None"]  # Added "None" option to style guides

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

def generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, placeholders, style_guide):
    if not title:
        return "Error: Title is required."

    messages = [
        {"role": "system", "content": "You are a content creator."},
        {"role": "user", "content": "Generate content."},
        {"role": "assistant", "content": f"Sure! What type of content would you like to generate?"},
        {"role": "user", "content": content_type},
        {"role": "assistant", "content": "Great! Please provide me with some keywords related to the content."},
        {"role": "user", "content": keywords},
        {"role": "assistant", "content": "Alright. Now, let's select the writing styles for the content."},
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
            verb_instruction = f"The content should include {verb}"
            adjective_instruction = f"The content should include {adjective}"
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

    if emulate:
        messages.append({"role": "user", "content": "Emulate the style and grammar of the following content:"})
        messages.append({"role": "assistant", "content": emulate})

    if style_guide == "MLA":
        style_prompt = "generate the content using the MLA style guide so that all grammar and citation rules of that style guide are followed and generated in the output."
    elif style_guide == "APA":
        style_prompt = "generate the content using the APA style guide so that all grammar and citation rules of that style guide are followed and generated in the output."
    elif style_guide == "Chicago":
        style_prompt = "generate the content using the Chicago style guide so that all grammar and citation rules of that style guide are followed and generated in the output."
    elif style_guide == "None":
        style_prompt = "generate the content without following any specific style guide."
    else:
        style_prompt = "generate the content."

    messages.append({"role": "assistant", "content": style_prompt})

    max_tokens = 4096  # Adjusted for token-to-word conversion
    response = None
    for i in range(0, len(messages), 4):
        partial_messages = messages[i:i+4]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=partial_messages,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=0.7,
        )

        if response.choices[0].message.content.endswith("..."):
            break

    result = response.choices[0].message.content.strip()

    return result

# UI layout
st.title("Carnegie Content Creator")

content_type = st.text_input("Define content type:")
keywords = st.text_input("Enter keywords (comma-separated):")
writing_styles = st.multiselect("Select writing styles:", list(placeholders.keys()))
style_weights = st.slider("Set style weights:", min_value=0.0, max_value=1.0, value=[0.5] * len(writing_styles), step=0.1)
audience = st.text_input("Specify target audience (optional):")
institution = st.text_input("Specify institution or organization (optional):")
emulate = st.text_area("Emulate the style and grammar of the following content (optional):")
word_count = st.number_input("Desired word count:", min_value=1, step=1, value=100)
stats_facts = st.text_area("Specific statistics or facts to include (optional):")
title = st.text_input("Enter a title:")
style_guide = st.selectbox("Select a style guide:", style_guides)

if st.button("Generate"):
    if not title:
        st.error("Please enter a title.")
    else:
        result = generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, placeholders, style_guide)
        st.markdown(result)
        st.download_button(
            label="Download content",
            data=result,
            file_name='Content.txt',
            mime='text/txt',
        )
