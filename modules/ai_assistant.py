import streamlit as st
from openai import OpenAI

SYSTEM = """You are an AI assistant specialized in M&A IT integration.
When asked, reference artifacts produced by other modules (playbooks, cost merges, readiness findings).
Be concise and action-oriented. Return Markdown."""

def render():
    st.header("🤖 AI M&A Assistant")
    if "chat" not in st.session_state:
        st.session_state.chat = []

    for role, content in st.session_state.chat:
        st.chat_message(role).markdown(content)

    user_msg = st.chat_input("Ask anything about integration, cost, migration, Day-1, etc.")
    if not user_msg:
        return

    st.session_state.chat.append(("user", user_msg))
    st.chat_message("user").markdown(user_msg)

    if not st.secrets.get("OPENAI_API_KEY"):
        st.chat_message("assistant").error("Missing OPENAI_API_KEY in .streamlit/secrets.toml")
        return

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    messages = [{"role":"system","content":SYSTEM}] + [
        {"role":r, "content":c} for r,c in st.session_state.chat
    ]
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2,
            )
        reply = resp.choices[0].message.content
        st.markdown(reply)
    st.session_state.chat.append(("assistant", reply))
