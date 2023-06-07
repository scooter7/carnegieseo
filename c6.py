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
    "Purple - caring, encouraging": ["caring", "encouraging"],
    "Green - adventurous, curious": ["adventurous", "curious"],
    "Maroon - gritty, determined": ["gritty", "determined"],
    "Orange - artistic, creative": ["artistic", "creative"],
    "Yellow - innovative, intelligent": ["innovative", "intelligent"],
    "Red - entertaining, humorous": ["entertaining", "humorous"],
    "Blue - confident, influential": ["confident", "influential"],
    "Pink - charming, elegant": ["charming", "elegant"],
    "Silver - rebellious, daring": ["rebellious", "daring"],
    "Beige - dedicated, humble": ["dedicated", "humble"],
    # Add more color and adjective placeholders as needed
}

def generate_article(content_type, keywords, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts):
    messages = [
        {"role": "user", "content": "This will be a " + content_type}
    ]

    # Modify user messages to include keywords
    for keyword in keywords:
        messages.append({"role": "user", "content": "This will be " + content_type + " about " + keyword})

    # Modify user messages to include writing styles with weighted percentages
    for i, style in enumerate(writing_styles):
        weight = style_weights[i][1]
        messages.append({"role": "user", "content": f"The {content_type} should have the style {style} with a weight of {weight*100:.1f}%"})

    messages.extend([
        {"role": "user", "content": "The " + content_type + " should be written to appeal to " + audience},
        {"role": "user", "content": "The " + content_type + " length should " + str(word_count)}
    ])

    if institution:
        messages.append({"role": "user", "content": "The " + content_type + " include references to the benefits of " + institution})

    if stats_facts:
        messages.append({"role": "user", "content": "The content produced is required to include the following statistics or facts: " + stats_facts})
    
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

    result = ''
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
keywords = st.text_input("Enter comma-separated keywords (up to 10):")
keyword_list = [keyword.strip() for keyword in keywords.split(",")][:10]

writing_styles = st.multiselect("Select writing styles:", list(placeholders.keys()))
style_weights = []
for style in writing_styles:
    weight = st.number_input(f"Weight for {style}", min_value=0.0, max_value=1.0, value=1.0, step=0.1)
    style_weights.append((style, weight))

style_weights = sorted(style_weights, key=lambda x: x[1], reverse=True)
selected_styles = [style for style, _ in style_weights]
weights_sum = sum(weight for _, weight in style_weights)
style_weights = [(style, weight / weights_sum) for style, weight in style_weights]

audience = st.text_input("Audience (optional):")
institution = st.text_input("Institution (optional):")
emulate = st.text_area("Emulate by pasting in up to 3000 words of sample content (optional):", value='', height=200, max_chars=3000)
stats_facts = st.text_area("Enter specific statistics or facts (optional):", value='', height=200, max_chars=3000)
word_count = st.slider("Select word count:", min_value=100, max_value=1000, step=50, value=100)
submit_button = st.button("Generate Content")

if submit_button:
    message = st.empty()
    message.text("Busy generating...")
    article = generate_article(content_type, keyword_list, writing_styles, style_weights, audience, institution, emulate, word_count, stats_facts)
    message.text("")
    st.write(article)
    st.download_button(
        label="Download content",
        data=article,
        file_name='Content.txt',
        mime='text/txt',
    )
