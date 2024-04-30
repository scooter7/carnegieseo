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
    "Purple - caring, encouraging": {"verbs": ["care", "encourage", "attend to", "empathize", "provide", "nurture", "protect", "support", "embrace"], "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"], "beliefs": ["Believe people should be cared for and encouraged", "Desire to make others feel safe and supported", "Have a strong desire to mend and heal", "Become loyal teammates and trusted allies", "Are put off by aggression and selfish motivations"],},
     "beliefs": ['Believe people should be cared for and encouraged', 'Desire to make others feel safe and supported', 'Have a strong desire to mend and heal', 'Become loyal teammates and trusted allies', 'Are put off by aggression and selfish motivations'],
    "Green - adventurous, curious": {"verbs": ["explore", "discover", "venture", "discern", "examine", "experience", "explore", "inquire", "investigate", "ponder"], "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"]}
     "beliefs": ['The noblest pursuit is the quest for new knowledge', 'Continually inquiring and examining everything', 'Have an insatiable thirst for progress and discovery', 'Cannot sit still or accept present realities', 'Curiosity and possibility underpin their actions'],
    "Maroon - gritty, determined": {"verbs": ["persevere", "strive", "compete", "determine"], "adjectives": ["competitive", "determined", "gritty", "industrious", "persevering", "relentless", "resilient", "tenacious", "tough", "unwavering"]}
     "beliefs": ['Value extreme and hard work', 'Gritty and strong, they’re determined to overcome', 'Have no tolerance for laziness or inability', 'Highly competitive and intent on proving prowess', 'Will not be outpaced or outworked'],
    "Orange - artistic, creative": {"verbs": ["create", "express", "conceive", "express", "imagine", "interpret"], "adjectives": ["artistic", "conceptual", "creative", "eclectic", "expressive", "imaginative", "interpretive", "novel", "original", "whimsical"]}
     "beliefs": ['Intensely expressive', 'Communicate in diverse ways', 'A lack of imagination and rigidity may feel oppressive', 'Constructive, conceptual, and adept storytellers', 'Manifesting new and creative concepts is their end goal'],
    "Yellow - innovative, intelligent": {"verbs": ["innovate", "think", "analyze", "experiment", "invent", "envision"], "adjectives": ["advanced", "analytical", "brilliant", "experimental", "forward-thinking", "innovative", "intelligent", "inventive", "leading-edge", "visionary"]}
     "beliefs": ['Thrive on new concepts and experimentation', 'Live to make things newer and better', 'Work well in ambiguity or unknowns', 'Feel stifled by established processes and the status quo', 'See endless possibilities and opportunities to invent'],
    "Red - entertaining, humorous": {"verbs": ["entertain", "amuse", "energize", "engage", "excite", "play", "laugh"], "adjectives": ["dynamic", "energetic", "engaging", "entertaining", "enthusiastic", "exciting", "fun", "lively", "magnetic", "playful", "humorous"]}
     "beliefs": ['Energetic and uplifting', 'Motivated to entertain and create excitement', 'Magnetic and able to rally support for new concepts', 'Often naturally talented presenters and speakers', 'Sensitive to the mood and condition of others'],
    "Blue - confident, influential": {"verbs": ["inspire", "influence", "accomplish", "assert", "decide", "influence", "prove", "demonstrate"], "adjectives": ["accomplished", "assertive", "confident", "decisive", "elite", "influential", "powerful", "prominent", "proven", "strong"]}
     "beliefs": ['Achievement is paramount', 'Highly tolerant of risk and stress', 'Seeks influence and accomplishments', 'Comfortable making decisions with incomplete information', 'Set strategic visions and lead the way'],
    "Pink - charming, elegant": {"verbs": ["charm", "grace", "dignify", "idealize", "polish", "refine"], "adjectives": ["aesthetic", "charming", "classic", "dignified", "idealistic", "meticulous", "poised", "polished", "refined", "sophisticated" "elegant"]}
     "beliefs": ['Hold high regard for tradition and excellence', 'Dream up and pursue refinement, beauty, and vitality', 'Typically highly detailed and very observant', 'Mess and disorder only deflates their enthusiasm'],
    "Silver - rebellious, daring": {"verbs": ["rebel", "dare", "risk", "defy"], "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"]}
     "beliefs": ['Rule breakers and establishment challengers', 'Have a low need to fit in with the pack', 'Value unconventional and independent thinking', 'Value freedom, boldness, and defiant ideas', 'Feel stifled by red tape and bureaucratic systems'],
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "empassion", "transform"], "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "proud", "traditional", "transformative"]}
     "beliefs": ['There’s no need to differentiate from others', 'All perspectives are equally worth holding', 'Will not risk offending anyone', 'Light opinions are held quite loosely', 'Information tells enough of a story'],
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
