import os
import json
import time
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
import datetime 
import re

from domain.context import Context


st.set_page_config(page_title="Execution Tree Viewer", layout="wide")
st.title("Execution Tree Viewer — execution")


# Inputs
# prefer environment variable, fallback to repo-local path used in this workspace
DUMP_PATH = os.environ.get('OCP_EXEC_DUMP') or "C:\\Users\\BRKEY864393\\OneDrive - Anheuser-Busch InBev\\My Documents\\projetos\\ocp\\ocp_score_ia\\data\\output\\execution.json"

# allow user upload as fallback (visible in UI for debugging)
uploaded = None #st.file_uploader("Ou carregue um dump JSON (opcional)", type=["json"])

if 'ctx' not in st.session_state:
    st.session_state.ctx = None

if uploaded is not None and st.session_state.ctx is None:
    # create a minimal Context if user uploaded a full JSON (optional)
    if Context is not None:
        try:
            # write uploaded to temp file and instantiate Context with it
            tmp = Path(st.secrets.get('TMP_UPLOAD_DIR', '.')) / f"_ocp_uploaded_{int(time.time())}.json"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            with open(tmp, 'wb') as f:
                f.write(uploaded.getvalue())
            st.session_state.ctx = Context(json_path=str(tmp))
        except Exception:
            st.session_state.ctx = None

if st.session_state.ctx is None and Context is not None and DUMP_PATH is None:
    # create an empty context so the app can call get_execution_tree if needed
    try:
        st.session_state.ctx = Context()
    except Exception:
        st.session_state.ctx = None

ctx = st.session_state.ctx

# --- Clear dump file on first load (start fresh) --------------------------------
# if DUMP_PATH and 'dump_cleared' not in st.session_state:
#     try:
#         p = Path(DUMP_PATH)
#         if p.exists():
#             try:
#                 p.unlink()
#                 st.info(f"Dump file removed to start fresh: {DUMP_PATH}")
#             except Exception:
#                 # ignore removal errors
#                 pass
#     finally:
#         st.session_state['dump_cleared'] = True


def read_payload():
    # 1) prefer env dump file
    if DUMP_PATH:
        try:
            p = Path(DUMP_PATH)
            if p.exists():
                with open(p, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"__error__": f"dump file not found: {DUMP_PATH}"}
        except Exception as e:
            return {"__error__": str(e)}

    # 2) uploaded file
    if uploaded is not None:
        try:
            return json.loads(uploaded.getvalue())
        except Exception as e:
            return {"__error__": f"uploaded file invalid JSON: {e}"}

    # 3) Context instance
    if ctx is not None:
        try:
            if hasattr(ctx, 'get_execution_tree'):
                return ctx.get_execution_tree()
            return getattr(ctx, 'execution_tree', None)
        except Exception as e:
            return {"__error__": str(e)}

    return {}


def _collect_executed_nodes(root: dict) -> list:
    out = []
    def dfs(n):
        try:
            status = (n.get('Status') or '').lower()
            if status in ('ended', 'error'):
                out.append(n)
        except Exception:
            pass
        for c in n.get('Children', []) or []:
            dfs(c)
    if isinstance(root, dict):
        dfs(root)
    return out

def _collect_all_nodes(root: dict) -> list:
    out = []
    def dfs(n):
        try:
            status = (n.get('Status') or '').lower()
            out.append(n)
        except Exception:
            pass
        for c in n.get('Children', []) or []:
            dfs(c)
    if isinstance(root, dict):
        dfs(root)
    return out

def _fmt_time(v) -> str:
    """Return hh:mm:ss representation for a value v.
    Handles numeric epoch (seconds), ISO-like strings and raw strings containing HH:MM:SS.
    """
    if v is None:
        return ""
    # numeric epoch
    try:
        if isinstance(v, (int, float)):
            return datetime.fromtimestamp(float(v)).strftime("%H:%M:%S")
    except Exception:
        pass

    # strings: try to extract a HH:MM:SS portion first
    if isinstance(v, str):
        m = re.search(r"(\d{2}:\d{2}:\d{2})", v)
        if m:
            return m.group(1)
        # try ISO parse
        try:
            s = v.split("+")[0].split("Z")[0]
            # allow both 'YYYY-MM-DDTHH:MM:SS' and 'YYYY-MM-DD HH:MM:SS'
            s = s.replace(" ", "T")
            dt = datetime.fromisoformat(s)
            return dt.strftime("%H:%M:%S")
        except Exception:
            # fallback to original string (trimmed)
            return v.strip()

    # fallback
    try:
        return str(v)
    except Exception:
        return ""
    
def _find_deepest_started_path(root: dict) -> list:
    best = []
    def dfs(node, path):
        nonlocal best
        cur = path + [node]
        status = (node.get('Status') or '').lower()
        if status == 'started':
            if len(cur) > len(best):
                best = cur
        for c in node.get('Children', []) or []:
            dfs(c, cur)
    if isinstance(root, dict):
        dfs(root, [])
    return best


def render_layout(payload: dict):
    left_col, mid_col, right_col = st.columns([1.5, 2, 1])

    # executed = _collect_all_nodes(payload) if isinstance(payload, dict) else []
    executed = _collect_all_nodes(payload) if isinstance(payload, dict) else []
    started_path = _find_deepest_started_path(payload) if isinstance(payload, dict) else []
    
    with left_col:
        st.subheader("Execucao das regras")
        if not executed:
            st.info("Nenhuma regra finalizada encontrada")
        else:
            rows = []
            for n in executed:
                rows.append({
                    "Rule": n.get('Rule'),
                    "Type": n.get('TypeRule'),
                    "Start": _fmt_time(n.get('Start')) ,
                    "End": _fmt_time(n.get('End')),
                    "Status": _fmt_time(n.get('Status'))
                })
            st.table(sorted(rows, key=lambda x: x.get('Start'), reverse=True))

    with mid_col:
        st.subheader("Em andamento")
        if not started_path:
            st.info("Nenhuma regra em andamento")
        else:
            for i, n in enumerate(started_path):
                is_current = (i == len(started_path) - 1)
                label = f"{n.get('Rule')}" + (" — current" if is_current else "")
                if is_current:
                    st.markdown(f"**{label}**")
                    st.write({
                        "Start": n.get('Start'),
                        "Status": n.get('Status'),
                        "Logs": n.get('Logs', [])
                    })
                else:
                    st.write(label)

    with right_col:
        st.subheader("Reservado")
        st.write("")



# Controls: Auto-refresh via streamlit-autorefresh (recommended)
auto_refresh = st.checkbox("Auto-refresh (poll every N seconds)", value=True)
interval = st.number_input("Intervalo (s)", min_value=1, max_value=10, value=1)

if auto_refresh:
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=interval * 1000, key="auto_rt")
    except Exception:
        # fallback: small client-side reload (full page reload)
        js = f"<script>setTimeout(()=>window.location.reload(), {int(interval)*1000});</script>"
        components.html(js, height=0)

payload = read_payload()
with st.expander("Payload (raw)", expanded=False):
    st.write(payload)

try:
    render_layout(payload)
except Exception as e:
    st.exception(e)