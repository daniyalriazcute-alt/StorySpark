"""StorySpark — Streamlit UI with chat history, theme toggle, and live agent view."""
import os
import time
import streamlit as st
from crew import run_storyspark_streaming, is_topic_valid, get_last_errors

# ---------- Page Config ----------
st.set_page_config(
    page_title="StorySpark",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Theme Toggle (top right) ----------
theme_col1, theme_col2 = st.columns([5, 1])
with theme_col2:
    dark_mode = st.toggle("🌙 Dark", value=False)

# Apply theme via CSS injection
if dark_mode:
    st.markdown("""
    <style>
    /* Force light text on all major Streamlit elements in dark mode */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp label, .stApp span, .stApp div, .stApp small, .stApp strong, .stApp em,
    .stApp .stMarkdown, .stApp .stText, .stApp .stCaption {
        color: #fafafa !important;
    }
    /* Input fields */
    .stApp input, .stApp textarea {
        background-color: #1a1d24 !important;
        color: #fafafa !important;
        border-color: #2a2f3a !important;
    }
    /* Slider track */
    .stApp .stSlider > div > div > div {
        background-color: #3b82f6 !important;
    }
    /* Custom agent cards */
    .agent-card { background: #1a1d24 !important; border: 1px solid #2a2f3a !important;
                  border-radius: 10px; padding: 14px; min-height: 300px; }
    .agent-title { font-weight: 600; font-size: 15px; margin-bottom: 6px; color: #fafafa; }
    .status-dot { display:inline-block; width:9px; height:9px;
                  border-radius:50%; margin-right:6px; }
    .running { background:#22c55e; animation:pulse 1s infinite; }
    .waiting { background:#9ca3af; }
    .done    { background:#3b82f6; }
    @keyframes pulse {0%{opacity:1}50%{opacity:.4}100%{opacity:1}}
    .log { font-family:'SF Mono',Monaco,monospace; font-size:12.5px;
           line-height:1.6; color:#d1d5db; }
    .mem-box { background:#1e2130; border-left:4px solid #6366f1;
               padding:10px 14px; border-radius:6px; font-size:13px; color:#d1d5db; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    /* Custom agent cards for light mode */
    .agent-card { background: #fafafa; border: 1px solid #e0e0e0;
                  border-radius: 10px; padding: 14px; min-height: 300px; }
    .agent-title { font-weight: 600; font-size: 15px; margin-bottom: 6px; }
    .status-dot { display:inline-block; width:9px; height:9px;
                  border-radius:50%; margin-right:6px; }
    .running { background:#22c55e; animation:pulse 1s infinite; }
    .waiting { background:#9ca3af; }
    .done    { background:#3b82f6; }
    @keyframes pulse {0%{opacity:1}50%{opacity:.4}100%{opacity:1}}
    .log { font-family:'SF Mono',Monaco,monospace; font-size:12.5px;
           line-height:1.6; color:#374151; }
    .mem-box { background:#eef2ff; border-left:4px solid #6366f1;
               padding:10px 14px; border-radius:6px; font-size:13px; }
    </style>
    """, unsafe_allow_html=True)

# ---------- Session State Init ----------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "story_count" not in st.session_state:
    st.session_state.story_count = 0

# ---------- Header ----------
st.markdown("## 📖 StorySpark · Multi-Agent Story Engine")
st.caption("Two CrewAI agents collaborate to write a children's story.")

# ---------- Top Controls (only Clear Chat now) ----------
ctrl1, ctrl2 = st.columns([5, 1])
with ctrl2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.story_count = 0
        st.rerun()

# ---------- Input Row ----------
c1, c2, c3 = st.columns([2, 1, 1])
theme = c1.text_input("Theme", "friendship")
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
    valid, msg = is_topic_valid(theme)
    if not valid:
        st.error(f"❌ {msg}")
        st.stop()

    if not os.getenv("GEMINI_API_KEY"):
        st.error("❌ GEMINI_API_KEY is not set. Add it in Settings → Secrets.")
        st.stop()

    t0 = time.time()
    task_bar.info(f"🎯 **Task** — Theme: `{theme}` · Age: `{age}`")

    p1.markdown(agent_panel("Agent 1", "IdeaGenerator", "running",
        ["▸ Reasoning: I need a story idea.",
         f"▸ Action: wiki_tool('{theme}')"], ""), unsafe_allow_html=True)
    p2.markdown(agent_panel("Agent 2", "StoryWriter", "waiting", [], ""),
                unsafe_allow_html=True)

    try:
        idea, story, meta = run_storyspark_streaming(theme, age)
        tokens = meta["tokens"]
        retries = meta["retries"]
    except Exception as e:
        st.error(f"❌ Backend error: {type(e).__name__}: {e}")
        st.stop()

    errors = get_last_errors()
    if errors.get("idea"):
        st.error(f"❌ Agent 1: {errors['idea']}")
    if errors.get("story"):
        st.error(f"❌ Agent 2: {errors['story']}")

    p1.markdown(agent_panel("Agent 1", "IdeaGenerator", "done",
        ["▸ Reasoning: I need a story idea.",
         f"▸ Action: wiki_tool('{theme}')",
         "✓ Idea generated"], idea), unsafe_allow_html=True)

    mem_bar.markdown(f"""
    <div class="mem-box">
    🔄 <b>A2A Handoff</b> — IdeaGenerator ➜ StoryWriter<br>
    <code>memory["idea"]</code> = "{idea[:90]}…" <b>[stored ✓]</b>
    </div>""", unsafe_allow_html=True)

    p2.markdown(agent_panel("Agent 2", "StoryWriter", "done",
        ["▸ Reasoning: Write 80-word story.",
         "✓ Story complete"], story), unsafe_allow_html=True)

    elapsed = round(time.time() - t0, 1)
    metric_bar.success(
        f"📊 Tokens: **{tokens}/300** · Retries: **{retries}/1** · "
        f"Time: **{elapsed}s** · Status: **OK**"
    )

    st.divider()
    st.subheader("📝 Final Output")
    st.markdown(f"**💡 Story Idea:** {idea}")
    st.markdown(f"**📖 Story:** {story}")

    story_text = (
        f"StorySpark — Generated Story\n{'=' * 40}\n"
        f"Theme: {theme}\nAge: {age}\n\nIdea:\n{idea}\n\nStory:\n{story}\n"
    )
    st.download_button(
        label="⬇️ Download Story (.txt)",
        data=story_text,
        file_name=f"story_{theme.replace(' ', '_')}.txt",
        mime="text/plain",
    )

    # ---- Save to chat history ----
    st.session_state.story_count += 1
    st.session_state.chat_history.append({
        "n": st.session_state.story_count,
        "theme": theme,
        "age": age,
        "idea": idea,
        "story": story,
        "tokens": tokens,
        "retries": retries,
        "time": elapsed,
    })


# ---------- Chat History Panel ----------
if st.session_state.chat_history:
    st.divider()
    st.subheader(f"💬 Chat History ({len(st.session_state.chat_history)} stories)")

    # Show newest first
    for item in reversed(st.session_state.chat_history):
        with st.chat_message("user"):
            st.markdown(f"**Story #{item['n']}** — Theme: `{item['theme']}` · Age: `{item['age']}`")
        with st.chat_message("assistant", avatar="📖"):
            st.markdown(f"**💡 Idea:** {item['idea']}")
            st.markdown(f"**📖 Story:** {item['story']}")
            st.caption(
                f"Tokens: {item['tokens']}/300 · "
                f"Retries: {item['retries']}/1 · "
                f"Time: {item['time']}s"
            )

    # Bottom action bar
    act1, act2 = st.columns([3, 1])
    with act2:
        # Export full chat
        chat_text = "\n\n".join([
            f"Story #{i['n']}\nTheme: {i['theme']} (age {i['age']})\n"
            f"Idea: {i['idea']}\nStory: {i['story']}\n"
            f"{'-' * 40}"
            for i in st.session_state.chat_history
        ])
        st.download_button(
            label="⬇️ Export All",
            data=chat_text,
            file_name="storyspark_history.txt",
            mime="text/plain",
            use_container_width=True,
        )
