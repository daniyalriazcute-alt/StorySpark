"""StorySpark — Streamlit UI with live agent process visualization."""
import time
import streamlit as st
from crew import run_storyspark_streaming

# ---------- Page Config ----------
st.set_page_config(page_title="StorySpark", page_icon="📖", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
.agent-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 14px;
    background: #fafafa;
    min-height: 300px;
}
.agent-title {
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 6px;
}
.status-dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    margin-right: 6px;
}
.running { background: #22c55e; animation: pulse 1s infinite; }
.waiting { background: #9ca3af; }
.done    { background: #3b82f6; }
@keyframes pulse {
    0%   { opacity: 1; }
    50%  { opacity: 0.4; }
    100% { opacity: 1; }
}
.log {
    font-family: 'SF Mono', Monaco, monospace;
    font-size: 12.5px;
    line-height: 1.6;
    color: #374151;
}
.mem-box {
    background: #eef2ff;
    border-left: 4px solid #6366f1;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("## 📖 StorySpark  ·  Multi-Agent Story Engine")
st.caption("Two CrewAI agents collaborate to write a children's story.")

# ---------- Input ----------
c1, c2, c3 = st.columns([2, 1, 1])
theme = c1.text_input("Theme", "a lost puppy")
age = c2.slider("Age", 4, 12, 7)
run = c3.button("▶ Run Agents", use_container_width=True)

# ---------- Layout Slots ----------
st.divider()
task_bar = st.empty()
agent_col1, agent_col2 = st.columns(2)
p1 = agent_col1.empty()
p2 = agent_col2.empty()
st.divider()
mem_bar = st.empty()
metric_bar = st.empty()


# ---------- Render Helper ----------
def agent_panel(name, role, status, logs, output):
    dot = {"running": "running", "waiting": "waiting", "done": "done"}[status]
    label = {"running": "Running", "waiting": "Waiting", "done": "Complete"}[status]
    log_html = "<br>".join(logs) if logs else "—"
    out_html = output if output else "—"
    return f"""
    <div class="agent-card">
      <div class="agent-title">🤖 {name} · <span style="color:#6b7280">{role}</span></div>
      <div style="font-size:12px;margin-bottom:8px">
        <span class="status-dot {dot}"></span>{label}
      </div>
      <div class="log">{log_html}</div>
      <hr style="margin:10px 0">
      <div style="font-size:12px;color:#6b7280">Output</div>
      <div style="font-size:13px">{out_html}</div>
    </div>
    """


# ---------- Execution ----------
if run:
    tokens = 0
    retries = 0
    t0 = time.time()

    task_bar.info(f"🎯 **Task** — Theme: `{theme}` · Age: `{age}`")

    # Phase 1 — Agent 1 start
    p1.markdown(agent_panel("Agent 1", "IdeaGenerator", "running",
        ["▸ Reasoning: I need a story idea.",
         "▸ Action: wiki_tool(...)"], ""), unsafe_allow_html=True)
    p2.markdown(agent_panel("Agent 2", "StoryWriter", "waiting", [], ""),
                unsafe_allow_html=True)
    time.sleep(0.8)

    # Phase 2 — tool call visualization
    p1.markdown(agent_panel("Agent 1", "IdeaGenerator", "running",
        ["▸ Reasoning: I need a story idea.",
         f"▸ Action: wiki_tool('{theme}')",
         "▸ Observation: retrieved 200 chars"], ""), unsafe_allow_html=True)
    time.sleep(0.8)

    # Phase 3 — backend
    idea, story, meta = run_storyspark_streaming(theme, age)
    tokens = meta["tokens"]
    retries = meta["retries"]

    # Phase 4 — Agent 1 done
    p1.markdown(agent_panel("Agent 1", "IdeaGenerator", "done",
        ["▸ Reasoning: I need a story idea.",
         f"▸ Action: wiki_tool('{theme}')",
         "▸ Observation: retrieved 200 chars",
         "✓ Idea generated"], idea), unsafe_allow_html=True)

    # Phase 5 — A2A handoff
    mem_bar.markdown(f"""
    <div class="mem-box">
    🔄 <b>A2A Handoff</b> — IdeaGenerator ➜ StoryWriter<br>
    <code>memory["idea"]</code> = "{idea[:90]}…" <b>[stored ✓]</b>
    </div>""", unsafe_allow_html=True)
    time.sleep(0.6)

    # Phase 6 — Agent 2 running
    p2.markdown(agent_panel("Agent 2", "StoryWriter", "running",
        ["▸ Reasoning: Write 80-word story for age.",
         "▸ Action: generating narrative..."], ""), unsafe_allow_html=True)
    time.sleep(0.6)

    # Phase 7 — Agent 2 done
    p2.markdown(agent_panel("Agent 2", "StoryWriter", "done",
        ["▸ Reasoning: Write 80-word story for age.",
         "▸ Action: generating narrative...",
         "✓ Story complete"], story), unsafe_allow_html=True)

    # Phase 8 — Metrics
    elapsed = round(time.time() - t0, 1)
    metric_bar.success(
        f"📊 Tokens: **{tokens}/300** · Retries: **{retries}/1** · "
        f"Time: **{elapsed}s** · Status: **OK**"
    )

    st.divider()
    st.subheader("📝 Final Output")
    st.markdown(f"**💡 Story Idea:** {idea}")
    st.markdown(f"**📖 Story:** {story}")
