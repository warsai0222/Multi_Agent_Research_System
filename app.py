import time

import streamlit as st

from src.pipelines.pipeline import research_pipeline


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# SESSION STATE
# =========================================================

if "results" not in st.session_state:
    st.session_state.results = None

if "running" not in st.session_state:
    st.session_state.running = False

if "current_stage" not in st.session_state:
    st.session_state.current_stage = "waiting"

if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""


# =========================================================
# CUSTOM CSS — LIGHT MODE
# =========================================================

st.html(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800'
        '&family=DM+Mono:wght@300;400;500'
        '&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300'
        '&display=swap'
    );


    /* ==================================================
       GLOBAL
    ================================================== */

    :root {
        color-scheme: light;
    }

    html,
    body,
    [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #172033 !important;
    }

    body {
        background: #ffffff;
    }

    .stApp {
        color: #172033 !important;

        background:
            radial-gradient(
                circle at top left,
                rgba(59, 130, 246, 0.10),
                transparent 30%
            ),
            radial-gradient(
                circle at bottom right,
                rgba(139, 92, 246, 0.08),
                transparent 28%
            ),
            linear-gradient(
                180deg,
                #f8fbff 0%,
                #ffffff 55%,
                #f7f9fc 100%
            );
    }

    #MainMenu,
    footer,
    header {
        visibility: hidden;
    }

    .block-container {
        padding: 2rem 3rem 4rem;
        max-width: 1200px;
    }


    /* ==================================================
       FORCE STREAMLIT NATIVE TEXT INTO LIGHT MODE
    ================================================== */

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stVerticalBlock"] {
        color: #172033 !important;
    }

    p,
    li,
    label {
        color: #334155;
    }


    /* ==================================================
       STREAMLIT MARKDOWN
    ================================================== */

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown span,
    .stMarkdown div {
        color: #334155 !important;
    }

    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        color: #111827 !important;
    }

    .stMarkdown strong,
    .stMarkdown b {
        color: #1e293b !important;
    }

    .stMarkdown a {
        color: #2563eb !important;
    }

    .stMarkdown blockquote {
        color: #475569 !important;
        border-left-color: #6366f1 !important;
    }

    .stMarkdown code {
        color: #7c3aed !important;
        background: #f1f5f9 !important;
        padding: 0.1rem 0.3rem;
        border-radius: 4px;
    }

    .stMarkdown pre {
        background: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
    }

    .stMarkdown pre code {
        color: #334155 !important;
        background: transparent !important;
    }


    /* ==================================================
       HERO
    ================================================== */

    .hero {
        text-align: center;
        padding: 3.3rem 0 2.2rem;
    }

    .hero-eyebrow {
        font-family: 'DM Mono', monospace;
        font-size: 0.70rem;
        font-weight: 500;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #4f46e5;
        margin-bottom: 1rem;
    }

    .hero h1 {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.8rem, 6vw, 5rem);
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.04em;
        color: #111827 !important;
        margin: 0 0 1rem;
    }

    .hero h1 span {
        background: linear-gradient(
            135deg,
            #2563eb,
            #7c3aed
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-sub {
        font-size: 1.05rem;
        font-weight: 400;
        color: #64748b;
        max-width: 590px;
        margin: 0 auto;
        line-height: 1.7;
    }


    /* ==================================================
       DIVIDER
    ================================================== */

    .divider {
        height: 1px;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(79, 70, 229, 0.22),
                transparent
            );

        margin: 1.8rem 0;
    }


    /* ==================================================
       TEXT INPUT
    ================================================== */

    .stTextInput > div > div > input {
        background: #ffffff !important;
        border: 1px solid #dbe3ef !important;
        border-radius: 12px !important;

        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;

        font-family: 'DM Sans', sans-serif !important;
        font-size: 1rem !important;

        padding: 0.8rem 1rem !important;

        transition: all 0.2s ease !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #6366f1 !important;

        box-shadow:
            0 0 0 4px
            rgba(99, 102, 241, 0.10) !important;
    }

    .stTextInput > label {
        font-family: 'DM Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
        color: #4f46e5 !important;
        font-weight: 500 !important;
    }


    /* ==================================================
       RUN BUTTON
    ================================================== */

    .stButton > button {
        background:
            linear-gradient(
                135deg,
                #2563eb 0%,
                #7c3aed 100%
            ) !important;

        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;

        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;

        letter-spacing: 0.03em !important;

        border: none !important;
        border-radius: 12px !important;

        padding: 0.8rem 2.2rem !important;

        transition: all 0.18s ease !important;

        box-shadow:
            0 8px 28px
            rgba(79, 70, 229, 0.18) !important;

        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;

        box-shadow:
            0 12px 32px
            rgba(79, 70, 229, 0.26) !important;
    }

    .stButton > button:disabled {
        opacity: 0.55 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }


    /* ==================================================
       PIPELINE STEP CARDS
    ================================================== */

    .step-card {
        background: rgba(255, 255, 255, 0.90);

        border:
            1px solid #e2e8f0;

        border-radius: 18px;

        padding: 1.4rem 1.6rem;

        margin-bottom: 1rem;

        position: relative;
        overflow: hidden;

        transition: all 0.25s ease;

        box-shadow:
            0 8px 24px
            rgba(15, 23, 42, 0.04);
    }

    .step-card:hover {
        transform: translateY(-2px);

        box-shadow:
            0 12px 30px
            rgba(15, 23, 42, 0.07);
    }


    /* ACTIVE */

    .step-card.active {
        border-color: #6366f1;

        background:
            linear-gradient(
                90deg,
                rgba(238, 242, 255, 0.95),
                rgba(255, 255, 255, 0.95)
            );

        box-shadow:
            0 12px 34px
            rgba(99, 102, 241, 0.12);

        animation:
            pulseCard 1.7s
            ease-in-out infinite;
    }


    /* DONE */

    .step-card.done {
        border-color: #86efac;
        background: #f0fdf4;
    }


    /* ERROR */

    .step-card.error {
        border-color: #fca5a5;
        background: #fef2f2;
    }


    /* LEFT STATUS BAR */

    .step-card::before {
        content: '';

        position: absolute;

        left: 0;
        top: 0;
        bottom: 0;

        width: 4px;

        background: #e2e8f0;
    }

    .step-card.active::before {
        background: #6366f1;
    }

    .step-card.done::before {
        background: #22c55e;
    }

    .step-card.error::before {
        background: #ef4444;
    }


    @keyframes pulseCard {

        0% {
            box-shadow:
                0 8px 28px
                rgba(99, 102, 241, 0.08);
        }

        50% {
            box-shadow:
                0 14px 38px
                rgba(99, 102, 241, 0.20);
        }

        100% {
            box-shadow:
                0 8px 28px
                rgba(99, 102, 241, 0.08);
        }
    }


    .step-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .step-num {
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.15em;
        color: #6366f1;
    }

    .step-title {
        font-family: 'Syne', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #172033;
    }

    .step-status {
        margin-left: auto;

        font-family: 'DM Mono', monospace;

        font-size: 0.68rem;
        letter-spacing: 0.08em;
    }

    .status-waiting {
        color: #94a3b8;
    }

    .status-running {
        color: #4f46e5;
        font-weight: 600;
    }

    .status-done {
        color: #16a34a;
        font-weight: 600;
    }

    .status-error {
        color: #dc2626;
        font-weight: 600;
    }

    .step-desc {
        font-size: 0.82rem;
        color: #64748b;
        margin-top: 0.45rem;
    }


    /* ==================================================
       SECTION HEADINGS
    ================================================== */

    .section-heading {
        font-family: 'Syne', sans-serif;

        font-size: 1.3rem;
        font-weight: 700;

        color: #172033;

        margin: 1.2rem 0 1rem;
    }


    /* ==================================================
       PANEL LABELS
    ================================================== */

    .panel-label {
        font-family: 'DM Mono', monospace;

        font-size: 0.70rem;

        letter-spacing: 0.18em;

        text-transform: uppercase;

        margin-top: 1.5rem;
        margin-bottom: 0.75rem;

        padding-bottom: 0.7rem;
    }

    .panel-label.blue {
        color: #2563eb;

        border-bottom:
            1px solid #dbeafe;
    }

    .panel-label.green {
        color: #16a34a;

        border-bottom:
            1px solid #dcfce7;
    }


    /* ==================================================
       EXPANDERS
    ================================================== */

    div[data-testid="stExpander"] {
        background: #ffffff !important;

        border:
            1px solid #e2e8f0 !important;

        border-radius:
            14px !important;

        box-shadow:
            0 5px 18px
            rgba(15, 23, 42, 0.03);
    }

    div[data-testid="stExpander"] details {
        background: #ffffff !important;
        color: #334155 !important;
    }

    div[data-testid="stExpander"] summary {
        background: #ffffff !important;

        color: #334155 !important;

        -webkit-text-fill-color:
            #334155 !important;
    }

    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary div {
        color: #334155 !important;

        -webkit-text-fill-color:
            #334155 !important;
    }

    div[data-testid="stExpander"] summary svg {
        fill: #475569 !important;
        color: #475569 !important;
    }


    /* ==================================================
       TEXT AREA — RAW SEARCH / SCRAPED CONTENT
    ================================================== */

    .stTextArea textarea {
        background-color: #f8fafc !important;

        color: #1e293b !important;

        -webkit-text-fill-color:
            #1e293b !important;

        caret-color:
            #1e293b !important;

        border:
            1px solid #e2e8f0 !important;

        border-radius:
            10px !important;

        font-family:
            'DM Mono',
            monospace !important;

        font-size:
            0.78rem !important;

        line-height:
            1.6 !important;

        opacity:
            1 !important;
    }

    .stTextArea textarea:disabled {
        background-color:
            #f8fafc !important;

        color:
            #1e293b !important;

        -webkit-text-fill-color:
            #1e293b !important;

        opacity:
            1 !important;

        cursor:
            default !important;
    }

    div[data-baseweb="textarea"] {
        background-color:
            #f8fafc !important;

        color:
            #1e293b !important;
    }

    div[data-baseweb="textarea"] textarea {
        background-color:
            #f8fafc !important;

        color:
            #1e293b !important;

        -webkit-text-fill-color:
            #1e293b !important;

        opacity:
            1 !important;
    }

    div[data-testid="stTextArea"] textarea {
        color:
            #1e293b !important;

        -webkit-text-fill-color:
            #1e293b !important;

        opacity:
            1 !important;
    }


    /* ==================================================
       NATIVE STREAMLIT CONTAINERS
    ================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;

        border-color:
            #e2e8f0 !important;

        border-radius:
            16px !important;

        box-shadow:
            0 8px 24px
            rgba(15, 23, 42, 0.04);
    }


    /* ==================================================
       DOWNLOAD BUTTON
    ================================================== */

    .stDownloadButton > button {
        border-radius:
            10px !important;

        border:
            1px solid
            #c7d2fe !important;

        background:
            #eef2ff !important;

        color:
            #4338ca !important;

        -webkit-text-fill-color:
            #4338ca !important;

        font-weight:
            600 !important;
    }

    .stDownloadButton > button:hover {
        border-color:
            #818cf8 !important;

        background:
            #e0e7ff !important;
    }


    /* ==================================================
       ALERTS
    ================================================== */

    div[data-testid="stAlert"] {
        color: #1e293b !important;
    }

    div[data-testid="stAlert"] p {
        color: #1e293b !important;
    }


    /* ==================================================
       FOOTER
    ================================================== */

    .notice {
        font-family:
            'DM Mono',
            monospace;

        font-size:
            0.70rem;

        color:
            #94a3b8;

        text-align:
            center;

        margin-top:
            3rem;

        letter-spacing:
            0.06em;
    }


    /* ==================================================
       MOBILE
    ================================================== */

    @media (max-width: 800px) {

        .block-container {
            padding:
                1.2rem 1rem 3rem;
        }

        .hero {
            padding:
                2rem 0 1rem;
        }

        .hero h1 {
            font-size:
                2.7rem;
        }
    }

    </style>
    """
)


# =========================================================
# PIPELINE CONFIG
# =========================================================

PIPELINE_STAGES = [
    {
        "key": "search",
        "num": "01",
        "title": "Search Agent",
        "description": (
            "Finds reliable sources and checks research coverage."
        ),
    },
    {
        "key": "scrape",
        "num": "02",
        "title": "Web Scraper",
        "description": (
            "Extracts useful text from selected sources."
        ),
    },
    {
        "key": "write",
        "num": "03",
        "title": "Writer Chain",
        "description": (
            "Synthesizes evidence into a structured report."
        ),
    },
    {
        "key": "critique",
        "num": "04",
        "title": "Critic Chain",
        "description": (
            "Evaluates accuracy, completeness and grounding."
        ),
    },
]

STAGE_ORDER = [
    "search",
    "scrape",
    "write",
    "critique",
    "done",
]


# =========================================================
# STEP CARD HELPER
# =========================================================

def step_card(
    num: str,
    title: str,
    state: str,
    desc: str = "",
):

    status_map = {
        "waiting": (
            "WAITING",
            "status-waiting",
        ),
        "running": (
            "● RUNNING",
            "status-running",
        ),
        "done": (
            "✓ DONE",
            "status-done",
        ),
        "error": (
            "✕ ERROR",
            "status-error",
        ),
    }

    label, status_class = status_map.get(
        state,
        status_map["waiting"],
    )

    card_class = ""

    if state == "running":
        card_class = "active"

    elif state == "done":
        card_class = "done"

    elif state == "error":
        card_class = "error"

    st.html(
        f"""
        <div class="step-card {card_class}">

            <div class="step-header">

                <span class="step-num">
                    {num}
                </span>

                <span class="step-title">
                    {title}
                </span>

                <span
                    class="
                        step-status
                        {status_class}
                    "
                >
                    {label}
                </span>

            </div>

            <div class="step-desc">
                {desc}
            </div>

        </div>
        """
    )


# =========================================================
# DETERMINE PIPELINE STEP STATE
# =========================================================

def get_stage_state(stage: str) -> str:

    current = st.session_state.current_stage

    if current == "waiting":
        return "waiting"

    if current == "done":
        return "done"

    if current == "error":

        if stage == st.session_state.get(
            "failed_stage"
        ):
            return "error"

        return "waiting"

    if current == stage:
        return "running"

    if (
        current in STAGE_ORDER
        and stage in STAGE_ORDER
    ):

        current_index = STAGE_ORDER.index(
            current
        )

        stage_index = STAGE_ORDER.index(
            stage
        )

        if stage_index < current_index:
            return "done"

    return "waiting"


# =========================================================
# RENDER PIPELINE
# =========================================================

def render_pipeline():

    for stage in PIPELINE_STAGES:

        step_card(
            stage["num"],
            stage["title"],
            get_stage_state(
                stage["key"]
            ),
            stage["description"],
        )


# =========================================================
# HERO
# =========================================================

st.html(
    """
    <div class="hero">

        <div class="hero-eyebrow">
            Multi-Agent AI Research
        </div>

        <h1>
            Researcher<span>Agent</span>
        </h1>

        <p class="hero-sub">
            Search the web, extract useful evidence,
            generate a detailed research report,
            and critically evaluate its quality
            through a multi-stage AI workflow.
        </p>

    </div>

    <div class="divider"></div>
    """
)


# =========================================================
# MAIN LAYOUT
# =========================================================

col_input, col_pipeline = st.columns(
    [5, 4],
    gap="large",
)


# =========================================================
# LEFT — INPUT
# =========================================================

with col_input:

    st.html(
        """
        <div class="section-heading">
            Start your research
        </div>
        """
    )

    topic = st.text_input(
        "Research Topic",
        placeholder=(
            "e.g. The impact of AI "
            "on the job market in 2026"
        ),
        key="topic_input",
    )

    run_btn = st.button(
        (
            "⏳ Research in progress..."
            if st.session_state.running
            else "⚡ Run Research Pipeline"
        ),
        use_container_width=True,
        disabled=st.session_state.running,
    )

    st.html(
        """
        <div style="
            margin-top:1.1rem;
            font-family:'DM Mono',monospace;
            font-size:0.68rem;
            color:#94a3b8;
            letter-spacing:0.08em;
        ">
            EXAMPLE TOPICS
        </div>
        """
    )

    examples = [
        "Impact of AI on jobs in 2026",
        "Future of AI agents",
        "Quantum computing breakthroughs",
    ]

    for example in examples:

        st.html(
            f"""
            <div style="
                margin-top:0.55rem;
                padding:0.45rem 0.7rem;
                background:#ffffff;
                border:1px solid #e2e8f0;
                border-radius:9px;
                font-size:0.78rem;
                color:#64748b;
            ">
                {example}
            </div>
            """
        )


# =========================================================
# RIGHT — LIVE PIPELINE
# =========================================================

with col_pipeline:

    st.html(
        """
        <div class="section-heading">
            Pipeline
        </div>
        """
    )

    pipeline_placeholder = st.empty()

    with pipeline_placeholder.container():
        render_pipeline()


# =========================================================
# LIVE PROGRESS CALLBACK
# =========================================================

def update_progress(stage: str):

    previous_stage = (
        st.session_state.current_stage
    )

    if stage == "error":

        if previous_stage in STAGE_ORDER:
            st.session_state.failed_stage = (
                previous_stage
            )

    else:

        st.session_state.current_stage = (
            stage
        )

    if stage == "error":
        st.session_state.current_stage = "error"

    pipeline_placeholder.empty()

    with pipeline_placeholder.container():
        render_pipeline()


# =========================================================
# RUN PIPELINE
# =========================================================

if run_btn:

    clean_topic = topic.strip()

    if not clean_topic:

        st.warning(
            "Please enter a research topic first."
        )

    else:

        st.session_state.results = None

        st.session_state.running = True

        st.session_state.current_stage = (
            "search"
        )

        st.session_state.failed_stage = None

        update_progress("search")

        try:

            result = research_pipeline(
                clean_topic,
                progress_callback=(
                    update_progress
                ),
            )

            st.session_state.results = (
                result
            )

            st.session_state.running = (
                False
            )

            if isinstance(result, dict):

                st.session_state.current_stage = (
                    "done"
                )

                update_progress("done")

            elif isinstance(result, str):

                if (
                    st.session_state.current_stage
                    != "error"
                ):
                    update_progress("error")

            else:

                st.session_state.results = (
                    "The pipeline returned "
                    "an unexpected result."
                )

                update_progress("error")

        except Exception as exc:

            st.session_state.running = False

            update_progress("error")

            st.session_state.results = (
                f"Pipeline failed: {exc}"
            )


# =========================================================
# RESULTS
# =========================================================

result = st.session_state.results


if result is not None:

    st.html(
        """
        <div class="divider"></div>

        <div class="section-heading">
            Results
        </div>
        """
    )


    # =====================================================
    # ERROR RESULT
    # =====================================================

    if isinstance(result, str):

        st.error(result)


    # =====================================================
    # SUCCESS RESULT
    # =====================================================

    elif isinstance(result, dict):

        search_results = result.get(
            "search_results",
            "",
        )

        scraped_content = result.get(
            "scraped_content",
            "",
        )

        report = result.get(
            "report",
            "",
        )

        critique = result.get(
            "critique",
            "",
        )


        # =================================================
        # RAW SEARCH RESULTS
        # =================================================

        if search_results:

            with st.expander(
                "🔍 Search Results",
                expanded=False,
            ):

                st.text_area(
                    "Search results",
                    value=search_results,
                    height=300,
                    disabled=True,
                    label_visibility="collapsed",
                    key="search_results_display",
                )


        # =================================================
        # SCRAPED CONTENT
        # =================================================

        if scraped_content:

            with st.expander(
                "📄 Scraped Research",
                expanded=False,
            ):

                st.text_area(
                    "Scraped content",
                    value=scraped_content,
                    height=420,
                    disabled=True,
                    label_visibility="collapsed",
                    key="scraped_content_display",
                )


        # =================================================
        # FINAL REPORT
        # =================================================

        if report:

            st.html(
                """
                <div class="
                    panel-label blue
                ">
                    📝 Final Research Report
                </div>
                """
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    report
                )

            st.download_button(
                label=(
                    "⬇ Download Report (.md)"
                ),
                data=report,
                file_name=(
                    "research_report_"
                    f"{int(time.time())}.md"
                ),
                mime="text/markdown",
                use_container_width=False,
            )


        # =================================================
        # CRITIC FEEDBACK
        # =================================================

        if critique:

            st.html(
                """
                <div class="
                    panel-label green
                ">
                    🧠 Critic Evaluation
                </div>
                """
            )

            with st.container(
                border=True
            ):

                st.markdown(
                    critique
                )


# =========================================================
# FOOTER
# =========================================================

st.html(
    """
    <div class="notice">
        ResearcherAgent ·
        Search → Scrape → Write → Critique ·
        Built with LangChain & Streamlit
    </div>
    """
)