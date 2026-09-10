import streamlit as st
from src.pipelines.pipeline import research_pipeline


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.html("""
<style>

.stApp {
    background:
        radial-gradient(circle at top left, rgba(99,102,241,0.10), transparent 30%),
        radial-gradient(circle at top right, rgba(168,85,247,0.08), transparent 28%),
        linear-gradient(180deg, #f8fafc 0%, #ffffff 50%, #f8fafc 100%);
    color: #111827;
}

.block-container {
    max-width: 1180px;
    padding-top: 3rem;
    padding-bottom: 4rem;
}


/* ================= HERO ================= */

.hero {
    padding: 2rem 0 1rem 0;
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border-radius: 999px;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    color: #4f46e5;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 54px;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -2px;
    margin-bottom: 16px;

    background: linear-gradient(
        90deg,
        #111827,
        #4f46e5,
        #7c3aed
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-subtitle {
    font-size: 17px;
    line-height: 1.7;
    color: #64748b;
    max-width: 820px;
}


/* ================= PIPELINE ================= */

.pipeline-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-top: 35px;
    margin-bottom: 40px;
}

.pipeline-card {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #e2e8f0;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 8px 24px rgba(15,23,42,0.05);
    transition: all 0.2s ease;
    min-height: 145px;
}

.pipeline-card:hover {
    transform: translateY(-4px);
    border-color: #c7d2fe;
    box-shadow: 0 12px 30px rgba(79,70,229,0.10);
}

.pipeline-number {
    color: #6366f1;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 12px;
}

.pipeline-title {
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #111827;
}

.pipeline-desc {
    font-size: 14px;
    line-height: 1.5;
    color: #64748b;
}


/* ================= INPUT ================= */

.input-heading {
    font-size: 22px;
    font-weight: 700;
    margin-top: 15px;
    margin-bottom: 5px;
    color: #111827;
}

.input-subheading {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 15px;
}


/* ================= TEXT INPUT ================= */

div[data-testid="stTextInput"] input {
    background: #ffffff;
    border: 1px solid #dbe3ef;
    color: #111827;
    border-radius: 12px;
    padding: 12px;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #6366f1;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.12);
}


/* ================= BUTTON ================= */

div.stButton > button {
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: 700;
    border: none;

    background: linear-gradient(
        90deg,
        #6366f1,
        #8b5cf6
    );

    color: white;
    transition: 0.2s;
}

div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(99,102,241,0.20);
}


/* ================= TABS ================= */

button[data-baseweb="tab"] {
    font-weight: 650;
    color: #64748b;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #4f46e5;
}


/* ================= RESULTS ================= */

.result-header {
    font-size: 24px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 5px;
    color: #111827;
}

.result-subtitle {
    color: #64748b;
    font-size: 14px;
    margin-bottom: 20px;
}


/* ================= TEXT AREA ================= */

textarea {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
}


/* ================= FOOTER ================= */

.footer {
    margin-top: 60px;
    padding-top: 20px;
    border-top: 1px solid #e2e8f0;
    color: #94a3b8;
    text-align: center;
    font-size: 13px;
}


/* ================= MOBILE ================= */

@media (max-width: 900px) {
    .pipeline-grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .hero-title {
        font-size: 42px;
    }
}

@media (max-width: 600px) {
    .pipeline-grid {
        grid-template-columns: 1fr;
    }

    .hero-title {
        font-size: 36px;
    }
}

</style>
""")


# =========================================================
# SESSION STATE
# =========================================================

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""


# =========================================================
# HERO
# =========================================================

st.html("""
<div class="hero">

    <div class="hero-badge">
        AI Research Workflow
    </div>

    <div class="hero-title">
        Multi-Agent Research System
    </div>

    <div class="hero-subtitle">
        Search reliable sources, extract relevant evidence,
        generate a comprehensive research report, and evaluate
        its factual grounding through a multi-stage AI workflow.
    </div>

</div>
""")


# =========================================================
# PIPELINE CARDS
# =========================================================

st.html("""
<div class="pipeline-grid">

    <div class="pipeline-card">
        <div class="pipeline-number">01</div>

        <div class="pipeline-title">
            🔎 Search
        </div>

        <div class="pipeline-desc">
            Finds recent, relevant, and reliable sources
            related to the research question.
        </div>
    </div>


    <div class="pipeline-card">
        <div class="pipeline-number">02</div>

        <div class="pipeline-title">
            📚 Scrape
        </div>

        <div class="pipeline-desc">
            Opens selected sources and extracts useful
            webpage content for analysis.
        </div>
    </div>


    <div class="pipeline-card">
        <div class="pipeline-number">03</div>

        <div class="pipeline-title">
            ✍️ Write
        </div>

        <div class="pipeline-desc">
            Synthesizes the collected evidence into a
            structured research report.
        </div>
    </div>


    <div class="pipeline-card">
        <div class="pipeline-number">04</div>

        <div class="pipeline-title">
            🧠 Critique
        </div>

        <div class="pipeline-desc">
            Evaluates the final report for accuracy,
            completeness, clarity, and grounding.
        </div>
    </div>

</div>
""")


# =========================================================
# INPUT SECTION
# =========================================================

st.html("""
<div class="input-heading">
    Start your research
</div>

<div class="input-subheading">
    Enter a topic below and let the research agents handle the rest.
</div>
""")


topic = st.text_input(
    "Research Topic",
    placeholder="e.g. The impact of AI on the job market in 2026",
    label_visibility="collapsed"
)


run_button = st.button(
    "Run Research",
    type="primary"
)


# =========================================================
# RUN PIPELINE
# =========================================================

if run_button:

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        st.session_state.last_topic = topic

        try:

            with st.status(
                "Running research pipeline...",
                expanded=True
            ) as status:

                st.write("🔎 Searching for relevant sources")
                st.write("📚 Extracting webpage content")
                st.write("✍️ Generating research report")
                st.write("🧠 Evaluating report quality")

                result = research_pipeline(topic)

                st.session_state.research_result = result

                status.update(
                    label="Research complete",
                    state="complete",
                    expanded=False
                )

        except Exception as e:

            st.error(f"Pipeline failed: {e}")


# =========================================================
# DISPLAY RESULTS
# =========================================================

result = st.session_state.research_result


if result is not None:

    if isinstance(result, str):

        st.error(result)

    else:

        st.success(
            f'Research completed for "{st.session_state.last_topic}"'
        )


        report_tab, critique_tab, sources_tab, raw_tab = st.tabs(
            [
                "📄 Research Report",
                "🧠 Critique",
                "🔗 Sources",
                "📚 Raw Research"
            ]
        )


        # =================================================
        # REPORT
        # =================================================

        with report_tab:

            st.html("""
            <div class="result-header">
                Research Report
            </div>

            <div class="result-subtitle">
                Evidence-based report generated from the collected research.
            </div>
            """)

            report = result.get("report", "")

            if report:

                # Markdown is correct HERE because
                # the report itself is Markdown.
                st.markdown(report)

            else:

                st.warning(
                    "No research report was generated."
                )


        # =================================================
        # CRITIQUE
        # =================================================

        with critique_tab:

            st.html("""
            <div class="result-header">
                Critic Evaluation
            </div>

            <div class="result-subtitle">
                Analysis of factual grounding, clarity,
                completeness, and overall report quality.
            </div>
            """)

            critique = result.get("critique", "")

            if critique:

                st.markdown(critique)

            else:

                st.warning(
                    "No critique was generated."
                )


        # =================================================
        # SOURCES
        # =================================================

        with sources_tab:

            st.html("""
            <div class="result-header">
                Sources Discovered
            </div>

            <div class="result-subtitle">
                Sources identified by the research search agent.
            </div>
            """)

            sources = result.get(
                "search_results",
                ""
            )

            if sources:

                st.markdown(sources)

            else:

                st.warning(
                    "No sources were found."
                )


        # =================================================
        # RAW SCRAPED RESEARCH
        # =================================================

        with raw_tab:

            st.html("""
            <div class="result-header">
                Extracted Research Content
            </div>

            <div class="result-subtitle">
                Raw text collected from webpages before
                synthesis by the writer.
            </div>
            """)

            scraped = result.get(
                "scraped_content",
                ""
            )

            if scraped:

                st.text_area(
                    "Raw Research",
                    value=scraped,
                    height=600,
                    disabled=True,
                    label_visibility="collapsed"
                )

            else:

                st.warning(
                    "No useful webpage content was extracted."
                )


# =========================================================
# FOOTER
# =========================================================

st.html("""
<div class="footer">
    Multi-Agent Research System
    &nbsp;•&nbsp;
    Search → Scrape → Write → Critique
</div>
""")