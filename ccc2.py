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

def generate_article(keyword, writing_style, institution, audience, word_count):
    #return "This is a test article generated without making API calls."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": "Write an email about " + keyword},
                {"role": "user", "content": "The email should be " + writing_style},
                {"role": "user", "content": "The email should mention the benefits of attending " + institution},
                {"role": "user", "content": "The email should be written to appeal to " + audience},
                {"role": "user", "content": "The email length should " + str(word_count)},
            ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result

writing_styles = {
    "Purple": "Casual",
    "Informative": "Informative",
    "Witty": "Witty"
}

keyword = st.text_input("Enter a keyword:")
writing_style = st.selectbox("Select writing style:", list(writing_styles.keys()))
selected_style = writing_styles[writing_style]
institution = st.text_input("Institution:")
audience = st.text_input("Audience:")
word_count = st.slider("Select word count:", min_value=100, max_value=1000, step=100, value=100)
submit_button = st.button("Generate Email")

if submit_button:
    message = st.empty()
    message.text("Busy generating...")
    article = generate_article(keyword, selected_style, institution, audience, word_count)
    message.text("")
    st.write(article)
    st.download_button(
        label="Download email",
        data=article,
        file_name='Email.txt',
        mime='text/txt',
    )
