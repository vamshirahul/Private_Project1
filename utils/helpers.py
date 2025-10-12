# utils/helpers.py
from __future__ import annotations
import os, io, json, uuid, datetime, re, pathlib
from typing import Optional, Dict, Any
import pandas as pd

# =========================
# Basic file/data utilities
# =========================
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
        prof.append({
            "column": col,
            "dtype": str(s.dtype),
            "nulls": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True)),
        })
    return pd.DataFrame(prof)

def readiness_score_from_profile(profile_df: pd.DataFrame) -> int:
    if profile_df.empty:
        return 30
    # naïve heuristic: fewer nulls & reasonable uniqueness => higher score
    total_nulls = profile_df["nulls"].sum()
    total_uniques = profile_df["unique"].sum()
    null_ratio = total_nulls / max(1, total_nulls + total_uniques)
    base = int(80 * (1 - null_ratio)) + 20
    return max(0, min(100, base))

# =========================
# API key helper (secrets/env)
# =========================
def get_api_key(st=None) -> Optional[str]:
    # Try Streamlit secrets first (if available), then environment
    try:
        if st is not None:
            k = st.secrets.get("OPENAI_API_KEY")
            if k:
                return k
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")

# =========================
# Artifacts & dataset logging
# =========================
ARTIFACT_ROOT = "artifacts"  # generated files per run
DATASET_ROOT = "knowledge_base/_datasets/qa_pairs"  # JSONL capture dir

def ensure_dirs():
    pathlib.Path(ARTIFACT_ROOT).mkdir(parents=True, exist_ok=True)
    pathlib.Path(DATASET_ROOT).mkdir(parents=True, exist_ok=True)

def new_job_id(prefix: str) -> str:
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{ts}_{uuid.uuid4().hex[:8]}"

def safe_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")

def save_artifact(job_id: str, filename: str, data: bytes) -> str:
    """
    Save a file under artifacts/<job_id>/<filename> and return the path.
    """
    ensure_dirs()
    subdir = os.path.join(ARTIFACT_ROOT, job_id)
    pathlib.Path(subdir).mkdir(parents=True, exist_ok=True)
    path = os.path.join(subdir, safe_name(filename))
    with open(path, "wb") as f:
        f.write(data)
    return path

def append_jsonl(record: Dict[str, Any], dataset_dir: str = DATASET_ROOT) -> str:
    ensure_dirs()
    day = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    path = os.path.join(dataset_dir, f"{day}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path

def record_dataset(
    module: str,
    job_id: str,
    inputs: Dict[str, Any],
    output_text: str,
    context_text: Optional[str] = None,
    artifacts: Optional[Dict[str, str]] = None,
    quality: str = "unreviewed",
    app_version: str = "0.1.0",
) -> str:
    """
    Append a JSONL record for later RAG eval / fine-tuning.
    """
    rec = {
        "module": module,
        "job_id": job_id,
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "inputs": inputs,
        "context": context_text,
        "output": output_text,
        "artifacts": artifacts or {},
        "quality": quality,
        "app_version": app_version,
    }
    return append_jsonl(rec)

# =========================
# (Optional) RAG helper to call your backend /search
# =========================
def rag_context(question: str, tags=None, k=6, base_url="http://localhost:8000"):
    """
    Fetch top-k chunks from the RAG backend. Returns (context_block_str, raw_hits_list).
    """
    import requests
    params = {"q": question, "k": k}
    if tags:
        params["tags"] = ",".join(tags) if isinstance(tags, (list, tuple)) else str(tags)
    r = requests.get(f"{base_url}/search", params=params, timeout=30)
    r.raise_for_status()
    hits = r.json()
    ctx = "\n\n".join([f"[CTX {i+1} | score={h['score']:.3f}]\n{h['text']}" for i, h in enumerate(hits)])
    return ctx, hits

def load_lottie(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
