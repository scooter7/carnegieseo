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

def generate_article(keyword, writing_style, institution, word_count):
    #return "This is a test article generated without making API calls."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Write a SEO optimized word {article_type} about " + keyword},
            {"role": "user", "content": "The {article_type} should be " + writing_style},
            {"role": "user", "content": "The {article_type} should mention the benefits of attending " + institution},
            {"role": "user", "content": "The {article_type} length should " + str(word_count)},
        ]
    )
    result = ""
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result

article_type = st.selectbox("Select content type:", ["Article", "Email"])
keyword = st.text_input("Enter a keyword:")
writing_style = st.selectbox("Select writing style:", ["Casual", "Informative", "Witty"])
institution = st.text_input("Institution:")
word_count = st.slider("Select word count:", min_value=300, max_value=1000, step=100, value=300)
submit_button = st.button("Generate Content")

if submit_button:
    message = st.empty()
    message.text("Busy generating...")
    
    if article_type == "Article":
        message_type = "SEO optimized word article"
    else:
        message_type = "email"
    
    article = generate_article(keyword, writing_style, institution, word_count, article_type=message_type)
    message.text("")
    st.write(article)
    st.download_button(
        label="Download content",
        data=article,
        file_name='Content.txt',
        mime='text/txt',
    )
