import streamlit as st
import openai
import requests
from collections import Counter, defaultdict
from bs4 import BeautifulSoup
from streamlit_oauth import OAuth2Component

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

# Create OAuth2Component instance
oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_URL, TOKEN_URL, REFRESH_TOKEN_URL, REVOKE_TOKEN_URL)

def fetch_user_info(token):
    user_info_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {
        "Authorization": f"Bearer {token['access_token']}"
    }
    response = requests.get(user_info_endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch user information.")
        return None

# Check if token exists in session state
if 'token' not in st.session_state:
    # If not, show authorize button
    result = oauth2.authorize_button("Authorize", REDIRECT_URI, SCOPE)
    if result and 'token' in result:
        # If authorization successful, save token in session state
        st.session_state.token = result.get('token')
        user_info = fetch_user_info(result.get('token'))
        st.session_state.user_info = user_info
        st.experimental_rerun()
else:
    # If token exists in session state, show the user info
    token = st.session_state['token']
    user_info = st.session_state.get('user_info')
    if user_info:
        st.write(f"Logged in as {user_info['email']}")
    else:
        st.error("Failed to retrieve user info. Please re-authenticate.")
    
    # Load your API key from Streamlit's secrets
    openai.api_key = st.secrets["OPENAI_API_KEY"]

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
        "Silver - rebellious, daring": {"verbs": ["activate", "campaign", "challenge", "commit", "confront", "dare", "defy", "disrupting", "drive", "excite", "face", "ignite", "incite", "influence", "inspire", "inspirit", "motivate", "move", "push", "rebel", "reimagine", "revolutionize", "rise", "spark", "stir", "fight", "free"], "adjectives": ["bold", "daring", "fearless", "independent", "non-conformist", "radical", "rebellious", "resolute", "unconventional", "valiant"], 
         "beliefs": ['Rule breakers and establishment challengers', 'Have a low need to fit in with the pack', 'Value unconventional and independent thinking', 'Value freedom, boldness, and defiant ideas', 'Feel stifled by red tape and bureaucratic systems']},
        "Beige - dedicated, humble": {"verbs": ["dedicate", "humble", "collaborate", "empower", "inspire", "empassion", "transform"], "adjectives": ["dedicated", "collaborative", "consistent", "empowering", "enterprising", "humble", "inspiring", "passionate", "proud", "traditional", "transformative"], 
         "beliefs": ['There’s no need to differentiate from others', 'All perspectives are equally worth holding', 'Will not risk offending anyone', 'Light opinions are held quite loosely', 'Information tells enough of a story']},
    }

    def chunk_text(text, max_tokens=3000):
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_tokens:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
            current_chunk.append(word)
            current_length += len(word) + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def analyze_text(text):
        summarized_placeholders = {
            color: {
                'verbs': ', '.join(info['verbs']),
                'adjectives': ', '.join(info['adjectives'])
            } for color, info in placeholders.items()
        }
        prompt_base = f"Please analyze the following text and identify which verbs and adjectives from the following categories are present. Also, explain how these relate to the predefined beliefs of each category:\n\nCategories:\n" + "\n".join([f"{color}: Verbs({info['verbs']}), Adjectives({info['adjectives']})" for color, info in summarized_placeholders.items()]) + "\n\nText: "

        text_chunks = chunk_text(text)
        all_responses = []

        for chunk in text_chunks:
            prompt_text = prompt_base + chunk
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt_text}],
                max_tokens=500
            )
            raw_content = response.choices[0]['message']['content'].strip()
            all_responses.append(raw_content)

        return "\n".join(all_responses)

    def match_text_to_color(text_analysis):
        word_counts = Counter(text_analysis.lower().split())
        color_scores = defaultdict(int)

        for color, traits in placeholders.items():
            verb_score = sum(word_counts[verb] for verb in traits['verbs'] if verb in word_counts)
            adjective_score = sum(word_counts[adjective] for adjective in traits['adjectives'] if adjective in word_counts)
            color_scores[color] += verb_score + adjective_score

        sorted_colors = sorted(color_scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_colors[:3]

    def generate_article(content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats):
        full_prompt = "Revise the following content according to the specified writing styles and other inputs.\n"
        if user_prompt:
            full_prompt += f"Prompt: {user_prompt}\n"
        if keywords:
            full_prompt += f"Keywords: {keywords}\n"
        if audience:
            full_prompt += f"Audience: {audience}\n"
        if specific_facts_stats:
            full_prompt += f"Facts/Stats: {specific_facts_stats}\n"
        for i, style in enumerate(writing_styles):
            weight = style_weights[i]
            full_prompt += f"Modify {weight}% of the content in a {style.split(' - ')[1]} manner.\n"

        full_prompt += "\nContent:\n" + content

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": full_prompt}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        return response.choices[0].message["content"].strip()

    st.title("Color Persona Text Analysis and Content Revision")

    # Hide the toolbar using CSS
    hide_toolbar_css = """
        <style>
            .css-14xtw13.e8zbici0 { display: none !important; }
        </style>
    """
    st.markdown(hide_toolbar_css, unsafe_allow_html=True)

    url_input = st.text_area("Paste comma-separated URLs here:", height=100)
    urls = [url.strip() for url in url_input.split(',')]

    if 'analyses' not in st.session_state:
        st.session_state.analyses = {}

    if st.button("Analyze URLs"):
        for url in urls:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                content = soup.get_text()

                raw_analysis = analyze_text(content)
                top_colors = match_text_to_color(raw_analysis)

                analysis_result = {
                    "content": content,
                    "raw_analysis": raw_analysis,
                    "top_colors": top_colors
                }

                st.session_state.analyses[url] = analysis_result

            except Exception as e:
                st.write(f"Error analyzing URL: {url}")
                st.write(f"Error message: {str(e)}")

    for url, analysis in st.session_state.analyses.items():
        st.write(f"Content from URL: {url}")
        st.text_area("Scraped Content", analysis["content"], height=200, key=f"content_{url}")
        st.download_button(f"Download Content from {url}", analysis["content"], f"content_{url.split('//')[-1].replace('/', '_')}.txt")

        st.write(f"Analysis for URL: {url}")
        for color, score in analysis["top_colors"]:
            st.write(f"**{color}** - Score: {score}")
            st.write("Reasons:")
            for belief in placeholders[color]['beliefs']:
                st.write(f"- {belief}")
        st.write("Detailed Analysis:")
        st.write(analysis["raw_analysis"])
        st.write("---")

    user_prompt = st.text_area("Specify a prompt about the type of content you want produced:", "")
    keywords = st.text_area("Optional: Specify specific keywords to be used:", "")
    audience = st.text_input("Optional: Define the audience for the generated content:", "")
    specific_facts_stats = st.text_area("Optional: Add specific facts or stats to be included:", "")

    pasted_content = st.text_area("Paste your content here:")
    writing_styles = st.multiselect("Select Writing Styles:", list(placeholders.keys()))
    
    style_weights = []
    for style in writing_styles:
        weight = st.slider(f"Weight for {style}:", 0, 100, 50)
        style_weights.append(weight)
    
    if st.button("Generate Content"):
        revised_content = generate_article(pasted_content, writing_styles, style_weights, user_prompt, keywords, audience, specific_facts_stats)
        st.text(revised_content)
        st.download_button("Download Content", revised_content, "content.txt")

    st.markdown("---")
    st.header("Revision Section")

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
