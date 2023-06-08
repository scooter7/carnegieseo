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

def generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, style_rules):
    if not title:
        return "Error: Title is required."

    messages = [
        {"role": "user", "content": "This will be a " + content_type},
        {"role": "user", "content": "This will be " + content_type + " about " + ", ".join(keywords)},
    ]

    # Modify user messages to include writing styles with weighted percentages
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "user", "content": f"The {content_type} should have {style} style with a weight of {weight * 100:.1f}%"})

    messages.extend([
        {"role": "user", "content": f"The {content_type} should have {', '.join(writing_styles)} styles"},
        {"role": "user", "content": f"The {content_type} should be written to appeal to {audience}"},
        {"role": "user", "content": f"The {content_type} length should be {word_count} words"},
    ])

    if institution:
        messages.append({"role": "user", "content": f"The {content_type} should include references to the benefits of {institution}"})

    if stats_facts:
        messages.append({"role": "user", "content": f"The content produced is required to include the following statistics or facts: {stats_facts}"})

    if style_rules:
        style_rules_list = [rule.strip() for rule in style_rules.split("\n") if "::" in rule]
        messages.append({"role": "user", "content": "The style rules are as follows: (style rules should not mention color names)"})
        for rule in style_rules_list:
            messages.append({"role": "user", "content": rule})

    if emulate:
        emulate_message = {
            "role": "assistant",
            "content": "Emulate the grammar and writing mechanics based on the given prompts but do not use any of the actual example content provided."
        }
        messages.append(emulate_message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=word_count * 10,  # Adjusted to account for token-to-word conversion
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
            max_tokens=word_count * 10 - len(result),  # Adjusted to account for token-to-word conversion
            n=1,
            stop=None,
            temperature=0.7,
        )
        for choice in response.choices:
            result += choice.message.content

    result = f"# {title}\n\n{result}"  # Prepend title to result

    # Apply style rules if specified
    if style_rules:
        result = apply_style_rules(result, style_rules_list)

    return result

def apply_style_rules(text, style_rules):
    modified_text = text

    # Apply each style rule to the modified text
    for rule in style_rules:
        rule_parts = rule.split("::")  # Split rule into two parts: pattern and replacement
        if len(rule_parts) == 2:
            pattern, replacement = rule_parts
            modified_text = modified_text.replace(pattern, replacement)

    # Return the modified text
    return modified_text

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
style_rules = st.text_area("Enter style rules:", value='', height=200)

if st.button("Generate"):
    if not title:
        st.error("Please enter a title.")
    else:
        result = generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, style_rules)
        st.markdown(result)
        st.download_button(
            label="Download content",
            data=result,
            file_name='Content.txt',
            mime='text/txt',
        )
