
import streamlit as st
import openai
from collections import Counter, defaultdict

# Load your API key from Streamlit's secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Define your color-based personas
placeholders = {
    "Purple - caring, encouraging": {"verbs": ["care", "encourage", "attend to", "empathize", "provide", "nurture", "protect", "support", "embrace"], "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"], 
     "beliefs": ['Believe people should be cared for and encouraged', 'Desire to make others feel safe and supported', 'Have a strong desire to mend and heal', 'Become loyal teammates and trusted allies', 'Are put off by aggression and selfish motivations']},
    "Green - adventurous, curious": {"verbs": ["explore", "discover", "venture", "discern", "examine", "experience", "explore", "inquire", "investigate", "ponder"], "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"], 
     "beliefs": ['The noblest pursuit is the quest for new knowledge', 'Continually inquiring and examining everything', 'Have an insatiable thirst for progress and discovery', 'Cannot sit still or accept present realities', 'Curiosity and possibility underpin their actions']},
    "Maroon - gritty, determined": {"verbs": ["persevere", "strive", "compete", "determine"], "adjectives": ["competitive", "determined", "gritty", "industrious", "persevering", "relentless", "resilient", "tenacious", "tough", "unwavering"], 
     "beliefs": ['Value extreme and hard work', 'Gritty and strong, they’re determined to overcome', 'Have no tolerance for laziness or inability', 'Highly competitive and intent on proving prowess', 'Will not be outpaced or outworked']},
    "Orange - artistic, creative": {"verbs": ["create", "express", "conceive", "express", "imagine", "interpret"], "adjectives": ["artistic", "conceptual", "creative", "eclectic", "expressive", "imaginative", "interpretive", "novel", "original", "whimsical"], 
     "beliefs": ['Intensely expressive', 'Communicate in diverse ways', 'A lack of imagination and rigidity may feel oppressive', 'Constructive, conceptual, and adept storytellers', 'Manifesting new and creative concepts is their end goal']},
    "Yellow - innovative, intelligent": {"verbs": ["innovate", "think", "analyze", "experiment", "invent", "envision"], "adjectives": ["advanced", "analytical", "brilliant", "experimental", "forward-thinking", "innovative", "intelligent", "inventive", "leading-edge", "visionary"], 
     "beliefs": ['Thrive on new concepts and experimentation', 'Live to make things newer and better', 'Work well in ambiguity or unknowns', 'Feel stifled by established processes and the status quo', 'See endless possibilities and opportunities to invent']},
    "Red - entertaining, humorous": {"verbs": ["entertain", "amuse", "energize", "engage", "excite", "play", "laugh"], "adjectives": ["dynamic", "energetic", "engaging", "entertaining", "enthusiastic", "exciting", "fun", "lively", "magnetic", "playful", "humorous"], 
     "beliefs": ['Energetic and uplifting', 'Motivated to entertain and create excitement', 'Magnetic and able to rally support for new concepts', 'Often naturally talented presenters and speakers', 'Sensitive to the mood and condition of others']},
    "Blue - confident, influential": {"verbs": ["inspire", "influence", "accomplish", "assert", "decide", "influence", "prove", "demonstrate"], "adjectives": ["accomplished", "assertive", "confident", "decisive", "elite", "influential", "powerful", "prominent", "proven", "strong"], 
     "beliefs": ['Achievement is paramount', 'Highly tolerant of risk and stress', 'Seeks influence and accomplishments', 'Comfortable making decisions with incomplete information', 'Set strategic visions and lead the way']},
    "Pink - charming, elegant": {"verbs": ["charm", "grace", "dignify", "idealize", "polish", "refine"], "adjectives": ["aesthetic", "charming", "classic", "dignified", "idealistic", "meticulous", "poised", "polished", "refined", "sophisticated", "elegant"], 
     "beliefs": ['Hold high regard for tradition and excellence', 'Dream up and pursue refinement, beauty, and vitality', 'Typically highly detailed and very observant', 'Mess and disorder only deflates their enthusiasm']},
    "Silver - rebellious, daring": {"verbs": ["rebel", "dare", "risk", "defy"], "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"], 
     "beliefs": ['Rule breakers and establishment challengers', 'Have a low need to fit in with the pack', 'Value unconventional and independent thinking', 'Value freedom, boldness, and defiant ideas', 'Feel stifled by red tape and bureaucratic systems']},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "empassion", "transform"], "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "proud", "traditional", "transformative"], 
     "beliefs": ['There’s no need to differentiate from others', 'All perspectives are equally worth holding', 'Will not risk offending anyone', 'Light opinions are held quite loosely', 'Information tells enough of a story']},
}

def analyze_text(text):
    # Constructing the prompt for the API
    prompt_text = f"Please analyze the following text and identify which verbs and adjectives from the following categories are present. Also, explain how these relate to the predefined beliefs of each category:\n\nText: {text}\n\nCategories:\n" + "\n".join([f"{color}: Verbs({', '.join(info['verbs'])}), Adjectives({', '.join(info['adjectives'])})" for color, info in placeholders.items()])
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=500
    )
    raw_content = response.choices[0].message['content'].strip()
    # Here you can optionally process the raw_content if necessary
    return raw_content  # Return only the raw_content if that's what's needed for further processing

def match_text_to_color(text_analysis):
    # Processing text to extract keyword matches
    word_counts = Counter(text_analysis.lower().split())
    color_scores = defaultdict(int)
    
    for color, traits in placeholders.items():
        verb_score = sum(word_counts[verb] for verb in traits['verbs'] if verb in word_counts)
        adjective_score = sum(word_counts[adjective] for adjective in traits['adjectives'] if adjective in word_counts)
        color_scores[color] += verb_score + adjective_score

    sorted_colors = sorted(color_scores.items(), key=lambda item: item[1], reverse=True)
    return sorted_colors[:3]  # Only return the top 3

# Streamlit interface
st.title("Color Persona Text Analysis")

user_input = st.text_area("Paste your content here:", height=300)
if st.button("Analyze Text"):
    raw_analysis = analyze_text(user_input)  # Now this function only returns the raw content
    top_colors = match_text_to_color(raw_analysis)  # Pass the correct data type
    st.write("Top color matches and their explanations:")
    for color, score in top_colors:
        st.write(f"**{color}** - Score: {score}")
        st.write("Reasons:")
        for belief in placeholders[color]['beliefs']:
            st.write(f"- {belief}")
    st.write("Detailed Analysis:")
    st.write(raw_analysis)  # Display raw analysis for insight
