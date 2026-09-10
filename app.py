import streamlit as st
import time

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

st.html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');


/* ======================================================
   GLOBAL
====================================================== */

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #172033;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(59,130,246,0.10), transparent 30%),
        radial-gradient(circle at bottom right, rgba(139,92,246,0.08), transparent 28%),
        linear-gradient(180deg, #f8fbff 0%, #ffffff 55%, #f7f9fc 100%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding: 2rem 3rem 4rem;
    max-width: 1200px;
}


/* ======================================================
   HERO
====================================================== */

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
    color: #111827;
    margin: 0 0 1rem;
}

.hero h1 span {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
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


/* ======================================================
   DIVIDER
====================================================== */

.divider {
    height: 1px;
    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(79,70,229,0.22),
            transparent
        );

    margin: 1.8rem 0;
}


/* ======================================================
   INPUT CARD
====================================================== */

.input-card {
    background: rgba(255,255,255,0.88);
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 2rem 2.3rem;
    margin-bottom: 1.4rem;

    box-shadow:
        0 12px 40px rgba(15,23,42,0.06);
}


/* ======================================================
   TEXT INPUT
====================================================== */

.stTextInput > div > div > input {
    background: #ffffff !important;
    border: 1px solid #dbe3ef !important;
    border-radius: 12px !important;
    color: #111827 !important;

    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;

    padding: 0.8rem 1rem !important;

    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #6366f1 !important;
    box-shadow:
        0 0 0 4px rgba(99,102,241,0.10) !important;
}

.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #4f46e5 !important;
    font-weight: 500 !important;
}


/* ======================================================
   BUTTON
====================================================== */

.stButton > button {
    background:
        linear-gradient(
            135deg,
            #2563eb 0%,
            #7c3aed 100%
        ) !important;

    color: white !important;

    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;

    letter-spacing: 0.03em !important;

    border: none !important;
    border-radius: 12px !important;

    padding: 0.8rem 2.2rem !important;

    transition: all 0.18s ease !important;

    box-shadow:
        0 8px 28px rgba(79,70,229,0.18) !important;

    width: 100%;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;

    box-shadow:
        0 12px 32px rgba(79,70,229,0.26) !important;
}


/* ======================================================
   PIPELINE STEP CARDS
====================================================== */

.step-card {
    background: rgba(255,255,255,0.82);

    border:
        1px solid #e2e8f0;

    border-radius: 18px;

    padding: 1.4rem 1.6rem;

    margin-bottom: 1rem;

    position: relative;
    overflow: hidden;

    transition: all 0.25s ease;

    box-shadow:
        0 8px 24px rgba(15,23,42,0.04);
}

.step-card:hover {
    transform: translateY(-2px);

    box-shadow:
        0 12px 30px rgba(15,23,42,0.07);
}


/* ACTIVE STEP */

.step-card.active {
    border-color: #6366f1;

    background:
        linear-gradient(
            90deg,
            rgba(238,242,255,0.95),
            rgba(255,255,255,0.95)
        );

    box-shadow:
        0 12px 34px rgba(99,102,241,0.12);

    animation:
        pulseCard 1.7s ease-in-out infinite;
}


/* DONE STEP */

.step-card.done {
    border-color: #86efac;
    background: #f0fdf4;
}


/* LEFT BAR */

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


/* ACTIVE PULSE */

@keyframes pulseCard {

    0% {
        box-shadow:
            0 8px 28px rgba(99,102,241,0.08);
    }

    50% {
        box-shadow:
            0 14px 38px rgba(99,102,241,0.20);
    }

    100% {
        box-shadow:
            0 8px 28px rgba(99,102,241,0.08);
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

.step-desc {
    font-size: 0.82rem;

    color: #64748b;

    margin-top: 0.45rem;

    padding-left: 0;
}


/* ======================================================
   SECTION HEADING
====================================================== */

.section-heading {
    font-family: 'Syne', sans-serif;

    font-size: 1.3rem;

    font-weight: 700;

    color: #172033;

    margin: 1.2rem 0 1rem;
}


/* ======================================================
   RESULT PANELS
====================================================== */

.result-panel {
    background: #ffffff;

    border:
        1px solid #e2e8f0;

    border-radius: 18px;

    padding: 1.7rem 1.9rem;

    margin-top: 1rem;

    margin-bottom: 1.5rem;

    box-shadow:
        0 8px 24px rgba(15,23,42,0.04);
}

.result-panel-title {
    font-family: 'DM Mono', monospace;

    font-size: 0.7rem;

    font-weight: 500;

    letter-spacing: 0.18em;

    text-transform: uppercase;

    color: #4f46e5;

    margin-bottom: 1rem;

    padding-bottom: 0.7rem;

    border-bottom:
        1px solid #eef2f7;
}

.result-content {
    font-size: 0.92rem;

    line-height: 1.8;

    color: #475569;

    white-space: pre-wrap;

    word-break: break-word;
}


/* ======================================================
   REPORT PANEL
====================================================== */

.report-panel {
    background: #ffffff;

    border:
        1px solid #dbeafe;

    border-radius: 20px;

    padding: 2rem 2.4rem;

    margin-top: 1rem;

    box-shadow:
        0 10px 32px rgba(37,99,235,0.06);
}


/* ======================================================
   CRITIC PANEL
====================================================== */

.feedback-panel {
    background: #ffffff;

    border:
        1px solid #bbf7d0;

    border-radius: 20px;

    padding: 2rem 2.4rem;

    margin-top: 1rem;

    box-shadow:
        0 10px 32px rgba(34,197,94,0.06);
}


.panel-label {
    font-family: 'DM Mono', monospace;

    font-size: 0.7rem;

    letter-spacing: 0.18em;

    text-transform: uppercase;

    margin-bottom: 1.2rem;

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


/* ======================================================
   EXPANDER
====================================================== */

details {
    background: #ffffff;

    border-radius: 14px;

    border:
        1px solid #e2e8f0;

    padding: 0.2rem 0.8rem;
}


details summary {
    font-family:
        'DM Mono',
        monospace !important;

    font-size:
        0.75rem !important;

    color:
        #475569 !important;

    letter-spacing:
        0.07em !important;
}


/* ======================================================
   DOWNLOAD BUTTON
====================================================== */

.stDownloadButton > button {
    border-radius: 10px !important;

    border:
        1px solid #c7d2fe !important;

    background:
        #eef2ff !important;

    color:
        #4338ca !important;

    font-weight:
        600 !important;
}


/* ======================================================
   FOOTER
====================================================== */

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


/* ======================================================
   MOBILE
====================================================== */

@media (max-width: 800px) {

    .block-container {
        padding:
            1.2rem 1rem 3rem;
    }

    .hero {
        padding:
            2rem 0 1rem;
    }

}

</style>
""")


# =========================================================
# STEP CARD HELPER
# =========================================================

def step_card(
    num: str,
    title: str,
    state: str,
    desc: str = ""
):

    status_map = {
        "waiting": (
            "WAITING",
            "status-waiting"
        ),
        "running": (
            "● RUNNING",
            "status-running"
        ),
        "done": (
            "✓ DONE",
            "status-done"
        ),
    }

    label, status_class = status_map[state]

    card_class = ""

    if state == "running":
        card_class = "active"

    elif state == "done":
        card_class = "done"

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

                <span class="step-status {status_class}">
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
# PIPELINE STATE HELPER
# =========================================================

stage_order = [
    "search",
    "scrape",
    "write",
    "critique",
    "done"
]


def get_stage_state(stage):

    current = st.session_state.current_stage

    if current == "waiting":
        return "waiting"

    if current == "error":
        return "waiting"

    if current == stage:
        return "running"

    if current == "done":
        return "done"

    if (
        current in stage_order
        and stage in stage_order
    ):

        if (
            stage_order.index(stage)
            <
            stage_order.index(current)
        ):
            return "done"

    return "waiting"


# =========================================================
# HERO
# =========================================================

st.html("""
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
""")


# =========================================================
# MAIN LAYOUT
# =========================================================

col_input, col_gap, col_pipeline = st.columns(
    [5, 0.5, 4]
)


# =========================================================
# LEFT — INPUT
# =========================================================

with col_input:

    st.html("""
    <div class="section-heading">
        Start your research
    </div>
    """)

    topic = st.text_input(
        "Research Topic",
        placeholder=(
            "e.g. The impact of AI "
            "on the job market in 2026"
        ),
        key="topic_input"
    )

    run_btn = st.button(
        "⚡ Run Research Pipeline",
        use_container_width=True
    )

    st.html("""
    <div style="
        margin-top:1.1rem;
        font-family:'DM Mono',monospace;
        font-size:0.68rem;
        color:#94a3b8;
        letter-spacing:0.08em;
    ">
        EXAMPLE TOPICS
    </div>
    """)

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

    st.html("""
    <div class="section-heading">
        Pipeline
    </div>
    """)

    pipeline_placeholder = st.empty()

    with pipeline_placeholder.container():

        step_card(
            "01",
            "Search Agent",
            get_stage_state("search"),
            "Finds reliable sources and checks research coverage."
        )

        step_card(
            "02",
            "Web Scraper",
            get_stage_state("scrape"),
            "Extracts useful text from selected sources."
        )

        step_card(
            "03",
            "Writer Chain",
            get_stage_state("write"),
            "Synthesizes evidence into a structured report."
        )

        step_card(
            "04",
            "Critic Chain",
            get_stage_state("critique"),
            "Evaluates accuracy, completeness and grounding."
        )


# =========================================================
# LIVE CALLBACK
# =========================================================

def update_progress(stage):

    st.session_state.current_stage = stage

    pipeline_placeholder.empty()

    with pipeline_placeholder.container():

        step_card(
            "01",
            "Search Agent",
            get_stage_state("search"),
            "Finds reliable sources and checks research coverage."
        )

        step_card(
            "02",
            "Web Scraper",
            get_stage_state("scrape"),
            "Extracts useful text from selected sources."
        )

        step_card(
            "03",
            "Writer Chain",
            get_stage_state("write"),
            "Synthesizes evidence into a structured report."
        )

        step_card(
            "04",
            "Critic Chain",
            get_stage_state("critique"),
            "Evaluates accuracy, completeness and grounding."
        )


# =========================================================
# RUN PIPELINE
# =========================================================

if run_btn:

    if not topic.strip():

        st.warning(
            "Please enter a research topic first."
        )

    else:

        st.session_state.results = None
        st.session_state.running = True
        st.session_state.current_stage = "search"

        try:

            result = research_pipeline(
                topic,
                progress_callback=update_progress
            )

            st.session_state.results = result
            st.session_state.running = False

            if isinstance(result, dict):

                st.session_state.current_stage = "done"

            else:

                st.session_state.current_stage = "error"

            update_progress(
                st.session_state.current_stage
            )

        except Exception as e:

            st.session_state.running = False
            st.session_state.current_stage = "error"

            st.error(
                f"Pipeline failed: {e}"
            )


# =========================================================
# RESULTS
# =========================================================

result = st.session_state.results


if result is not None:

    st.html("""
    <div class="divider"></div>

    <div class="section-heading">
        Results
    </div>
    """)


    # -----------------------------------------------------
    # ERROR
    # -----------------------------------------------------

    if isinstance(result, str):

        st.error(result)


    # -----------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------

    else:

        search_results = result.get(
            "search_results",
            ""
        )

        scraped_content = result.get(
            "scraped_content",
            ""
        )

        report = result.get(
            "report",
            ""
        )

        critique = result.get(
            "critique",
            ""
        )


        # =================================================
        # RAW SEARCH RESULTS
        # =================================================

        if search_results:

            with st.expander(
                "🔍 Search Results",
                expanded=False
            ):

                st.text_area(
                    "Search results",
                    value=search_results,
                    height=300,
                    disabled=True,
                    label_visibility="collapsed"
                )


        # =================================================
        # SCRAPED CONTENT
        # =================================================

        if scraped_content:

            with st.expander(
                "📄 Scraped Research",
                expanded=False
            ):

                st.text_area(
                    "Scraped content",
                    value=scraped_content,
                    height=420,
                    disabled=True,
                    label_visibility="collapsed"
                )


        # =================================================
        # FINAL REPORT
        # =================================================

        if report:

            st.html("""
            <div class="report-panel">

                <div class="panel-label blue">
                    📝 Final Research Report
                </div>

            </div>
            """)

            st.markdown(report)

            st.download_button(
                label="⬇ Download Report (.md)",
                data=report,
                file_name=(
                    f"research_report_"
                    f"{int(time.time())}.md"
                ),
                mime="text/markdown"
            )


        # =================================================
        # CRITIC
        # =================================================

        if critique:

            st.html("""
            <div class="feedback-panel">

                <div class="panel-label green">
                    🧠 Critic Evaluation
                </div>

            </div>
            """)

            st.markdown(critique)


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="notice">
    ResearcherAgent ·
    Search → Scrape → Write → Critique ·
    Built with LangChain & Streamlit
</div>
""")