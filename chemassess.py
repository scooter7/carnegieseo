import streamlit as st
import requests
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import io
import hashlib

# Load Google Auth credentials from Streamlit secrets
google_auth = {
    "client_id": st.secrets["google_auth"]["client_id"],
    "project_id": st.secrets["google_auth"]["project_id"],
    "auth_uri": st.secrets["google_auth"]["auth_uri"],
    "token_uri": st.secrets["google_auth"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["google_auth"]["auth_provider_x509_cert_url"],
    "client_secret": st.secrets["google_auth"]["client_secret"],
    "redirect_uris": st.secrets["google_auth"]["redirect_uris"]
}

AUTHORIZE_URL = google_auth["auth_uri"]
TOKEN_URL = google_auth["token_uri"]
REFRESH_TOKEN_URL = google_auth["token_uri"]
REVOKE_TOKEN_URL = "https://accounts.google.com/o/oauth2/revoke"
CLIENT_ID = google_auth["client_id"]
CLIENT_SECRET = google_auth["client_secret"]
REDIRECT_URI = google_auth["redirect_uris"][0]
SCOPE = "email profile"

# Define your color-based personas
placeholders = {
    "Purple - caring, encouraging": {"verbs": ["assist", "befriend", "care", "collaborate", "connect", "embrace", "empower", "encourage", "foster", "give", "help", "nourish", "nurture", "promote", "protect", "provide", "serve", "share", "shepherd", "steward", "tend", "uplift", "value", "welcome"], "adjectives": ["caring", "encouraging", "attentive", "compassionate", "empathetic", "generous", "hospitable", "nurturing", "protective", "selfless", "supportive", "welcoming"], 
     "beliefs": ['Believe people should be cared for and encouraged', 'Desire to make others feel safe and supported', 'Have a strong desire to mend and heal', 'Become loyal teammates and trusted allies', 'Are put off by aggression and selfish motivations']},
    "Green - adventurous, curious": {"verbs": ["analyze", "discover", "examine", "expand", "explore", "extend", "inquire", "journey", "launch", "move", "pioneer", "pursue", "question", "reach", "search", "uncover", "venture", "wonder"], "adjectives": ["adventurous", "curious", "discerning", "examining", "experiential", "exploratory", "inquisitive", "investigative", "intrepid", "philosophical"], 
     "beliefs": ['The noblest pursuit is the quest for new knowledge', 'Continually inquiring and examining everything', 'Have an insatiable thirst for progress and discovery', 'Cannot sit still or accept present realities', 'Curiosity and possibility underpin their actions']},
    "Maroon - gritty, determined": {"verbs": ["accomplish", "achieve", "build", "challenge", "commit", "compete", "contend", "dedicate", "defend", "devote", "drive", "endeavor", "entrust", "endure", "fight", "grapple", "grow", "improve", "increase", "overcome", "persevere", "persist", "press on", "pursue", "resolve"], "adjectives": ["competitive", "determined", "gritty", "industrious", "persevering", "relentless", "resilient", "tenacious", "tough", "unwavering"], 
     "beliefs": ['Value extreme and hard work', 'Gritty and strong, they’re determined to overcome', 'Have no tolerance for laziness or inability', 'Highly competitive and intent on proving prowess', 'Will not be outpaced or outworked']},
    "Orange - artistic, creative": {"verbs": ["compose", "conceptualize", "conceive", "craft", "create", "design", "dream", "envision", "express", "fashion", "form", "imagine", "interpret", "make", "originate", "paint", "perform", "portray", "realize", "shape"], "adjectives": ["artistic", "conceptual", "creative", "eclectic", "expressive", "imaginative", "interpretive", "novel", "original", "whimsical"], 
     "beliefs": ['Intensely expressive', 'Communicate in diverse ways', 'A lack of imagination and rigidity may feel oppressive', 'Constructive, conceptual, and adept storytellers', 'Manifesting new and creative concepts is their end goal']},
    "Yellow - innovative, intelligent": {"verbs": ["accelerate", "advance", "change", "conceive", "create", "engineer", "envision", "experiment", "dream", "ignite", "illuminate", "imagine", "innovate", "inspire", "invent", "pioneer", "progress", "shape", "spark", "solve", "transform", "unleash", "unlock"], "adjectives": ["advanced", "analytical", "brilliant", "experimental", "forward-thinking", "innovative", "intelligent", "inventive", "leading-edge", "visionary"], 
     "beliefs": ['Thrive on new concepts and experimentation', 'Live to make things newer and better', 'Work well in ambiguity or unknowns', 'Feel stifled by established processes and the status quo', 'See endless possibilities and opportunities to invent']},
    "Red - entertaining, humorous": {"verbs": ["animate", "amuse", "captivate", "cheer", "delight", "encourage", "energize", "engage", "enjoy", "enliven", "entertain", "excite", "express", "inspire", "joke", "motivate", "play", "stir", "uplift"], "adjectives": ["dynamic", "energetic", "engaging", "entertaining", "enthusiastic", "exciting", "fun", "lively", "magnetic", "playful", "humorous"], 
     "beliefs": ['Energetic and uplifting', 'Motivated to entertain and create excitement', 'Magnetic and able to rally support for new concepts', 'Often naturally talented presenters and speakers', 'Sensitive to the mood and condition of others']},
    "Blue - confident, influential": {"verbs": ["accomplish", "achieve", "affect", "assert", "cause", "command", "determine", "direct", "dominate", "drive", "empower", "establish", "guide", "impact", "impress", "influence", "inspire", "lead", "outpace", "outshine", "realize", "shape", "succeed", "transform", "win"], "adjectives": ["accomplished", "assertive", "confident", "decisive", "elite", "influential", "powerful", "prominent", "proven", "strong"], 
     "beliefs": ['Achievement is paramount', 'Highly tolerant of risk and stress', 'Seeks influence and accomplishments', 'Comfortable making decisions with incomplete information', 'Set strategic visions and lead the way']},
    "Pink - charming, elegant": {"verbs": ["arise", "aspire", "detail", "dream", "elevate", "enchant", "enrich", "envision", "exceed", "excel", "experience", "improve", "idealize", "imagine", "inspire", "perfect", "poise", "polish", "prepare", "refine", "uplift"], "adjectives": ["aesthetic", "charming", "classic", "dignified", "idealistic", "meticulous", "poised", "polished", "refined", "sophisticated", "elegant"], 
     "beliefs": ['Hold high regard for tradition and excellence', 'Dream up and pursue refinement, beauty, and vitality', 'Typically highly detailed and very observant', 'Mess and disorder only deflates their enthusiasm']},
    "Silver - rebellious, daring": {"verbs": ["activate", "campaign", "challenge", "commit", "confront", "dare", "defy", "disrupt", "drive", "excite", "face", "ignite", "incite", "influence", "inspire", "inspirit", "motivate", "move", "push", "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", "fight", "free"], "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"], 
     "beliefs": ['Rule breakers and establishment challengers', 'Have a low need to fit in with the pack', 'Value unconventional and independent thinking', 'Value freedom, boldness, and defiant ideas', 'Feel stifled by red tape and bureaucratic systems']},
    "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "empassion", "transform"], "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "proud", "traditional", "transformative"], 
     "beliefs": ['There’s no need to differentiate from others', 'All perspectives are equally worth holding', 'Will not risk offending anyone', 'Light opinions are held quite loosely', 'Information tells enough of a story']},
}

def get_content_hash(content):
    return hashlib.md5(content.encode()).hexdigest()

def extract_words(text, words_list):
    words_counter = Counter()
    for word in words_list:
        words_counter[word] = text.lower().split().count(word.lower())
    return words_counter

def analyze_url_content(content):
    color_scores = defaultdict(int)
    for color, traits in placeholders.items():
        verbs_count = extract_words(content, traits['verbs'])
        adjectives_count = extract_words(content, traits['adjectives'])
        color_scores[color] = sum(verbs_count.values()) + sum(adjectives_count.values())
    return color_scores

st.title("Color Persona Text Analysis")

# Hide the toolbar using CSS
hide_toolbar_css = """
    <style>
        .css-14xtw13.e8zbici0 { display: none !important; }
    </style>
"""
st.markdown(hide_toolbar_css, unsafe_allow_html=True)

url_input = st.text_area("Paste comma-separated URLs here:", height=100)
urls = [url.strip() for url in url_input.split(',')]

results = st.session_state.get('results', [])
aggregate_scores = st.session_state.get('aggregate_scores', defaultdict(int))

if st.button("Analyze URLs"):
    results = []
    aggregate_scores = defaultdict(int)

    for url in urls:
        try:
            st.write(f"Analyzing URL: {url}")  # Debug statement
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.get_text()
            content_hash = get_content_hash(content)

            # Check if analysis for this content already exists
            if 'analysis_cache' not in st.session_state:
                st.session_state.analysis_cache = {}

            if content_hash in st.session_state.analysis_cache:
                color_scores = st.session_state.analysis_cache[content_hash]
            else:
                color_scores = analyze_url_content(content)
                st.session_state.analysis_cache[content_hash] = color_scores

            sorted_colors = sorted(color_scores.items(), key=lambda item: item[1], reverse=True)
            top_colors = sorted_colors[:3]

            url_result = {"URL": url}
            for i, (color, score) in enumerate(top_colors):
                url_result[f"Top Color {i + 1}"] = color
                aggregate_scores[color] += score
            results.append(url_result)

            st.write(f"Analysis for URL: {url}")
            for color, score in top_colors:
                st.write(f"**{color}** - Score: {score}")
                st.write("Reasons:")
                for belief in placeholders[color]['beliefs']:
                    st.write(f"- {belief}")
            st.write("---")
        except Exception as e:
            st.write(f"Error analyzing URL: {url}")
            st.write(f"Error message: {str(e)}")

    st.session_state.results = results
    st.session_state.aggregate_scores = aggregate_scores

if results:
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    # Downloadable table of results
    csv = df_results.to_csv(index=False)
    st.download_button(label="Download Table as CSV", data=csv, file_name="color_persona_analysis.csv", mime="text/csv")

    # Aggregate color scores chart
    st.subheader("Aggregate Color Scores")
    colors = list(aggregate_scores.keys())
    scores = [aggregate_scores[color] for color in colors]
    plt.figure(figsize=(12, 6))
    plt.bar(colors, scores, color='skyblue')
    plt.xlabel("Color Categories")
    plt.ylabel("Aggregate Scores")
    plt.title("Aggregate Color Scores for All URLs")
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # Downloadable chart
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    st.download_button(label="Download Chart as PNG", data=buf, file_name="aggregate_color_scores.png", mime="image/png")
