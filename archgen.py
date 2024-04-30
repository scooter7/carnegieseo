import streamlit as st
import openai
import sys
import logging
import random

user_prompt = st.text_area("Specify a prompt about the type of content you want produced:", "")
keywords = st.text_area("Optional: Specify specific keywords to be used:", "")
audience = st.text_input("Optional: Define the audience for the generated content:", "")
specific_facts_stats = st.text_area("Optional: Add specific facts or stats to be included:", "")

if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

openai_api_key = st.secrets["OPENAI_API_KEY"]

placeholders = {
    "Purple - caring, encouraging": {"verbs": ["care", "encourage", "attend to", "empathize", "provide", "nurture", "protect", "support", "embrace"], "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"]},
    "Green - adventurous, curious": {"verbs": ["explore", "discover", "venture", "discern", "examine", "experience", "explore", "inquire", "investigate", "ponder"], "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"]},
    "Maroon - gritty, determined": {"verbs": ["persevere", "strive", "compete", "determine"], "adjectives": ["competitive", "determined", "gritty", "industrious", "persevering", "relentless", "resilient", "tenacious", "tough", "unwavering"]},
    "Orange - artistic, creative": {"verbs": ["create", "express", "conceive", "express", "imagine", "interpret"], "adjectives": ["artistic", "conceptual", "creative", "eclectic", "expressive", "imaginative", "interpretive", "novel", "original", "whimsical"]},
    "Yellow - innovative, intelligent": {"verbs": ["innovate", "think", "analyze", "experiment", "invent", "envision"], "adjectives": ["advanced", "analytical", "brilliant", "experimental", "forward-thinking", "innovative", "intelligent", "inventive", "leading-edge", "visionary"]},
    "Red - entertaining, humorous": {"verbs": ["entertain", "amuse", "energize", "engage", "excite", "play", "laugh"], "adjectives": ["dynamic", "energetic", "engaging", "entertaining", "enthusiastic", "exciting", "fun", "lively", "magnetic", "playful", "humorous"]},
    "Blue - confident, influential": {"verbs": ["inspire", "influence", "accomplish", "assert", "decide", "influence", "prove", "demonstrate"], "adjectives": ["accomplished", "assertive", "confident", "decisive", "elite", "influential", "powerful", "prominent", "proven", "strong"]},
    "Pink - charming, elegant": {"verbs": ["charm", "grace", "dignify", "idealize", "polish", "refine"], "adjectives": ["aesthetic", "charming", "classic", "dignified", "idealistic", "meticulous", "poised", "polished", "refined", "sophisticated" "elegant"]},
    "Silver - rebellious, daring": {"verbs": ["rebel", "dare", "risk", "defy"], "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"]},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "empassion", "transform"], "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "proud", "traditional", "transformative"]}
}

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
    full_prompt = user_prompt
    if keywords:
        full_prompt += f"\nKeywords: {keywords}"
    if audience:
        full_prompt += f"\nAudience: {audience}"
    if specific_facts_stats:
        full_prompt += f"\nFacts/Stats: {specific_facts_stats}"

    messages = [{"role": "system", "content": full_prompt}]
    messages.append({"role": "user", "content": content})
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})

    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message["content"].strip()

def main():
    
    user_content = st.text_area("Paste your content here:")
    writing_styles = st.multiselect("Select Writing Styles:", list(placeholders.keys()))
    
    style_weights = []
    for style in writing_styles:
        weight = st.slider(f"Weight for {style}:", 0, 100, 50)
        style_weights.append(weight)
    
    if st.button("Generate Content"):
        revised_content = generate_article(user_content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats)
        st.text(revised_content)
        st.download_button("Download Content", revised_content, "content.txt")

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
