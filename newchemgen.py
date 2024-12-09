import streamlit as st
import openai
import sys

if "OPENAI_API_KEY" in st.secrets:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
else:
    st.error("Please set the OPENAI_API_KEY secret on the Streamlit dashboard.")
    sys.exit(1)

# URL of the logo
logo_url = "https://www.carnegiehighered.com/wp-content/uploads/2021/11/Twitter-Image-2-2021.png"

placeholders = {
    "Purple - caring, encouraging": {
        "verbs": [
            "assist", "befriend", "care", "collaborate", "connect", "embrace", 
            "empower", "encourage", "foster", "give", "help", "nourish", 
            "nurture", "promote", "protect", "provide", "serve", "share", 
            "shepherd", "steward", "tend", "uplift", "value", "welcome"
        ],
        "adjectives": [
            "caring", "encouraging", "attentive", "compassionate", 
            "empathetic", "generous", "hospitable", "nurturing", 
            "protective", "selfless", "supportive", "welcoming"
        ],
        "beliefs": [
            "Believe people should be cared for and encouraged",
            "Desire to make others feel safe and supported",
            "Have a strong desire to mend and heal",
            "Become loyal teammates and trusted allies",
            "Are put off by aggression and selfish motivations"
        ]
    },
    "Green - adventurous, curious": {
        "verbs": [
            "analyze", "discover", "examine", "expand", "explore", "extend", 
            "inquire", "journey", "launch", "move", "pioneer", "pursue", 
            "question", "reach", "search", "uncover", "venture", "wonder"
        ],
        "adjectives": [
            "adventurous", "curious", "discerning", "examining", "experiential", 
            "exploratory", "inquisitive", "investigative", "intrepid", 
            "philosophical"
        ],
        "beliefs": [
            "The noblest pursuit is the quest for new knowledge",
            "Continually inquiring and examining everything",
            "Have an insatiable thirst for progress and discovery",
            "Cannot sit still or accept present realities",
            "Curiosity and possibility underpin their actions"
        ]
    },
    "Maroon - gritty, determined": {
        "verbs": [
            "accomplish", "achieve", "build", "challenge", "commit", 
            "compete", "contend", "dedicate", "defend", "devote", "drive", 
            "endeavor", "entrust", "endure", "fight", "grapple", "grow", 
            "improve", "increase", "overcome", "persevere", "persist", 
            "press on", "pursue", "resolve"
        ],
        "adjectives": [
            "competitive", "determined", "gritty", "industrious", 
            "persevering", "relentless", "resilient", "tenacious", "tough", 
            "unwavering"
        ],
        "beliefs": [
            "Value extreme and hard work",
            "Gritty and strong, they’re determined to overcome",
            "Have no tolerance for laziness or inability",
            "Highly competitive and intent on proving prowess",
            "Will not be outpaced or outworked"
        ]
    },
    "Orange - artistic, creative": {
        "verbs": [
            "compose", "conceptualize", "conceive", "craft", "create", 
            "design", "dream", "envision", "express", "fashion", "form", 
            "imagine", "interpret", "make", "originate", "paint", "perform", 
            "portray", "realize", "shape"
        ],
        "adjectives": [
            "artistic", "conceptual", "creative", "eclectic", "expressive", 
            "imaginative", "interpretive", "novel", "original", "whimsical"
        ],
        "beliefs": [
            "Intensely expressive",
            "Communicate in diverse ways",
            "A lack of imagination and rigidity may feel oppressive",
            "Constructive, conceptual, and adept storytellers",
            "Manifesting new and creative concepts is their end goal"
        ]
    },
    "Yellow - innovative, intelligent": {
        "verbs": [
            "accelerate", "advance", "change", "conceive", "create", 
            "engineer", "envision", "experiment", "dream", "ignite", 
            "illuminate", "imagine", "innovate", "inspire", "invent", 
            "pioneer", "progress", "shape", "spark", "solve", "transform", 
            "unleash", "unlock"
        ],
        "adjectives": [
            "advanced", "analytical", "brilliant", "experimental", 
            "forward-thinking", "innovative", "intelligent", "inventive", 
            "leading-edge", "visionary"
        ],
        "beliefs": [
            "Thrive on new concepts and experimentation",
            "Live to make things newer and better",
            "Work well in ambiguity or unknowns",
            "Feel stifled by established processes and the status quo",
            "See endless possibilities and opportunities to invent"
        ]
    },
    "Red - entertaining, humorous": {
        "verbs": [
            "animate", "amuse", "captivate", "cheer", "delight", "encourage", 
            "energize", "engage", "enjoy", "enliven", "entertain", "excite", 
            "express", "inspire", "joke", "motivate", "play", "stir", "uplift"
        ],
        "adjectives": [
            "dynamic", "energetic", "engaging", "entertaining", 
            "enthusiastic", "exciting", "fun", "lively", "magnetic", 
            "playful", "humorous"
        ],
        "beliefs": [
            "Energetic and uplifting",
            "Motivated to entertain and create excitement",
            "Magnetic and able to rally support for new concepts",
            "Often naturally talented presenters and speakers",
            "Sensitive to the mood and condition of others"
        ]
    },
    "Blue - confident, influential": {
        "verbs": [
            "accomplish", "achieve", "affect", "assert", "cause", "command", 
            "determine", "direct", "dominate", "drive", "empower", 
            "establish", "guide", "impact", "impress", "influence", "inspire", 
            "lead", "outpace", "outshine", "realize", "shape", "succeed", 
            "transform", "win"
        ],
        "adjectives": [
            "accomplished", "assertive", "confident", "decisive", "elite", 
            "influential", "powerful", "prominent", "proven", "strong"
        ],
        "beliefs": [
            "Achievement is paramount",
            "Highly tolerant of risk and stress",
            "Seeks influence and accomplishments",
            "Comfortable making decisions with incomplete information",
            "Set strategic visions and lead the way"
        ]
    },
    "Pink - charming, elegant": {
        "verbs": [
            "arise", "aspire", "detail", "dream", "elevate", "enchant", 
            "enrich", "envision", "exceed", "excel", "experience", "improve", 
            "idealize", "imagine", "inspire", "perfect", "poise", "polish", 
            "prepare", "refine", "uplift"
        ],
        "adjectives": [
            "aesthetic", "charming", "classic", "dignified", "idealistic", 
            "meticulous", "poised", "polished", "refined", "sophisticated", 
            "elegant"
        ],
        "beliefs": [
            "Hold high regard for tradition and excellence",
            "Dream up and pursue refinement, beauty, and vitality",
            "Typically highly detailed and very observant",
            "Mess and disorder only deflates their enthusiasm"
        ]
    },
    "Silver - rebellious, daring": {
        "verbs": [
            "activate", "campaign", "challenge", "commit", "confront", "dare", 
            "defy", "disrupting", "drive", "excite", "face", "ignite", "incite", 
            "influence", "inspire", "inspirit", "motivate", "move", "push", 
            "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", 
            "fight", "free"
        ],
        "adjectives": [
            "bold", "daring", "fearless", "independent", "non-conformist", 
            "radical", "rebellious", "resolute", "unconventional", "valiant"
        ],
        "beliefs": [
            "Rule breakers and establishment challengers",
            "Have a low need to fit in with the pack",
            "Value unconventional and independent thinking",
            "Value freedom, boldness, and defiant ideas",
            "Feel stifled by red tape and bureaucratic systems"
        ]
    },
    "Beige - dedicated, humble": {
        "verbs": [
            "dedicate", "humble", "collaborate", "empower", "inspire", 
            "empassion", "transform"
        ],
        "adjectives": [
            "dedicated", "collaborative", "consistent", "empowering", 
            "enterprising", "humble", "inspiring", "passionate", "proud", 
            "traditional", "transformative"
        ],
        "beliefs": [
            "There’s no need to differentiate from others",
            "All perspectives are equally worth holding",
            "Will not risk offending anyone",
            "Light opinions are held quite loosely",
            "Information tells enough of a story"
        ]
    }
}

def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats, min_chars, max_chars):
    full_prompt = user_prompt
    if keywords:
        full_prompt += f"\nKeywords: {keywords}"
    if audience:
        full_prompt += f"\nAudience: {audience}"
    if specific_facts_stats:
        full_prompt += f"\nFacts/Stats: {specific_facts_stats}"
    if min_chars:
        full_prompt += f"\nMinimum characters: {min_chars}"
    if max_chars:
        full_prompt += f"\nMaximum characters: {max_chars}"

    messages = [{"role": "system", "content": full_prompt}]
    messages.append({"role": "user", "content": content})
    for i, style in enumerate(writing_styles):
        weight = style_weights[i]
        messages.append({"role": "assistant", "content": f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner."})

    response = openai.ChatCompletion.create(model="gpt-4o", messages=messages)
    generated_content = response.choices[0].message["content"].strip()

    if min_chars and len(generated_content) < int(min_chars):
        generated_content += " " * (int(min_chars) - len(generated_content))
    if max_chars and len(generated_content) > int(max_chars):
        generated_content = generated_content[:int(max_chars)]

    return generated_content

def main():
    hide_toolbar_css = """
    <style>
        .css-14xtw13.e8zbici0 { display: none !important; }
    </style>
    """
    st.markdown(hide_toolbar_css, unsafe_allow_html=True)

    # Add logo at the top of the app
    st.image(logo_url, width=800)

    # App Title
    st.title("ChemGen")
    
    user_prompt = st.text_area("Specify a prompt about the type of content you want produced:", "")
    keywords = st.text_area("Optional: Specify specific keywords to be used:", "")
    audience = st.text_input("Optional: Define the audience for the generated content:", "")
    specific_facts_stats = st.text_area("Optional: Add specific facts or stats to be included:", "")

    user_content = st.text_area("Paste your content here:")
    writing_styles = st.multiselect("Select Writing Styles:", list(placeholders.keys()))

    min_chars = st.text_input("Minimum Character Count:", "")
    max_chars = st.text_input("Maximum Character Count:", "")
    
    style_weights = []
    for style in writing_styles:
        weight = st.slider(f"Weight for {style}:", 0, 100, 50)
        style_weights.append(weight)
    
    if st.button("Generate Content"):
        revised_content = generate_article(user_content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats, min_chars, max_chars)
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
        response = openai.ChatCompletion.create(model="gpt-4o", messages=revision_messages)
        revised_content = response.choices[0].message["content"].strip()
        st.text(revised_content)
        st.download_button("Download Revised Content", revised_content, "revised_content_revision.txt")

if __name__ == "__main__":
    main()
