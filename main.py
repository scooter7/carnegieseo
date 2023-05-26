import streamlit as st
import openai

openai.api_key = "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"
st.title("SEO Article Writer with ChatGPT")

def generate_article(keyword, writing_style, word_count):
    #return "This is a test article generated without making API calls."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": "Write a SEO optimized word article about " + keyword},
                {"role": "user", "content": "The article should be " + writing_style},
                {"role": "user", "content": "The article length should " + str(word_count)},
            ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result

keyword = st.text_input("Enter a keyword:")
writing_style = st.selectbox("Select writing style:", ["Casual", "Informative", "Witty"])
word_count = st.slider("Select word count:", min_value=300, max_value=1000, step=100, value=300)
submit_button = st.button("Generate Article")

if submit_button:
    message = st.empty()
    message.text("Busy generating...")
    article = generate_article(keyword, writing_style, word_count)
    message.text("")
    st.write(article)
    st.download_button(
        label="Download article",
        data=article,
        file_name= 'Article.txt',
        mime='text/txt',
    )
