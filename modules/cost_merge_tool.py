import streamlit as st
import pandas as pd
from utils.helpers import parse_csv_upload, df_to_download_bytes

EXAMPLE_HELP = """Upload two CSVs (Buyer & Target) with cost data.
Required columns (flexible names allowed, just map them below):
- cost_center / gl_account / amount / currency / system
"""

def render():
    st.header("💸 Cost Merge Tool")
    st.write("Normalize and merge Buyer/Target cost data to see a combined view and spot quick-win synergies.")
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

        # Simple pivot to summarize
        summary = (
            merged
            .groupby(["_system", "_gl", "_source"], dropna=False)["_amount"]
            .sum().reset_index()
            .rename(columns={"_system":"system","_gl":"gl_account","_source":"source","_amount":"amount"})
        )

        st.success("✅ Merged")
        st.dataframe(summary, use_container_width=True)

        st.download_button(
            "⬇️ Download merged summary (.csv)",
            data=df_to_download_bytes(summary),
            file_name="cost_merge_summary.csv",
            mime="text/csv",
            use_container_width=True
        )
