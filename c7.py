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
        "adjectives": ["caring", "encouraging"]
    },
    "Green - adventurous, curious": {
        "verbs": ["adventure", "explore"],
        "adjectives": ["adventurous", "curious"]
    },
    "Maroon - gritty, determined": {
        "verbs": ["persevere", "strive"],
        "adjectives": ["gritty", "determined"]
    },
    "Orange - artistic, creative": {
        "verbs": ["create", "imagine"],
        "adjectives": ["artistic", "creative"]
    },
    "Yellow - innovative, intelligent": {
        "verbs": ["innovate", "discover"],
        "adjectives": ["innovative", "intelligent"]
    },
    "Red - entertaining, humorous": {
        "verbs": ["entertain", "amuse"],
        "adjectives": ["entertaining", "humorous"]
    },
    "Blue - confident, influential": {
        "verbs": ["inspire", "influence"],
        "adjectives": ["confident", "influential"]
    },
    "Pink - charming, elegant": {
        "verbs": ["charm", "captivate"],
        "adjectives": ["charming", "elegant"]
    },
    "Silver - rebellious, daring": {
        "verbs": ["rebel", "dare"],
        "adjectives": ["rebellious", "daring"]
    },
    "Beige - dedicated, humble": {
        "verbs": ["dedicate", "humble"],
        "adjectives": ["dedicated", "humble"]
    },
    # Add more color and adjective placeholders as needed
}

def generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, h1_text, h2_text, style_rules):
    messages = [
        {"role": "user", "content": "The " + content_type + " should have the style: "}
    ]

    for style, weight in zip(writing_styles, style_weights):
        messages.append({"role": "user", "content": f"- {style} ({weight}%) "})

    # Append verb and adjective banks based on selected writing styles
    for style in writing_styles:
        style_message = {
            "role": "user",
            "content": "The " + content_type + " should use verbs from the " + style + " verb bank and adjectives from the " + style + " adjective bank."
        }
        messages.append(style_message)
        
        if style in placeholders:
            verb_bank = placeholders[style]["verbs"]
            adjective_bank = placeholders[style]["adjectives"]
            verb_bank_message = {
                "role": "assistant",
                "content": "Verb Bank: " + ", ".join(verb_bank)
            }
            adjective_bank_message = {
                "role": "assistant",
                "content": "Adjective Bank: " + ", ".join(adjective_bank)
            }
            messages.append(verb_bank_message)
            messages.append(adjective_bank_message)

    messages.extend([
        {"role": "user", "content": "This will be a " + content_type},
        {"role": "user", "content": "This will be " + content_type + " about " + keywords},
        {"role": "user", "content": "The " + content_type + " should have the style " + writing_styles},
        {"role": "user", "content": "The " + content_type + " should be written to appeal to " + audience},
        {"role": "user", "content": "The " + content_type + " length should be " + str(word_count) + " words"}
    ])

    if institution:
        messages.append({"role": "user", "content": "The " + content_type + " should include references to the benefits of " + institution})

    if stats_facts:
        messages.append({"role": "user", "content": "The content produced is required to include the following statistics or facts: " + stats_facts})

    if emulate:
        emulate_message = {
            "role": "assistant",
            "content": emulate
        }
        messages.append(emulate_message)

    if style_rules:
        style_rules_message = {
            "role": "user",
            "content": "Style Rules:\n" + style_rules
        }
        messages.append(style_rules_message)

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

    print(result)
    return result


content_type = st.text_input("Define content type:")
keywords = st.text_input("Enter keywords (comma-separated):")
writing_styles = st.multiselect("Select writing styles:", list(placeholders.keys()))
style_weights = st.multiselect("Select style weights:", [f"{style} ({weight}%)"
                                                         for style, weight in zip(writing_styles, range(0, 101, 10))],
                               default=[f"{style} (100%)" for style in writing_styles])
audience = st.text_input("Audience (optional):")
institution = st.text_input("Institution (optional):")
emulate = st.text_area("Emulate by pasting in up to 3000 words of sample content (optional):", value="", height=200, max_chars=3000)
stats_facts = st.text_area("Enter specific statistics or facts (optional):", value="", height=200, max_chars=3000)
word_count = st.slider("Select word count:", min_value=100, max_value=1000, step=50, value=100)
title = st.text_input("Enter title (required):")
h1_text = st.text_input("Enter H1 text:")
h2_text = st.text_input("Enter H2 text:")
style_rules = st.text_area("Enter style rules (optional):", value="", height=200)

submit_button = st.button("Generate Content")

if submit_button:
    message = st.empty()
    message.text("Busy generating...")
    article = generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts, title, h1_text, h2_text, style_rules)
    message.text("")
    st.write(article)
    st.download_button(
        label="Download content",
        data=article,
        file_name="Content.txt",
        mime="text/txt",
    )
