import json
import streamlit as st
from openai import OpenAI
from utils.prompts import INVOICE_JSON_INSTRUCTIONS

def render():
    st.header("🧾 Invoice Parser")
    st.write("Extract structured fields from invoice text. (Starter version: paste text or OCR output.)")

    txt = st.text_area("Paste invoice text here (or copy OCR output)", height=220)
    if st.button("Extract JSON", width='stretch', disabled=not txt.strip()):
        if not st.secrets.get("OPENAI_API_KEY"):
            st.error("Missing OPENAI_API_KEY in .streamlit/secrets.toml")
            return
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        messages = [
            {"role":"system","content":"You extract structured data from invoices."},
            {"role":"user","content": INVOICE_JSON_INSTRUCTIONS + "\n\nINVOICE TEXT:\n" + txt}
        ]
        with st.spinner("Parsing..."):
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.0,
            )
        raw = resp.choices[0].message.content

        try:
            data = json.loads(raw)
            st.json(data)
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(data, indent=2),
                file_name="invoice.json",
                mime="application/json",
                width='stretch'
            )
        except Exception:
            st.error("Model did not return valid JSON. Try again or adjust the text.")
            st.code(raw)
