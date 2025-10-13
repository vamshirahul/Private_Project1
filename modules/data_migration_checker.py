import io, zipfile, re, json
import pandas as pd
import streamlit as st

from utils.helpers import (
    parse_csv_upload,
    simple_profile,
    readiness_score_from_profile,
    new_job_id,
    save_artifact,
    record_dataset,
    df_to_download_bytes,
    text_to_bytes,
)

# ---------------------------
# Helpers: new feature blocks
# ---------------------------

def infer_roles(df: pd.DataFrame):
    roles = {c: [] for c in df.columns}
    for c in df.columns:
        lc = c.lower()
        if re.search(r'(id|number|code)\b', lc):
            roles[c].append('id')
        if re.search(r'(date|dt|updated|created)', lc):
            roles[c].append('date')
        if re.search(r'email', lc):
            roles[c].append('email')
        if re.search(r'(amount|balance|qty|quantity|price|total)', lc):
            roles[c].append('amount')
        if re.search(r'(phone|mobile|tel)', lc):
            roles[c].append('phone')
    return roles

def id_quality(df: pd.DataFrame, key_col: str):
    nulls = int(df[key_col].isna().sum())
    dups_mask = df[key_col].duplicated(keep=False)
    dups = int(dups_mask.sum())
    unique_ratio = float(df[key_col].nunique() / len(df)) if len(df) else 0.0
    # also return offending row indexes for fix-list
    dup_rows = df.index[dups_mask].tolist()
    null_rows = df[df[key_col].isna()].index.tolist()
    return {
        "nulls": nulls,
        "dups": dups,
        "unique_ratio": unique_ratio,
        "dup_rows": dup_rows,
        "null_rows": null_rows,
    }

def readiness_subscores(profile: pd.DataFrame | dict, df: pd.DataFrame):
    """
    Compute sub-scores that roll up to an overall 0-100 readiness.
    Expects the profile to expose some aggregate metrics; falls back to defaults if missing.
    """
    # Try to read aggregates from a dict-like profile (graceful fallbacks)
    overall_null_rate   = float(profile.get("overall_null_rate", 0.05)) if isinstance(profile, dict) else 0.05
    type_consistency    = float(profile.get("type_consistency", 0.90))   if isinstance(profile, dict) else 0.90
    avg_unique_ratio    = float(profile.get("avg_unique_ratio_keys", 0.95)) if isinstance(profile, dict) else 0.95
    avg_valid_ratio     = float(profile.get("avg_valid_ratio", 0.90))    if isinstance(profile, dict) else 0.90
    freshness_ratio     = float(profile.get("freshness_ratio", 0.80))    if isinstance(profile, dict) else 0.80

    weights = dict(completeness=30, consistency=25, uniqueness=20, validity=15, freshness=10)

    completeness = max(0.0, 100.0 * (1.0 - overall_null_rate))
    consistency  = max(0.0, 100.0 * type_consistency)
    uniqueness   = max(0.0, 100.0 * avg_unique_ratio)
    validity     = max(0.0, 100.0 * avg_valid_ratio)
    freshness    = max(0.0, 100.0 * freshness_ratio)

    score = round(
        completeness * weights['completeness']/100 +
        consistency  * weights['consistency']/100 +
        uniqueness   * weights['uniqueness']/100 +
        validity     * weights['validity']/100 +
        freshness    * weights['freshness']/100
    )

    return dict(
        score=score,
        completeness=round(completeness, 1),
        consistency=round(consistency, 1),
        uniqueness=round(uniqueness, 1),
        validity=round(validity, 1),
        freshness=round(freshness, 1),
    )

def validate_against_schema(df: pd.DataFrame, schema_json: str) -> pd.DataFrame:
    """
    schema_json example:
    [
      {"name":"Customer_ID","dtype":"string","required":true,"enum":null,"regex":null},
      {"name":"Country","dtype":"string","required":false,"enum":["USA","UK","Canada"],"regex":null}
    ]
    """
    schema = json.loads(schema_json)
    results = []
    for coldef in schema:
        name = coldef['name']
        required = bool(coldef.get('required', False))
        enum = coldef.get('enum')
        regex = coldef.get('regex')

        present = name in df.columns
        nulls = int(df[name].isna().sum()) if present else None

        enum_viol = None
        regex_viol = None
        enum_bad_rows = []
        regex_bad_rows = []

        if present and enum:
            isin = df[name].isin(enum)
            enum_viol = int((~isin).fillna(False).sum())
            enum_bad_rows = df.index[(~isin).fillna(False)].tolist()

        if present and regex:
            pat = re.compile(regex)
            ok = df[name].astype(str).apply(lambda x: bool(pat.fullmatch(x)) if x not in (None, "", "nan") else True)
            regex_viol = int((~ok).fillna(False).sum())
            regex_bad_rows = df.index[(~ok).fillna(False)].tolist()

        results.append(dict(
            column=name,
            present=present,
            required=required,
            nulls=nulls,
            enum_violations=enum_viol,
            regex_violations=regex_viol,
            enum_bad_rows=enum_bad_rows,
            regex_bad_rows=regex_bad_rows,
        ))
    return pd.DataFrame(results)

def eval_rules(df: pd.DataFrame, rules_df: pd.DataFrame) -> pd.DataFrame:
    """
    rules.csv columns: condition, expectation, message
    Example:
      condition: Country in ['USA','CA']
      expectation: Phone.str.startswith('+1')
      message: NA phone prefix for North America
    """
    violations = []
    for _, r in rules_df.iterrows():
        try:
            mask_cond = df.eval(r['condition'])
            mask_ok = df.eval(r['expectation'])
            bad = mask_cond & ~mask_ok
            idx = df.index[bad].tolist()
            if idx:
                violations.append({"rule": r['message'], "rows": idx, "count": len(idx)})
        except Exception as e:
            violations.append({"rule": f"Rule error: {r.get('message','(unnamed rule)')}", "rows": [], "count": 0, "error": str(e)})
    return pd.DataFrame(violations)

def build_fix_list(df: pd.DataFrame, validators_output: dict, rule_violations_df: pd.DataFrame) -> pd.DataFrame:
    """
    validators_output: dict like
      {
        "Customer_ID": {"issue": "Duplicate IDs", "rows": [1,7,9]},
        "Customer_ID": {"issue": "Null IDs", "rows": [3]},
        "Country": {"issue":"Invalid enum value", "rows":[2,5]}
      }
    """
    rows = []
    for col, probs in validators_output.items():
        issue = probs.get("issue")
        for r in probs.get("rows", [])[:10000]:  # cap file size
            rows.append({"row_index": r, "column": col, "issue": issue})
    if isinstance(rule_violations_df, pd.DataFrame) and not rule_violations_df.empty:
        for _, v in rule_violations_df.iterrows():
            for r in v.get("rows", [])[:10000]:
                rows.append({"row_index": r, "column": None, "issue": v.get("rule")})
    return pd.DataFrame(rows)

def make_export_zip(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    return buf.getvalue()

# -------------
# Main render()
# -------------
def render():
    st.header("🚦 Data Migration Readiness Checker")
    st.caption("Profile a source extract → readiness score, profile table, export pack.")

    # Upload CSV
    f = st.file_uploader("Upload source extract (.csv)", type=["csv"])
    if not f:
        st.caption("Provide a CSV extract to continue.")
        return

    # Parse CSV using your existing helper (unchanged behavior)
    df = parse_csv_upload(f)

    # KPI strip
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="kpi">📄 Rows<br><b>{len(df):,}</b></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="kpi">🧱 Columns<br><b>{len(df.columns):,}</b></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="kpi">📂 File<br><b>{getattr(f,"name","source.csv")}</b></div>', unsafe_allow_html=True)

    # Profile + original readiness score (kept)
    profile = simple_profile(df)
    score = readiness_score_from_profile(profile)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("✅ Readiness Result")
    st.metric("Readiness Score", f"{score}/100")

    st.subheader("Data Profile")
    st.dataframe(profile, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick readout (kept)
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

    # ----------------------------
    # New: Optional analysis block
    # ----------------------------
    st.divider()
    st.subheader("🔧 Optional Analysis")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        detect_roles = st.checkbox("Detect column roles", value=True)
    with c2:
        run_schema_validation = st.checkbox("Validate against target schema", value=False)
    with c3:
        run_rules = st.checkbox("Apply business rules", value=False)
    with c4:
        show_subscores = st.checkbox("Show component scores", value=True)

    # Role detection + key checks
    validators_output = {}

    if detect_roles:
        st.write("#### Detected Column Roles")
        roles = infer_roles(df)
        st.json(roles)

        # For any inferred ID column, run simple key-quality checks and collect rows for fix-list
        for col, tags in roles.items():
            if 'id' in tags:
                quality = id_quality(df, col)
                st.write(f"**Key quality for `{col}`** → nulls: {quality['nulls']}, dups: {quality['dups']}, unique_ratio: {quality['unique_ratio']:.3f}")

                if quality["dups"] > 0:
                    validators_output[f"{col}__dup"] = {"issue": f"Duplicate keys in {col}", "rows": quality["dup_rows"]}
                if quality["nulls"] > 0:
                    validators_output[f"{col}__null"] = {"issue": f"Null keys in {col}", "rows": quality["null_rows"]}

    # Schema validation (optional)
    validation_df = pd.DataFrame()
    if run_schema_validation:
        schema_file = st.file_uploader("Upload target schema (JSON)", type=["json"], key="schema_upl")
        if schema_file:
            schema_json = schema_file.read().decode("utf-8")
            validation_df = validate_against_schema(df, schema_json)
            st.write("#### Schema Validation Results")
            st.dataframe(validation_df, use_container_width=True)

            # Add invalid rows to validators_output for fix-list
            for _, r in validation_df.iterrows():
                col = r["column"]
                enum_rows = r.get("enum_bad_rows")
                if isinstance(enum_rows, (list, tuple)) and len(enum_rows) > 0:
                    validators_output[f"{col}__enum"] = {"issue": f"Invalid enum values in {col}", "rows": enum_rows}

                regex_rows = r.get("regex_bad_rows")
                if isinstance(regex_rows, (list, tuple)) and len(regex_rows) > 0:
                    validators_output[f"{col}__regex"] = {"issue": f"Regex violations in {col}", "rows": regex_rows}

                if bool(r.get("required")) and (r.get("present") is False):
                    validators_output[f"{col}__missing"] = {"issue": f"Required column {col} missing", "rows": []}


    # Rules engine (optional)
    rule_violations = pd.DataFrame()
    if run_rules:
        rules_file = st.file_uploader("Upload rules file (.csv)", type=["csv"], key="rules_upl")
        if rules_file:
            rules_df = pd.read_csv(rules_file)
            st.write("#### Loaded Rules")
            st.dataframe(rules_df, use_container_width=True)

            rule_violations = eval_rules(df, rules_df)
            st.write("#### Rule Violations")
            st.dataframe(rule_violations, use_container_width=True)

            if not rule_violations.empty:
                st.download_button(
                    "⬇️ Download Violations CSV",
                    rule_violations.to_csv(index=False).encode("utf-8"),
                    "rule_violations.csv",
                    "text/csv",
                    use_container_width=True,
                )

    # Sub-scores (optional visualization)
    if show_subscores:
        try:
            subscores = readiness_subscores(profile if isinstance(profile, dict) else {}, df)
            st.write("#### Component Scores")
            st.write(subscores)
            # Light-weight bar chart for visibility without extra deps
            subs_df = pd.DataFrame(
                [{"component": k.capitalize(), "score": v}
                 for k, v in subscores.items() if k != "score"]
            )
            st.bar_chart(subs_df.set_index("component"))
        except Exception as e:
            st.info(f"Component scores unavailable: {e}")

    # --------------------------
    # Downloads (kept + extras)
    # --------------------------
    st.divider()
    st.subheader("⬇️ Downloads")

    prof_csv = df_to_download_bytes(profile)
    st.download_button(
        "Download profile (.csv)",
        data=prof_csv,
        file_name="readiness_profile.csv",
        mime="text/csv",
        use_container_width=True,
    )

    readout_bytes = text_to_bytes(readout)
    export_zip = make_export_zip({
        "readiness_profile.csv": prof_csv,
        "readout.txt": readout_bytes,
    })
    st.download_button(
        "Download Export Pack (.zip)",
        data=export_zip,
        file_name="readiness_pack.zip",
        mime="application/zip",
        use_container_width=True,
    )

    # New: Fix-list export (if we have anything)
    if validators_output or (isinstance(rule_violations, pd.DataFrame) and not rule_violations.empty):
        st.write("#### Fix List")
        fix_list_df = build_fix_list(df, validators_output, rule_violations)
        if not fix_list_df.empty:
            st.dataframe(fix_list_df.head(50), use_container_width=True)
            st.download_button(
                "Download Fix List (.csv)",
                data=fix_list_df.to_csv(index=False).encode("utf-8"),
                file_name="fix_list.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("No row-level issues to export.")

    # ----------------------------
    # Artifacts + dataset (kept)
    # ----------------------------
    job_id = new_job_id("readiness")
    path_prof = save_artifact(job_id, "profile.csv", prof_csv)
    if st.session_state.get("capture_outputs", False):
        record_dataset(
            module="readiness_checker",
            job_id=job_id,
            inputs={"source_filename": getattr(f, "name", "source.csv")},
            output_text=readout,
            artifacts={"profile_csv": path_prof},
            quality="unreviewed",
        )
