import streamlit as st
import openai
import sys
import random

# Check if the OPENAI_API_KEY is set in Streamlit secrets
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

# OpenAI API key from the secrets
openai_api_key = st.secrets["OPENAI_API_KEY"]

# Placeholder definitions with verbs and adjectives
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
    "Consider donating to the annual fund.",
    "Consider planned giving to support the future.",
    "Consider making a major gift to transform the campus."
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

# Sliders for color influence ratio if multiple styles are selected
style_weights = []
if writing_styles:
    st.markdown("#### Set the influence ratio for each selected color:")
    total_weight = sum(style_weights)
    for style in writing_styles:
        weight = st.slider(f"Weight for {style}:", 0, 100, 100 // len(writing_styles))
        style_weights.append(weight)

# Function to generate detailed content using GPT model
def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
    # Build the initial prompt
    full_prompt = f"Generate a compelling and thoughtful email to encourage alumni to donate. Here are the details:\n"
    full_prompt += f"Request Type: {content}\nCollege/University Name: {college_name}\n"
    
    if keywords:
        full_prompt += f"Keywords: {keywords}\n"
    if audience:
        full_prompt += f"Audience: {audience}\n"
    if specific_facts_stats:
        full_prompt += f"Facts/Stats: {specific_facts_stats}\n"
    
    # Add instructions for each writing style
    messages = [{"role": "system", "content": full_prompt}]
    for i, style in enumerate(writing_styles):
        if style_weights[i] > 0:  # Only add the style if its weight is positive
            messages.append({"role": "system", "content": f"Include about {style_weights[i]}% of '{style.split(' - ')[1]}' style using verbs like {', '.join(random.sample(placeholders[style]['verbs'], min(3, len(placeholders[style]['verbs']))))} and adjectives like {', '.join(random.sample(placeholders[style]['adjectives'], min(3, len(placeholders[style]['adjectives']))))}."})
    
    # Generate content using the OpenAI Chat API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1024
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        st.error(f"An error occurred while generating the content: {str(e)}")
        return "Error in content generation."

# Main function to generate and revise content
def main():
    # Generate the initial email
    if st.button("Generate Donation Email"):
        if not college_name:
            st.error("Please specify the name of the college/university.")
        elif not writing_styles:
            st.error("Please select at least one writing style based on color categories.")
        else:
            content_description = f"{selected_request} Support for {college_name} is crucial."
            generated_content = generate_article(content_description, writing_styles, style_weights, selected_request, keywords, audience, specific_facts_stats)
            st.text_area("Generated Donation Email:", generated_content, height=300)
            st.download_button("Download Donation Email", generated_content, f"{college_name}_donation_email.txt")

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
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=revision_messages
            )
            revised_content = response['choices'][0]['message']['content'].strip()
            st.text_area("Revised Content:", revised_content, height=300)
            st.download_button("Download Revised Content", revised_content, "revised_content.txt")
        except Exception as e:
            st.error(f"An error occurred while revising the content: {str(e)}")

if __name__ == "__main__":
    main()
