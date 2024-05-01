import streamlit as st
import openai
from collections import defaultdict

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
    # Creating a detailed prompt for OpenAI's API
    prompt_text = "Please analyze the following text and identify which verbs and adjectives from the following categories are present. Explain how these relate to the predefined beliefs of each category:\n\n" + f"Text: {text}\n\n" + "Categories:\n" + "\n".join([f"{color}: Verbs({', '.join(info['verbs'])}), Adjectives({', '.join(info['adjectives'])})" for color, info in placeholders.items()])
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt_text}],
        max_tokens=1500
    )
    return response.choices[0].message['content'].strip()

def match_text_to_color(text_analysis, original_text):
    words = set(original_text.lower().split())
    color_details = defaultdict(dict)

    for color, traits in placeholders.items():
        verb_hits = {verb for verb in traits['verbs'] if verb in words}
        adj_hits = {adj for adj in traits['adjectives'] if adj in words}
        total_hits = len(verb_hits) + len(adj_hits)
        
        relevant_beliefs = [belief for belief in traits['beliefs'] if any(word in belief.lower() for word in words)]
        
        color_details[color] = {
            'score': total_hits,
            'keywords': list(verb_hits.union(adj_hits)),
            'relevant_beliefs': relevant_beliefs
        }

    # Filter general detailed analysis per color
    for color in color_details.keys():
        color_details[color]['specific_analysis'] = extract_relevant_analysis(text_analysis, color, color_details[color]['keywords'])

    sorted_colors = sorted(color_details.items(), key=lambda item: item[1]['score'], reverse=True)[:3]
    return sorted_colors

def extract_relevant_analysis(detailed_text, color, keywords):
    sentences = detailed_text.split('.')
    relevant_sentences = [sentence for sentence in sentences if color.lower() in sentence.lower() or any(keyword in sentence.lower() for keyword in keywords)]
    return ' '.join(relevant_sentences).strip()

# Streamlit interface
st.title("Color Persona Text Analysis")

user_input = st.text_area("Paste your content here:", height=300)
if st.button("Analyze Text"):
    raw_analysis = analyze_text(user_input)
    top_colors = match_text_to_color(raw_analysis, user_input)
    st.write("Top color matches and their explanations:")
    for color, details in top_colors:
        st.write(f"**{color}** - Score: {details['score']}")
        st.write("Identified Keywords: ", ", ".join(details['keywords']))
        st.write("Relevant Beliefs:")
        for belief in details['relevant_beliefs']:
            st.write(f"- {belief}")
        st.write("General Detailed Analysis for this Color:")
        st.write(details['specific_analysis'])

    st.write("General Detailed Analysis (Full):")
    st.write(raw_analysis)
