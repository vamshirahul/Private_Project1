import streamlit as st
from utils.helpers import parse_csv_upload, simple_profile, readiness_score_from_profile
import pandas as pd

def render():
    st.header("🚦 Data Migration Readiness Checker")
    st.write("Upload sample extracts from a source system to quickly assess readiness.")

    f = st.file_uploader("Upload source extract (.csv)", type=["csv"])
    if not f:
        st.caption("Provide a CSV extract to continue.")
        return

    df = parse_csv_upload(f)
    st.subheader("Preview")
    st.dataframe(df.head(50), use_container_width=True)

    profile = simple_profile(df)
    st.subheader("Data Profile")
    st.dataframe(profile, use_container_width=True)

    # Very basic scoring + narrative (improve later with LLM)
    score = readiness_score_from_profile(profile)
    st.metric("Readiness Score", f"{score}/100")

    st.markdown("### Quick Readout")
    if score >= 80:
        st.success("High readiness. Minimal cleansing expected; validate PII and interface cutover plan.")
    elif score >= 60:
        st.warning("Moderate readiness. Address nulls in key columns and verify mapping to target CoA/system.")
    else:
        st.error("Low readiness. Prioritize profiling, dedupe, and mandatory fields completion before migration.")
