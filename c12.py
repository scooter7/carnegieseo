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

def generate_article (content_type, keywords, writing_styles, style_weights, audience, institution, emulate_text, word_count, stats_facts, title, placeholders, style_guide, include_h1, include_subheadings):
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

    if emulate_text:
        grammar_analysis = openai.Completion.create(
            engine="text-davinci-003",
            prompt=emulate_text,
            max_tokens=1,
            temperature=0,
            n=1,
            stop=None,
        )
        # Extract the grammar and style analysis result
        grammar_result = grammar_analysis.choices[0].text.strip()

        # Include the grammar and style analysis result in the assistant's messages
        messages.append({"role": "assistant", "content": grammar_result})
    else:
        grammar_result = ""  # Add this line to assign an empty string if emulate_text is not provided

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=word_count,
        n=1,  # Generate a single response
        stop=None,  # Stop when max_tokens reached
        temperature=0.7,  # Adjust temperature as needed
    )

    result = response.choices[0].message.content

    # If the response is incomplete, continue generating until completion
    while response.choices[0].message.content.endswith("..."):
        messages[-1]["content"] = response.choices[0].message.content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=word_count * 10 - len(result),  # Adjusted to account for token-to-word conversion
            n=1,
            stop=None,
            temperature=0.7,
        )
        result += response.choices[0].message.content

    result = f"# {title}\n\n{result}"  # Prepend title to result

    return result

content_type = st.selectbox("Content Type", ["College Academic Program Webpage", "Thought leadership Content Webpage", "College Admissions Webpage"])
keywords = st.text_input("Enter comma-separated keywords:")
writing_styles = st.multiselect("Select writing styles:", list(placeholders.keys()))
style_weights = []
for style in writing_styles:
    weight = st.slider(f"Select weight for {style}:", min_value=1, max_value=10, step=1, value=1)
    style_weights.append(weight)
audience = st.text_input("Audience (optional):")
institution = st.text_input("Institution (optional):")
emulate_text = st.text_area("Emulate by pasting in up to 3000 words of sample content (optional):")
word_count = st.number_input("Desired word count:", min_value=1, value=500)
stats_facts = st.text_area("Statistics or facts to include (optional):")
title = st.text_input("Title:")
style_guide = st.selectbox("Select style guide:", style_guides, index=0)  # Set "None" as the default option
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
