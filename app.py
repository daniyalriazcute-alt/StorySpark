"""StorySpark — Streamlit UI with full dark/light mode, chat history, and live agents."""
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

# ---------- Session State ----------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "story_count" not in st.session_state:
    st.session_state.story_count = 0

# ---------- Theme Colors ----------
if st.session_state.dark_mode:
    BG = "#0a0e27"           # deep navy background
    CARD_BG = "#111633"      # dark navy card
    CARD_BORDER = "#1e3a8a"  # royal blue border
    TEXT = "#e5e7eb"         # light gray text
    SUBTEXT = "#93c5fd"      # light blue subtext
    ACCENT = "#1e3a8a"       # royal blue accent
    ACCENT_HOVER = "#2563eb"
    MEM_BG = "#0f172a"
    INPUT_BG = "#1a1f3d"
    INPUT_BORDER = "#1e3a8a"
    BTN_TEXT = "#ffffff"     # white text on blue buttons
else:
    BG = "#ffffff"
    CARD_BG = "#f8fafc"
    CARD_BORDER = "#cbd5e1"
    TEXT = "#111827"
    SUBTEXT = "#1e40af"
    ACCENT = "#3b82f6"
    ACCENT_HOVER = "#2563eb"
    MEM_BG = "#eff6ff"
    INPUT_BG = "#ffffff"
    INPUT_BORDER = "#cbd5e1"
    BTN_TEXT = "#ffffff"

# ---------- Full-Page Theme CSS ----------
st.markdown(f"""
<style>
/* ===== GLOBAL BACKGROUND ===== */
.stApp, [data-testid="stAppViewContainer"] {{
    background-color: {BG} !important;
}}
[data-testid="stHeader"] {{
    background-color: {BG} !important;
}}

/* ===== ALL TEXT (except buttons) ===== */
.stApp p, .stApp span, .stApp div, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp strong, .stApp em, .stApp small, .stApp li,
.stApp .stMarkdown, .stApp .stCaption, .stApp .stText {{
    color: {TEXT} !important;
}}

/* ===== CAPTION ===== */
.stApp .stCaption, .stApp [data-testid="stCaptionContainer"] {{
    color: {SUBTEXT} !important;
}}

/* ===== SLIDER (label + value + track) ===== */
.stApp .stSlider label,
.stApp .stSlider [data-testid="stTickBarMin"],
.stApp .stSlider [data-testid="stTickBarMax"],
.stApp .stSlider [data-baseweb="slider"] div {{
    color: {TEXT} !important;
}}
.stApp .stSlider [data-baseweb="slider"] > div > div > div {{
    background: {ACCENT} !important;
}}
/* Slider thumb */
.stApp .stSlider [role="slider"] {{
    background-color: {ACCENT} !important;
    border-color: {ACCENT} !important;
}}
/* Slider value bubble above thumb */
.stApp .stSlider [data-testid="stThumbValue"] {{
    color: {TEXT} !important;
    background-color: transparent !important;
}}

/* ===== TEXT INPUT ===== */
.stApp input[type="text"],
.stApp .stTextInput > div > div > input {{
    background-color: {INPUT_BG} !important;
    color: {TEXT} !important;
    border: 1px solid {INPUT_BORDER} !important;
    border-radius: 6px !important;
}}
.stApp .stTextInput label {{
    color: {TEXT} !important;
}}

/* ===== BUTTONS — ALL of them ===== */
.stApp .stButton > button,
.stApp .stDownloadButton > button {{
    background-color: {ACCENT} !important;
    border: 1px solid {ACCENT} !important;
    border-radius: 6px !important;
    font-weight: 500 !important;
}}
.stApp .stButton > button *,
.stApp .stButton > button p,
.stApp .stButton > button span,
.stApp .stButton > button div,
.stApp .stDownloadButton > button *,
.stApp .stDownloadButton > button p,
.stApp .stDownloadButton > button span,
.stApp .stDownloadButton > button div {{
    color: {BTN_TEXT} !important;
}}
.stApp .stButton > button:hover,
.stApp .stDownloadButton > button:hover {{
    background-color: {ACCENT_HOVER} !important;
    border-color: {ACCENT_HOVER} !important;
}}

/* ===== ALERT BOXES (info, success, error, warning) ===== */
.stApp .stAlert {{
    background-color: {CARD_BG} !important;
    color: {TEXT} !important;
    border: 1px solid {CARD_BORDER} !important;
}}
.stApp .stAlert * {{
    color: {TEXT} !important;
}}

/* ===== CHAT MESSAGES ===== */
.stApp [data-testid="stChatMessage"] {{
    background-color: {CARD_BG} !important;
    border: 1px solid {CARD_BORDER} !important;
    border-radius: 8px !important;
}}
.stApp [data-testid="stChatMessage"] * {{
    color: {TEXT} !important;
}}

/* ===== DIVIDER ===== */
.stApp hr {{
    border-color: {CARD_BORDER} !important;
}}

/* ===== CUSTOM AGENT CARDS ===== */
.agent-card {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
    padding: 14px;
    min-height: 300px;
}}
.agent-title {{
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 6px;
    color: {TEXT};
}}
.agent-role {{
    color: {SUBTEXT};
}}
.status-dot {{
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    margin-right: 6px;
}}
.running {{ background: #22c55e; animation: pulse 1s infinite; }}
.waiting {{ background: #9ca3af; }}
.done    {{ background: #3b82f6; }}
@keyframes pulse {{0%{{opacity:1}}50%{{opacity:.4}}100%{{opacity:1}}}}
.log {{
    font-family: 'SF Mono', Monaco, monospace;
    font-size: 12.5px;
    line-height: 1.6;
    color: {TEXT};
}}
.mem-box {{
    background: {MEM_BG};
    border-left: 4px solid {ACCENT};
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 13px;
    color: {TEXT};
}}
.agent-output-label {{
    font-size: 12px;
    color: {SUBTEXT};
}}

/* ===== HIDE STREAMLIT MENU/FOOTER ===== */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ---------- Header with Theme Toggle ----------
header_left, header_right = st.columns([5, 1])
with header_left:
    st.markdown("## 📖 StorySpark · Multi-Agent Story Engine")
    st.caption("Two CrewAI agents collaborate to write a children's story.")
with header_right:
    # Show CURRENT mode, not target
    if st.session_state.dark_mode:
        toggle_label = "🌙 Dark Mode"
    else:
        toggle_label = "☀️ Light Mode"
    if st.button(toggle_label, use_container_width=True, key="theme_toggle"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ---------- Top Controls ----------
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
      <div class="agent-title">🤖 {name} · <span class="agent-role">{role}</span></div>
      <div style="font-size:12px;margin-bottom:8px">
        <span class="status-dot {dot}"></span>{label}
      </div>
      <div class="log">{log_html}</div>
      <hr style="margin:10px 0">
      <div class="agent-output-label">Output</div>
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

    act1, act2 = st.columns([3, 1])
    with act2:
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
