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

DEFAULT_SESSION_STATE = {
    "results": None,
    "running": False,
    "current_stage": "waiting",
    "failed_stage": None,
    "topic_input": "",
}

for key, value in DEFAULT_SESSION_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.html(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800'
        '&family=DM+Mono:wght@300;400;500'
        '&family=DM+Sans:wght@300;400;500;600&display=swap'
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
        color: #1e293b !important;
    }

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(59, 130, 246, 0.09),
                transparent 28%
            ),
            radial-gradient(
                circle at bottom right,
                rgba(124, 58, 237, 0.07),
                transparent 28%
            ),
            linear-gradient(
                180deg,
                #f8fbff 0%,
                #ffffff 55%,
                #f8fafc 100%
            );
    }

    #MainMenu,
    footer,
    header {
        visibility: hidden;
    }

    .block-container {
        padding: 2rem 3rem 4rem;
        max-width: 1180px;
    }


    /* ==================================================
       MARKDOWN
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
        color: #0f172a !important;
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


    /* ==================================================
       HERO
    ================================================== */

    .hero {
        text-align: center;
        padding: 3.2rem 0 2rem;
    }

    .hero-eyebrow {
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.24em;
        text-transform: uppercase;
        color: #4f46e5;
        margin-bottom: 0.9rem;
    }

    .hero h1 {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2.8rem, 6vw, 4.8rem);
        font-weight: 800;
        line-height: 1;
        letter-spacing: -0.04em;
        color: #0f172a !important;
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
        font-size: 1.02rem;
        color: #64748b;
        max-width: 610px;
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
                rgba(99, 102, 241, 0.20),
                transparent
            );

        margin: 1.8rem 0;
    }


    /* ==================================================
       SECTION HEADINGS
    ================================================== */

    .section-heading {
        font-family: 'Syne', sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        color: #172033;
        margin: 1.1rem 0 1rem;
    }


    /* ==================================================
       TEXT INPUT
    ================================================== */

    .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;

        border: 1px solid #dbe3ef !important;
        border-radius: 12px !important;

        font-size: 1rem !important;
        padding: 0.8rem 1rem !important;
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
        letter-spacing: 0.14em !important;
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

        border: none !important;
        border-radius: 12px !important;

        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;

        padding: 0.8rem 2rem !important;

        box-shadow:
            0 8px 26px
            rgba(79, 70, 229, 0.18) !important;

        transition: all 0.18s ease !important;

        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;

        box-shadow:
            0 12px 32px
            rgba(79, 70, 229, 0.25) !important;
    }

    .stButton > button:disabled {
        opacity: 0.55 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }


    /* ==================================================
       PIPELINE CARDS
    ================================================== */

    .step-card {
        background: rgba(255, 255, 255, 0.92);

        border: 1px solid #e2e8f0;
        border-radius: 16px;

        padding: 1.25rem 1.45rem;
        margin-bottom: 0.9rem;

        position: relative;
        overflow: hidden;

        box-shadow:
            0 6px 22px
            rgba(15, 23, 42, 0.04);

        transition: all 0.2s ease;
    }

    .step-card:hover {
        transform: translateY(-1px);

        box-shadow:
            0 10px 26px
            rgba(15, 23, 42, 0.06);
    }

    .step-card::before {
        content: '';

        position: absolute;

        left: 0;
        top: 0;
        bottom: 0;

        width: 4px;

        background: #e2e8f0;
    }


    /* ACTIVE */

    .step-card.active {
        border-color: #818cf8;

        background:
            linear-gradient(
                90deg,
                rgba(238, 242, 255, 0.95),
                rgba(255, 255, 255, 0.98)
            );

        animation:
            pulseCard 1.8s ease-in-out infinite;
    }

    .step-card.active::before {
        background: #6366f1;
    }


    /* DONE */

    .step-card.done {
        border-color: #86efac;
        background: #f0fdf4;
    }

    .step-card.done::before {
        background: #22c55e;
    }


    /* ERROR */

    .step-card.error {
        border-color: #fca5a5;
        background: #fef2f2;
    }

    .step-card.error::before {
        background: #ef4444;
    }


    @keyframes pulseCard {

        0% {
            box-shadow:
                0 8px 24px
                rgba(99, 102, 241, 0.08);
        }

        50% {
            box-shadow:
                0 12px 32px
                rgba(99, 102, 241, 0.18);
        }

        100% {
            box-shadow:
                0 8px 24px
                rgba(99, 102, 241, 0.08);
        }
    }


    .step-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }

    .step-num {
        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        color: #6366f1;
        font-weight: 500;
    }

    .step-title {
        font-family: 'Syne', sans-serif;
        font-size: 0.98rem;
        font-weight: 700;
        color: #172033;
    }

    .step-status {
        margin-left: auto;

        font-family: 'DM Mono', monospace;

        font-size: 0.65rem;
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
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.4rem;
    }


    /* ==================================================
       EVIDENCE BADGE
    ================================================== */

    .evidence-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;

        padding: 0.45rem 0.75rem;

        border-radius: 999px;

        font-family: 'DM Mono', monospace;
        font-size: 0.68rem;
        font-weight: 500;
        letter-spacing: 0.06em;

        margin-bottom: 0.8rem;
    }

    .badge-grounded {
        background: #ecfdf5;
        color: #15803d;
        border: 1px solid #bbf7d0;
    }

    .badge-partial {
        background: #fffbeb;
        color: #a16207;
        border: 1px solid #fde68a;
    }

    .badge-model {
        background: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
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

    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary div {
        color: #334155 !important;

        -webkit-text-fill-color:
            #334155 !important;
    }

    div[data-testid="stExpander"] summary svg {
        color: #475569 !important;
        fill: #475569 !important;
    }


    /* ==================================================
       TEXT AREAS
    ================================================== */

    .stTextArea textarea,
    .stTextArea textarea:disabled,
    div[data-baseweb="textarea"] textarea,
    div[data-testid="stTextArea"] textarea {
        background-color: #f8fafc !important;

        color: #1e293b !important;

        -webkit-text-fill-color:
            #1e293b !important;

        opacity: 1 !important;

        border:
            1px solid #e2e8f0 !important;

        border-radius:
            10px !important;

        font-family:
            'DM Mono',
            monospace !important;

        font-size:
            0.77rem !important;

        line-height:
            1.55 !important;
    }

    div[data-baseweb="textarea"] {
        background-color:
            #f8fafc !important;
    }


    /* ==================================================
       METRICS
    ================================================== */

    div[data-testid="stMetric"] {
        background: #ffffff;

        border: 1px solid #e2e8f0;
        border-radius: 14px;

        padding: 1rem 1.2rem;

        box-shadow:
            0 5px 16px
            rgba(15, 23, 42, 0.03);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div {
        color: #334155 !important;
    }


    /* ==================================================
       CONTAINERS
    ================================================== */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;

        border-color:
            #e2e8f0 !important;

        border-radius:
            16px !important;

        box-shadow:
            0 7px 22px
            rgba(15, 23, 42, 0.04);
    }


    /* ==================================================
       PANEL LABEL
    ================================================== */

    .panel-label {
        font-family: 'DM Mono', monospace;

        font-size: 0.70rem;

        letter-spacing: 0.17em;

        text-transform: uppercase;

        margin-top: 1.8rem;
        margin-bottom: 0.75rem;

        padding-bottom: 0.7rem;
    }

    .panel-label.blue {
        color: #2563eb;
        border-bottom: 1px solid #dbeafe;
    }

    .panel-label.green {
        color: #16a34a;
        border-bottom: 1px solid #dcfce7;
    }


    /* ==================================================
       DOWNLOAD BUTTON
    ================================================== */

    .stDownloadButton > button {
        border-radius: 10px !important;

        border:
            1px solid #c7d2fe !important;

        background:
            #eef2ff !important;

        color:
            #4338ca !important;

        -webkit-text-fill-color:
            #4338ca !important;

        font-weight:
            600 !important;
    }


    /* ==================================================
       ALERTS
    ================================================== */

    div[data-testid="stAlert"],
    div[data-testid="stAlert"] p {
        color: #1e293b !important;
    }


    /* ==================================================
       FOOTER
    ================================================== */

    .notice {
        font-family: 'DM Mono', monospace;

        font-size: 0.68rem;
        color: #94a3b8;

        text-align: center;

        margin-top: 3rem;

        letter-spacing: 0.05em;
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
            font-size: 2.7rem;
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
        "description": "Finds recent and reliable candidate sources.",
    },
    {
        "key": "scrape",
        "num": "02",
        "title": "Web Scraper",
        "description": "Retrieves usable evidence from selected sources.",
    },
    {
        "key": "write",
        "num": "03",
        "title": "Writer Chain",
        "description": "Synthesizes the available evidence into a report.",
    },
    {
        "key": "critique",
        "num": "04",
        "title": "Critic Chain",
        "description": "Checks grounding, attribution, and report quality.",
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
# PIPELINE CARD
# =========================================================

def step_card(
    num: str,
    title: str,
    state: str,
    desc: str,
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

                <span class="
                    step-status
                    {status_class}
                ">
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
# PIPELINE STATE LOGIC
# =========================================================

def get_stage_state(stage: str) -> str:

    current = st.session_state.current_stage

    if current == "waiting":
        return "waiting"

    if current == "done":
        return "done"

    if current == "error":

        if stage == st.session_state.failed_stage:
            return "error"

        failed_stage = st.session_state.failed_stage

        if (
            failed_stage in STAGE_ORDER
            and stage in STAGE_ORDER
        ):

            if (
                STAGE_ORDER.index(stage)
                <
                STAGE_ORDER.index(failed_stage)
            ):
                return "done"

        return "waiting"

    if current == stage:
        return "running"

    if (
        current in STAGE_ORDER
        and stage in STAGE_ORDER
    ):

        if (
            STAGE_ORDER.index(stage)
            <
            STAGE_ORDER.index(current)
        ):
            return "done"

    return "waiting"


def render_pipeline():

    for stage in PIPELINE_STAGES:

        step_card(
            num=stage["num"],
            title=stage["title"],
            state=get_stage_state(
                stage["key"]
            ),
            desc=stage["description"],
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
            Search the web, retrieve useful evidence,
            generate a structured report, and evaluate
            its grounding through a multi-stage AI workflow.
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
# RIGHT — PIPELINE
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
# PROGRESS CALLBACK
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

        st.session_state.current_stage = (
            "error"
        )

    else:

        st.session_state.current_stage = (
            stage
        )

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
        st.session_state.failed_stage = None
        st.session_state.current_stage = "search"

        update_progress("search")

        try:

            result = research_pipeline(
                clean_topic,
                progress_callback=update_progress,
            )

            st.session_state.results = result
            st.session_state.running = False

            if isinstance(result, dict):

                update_progress("done")

            else:

                update_progress("error")

        except Exception as exc:

            st.session_state.running = False

            st.session_state.results = (
                f"Pipeline failed: {exc}"
            )

            update_progress("error")


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
    # ERROR
    # =====================================================

    if isinstance(result, str):

        st.error(result)


    # =====================================================
    # SUCCESS
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

        successful_sources = result.get(
            "successful_sources",
            [],
        )

        failed_sources = result.get(
            "failed_sources",
            [],
        )

        evidence_mode = result.get(
            "evidence_mode",
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
        # EVIDENCE STATUS
        # =================================================

        st.html(
            """
            <div class="section-heading">
                Evidence Status
            </div>
            """
        )


        # -------------------------------------------------
        # Grounded
        # -------------------------------------------------

        if evidence_mode == "grounded":

            st.html(
                """
                <div class="
                    evidence-badge
                    badge-grounded
                ">
                    ✓ GROUNDED
                </div>
                """
            )

            st.success(
                (
                    f"{len(successful_sources)} "
                    "sources were successfully "
                    "retrieved and used as evidence."
                )
            )


        # -------------------------------------------------
        # Partially grounded
        # -------------------------------------------------

        elif evidence_mode == "partially_grounded":

            st.html(
                """
                <div class="
                    evidence-badge
                    badge-partial
                ">
                    ⚠ PARTIALLY GROUNDED
                </div>
                """
            )

            st.warning(
                (
                    f"{len(successful_sources)} "
                    "source(s) were successfully retrieved, "
                    f"while {len(failed_sources)} "
                    "source(s) could not be accessed. "
                    "The report may use clearly identified "
                    "model knowledge where evidence is limited."
                )
            )


        # -------------------------------------------------
        # Model-generated fallback
        # -------------------------------------------------

        elif evidence_mode == "model_generated":

            st.html(
                """
                <div class="
                    evidence-badge
                    badge-model
                ">
                    ⚠ MODEL-GENERATED FALLBACK
                </div>
                """
            )

            st.error(
                (
                    "None of the selected webpages could "
                    "be successfully retrieved. "
                    "The report therefore relies primarily "
                    "on model knowledge and should not be "
                    "treated as externally verified."
                )
            )


        # =================================================
        # SOURCE METRICS
        # =================================================

        metric_success, metric_failed = (
            st.columns(2)
        )

        with metric_success:

            st.metric(
                label="Retrieved Sources",
                value=len(successful_sources),
            )

        with metric_failed:

            st.metric(
                label="Retrieval Failures",
                value=len(failed_sources),
            )


        # =================================================
        # SEARCH RESULTS
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
        # SCRAPED RESEARCH
        # =================================================

        if scraped_content:

            with st.expander(
                "📄 Retrieval Details",
                expanded=False,
            ):

                st.text_area(
                    "Retrieval details",
                    value=scraped_content,
                    height=420,
                    disabled=True,
                    label_visibility="collapsed",
                    key="scraped_content_display",
                )


        # =================================================
        # SUCCESSFUL SOURCES
        # =================================================

        if successful_sources:

            with st.expander(
                "✅ Successfully Retrieved Sources",
                expanded=False,
            ):

                for index, source in enumerate(
                    successful_sources,
                    start=1,
                ):

                    st.markdown(
                        f"### Source {index}"
                    )

                    st.markdown(
                        f"**URL:** {source.get('url', '')}"
                    )

                    st.markdown(
                        "**Status:** Successfully retrieved"
                    )

                    if (
                        index
                        <
                        len(successful_sources)
                    ):
                        st.divider()


        # =================================================
        # FAILED SOURCES
        # =================================================

        if failed_sources:

            with st.expander(
                "⚠️ Retrieval Failures",
                expanded=False,
            ):

                for index, source in enumerate(
                    failed_sources,
                    start=1,
                ):

                    st.markdown(
                        f"### Failed Source {index}"
                    )

                    st.markdown(
                        f"**URL:** {source.get('url', '')}"
                    )

                    reason = source.get(
                        "reason",
                        "Unknown retrieval error.",
                    )

                    st.text_area(
                        "Failure reason",
                        value=reason,
                        height=110,
                        disabled=True,
                        label_visibility="collapsed",
                        key=(
                            f"failed_source_"
                            f"{index}_reason"
                        ),
                    )

                    if (
                        index
                        <
                        len(failed_sources)
                    ):
                        st.divider()


        # =================================================
        # REPORT
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
                label="⬇ Download Report (.md)",
                data=report,
                file_name=(
                    "research_report_"
                    f"{int(time.time())}.md"
                ),
                mime="text/markdown",
            )


        # =================================================
        # CRITIC
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
        Search → Retrieve → Write → Critique ·
        Built with LangChain & Streamlit

    </div>
    """
)