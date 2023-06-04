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
    "Purple": ["caring", "encouraging"],
    "Green": ["adventurous", "curious"],
    "Maroon": ["gritty", "determined"],
    "Orange": ["artistic", "creative"],
    "Yellow": ["innovative", "intelligent"],
    "Red": ["entertaining", "humorous"],
    "Blue": ["confident", "influential"],
    "Pink": ["charming", "elegant"],
    "Silver": ["rebellious", "daring"],
    "Beige": ["dedicated", "humble"],
    # Add more color and adjective placeholders as needed
}

def generate_article(content_type, keyword, writing_style, audience, style_guide, institution, word_count):
    
    messages = [
        {"role": "user", "content": "This will be a SEO optimized " + content_type},
        {"role": "user", "content": "This will be " + content_type + " about " + keyword},
        {"role": "user", "content": "The " + content_type + " should have the style " + writing_style},
        {"role": "user", "content": "The email should mention the benefits of attending " + institution},
        {"role": "user", "content": "The " + content_type + " length should " + str(word_count)}
    ]
    
    if audience:
        messages.append({"role": "user", "content": "The " + content_type + " should be written to appeal to " + audience})
    
    if style_guide:
        messages.append({"role": "user", "content": "Use the rules of the " + style_guide + " style guide when writing"})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result

content_type = st.text_input("Define content type:")
keyword = st.text_input("Enter a keyword:")
writing_style = st.selectbox("Select writing style:", list(placeholders.keys()))
audience = st.text_input("Audience (optional):")
style_guide = st.text_input("Style Guide (optional):")
institution = st.text_input("Institution:")
word_count = st.slider("Select word count:", min_value=100, max_value=1000, step=50, value=100)
submit_button = st.button("Generate Content")

if submit_button:
    message = st.empty()
    message.text("Busy generating...")
    article = generate_article(content_type, keyword, writing_style, audience, style_guide, institution, word_count)
    message.text("")
    st.write(article)
    st.download_button(
        label="Download content",
        data=article,
        file_name='Content.txt',
        mime='text/txt',
    )
