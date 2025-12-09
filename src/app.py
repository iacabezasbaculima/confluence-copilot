import os

import streamlit as st

from confluence_qa import ConfluenceQA

st.set_page_config(
    page_title="Q&A Bot for Confluence Page",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto",
)
if "config" not in st.session_state:
    st.session_state["config"] = {}
if "confluence_qa" not in st.session_state:
    st.session_state["confluence_qa"] = None


@st.cache_resource
def load_confluence(config):
    confluence_qa = ConfluenceQA(config=config)
    confluence_qa.init_embeddings()
    confluence_qa.init_models()
    confluence_qa.vector_db_confluence_docs()
    confluence_qa.retreival_qa_chain()
    return confluence_qa


confluence_url = os.environ.get(
    "CONFLUENCE_URL", "https://templates.atlassian.net/wiki/"
)
confluence_username = os.environ.get("CONFLUENCE_USERNAME", "")
confluence_api_key = os.environ.get("CONFLUENCE_API_KEY", "")
confluence_space_key = os.environ.get("CONFLUENCE_SPACE_KEY", "RD")

with st.sidebar.form(key="Form1"):
    st.markdown("## Add your configs")
    confluence_url = st.text_input("paste the confluence URL", confluence_url)
    username = st.text_input(
        label="confluence username",
        value=confluence_username,
        help="leave blank if confluence page is public",
    )
    space_key = st.text_input(
        label="confluence space", help="Space of Confluence", value=confluence_space_key
    )
    api_key = st.text_input(
        label="confluence api key",
        value=confluence_api_key,
        help="leave blank if confluence page is public",
        type="password",
    )
    submitted1 = st.form_submit_button(label="Submit")

    if submitted1 and confluence_url and space_key:
        st.session_state["config"] = {
            "persist_directory": None,
            "confluence_url": confluence_url,
            "username": username if username != "" else None,
            "api_key": api_key if api_key != "" else None,
            "space_key": space_key,
        }
        with st.spinner(text="Ingesting Confluence..."):
            st.session_state["confluence_qa"] = load_confluence(
                st.session_state["config"]
            )
        st.write("Confluence Space Ingested")


st.title("Confluence Q&A Demo")

question = st.text_input("Ask a question", "How do I make a space public?")

if st.button("Get Answer", key="button2"):
    with st.spinner(text="Asking LLM..."):
        confluence_qa = st.session_state.get("confluence_qa")
        if confluence_qa is not None:
            result = confluence_qa.answer_confluence(question)
            st.write(result)
        else:
            st.write("Please load Confluence page first.")
