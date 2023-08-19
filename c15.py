import streamlit as st
import openai
import sys
import logging
import random

# Additional Prompts for User Input
user_prompt = st.text_area("Specify a prompt about the type of content you want produced:", "")
keywords = st.text_area("Optional: Specify specific keywords to be used:", "")
audience = st.text_input("Optional: Define the audience for the generated content:", "")
specific_facts_stats = st.text_area("Optional: Add specific facts or stats to be included:", "")

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]
logging.info(f"OPENAI_API_KEY: {openai_api_key}")

placeholders = {
    "Purple - caring, encouraging": {"verbs": ["care", "encourage"], "adjectives": ["caring", "encouraging"]},
    "Green - adventurous, curious": {"verbs": ["explore", "discover"], "adjectives": ["adventurous", "curious"]},
    "Maroon - gritty, determined": {"verbs": ["persevere", "strive"], "adjectives": ["gritty", "determined"]},
    "Orange - artistic, creative": {"verbs": ["create", "express"], "adjectives": ["artistic", "creative"]},
    "Yellow - innovative, intelligent": {"verbs": ["innovate", "intellect"], "adjectives": ["innovative", "intelligent"]},
    "Red - entertaining, humorous": {"verbs": ["entertain", "amuse"], "adjectives": ["entertaining", "humorous"]},
    "Blue - confident, influential": {"verbs": ["inspire", "influence"], "adjectives": ["confident", "influential"]},
    "Pink - charming, elegant": {"verbs": ["charm", "grace"], "adjectives": ["charming", "elegant"]},
    "Silver - rebellious, daring": {"verbs": ["rebel", "dare"], "adjectives": ["rebellious", "daring"]},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble"], "adjectives": ["dedicated", "humble"]}
}

def generate_article(content, writing_styles, style_weights):
    messages = [{"role": "system", "content": "You are a content creator that changes the tone of user-generated content based on the writing styles listed."}]
    messages.append({"role": "user", "content": content})
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"].strip()

def main():
    st.title("Carnegie Content Refresher")
    
    user_content = st.text_area("Paste your content here:")
    writing_styles = st.multiselect("Select Writing Styles:", list(placeholders.keys()))
    
    style_weights = []
    for style in writing_styles:
        weight = st.slider(f"Weight for {style}:", 0, 100, 50)
        style_weights.append(weight)
    
    if st.button("Generate Revised Content"):
        revised_content = generate_article(user_content, writing_styles, style_weights)
        st.text(revised_content)
        st.download_button("Download Revised Content", revised_content, "revised_content.txt")

    st.markdown("---")
    st.header("Revision Section")

    pasted_content = st.text_area("Paste Generated Content Here (for further revisions):")
    revision_requests = st.text_area("Specify Revisions Here:")

    if st.button("Revise Further"):
        revision_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": pasted_content},
            {"role": "user", "content": revision_requests}
        ]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=revision_messages)
        revised_content = response.choices[0].message["content"].strip()
        st.text(revised_content)
        st.download_button("Download Revised Content", revised_content, "revised_content_revision.txt")

if __name__ == "__main__":
    main()
