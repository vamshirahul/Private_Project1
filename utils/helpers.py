import io
import os
import pandas as pd

def df_to_download_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def text_to_bytes(txt: str) -> bytes:
    return txt.encode("utf-8")

def parse_csv_upload(file) -> pd.DataFrame:
    return pd.read_csv(file)

def simple_profile(df: pd.DataFrame) -> pd.DataFrame:
    prof = []
    for col in df.columns:
        s = df[col]
        nulls = int(s.isna().sum())
        unique = int(s.nunique(dropna=True))
        dtype = str(s.dtype)
        prof.append({"column": col, "dtype": dtype, "nulls": nulls, "unique": unique})
    return pd.DataFrame(prof)

def readiness_score_from_profile(profile_df: pd.DataFrame) -> int:
    # Very simple heuristic starter: fewer nulls & moderate cardinality => higher score
    if profile_df.empty:
        return 30
    null_ratio = profile_df["nulls"].sum() / max(1, profile_df["nulls"].sum() + profile_df["unique"].sum())
    base = int(80 * (1 - null_ratio)) + 20
    return max(0, min(100, base))

def get_api_key(st=None):
    # works with or without Streamlit present
    try:
        if st is not None:
            k = st.secrets.get("OPENAI_API_KEY")
            if k:
                return k
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")

