import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from llm_chains import load_normal_chain, load_pdf_chat_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from streamlit_mic_recorder import speech_to_text
from utils import save_chat_history_json, get_timestamp, load_chat_history_json
from pdf_handler import add_documents_to_db
from html_templates import get_bot_template, get_user_template, css
import yaml
import os
import uuid
import gtts
import playsound
from langdetect import detect
from googletrans import Translator
import asyncio

# ---------------- Load Config ---------------- #
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)


# ---------------- Translation Function ---------------- #
async def translate_to_english(text):
    try:
        translator = Translator()
        lang = detect(text) 
        if lang != "en":
            translated = await translator.translate(text, src=lang, dest="en")
            return translated.text, lang
        else:
            return text, "en"
    except Exception as e:
        print(f"Error during translation: {e}")
        return text, "en"
    
async def translate_to_input_lang(text, target_lang):
    try:
        translator = Translator()
        if target_lang != "en":
            translated = await translator.translate(text, src="en", dest=target_lang)
            return translated.text
        else:
            return text
    except Exception as e:
        print(f"Error during translation to input language: {e}")
        return text

# ---------------- Theme Handling ---------------- #
def toggle_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

def apply_theme():
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"

    if st.session_state.theme == "dark":
        st.markdown("""
            <style>
            html, body, [class*="css"] { background-color: #0e1117 !important; color: white !important; }
            .stApp { background-color: #0e1117 !important; }
            header, .st-emotion-cache-1avcm0n, .st-emotion-cache-18ni7ap { background-color: #0e1117 !important; }
            h1, h2, h3, h4, h5, h6, .stMarkdown p { color: white !important; }
            .stTextInput input { background-color: #1a1c23 !important; color: white !important; border: 1px solid #444 !important; }
            .stButton button { background-color: #262730 !important; color: white !important; border: 1px solid #555 !important; }
            .stSidebar, section[data-testid="stSidebar"] { background-color: #161b22 !important; color: white !important; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            html, body, [class*="css"] { background-color: #ffffff !important; color: black !important; }
            .stApp { background-color: #ffffff !important; }
            header, .st-emotion-cache-1avcm0n, .st-emotion-cache-18ni7ap { background-color: #ffffff !important; }
            h1, h2, h3, h4, h5, h6, .stMarkdown p { color: black !important; }
            .stTextInput input { background-color: #ffffff !important; color: black !important; border: 1px solid #ccc !important; }
            .stButton button { background-color: #f0f0f0 !important; color: black !important; border: 1px solid #aaa !important; }
            .stSidebar, section[data-testid="stSidebar"] { background-color: #f8f9fa !important; color: black !important; }
            </style>
        """, unsafe_allow_html=True)

# ---------------- Core Functions ---------------- #
def load_chain(chat_history):
    if st.session_state.pdf_chat:
        return load_pdf_chat_chain(chat_history)
    return load_normal_chain(chat_history)

def clear_input_field():
    st.session_state.user_question = st.session_state.user_input
    st.session_state.user_input = ""

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def genrate_audio(text):
    audio = gtts.gTTS(text)
    file_path = f"{uuid.uuid4()}.mp3"
    audio.save(file_path)
    playsound.playsound(file_path)
    os.remove(file_path)

def toggle_pdf_chat():
    st.session_state.pdf_chat = True

def save_chat_history():
    if st.session_state.history != []:
        if st.session_state.session_key == "new_session":
            st.session_state.new_session_key = get_timestamp() + ".json"
            save_chat_history_json(
                st.session_state.history,
                config["chat_history_path"] + st.session_state.new_session_key,
            )
        else:
            save_chat_history_json(
                st.session_state.history,
                config["chat_history_path"] + st.session_state.session_key,
            )

# ---------------- Main App ---------------- #
def main():
    
    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        if st.button("☀️" if st.session_state.get("theme", "dark") == "dark" else "🌙"):
            toggle_theme()
    apply_theme()

    st.title("DocuGenie")
    st.write(css, unsafe_allow_html=True)
    chat_container = st.container()
    st.sidebar.title("Chat Sessions")

    chat_sessions = ["new_session"] + os.listdir(config["chat_history_path"])
    if "send_input" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"

    if st.session_state.session_key == "new_session" and st.session_state.new_session_key:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index)
    st.sidebar.toggle("PDF Chat", key="pdf_chat", value=False)

    if st.session_state.session_key != "new_session":
        st.session_state.history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
    else:
        st.session_state.history = []

    chat_history = StreamlitChatMessageHistory(key="history")

    user_input = st.text_input("Type your message here", key="user_input", on_change=set_send_input)

    voice_recording_column, send_button_column = st.columns(2)
    with voice_recording_column:
        voice_recording = speech_to_text(language="en", use_container_width=True, just_once=True, key="STT")
    with send_button_column:
        send_button = st.button("Send", key="send_button", on_click=clear_input_field)

    uploaded_pdf = st.sidebar.file_uploader("Upload a pdf file", accept_multiple_files=True, key="pdf_upload", type=["pdf"], on_change=toggle_pdf_chat)
    if uploaded_pdf:
        with st.spinner("Processing pdf..."):
            add_documents_to_db(uploaded_pdf)

    audio_flag = False
    if voice_recording is not None:
        audio_flag = True
        llm_chain = load_chain(chat_history)
        llm_chain.run(voice_recording)

    # if send_button or st.session_state.send_input:
    #     if st.session_state.user_question != "":
    #         # ------------- Translation ------------- #
    #         translated_text, detected_lang = asyncio.run(translate_to_english(st.session_state.user_question))

    #         if detected_lang != "en":
    #             st.write(f"You have entered the question in **{detected_lang}**.")
    #             st.write(f"Here is the translated version in English:")
    #             st.write(f"**{translated_text}**")

    #         print("Translated Text:", translated_text)
    #         # print("Original Text:", st.session_state.user_question)
    #         print("Detected Language:", detected_lang)

            

    #         # Use a temporary history so it doesn't auto-log twice
    #         temp_history = StreamlitChatMessageHistory(key=str(uuid.uuid4()))
    #         llm_chain = load_chain(temp_history)
    #         llm_response = llm_chain.run(translated_text)

    #         # Add only original + bot reply manually to main chat
    #         chat_history.add_user_message(st.session_state.user_question)
    #         chat_history.add_ai_message(llm_response)

    #         st.session_state.user_question = ""
    #         st.session_state.send_input = False

    if send_button or st.session_state.send_input:
        if st.session_state.user_question != "":
            # ------------- Translation ------------- #
            translated_text, detected_lang = asyncio.run(translate_to_english(st.session_state.user_question))

            if detected_lang != "en":
                st.write(f"You have entered the question in **{detected_lang.upper()}**.")
                st.write(f"Translated to English: **{translated_text}**")

            # Use temporary chat history so it doesn’t double-log
            temp_history = StreamlitChatMessageHistory(key=str(uuid.uuid4()))
            llm_chain = load_chain(temp_history)

            # Get response from LLM (always in English)
            llm_response = llm_chain.run(translated_text)

            # If question was not in English → translate the response to Hindi
            if detected_lang != "en":
                # translator = Translator()
                try:
                    # translated_response = translator.translate(llm_response, src="en", dest="hi").text
                    translated_response = asyncio.run(translate_to_input_lang(llm_response, detected_lang))
                except Exception as e:
                    print("Error translating response:", e)
                    translated_response = "[Translation failed]"

                combined_response = f"**English:** {llm_response}\n\n**Hindi:** {translated_response}"
                chat_history.add_user_message(st.session_state.user_question)
                chat_history.add_ai_message(combined_response)

            else:
                chat_history.add_user_message(st.session_state.user_question)
                chat_history.add_ai_message(llm_response)

            st.session_state.user_question = ""
            st.session_state.send_input = False


    # Display chat messages
    messages_list = []
    if chat_history.messages:
        with chat_container:
            st.write("Chat History:")
            for message in chat_history.messages:
                if message.type == "human":
                    st.write(get_user_template(message.content), unsafe_allow_html=True)
                else:
                    st.write(get_bot_template(message.content), unsafe_allow_html=True)
                    messages_list.append(message.content)

    # Generate audio for last bot message
    if audio_flag and messages_list:
        genrate_audio(messages_list[-1])

    save_chat_history()

# ---------------- Run App ---------------- #
if __name__ == "__main__":
    main()
