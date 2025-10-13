import io, zipfile
import streamlit as st
from utils.helpers import parse_csv_upload, simple_profile, readiness_score_from_profile, new_job_id, save_artifact, record_dataset, df_to_download_bytes, text_to_bytes

def make_export_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()

def render():
    st.header("🚦 Data Migration Readiness Checker")
    st.caption("Profile a source extract → readiness score, profile table, export pack.")

    f = st.file_uploader("Upload source extract (.csv)", type=["csv"])
    if not f:
        st.caption("Provide a CSV extract to continue.")
        return

    df = parse_csv_upload(f)

    # KPI row
    k1,k2,k3 = st.columns(3)
    with k1: st.markdown(f'<div class="kpi">📄 Rows<br><b>{len(df):,}</b></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi">🧱 Columns<br><b>{len(df.columns):,}</b></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi">📂 File<br><b>{getattr(f,"name","source.csv")}</b></div>', unsafe_allow_html=True)

    # Profile
    profile = simple_profile(df)
    score = readiness_score_from_profile(profile)

    # Output card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Readiness Result")
    st.metric("Readiness Score", f"{score}/100")
    st.subheader("Data Profile")
    st.dataframe(profile, width='stretch')
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick readout
    st.markdown("### Quick Readout")
    if score >= 80:
        readout = "High readiness. Minimal cleansing expected; validate PII and interface cutover plan."
        st.success(readout)
    elif score >= 60:
        readout = "Moderate readiness. Address nulls in key columns and verify mapping to target CoA/system."
        st.warning(readout)
    else:
        readout = "Low readiness. Prioritize profiling, dedupe, and mandatory fields completion before migration."
        st.error(readout)

    # Downloads
    prof_csv = df_to_download_bytes(profile)
    st.download_button("⬇️ Download profile (.csv)", data=prof_csv,
                       file_name="readiness_profile.csv", mime="text/csv", width='stretch')

    readout_bytes = text_to_bytes(readout)
    export_zip = make_export_zip({
        "readiness_profile.csv": prof_csv,
        "readout.txt": readout_bytes
    })
    st.download_button("📦 Download Export Pack (.zip)", data=export_zip,
                       file_name="readiness_pack.zip", mime="application/zip", width='stretch')

    # Artifacts + dataset
    job_id = new_job_id("readiness")
    path_prof = save_artifact(job_id, "profile.csv", prof_csv)
    if st.session_state.get("capture_outputs", False):
        record_dataset(
            module="readiness_checker",
            job_id=job_id,
            inputs={"source_filename": getattr(f, "name", "source.csv")},
            output_text=readout,
            artifacts={"profile_csv": path_prof},
            quality="unreviewed"
        )
