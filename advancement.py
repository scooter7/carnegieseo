import streamlit as st
import openai
import sys
import random

# Check if the OPENAI_API_KEY is set in the Streamlit secrets
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

# OpenAI API key from the secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Placeholder definitions as previously defined
placeholders = {
    "Purple - caring, encouraging": {"verbs": ["assist", "befriend", "care", "collaborate", "connect", "embrace", "empower", "encourage", "foster", "give", "help", "nourish", "nurture", "promote", "protect", "provide", "serve", "share", "shepherd", "steward", "tend", "uplift", "value", "welcome"], "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"], "beliefs": ['Believe people should be cared for and encouraged', 'Desire to make others feel safe and supported', 'Have a strong desire to mend and heal', 'Become loyal teammates and trusted allies', 'Are put off by aggression and selfish motivations']},
    "Green - adventurous, curious": {"verbs": ["analyze", "discover", "examine", "expand", "explore", "extend", "inquire", "journey", "launch", "move", "pioneer", "pursue", "question", "reach", "search", "uncover", "venture", "wonder"], "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"], "beliefs": ['The noblest pursuit is the quest for new knowledge', 'Continually inquiring and examining everything', 'Have an insatiable thirst for progress and discovery', 'Cannot sit still or accept present realities', 'Curiosity and possibility underpin their actions']},
    "Maroon - gritty, determined": {"verbs": ["accomplish", "achieve", "build", "challenge", "commit", "compete", "contend", "dedicate", "defend", "devote", "drive", "endeavor", "entrust", "endure", "fight", "grapple", "grow", "improve", "increase", "overcome", "persevere", "persist", "press on", "pursue", "resolve"], "adjectives": ["competitive", "determined", "gritty", "industrious", "persevering", "relentless", "resilient", "tenacious", "tough", "unwavering"], "beliefs": ['Value extreme and hard work', 'Gritty and strong, they’re determined to overcome', 'Have no tolerance for laziness or inability', 'Highly competitive and intent on proving prowess', 'Will not be outpaced or outworked']},
    "Orange - artistic, creative": {"verbs": ["compose", "conceptualize", "conceive", "craft", "create", "design", "dream", "envision", "express", "fashion", "form", "imagine", "interpret", "make", "originate", "paint", "perform", "portray", "realize", "shape"], "adjectives": ["artistic", "conceptual", "creative", "eclectic", "expressive", "imaginative", "interpretive", "novel", "original", "whimsical"], "beliefs": ['Intensely expressive', 'Communicate in diverse ways', 'A lack of imagination and rigidity may feel oppressive', 'Constructive, conceptual, and adept storytellers', 'Manifesting new and creative concepts is their end goal']},
    "Yellow - innovative, intelligent": {"verbs": ["accelerate", "advance", "change", "conceive", "create", "engineer", "envision", "experiment", "dream", "ignite", "illuminate", "imagine", "innovate", "inspire", "invent", "pioneer", "progress", "shape", "spark", "solve", "transform", "unleash", "unlock"], "adjectives": ["advanced", "analytical", "brilliant", "experimental", "forward-thinking", "innovative", "intelligent", "inventive", "leading-edge", "visionary"], "beliefs": ['Thrive on new concepts and experimentation', 'Live to make things newer and better', 'Work well in ambiguity or unknowns', 'Feel stifled by established processes and the status quo', 'See endless possibilities and opportunities to invent']},
    "Red - entertaining, humorous": {"verbs": ["animate", "amuse", "captivate", "cheer", "delight", "encourage", "energize", "engage", "enjoy", "enliven", "entertain", "excite", "express", "inspire", "joke", "motivate", "play", "stir", "uplift"], "adjectives": ["dynamic", "energetic", "engaging", "entertaining", "enthusiastic", "exciting", "fun", "lively", "magnetic", "playful", "humorous"], "beliefs": ['Energetic and uplifting', 'Motivated to entertain and create excitement', 'Magnetic and able to rally support for new concepts', 'Often naturally talented presenters and speakers', 'Sensitive to the mood and condition of others']},
    "Blue - confident, influential": {"verbs": ["accomplish", "achieve", "affect", "assert", "cause", "command", "determine", "direct", "dominate", "drive", "empower", "establish", "guide", "impact", "impress", "influence", "inspire", "lead", "outpace", "outshine", "realize", "shape", "succeed", "transform", "win"], "adjectives": ["accomplished", "assertive", "confident", "decisive", "elite", "influential", "powerful", "prominent", "proven", "strong"], "beliefs": ['Achievement is paramount', 'Highly tolerant of risk and stress', 'Seeks influence and accomplishments', 'Comfortable making decisions with incomplete information', 'Set strategic visions and lead the way']},
    "Pink - charming, elegant": {"verbs": ["arise", "aspire", "detail", "dream", "elevate", "enchant", "enrich", "envision", "exceed", "excel", "experience", "improve", "idealize", "imagine", "inspire", "perfect", "poise", "polish", "prepare", "refine", "uplift"], "adjectives": ["aesthetic", "charming", "classic", "dignified", "idealistic", "meticulous", "poised", "polished", "refined", "sophisticated", "elegant"], "beliefs": ['Hold high regard for tradition and excellence', 'Dream up and pursue refinement, beauty, and vitality', 'Typically highly detailed and very observant', 'Mess and disorder only deflates their enthusiasm']},
    "Silver - rebellious, daring": {"verbs": ["activate", "campaign", "challenge", "commit", "confront", "dare", "defy", "disrupt", "drive", "excite", "face", "ignite", "incite", "influence", "inspire", "inspirit", "motivate", "move", "push", "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", "fight", "free"], "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"], "beliefs": ['Rule breakers and establishment challengers', 'Have a low need to fit in with the pack', 'Value unconventional and independent thinking', 'Value freedom, boldness, and defiant ideas', 'Feel stifled by red tape and bureaucratic systems']},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "empassion", "transform"], "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "proud", "traditional", "transformative"], "beliefs": ['There’s no need to differentiate from others', 'All perspectives are equally worth holding', 'Will not risk offending anyone', 'Light opinions are held quite loosely', 'Information tells enough of a story']},
}

# List of predefined donation requests
donation_requests = [
    "Ask the alum to consider donating to the annual fund of the college",
    "Ask the alum to consider planned giving to the college",
    "Ask the alum to consider making a major gift to the college"
]

# User selects the type of donation request
selected_request = st.selectbox("Select the type of donation request:", donation_requests)

# User inputs the name of the college/university
college_name = st.text_input("Specify the name of the college/university:", "")

# Optional: Specify specific keywords to be used
keywords = st.text_area("Optional: Specify specific keywords to be used:", "")

# Optional: Define the audience for the generated content
audience = st.text_input("Optional: Define the audience for the generated content:", "")

# Optional: Add specific facts or stats to be included
specific_facts_stats = st.text_area("Optional: Add specific facts or stats to be included:", "")

# Select writing styles based on color categories
writing_styles = st.multiselect("Select Writing Styles Based on Color Categories:", list(placeholders.keys()))

# Sliders for color influence ratio
if writing_styles:
    st.markdown("### Set the influence ratio for each selected color:")
    style_weights = {}
    for style in writing_styles:
        style_weights[style] = st.slider(f"Weight for {style}:", 0, 100, 100 // len(writing_styles))

# Function to generate dynamic parts of the email
def generate_dynamic_content(college_name, request_type, specific_facts_stats, placeholders, writing_styles, style_weights):
    dynamic_content = ""
    total_weight = sum(style_weights.values())
    
    # Normalize weights if needed
    if total_weight == 0:
        for style in writing_styles:
            style_weights[style] = 1
        total_weight = sum(style_weights.values())
    
    # Calculate how many sentences to generate from each style
    num_sentences = 5  # Total dynamic sentences to generate
    style_sentences = {style: (weight / total_weight) * num_sentences for style, weight in style_weights.items()}
    
    for style, count in style_sentences.items():
        for _ in range(int(round(count))):
            verb = random.choice(placeholders[style]["verbs"])
            adjective = random.choice(placeholders[style]["adjectives"])
            if request_type == donation_requests[0]:  # Annual fund
                dynamic_content += f"Your {adjective} {verb} can empower the next generation of leaders and innovators at {college_name}. "
            elif request_type == donation_requests[1]:  # Planned giving
                dynamic_content += f"By choosing to {verb} through planned giving, you are {adjective} shaping the future of our students and faculty. "
            elif request_type == donation_requests[2]:  # Major gift
                dynamic_content += f"A {adjective} gift can {verb} areas of critical need and create lasting impact at {college_name}. "
    
    if specific_facts_stats:
        dynamic_content += f"Did you know? {specific_facts_stats} "

    return dynamic_content

# Function to generate the full email
def generate_full_email(college_name, request_type, keywords, audience, specific_facts_stats, writing_styles, style_weights):
    # Introductory greeting
    greeting = f"Dear {audience or 'Alumni'},\n\n"

    # Dynamic introduction based on the college and request type
    introduction = ""
    if request_type == donation_requests[0]:
        introduction = f"We are reaching out to share how the annual fund at {college_name} is making a difference. "
    elif request_type == donation_requests[1]:
        introduction = f"As we look to the future, planned giving continues to be a cornerstone for {college_name}'s growth. "
    elif request_type == donation_requests[2]:
        introduction = f"We are excited to discuss the transformative power of major gifts at {college_name}. "

    # Generate dynamic content based on the selected colors and their weights
    dynamic_content = generate_dynamic_content(college_name, request_type, specific_facts_stats, placeholders, writing_styles, style_weights)

    # Closing remarks
    closing = "\nWe hope you will consider joining us in this effort. Your support is crucial and much appreciated."

    # Signature
    signature = "\n\nSincerely,\n[Your Name or Signature]"

    # Combine all parts to form the full email
    full_email = greeting + introduction + dynamic_content + closing + signature
    return full_email

# Main function to generate and revise content
def main():
    # Section to generate the initial email
    if st.button("Generate Donation Email"):
        if not college_name:
            st.error("Please specify the name of the college/university.")
        else:
            full_email = generate_full_email(college_name, selected_request, keywords, audience, specific_facts_stats, writing_styles, style_weights)
            st.text_area("Generated Donation Email:", full_email, height=300)
            st.download_button("Download Donation Email", full_email, f"{college_name}_donation_email.txt")

    st.markdown("---")
    st.header("Revision Section")

    # Revision functionality
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
        st.text_area("Revised Content:", revised_content, height=300)
        st.download_button("Download Revised Content", revised_content, "revised_content.txt")

if __name__ == "__main__":
    main()
