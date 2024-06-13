import streamlit as st
import openai
import requests
from collections import Counter, defaultdict
from bs4 import BeautifulSoup

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

def chunk_html(html, max_tokens=1500):
    soup = BeautifulSoup(html, "html.parser")
    chunks = []
    current_chunk = ""
    current_length = 0

    for element in soup.recursiveChildGenerator():
        if isinstance(element, str):
            if current_length + len(element.split()) > max_tokens:
                chunks.append(current_chunk)
                current_chunk = ""
                current_length = 0
            current_chunk += element
            current_length += len(element.split())
        else:
            if element.name in ['script', 'style']:
                continue
            element_str = str(element)
            if current_length + len(element_str.split()) > max_tokens:
                chunks.append(current_chunk)
                current_chunk = ""
                current_length = 0
            current_chunk += element_str
            current_length += len(element_str.split())

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def analyze_text(html):
    summarized_placeholders = {
        color: {
            'verbs': ', '.join(info['verbs']),
            'adjectives': ', '.join(info['adjectives'])
        } for color, info in placeholders.items()
    }
    prompt_base = "Please analyze the following HTML content and identify which verbs and adjectives from the following categories are present. Also, explain how these relate to the predefined beliefs of each category:\n\nCategories:\n" + "\n".join([f"{color}: Verbs({', '.join(info['verbs'])}), Adjectives({', '.join(info['adjectives'])})" for color, info in summarized_placeholders.items()]) + "\n\nHTML: "

    html_chunks = chunk_html(html)
    all_responses = []

    for chunk in html_chunks:
        prompt_html = prompt_base + chunk
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_html}],
            max_tokens=2000
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
        messages=messages,
        max_tokens=1500
    )

    return response.choices[0].message["content"].strip()

def insert_revised_text_to_html(original_html, revised_text):
    soup = BeautifulSoup(original_html, "html.parser")
    for p_tag in soup.find_all('p'):
        p_tag.string = revised_text
    return str(soup)

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
            raw_html = str(soup)

            raw_analysis = analyze_text(raw_html)
            top_colors = match_text_to_color(raw_analysis)

            analysis_result = {
                "content": content,
                "raw_analysis": raw_analysis,
                "top_colors": top_colors,
                "raw_html": raw_html
            }

            st.session_state.analyses[url] = analysis_result

        except Exception as e:
            st.write(f"Error analyzing URL: {url}")
            st.write(f"Error message: {str(e)}")

for url, analysis in st.session_state.analyses.items():
    st.write(f"Content from URL: {url}")
    st.text_area("Scraped Content", analysis["content"], height=200, key=f"content_{url}")
    st.download_button(f"Download Content from {url}", analysis["content"], f"content_{url.split('//')[-1].replace('/', '_')}.txt")
    st.download_button(f"Download HTML from {url}", analysis["raw_html"], f"content_{url.split('//')[-1].replace('/', '_')}.html")

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
    # Optionally insert the revised content back into the HTML structure and allow downloading
    revised_html_chunks = []
    html_chunks = chunk_html(pasted_content)
    for chunk in html_chunks:
        revised_html_chunks.append(insert_revised_text_to_html(chunk, revised_content))
    revised_html = ''.join(revised_html_chunks)
    st.download_button("Download Revised HTML", revised_html, "revised_content.html")

st.markdown("---")
st.header("Revision Section")

revision_pasted_content = st.text_area("Paste Content to Revise Here:")
revision_requests = st.text_area("Specify Revisions Here:")

if st.button("Revise Further"):
    revision_prompt = f"Revise the following content according to the specified revisions.\nRevisions: {revision_requests}\n\nContent:\n{revision_pasted_content}"

    revision_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": revision_prompt}
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=revision_messages, max_tokens=1500)
    revised_content = response.choices[0].message["content"].strip()
    st.text(revised_content)
    st.download_button("Download Revised Content", revised_content, "revised_content_revision.txt")
    # Optionally insert the revised content back into the HTML structure and allow downloading
    revised_html_chunks = []
    html_chunks = chunk_html(revision_pasted_content)
    for chunk in html_chunks:
        revised_html_chunks.append(insert_revised_text_to_html(chunk, revised_content))
    revised_html = ''.join(revised_html_chunks)
    st.download_button("Download Revised HTML", revised_html, "revised_content_revision.html")
