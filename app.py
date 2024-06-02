import logging
import streamlit as st
import sys

from rag import get_streamed_rag_query_engine

# ! comment if you don't want to see everything that's happening under the hood
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []


def get_streamed_res(input_prompt: str):
    query_engine = get_streamed_rag_query_engine()
    res = query_engine.query(input_prompt)
    for x in res.response_gen:
        yield x + ""


st.title("technical documentation RAG demo 🤖📚")

# display chat messages history
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# react to user input
if prompt := st.chat_input("Hello 👋"):
    # display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    # add it to chat history
    st.session_state.history.append({"role": "user", "content": prompt})

    # display bot response
    with st.chat_message("assistant"):
        response = st.write_stream(get_streamed_res(prompt))
    # add bot response to history as well
    st.session_state.history.append({"role": "assistant", "content": response})
