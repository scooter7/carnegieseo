import streamlit as st
import openai
from github import Github
import os
import sys
import logging

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]

logging.info(f"OPENAI_API_KEY: {openai_api_key}")

# Set up the GitHub API
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo("scooter7/carnegieseo")

st.title("Carnegie Content Creator")

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

def generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, h1_settings, h2_settings, style_rules):
    messages = [
        {"role": "user", "content": "This will be a " + content_type},
        {"role": "user", "content": "This will be " + content_type + " about " + ", ".join(keywords)},
    ]

    # Modify user messages to include writing styles with weighted percentages
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "user", "content": f"The {content_type} should have the style {style} with a weight of {weight * 100:.1f}%"})

    messages.extend([
        {"role": "user", "content": "The " + content_type + " should have the style " + ", ".join(writing_styles)},
        {"role": "user", "content": "The " + content_type + " should be written to appeal to " + audience},
        {"role": "user", "content": "The " + content_type + " length should be " + str(word_count)},
    ])

    if institution:
        messages.append({"role": "user", "content": "The " + content_type + " include references to the benefits of " + institution})

    if stats_facts:
        messages.append({"role": "user", "content": "The content produced is required to include the following statistics or facts: " + stats_facts})

    if style_rules:
        messages.append({"role": "user", "content": "The style rules are as follows: " + style_rules})

    if emulate:
        emulate_message = {
            "role": "assistant",
            "content": emulate
        }
        messages.append(emulate_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=word_count,
        n=1,  # Generate a single response
        stop=None,  # Stop when max_tokens reached
        temperature=0.7,  # Adjust temperature as needed
    )

    result = ""
    for choice in response.choices:
        result += choice.message.content

    # If the response is incomplete, continue generating until completion
    while response.choices[0].message.content.endswith("..."):
        messages[-1]["content"] = response.choices[0].message.content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=word_count - len(result),
            n=1,
            stop=None,
            temperature=0.7,
        )
        for choice in response.choices:
            result += choice.message.content

    return result


content_type = st.text_input("Define content type:")
keywords = st.text_input("Enter comma-separated keywords:")
writing_styles = st.multiselect("Select writing styles:", list(placeholders.keys()))
style_weights = []
for style in writing_styles:
    weight = st.slider(f"Select weight for {style}:", min_value=1, max_value=10, step=1, value=1)
    style_weights.append(weight)
audience = st.text_input("Audience (optional):")
institution = st.text_input("Institution (optional):")
emulate = st.text_area("Emulate by pasting in up to 3000 words of sample content (optional):", value='', height=200, max_chars=3000)
stats_facts = st.text_area("Enter specific statistics or facts (optional):", value='', height=200, max_chars=3000)
word_count = st.slider("Select word count:", min_value=100, max_value=1000, step=50, value=100)
title = st.text_input("Enter the title:")
style_rules = st.text_area("Enter style rules (optional):", value='', height=200, max_chars=3000)

if st.button("Generate"):
    result = generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, style_rules)
    st.markdown(result)
    st.download_button(
        label="Download content",
        data=result,
        file_name='Content.txt',
        mime='text/txt',
    )
