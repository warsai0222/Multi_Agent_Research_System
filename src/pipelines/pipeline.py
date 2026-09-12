from src.agents.agents.agents import (
    build_search_agent,
    write_chain,
    critic_chain
)

from src.tools.tools import scrape_url

import time
import re


# =========================================================
# PIPELINE SETTINGS
# =========================================================

TARGET_SUCCESSFUL_SOURCES = 3
MAX_CONTENT_PER_SOURCE = 5000


# =========================================================
# HELPER — CHECK WHETHER SCRAPING FAILED
# =========================================================

def scrape_failed(scraped_text: str) -> bool:
    """
    Returns True when the scraper did not retrieve useful webpage content.
    """

    if not scraped_text:
        return True

    text = scraped_text.lower()

    failure_signals = [
        "http error occurred",
        "403 client error",
        "401 client error",
        "forbidden",
        "no useful content found",
        "connection error",
        "request exception",
        "failed to retrieve",
        "error occurred",
    ]

    return any(
        signal in text
        for signal in failure_signals
    )


# =========================================================
# MAIN RESEARCH PIPELINE
# =========================================================

def research_pipeline(
    topic: str,
    progress_callback=None
) -> dict:

    """
    Runs the multi-stage research pipeline.

    Stages:
        1. Search for candidate sources
        2. Attempt retrieval until enough useful sources are found
        3. Generate the report
        4. Critique the report

    Args:
        topic:
            Research topic.

        progress_callback:
            Optional callback used by Streamlit
            to display the current pipeline stage.

    Returns:
        dict containing:
            search_results
            scraped_content
            successful_sources
            failed_sources
            evidence_mode
            report
            critique
    """

    def update_stage(stage_name):

        if progress_callback:
            progress_callback(stage_name)

    try:

        state = {}


        # =================================================
        # STEP 1 — SEARCH
        # =================================================

        update_stage("search")

        search_agent = build_search_agent()

        search_results = search_agent.invoke({
            "messages": [
                (
                    "user",
                    (
                        "Find the most relevant, recent, "
                        "and reliable sources for: "
                        f"{topic}"
                    )
                )
            ]
        })

        state["search_results"] = (
            search_results["messages"][-1].content
        )


        # =================================================
        # EXTRACT CANDIDATE URLS
        # =================================================

        urls = re.findall(
            r'URL:\s*(https?://\S+)',
            state["search_results"]
        )

        # Remove duplicate URLs while preserving order
        urls = list(dict.fromkeys(urls))


        # =================================================
        # STEP 2 — RETRIEVAL / SCRAPING
        # =================================================

        update_stage("scrape")

        successful_sources = []
        failed_sources = []

        display_results = []


        # -------------------------------------------------
        # Try candidates until 3 successful sources
        # -------------------------------------------------

        for url in urls:

            # We already have enough evidence
            if (
                len(successful_sources)
                >= TARGET_SUCCESSFUL_SOURCES
            ):
                break

            try:

                scraped_text = scrape_url.invoke({
                    "url": url
                })

            except Exception as exc:

                scraped_text = (
                    f"Scraping exception: {exc}"
                )


            # ---------------------------------------------
            # FAILED RETRIEVAL
            # ---------------------------------------------

            if scrape_failed(scraped_text):

                failed_sources.append({
                    "url": url,
                    "reason": scraped_text
                })

                display_results.append(
                    f"Source: {url}\n"
                    f"Status: RETRIEVAL FAILED\n"
                    f"{scraped_text}\n"
                )

                continue


            # ---------------------------------------------
            # SUCCESSFUL RETRIEVAL
            # ---------------------------------------------

            content = (
                scraped_text[
                    :MAX_CONTENT_PER_SOURCE
                ]
            )

            successful_sources.append({
                "url": url,
                "content": content
            })

            display_results.append(
                f"Source: {url}\n"
                f"Status: RETRIEVED SUCCESSFULLY\n"
                f"{content}\n"
            )

            time.sleep(1)


        # =================================================
        # STORE RETRIEVAL RESULTS
        # =================================================

        state["successful_sources"] = (
            successful_sources
        )

        state["failed_sources"] = (
            failed_sources
        )

        state["scraped_content"] = (
            "\n\n".join(display_results)
        )


        # =================================================
        # DETERMINE EVIDENCE MODE
        # =================================================

        success_count = len(
            successful_sources
        )

        if (
            success_count
            >= TARGET_SUCCESSFUL_SOURCES
        ):

            evidence_mode = "grounded"

        elif success_count > 0:

            evidence_mode = (
                "partially_grounded"
            )

        else:

            evidence_mode = (
                "model_generated"
            )

        state["evidence_mode"] = (
            evidence_mode
        )


        # =================================================
        # BUILD RETRIEVED EVIDENCE
        # =================================================

        retrieved_evidence = ""

        if successful_sources:

            retrieved_sections = []

            for index, source in enumerate(
                successful_sources,
                start=1
            ):

                retrieved_sections.append(
                    f"""
RETRIEVED SOURCE {index}

URL:
{source["url"]}

CONTENT:
{source["content"]}
"""
                )

            retrieved_evidence = (
                "\n\n".join(
                    retrieved_sections
                )
            )

        else:

            retrieved_evidence = (
                "No full webpage content was "
                "successfully retrieved."
            )


        # =================================================
        # BUILD FAILED SOURCE INFORMATION
        # =================================================

        failed_source_context = ""

        if failed_sources:

            failed_sections = []

            for source in failed_sources:

                failed_sections.append(
                    f"""
URL:
{source["url"]}

STATUS:
Retrieval failed.

REASON:
{source["reason"]}
"""
                )

            failed_source_context = (
                "\n\n".join(
                    failed_sections
                )
            )

        else:

            failed_source_context = (
                "No source retrieval failures."
            )


        # =================================================
        # EVIDENCE NOTICE FOR WRITER
        # =================================================

        if evidence_mode == "grounded":

            evidence_notice = """
EVIDENCE MODE: GROUNDED

Three successfully retrieved sources are available.

Base externally supported factual claims on the retrieved evidence.
"""

        elif (
            evidence_mode
            == "partially_grounded"
        ):

            evidence_notice = f"""
EVIDENCE MODE: PARTIALLY GROUNDED

Only {success_count} source(s) were successfully retrieved.

Use retrieved sources as the primary evidence.

You may use general model knowledge to provide additional context,
but clearly distinguish model-generated background from externally
retrieved evidence.

Do not imply that failed sources were read or verified.
"""

        else:

            evidence_notice = """
EVIDENCE MODE: MODEL-GENERATED FALLBACK

None of the selected webpages could be successfully retrieved.

You may still provide a useful general overview using your existing
model knowledge.

However:

- Clearly state near the beginning of the report that external
  source retrieval failed.
- Do not represent the report as externally verified.
- Do not attribute claims to the failed URLs.
- Do not imply that any failed source was read.
- Clearly distinguish this report as model-generated background.
"""


        # =================================================
        # FINAL RESEARCH CONTEXT
        # =================================================

        research_context = f"""
{evidence_notice}


==============================
RETRIEVED EVIDENCE
==============================

{retrieved_evidence}


==============================
SOURCES THAT COULD NOT BE RETRIEVED
==============================

{failed_source_context}
"""


        # =================================================
        # STEP 3 — WRITE
        # =================================================

        update_stage("write")

        state["report"] = (
            write_chain.invoke({
                "topic": topic,
                "research": research_context
            })
        )


        # =================================================
        # STEP 4 — CRITIQUE
        # =================================================

        update_stage("critique")

        state["critique"] = (
            critic_chain.invoke({
                "topic": topic,
                "report": state["report"],
                "research": research_context
            })
        )


        # =================================================
        # DONE
        # =================================================

        update_stage("done")

        return state


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as exc:

        if progress_callback:
            progress_callback("error")

        return str(exc)