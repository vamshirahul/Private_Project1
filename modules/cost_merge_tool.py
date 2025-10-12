import io, zipfile
import streamlit as st
import pandas as pd
from utils.helpers import parse_csv_upload, df_to_download_bytes, new_job_id, save_artifact, record_dataset

EXAMPLE_HELP = """Upload two CSVs (Buyer & Target) with cost data.
Required columns (flexible names allowed; just map them below):
- cost_center / gl_account / amount / currency / system
"""

def make_export_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()

def render():
    st.header("💸 Cost Merge Tool")
    st.caption("Normalize Buyer/Target cost data → merged summary & synergy hints.")
    st.info(EXAMPLE_HELP)

    col1, col2 = st.columns(2)
    with col1:
        f1 = st.file_uploader("Buyer Cost CSV", type=["csv"], key="buyer")
    with col2:
        f2 = st.file_uploader("Target Cost CSV", type=["csv"], key="target")

    if not f1 or not f2:
        st.caption("Upload both CSVs to proceed.")
        return

    buyer = parse_csv_upload(f1)
    target = parse_csv_upload(f2)

    st.subheader("Column Mapping")
    all_cols = sorted(list(set(buyer.columns.tolist() + target.columns.tolist())))
    map_cost_center = st.selectbox("Cost Center column", options=all_cols)
    map_gl = st.selectbox("GL/Account column", options=all_cols)
    map_amount = st.selectbox("Amount column", options=all_cols)
    map_system = st.selectbox("System/App column", options=all_cols)

    if st.button("Merge & Normalize", use_container_width=True):
        # Lightweight normalization
        for df, who in [(buyer, "Buyer"), (target, "Target")]:
            df["_source"] = who
            df["_cost_center"] = df[map_cost_center].astype(str)
            df["_gl"] = df[map_gl].astype(str)
            df["_amount"] = pd.to_numeric(df[map_amount], errors="coerce").fillna(0.0)
            df["_system"] = df[map_system].astype(str)

        merged = pd.concat([buyer, target], ignore_index=True)

        # Summary pivot
        summary = (
            merged
            .groupby(["_system", "_gl", "_source"], dropna=False)["_amount"]
            .sum().reset_index()
            .rename(columns={"_system":"system","_gl":"gl_account","_source":"source","_amount":"amount"})
            .sort_values(["system","gl_account","source"])
        )

        # KPI row
        r1, r2, r3 = st.columns(3)
        with r1: st.markdown(f'<div class="kpi">📄 Buyer rows<br><b>{len(buyer):,}</b></div>', unsafe_allow_html=True)
        with r2: st.markdown(f'<div class="kpi">📄 Target rows<br><b>{len(target):,}</b></div>', unsafe_allow_html=True)
        with r3: st.markdown(f'<div class="kpi">🔗 Unique systems<br><b>{summary["system"].nunique()}</b></div>', unsafe_allow_html=True)

        # Output card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### ✅ Merged Summary")
        st.dataframe(summary, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Downloads
        csv_bytes = df_to_download_bytes(summary)
        st.download_button("⬇️ Download merged summary (.csv)",
                           data=csv_bytes, file_name="cost_merge_summary.csv",
                           mime="text/csv", use_container_width=True)

        # Export pack
        export_zip = make_export_zip({
            "cost_merge_summary.csv": csv_bytes,
            "mapping.json": str({
                "cost_center": map_cost_center,
                "gl_account": map_gl,
                "amount": map_amount,
                "system": map_system
            }).encode("utf-8")
        })
        st.download_button("📦 Download Export Pack (.zip)", data=export_zip,
                           file_name="cost_merge_pack.zip", mime="application/zip", use_container_width=True)

        # Artifacts + dataset
        job_id = new_job_id("cost_merge")
        path_csv = save_artifact(job_id, "cost_merge_summary.csv", csv_bytes)
        if st.session_state.get("capture_outputs", False):
            record_dataset(
                module="cost_merge",
                job_id=job_id,
                inputs={
                    "buyer_filename": getattr(f1, "name", "buyer.csv"),
                    "target_filename": getattr(f2, "name", "target.csv"),
                    "map_cost_center": map_cost_center,
                    "map_gl": map_gl,
                    "map_amount": map_amount,
                    "map_system": map_system,
                },
                output_text=summary.to_csv(index=False),
                artifacts={"summary_csv": path_csv},
                quality="unreviewed"
            )
