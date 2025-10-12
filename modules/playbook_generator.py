import math
import streamlit as st
from openai import OpenAI
from utils.prompts import PLAYBOOK_SYSTEM, PLAYBOOK_USER, PLAYBOOK_DETAILED_USER
from utils.helpers import text_to_bytes, get_api_key

def _get_client():
    api_key = get_api_key(st)
    if not api_key:
        st.error("Missing OPENAI_API_KEY (set in .streamlit/secrets.toml or environment).")
        return None
    return OpenAI(api_key=api_key)

def _clean_app_list(raw: str):
    items = [a.strip() for a in raw.replace("\r", "\n").replace(",", "\n").split("\n")]
    return [a for a in items if a]

def render():
    st.header("🧩 Integration Playbook Generator")
    st.caption("Standard summary mode + Advanced per-application mode")

    tab_standard, tab_advanced = st.tabs(["⭐ Standard Mode", "🛠 Advanced Mode"])

    # -------------------------
    # STANDARD MODE (existing)
    # -------------------------
    with tab_standard:
        st.write("Generate a concise playbook across key workstreams.")
        with st.form("pg_form_standard"):
            company_name = st.text_input("Company Name")
            company_size = st.selectbox("Company Size", ["Small", "Mid-size", "Large"])
            key_systems = st.text_area("Key Systems (comma- or newline-separated)")
            day1_priority = st.text_area("Day-1 Priorities")
            integration_approach = st.selectbox("Integration Approach", ["Full Integration", "Phased", "Hybrid"])
            timeline = st.text_input("Integration Timeline (e.g., 30/60/90 or 100 days)")
            submitted = st.form_submit_button("Generate Playbook")

        if submitted:
            client = _get_client()
            if not client:
                return

            apps = _clean_app_list(key_systems)
            user_prompt = PLAYBOOK_USER.format(
                company_name=company_name.strip(),
                company_size=company_size,
                key_systems=", ".join(apps),
                day1_priority=day1_priority.strip(),
                integration_approach=integration_approach,
                timeline=timeline.strip()
            )

            with st.spinner("Generating playbook..."):
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": PLAYBOOK_SYSTEM},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.3,
                )
            md = resp.choices[0].message.content
            st.success("✅ Playbook generated")
            st.markdown(md)
            st.download_button("⬇️ Download Playbook (.md)", data=text_to_bytes(md),
                               file_name="integration_playbook.md", mime="text/markdown", use_container_width=True)

    # -------------------------
    # ADVANCED MODE (per-app)
    # -------------------------
    with tab_advanced:
        st.write("Create a **mini-plan per application** (scaled, batched generation).")

        with st.form("pg_form_advanced"):
            company_name_a = st.text_input("Company Name", key="adv_name")
            company_size_a = st.selectbox("Company Size", ["Small", "Mid-size", "Large"], key="adv_size")
            apps_text = st.text_area(
                "Applications list (comma or newline separated)",
                placeholder="SAP ECC\nSalesforce\nWorkday\nServiceNow\nJD Edwards\n...",
                height=200,
                key="adv_apps",
            )
            integration_approach_a = st.selectbox("Integration Approach", ["Full Integration", "Phased", "Hybrid"], key="adv_appr")
            timeline_a = st.text_input("Overall Integration Timeline", value="100 days", key="adv_time")

            st.markdown("**Generation Controls**")
            col1, col2, col3 = st.columns(3)
            with col1:
                batch_size = st.number_input("Batch size (apps per call)", min_value=10, max_value=50, value=25, step=5)
            with col2:
                model_name = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini"], index=0)
            with col3:
                temperature = st.slider("Creativity (temperature)", 0.0, 1.0, 0.3, 0.1)

            submitted_a = st.form_submit_button("Generate Detailed Per-App Playbook")

        if submitted_a:
            apps = _clean_app_list(apps_text)
            if not apps:
                st.error("Please provide at least one application.")
                return

            client = _get_client()
            if not client:
                return

            # Batch the apps for scalability
            batches = [apps[i:i+int(batch_size)] for i in range(0, len(apps), int(batch_size))]
            progress = st.progress(0, text=f"Generating {len(apps)} apps in {len(batches)} batch(es)...")
            results = []
            total = len(batches)

            for idx, group in enumerate(batches, start=1):
                apps_block = "\n".join(group)
                user_prompt = PLAYBOOK_DETAILED_USER.format(
                    applications=apps_block,
                    company_name=company_name_a.strip(),
                    company_size=company_size_a,
                    integration_approach=integration_approach_a,
                    timeline=timeline_a.strip(),
                    app_name="{app_name}"  # not used directly; kept for clarity/template
                )
                with st.spinner(f"Batch {idx}/{total}…"):
                    resp = client.chat.completions.create(
                        model=model_name,
                        messages=[
                            {"role": "system", "content": PLAYBOOK_SYSTEM},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=temperature,
                    )
                results.append(resp.choices[0].message.content)
                progress.progress(idx / total, text=f"Completed {idx}/{total} batches")

            # Combine and present
            st.success("✅ Detailed per-application playbook generated")
            final_md = "\n\n---\n\n".join(results)

            # Optional front matter: simple ToC (app names list)
            st.markdown("### Table of Contents")
            st.markdown("\n".join([f"- {a}" for a in apps]))

            st.markdown("### Detailed Plan")
            st.markdown(final_md)

            st.download_button("⬇️ Download Detailed Playbook (.md)",
                               data=text_to_bytes(final_md),
                               file_name="integration_playbook_detailed.md",
                               mime="text/markdown",
                               use_container_width=True)
