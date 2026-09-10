from src.agents.agents.agents import (
    build_search_agent,
    build_scrape_agent,
    write_chain,
    critic_chain
)

import time
import re


def research_pipeline(topic: str, progress_callback=None) -> dict:
    """
    Runs the multi-stage research pipeline.

    Args:
        topic: Research topic
        progress_callback: Optional function to update UI with current stage

    Returns:
        dict: Contains search results, scraped content, research report, and critique.
    """

    def update_stage(stage_name):
        if progress_callback:
            progress_callback(stage_name)

    try:
        state = {}

        # ---------------------------
        # Step 1: Search
        # ---------------------------
        update_stage("search")

        search_agent = build_search_agent()
        search_results = search_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Find the most relevant, recent, and reliable sources for: {topic}"
                )
            ]
        })

        state["search_results"] = search_results["messages"][-1].content

        # ---------------------------
        # Step 2: Scrape
        # ---------------------------
        update_stage("scrape")

        reader_agent = build_scrape_agent()

        urls = re.findall(
                        r'URL:\s*(https?://\S+)',
                        state["search_results"]
                    )

        reader_results = ""

        for url in urls[:3]:
            result = reader_agent.invoke({
                "messages": [
                    (
                        "user",
                        f"""
                        Scrape the following URL and return the extracted webpage content.

                        URL:
                        {url}
                        """
                    )
                ]
            })

            scraped_text = result["messages"][-1].content
            reader_results += f"\nSource: {url}\n{scraped_text[:5000]}\n"
            time.sleep(1)

        state["scraped_content"] = reader_results

        # ---------------------------
        # Step 3: Write
        # ---------------------------
        update_stage("write")

        research_context = (
            f"Search Results:\n{state['search_results']}\n\n"
            f"Scraped Content:\n{state['scraped_content']}\n"
        )

        state["report"] = write_chain.invoke({
            "topic": topic,
            "research": research_context
        })

        # ---------------------------
        # Step 4: Critique
        # ---------------------------
        update_stage("critique")

        state["critique"] = critic_chain.invoke({
            "topic": topic,
            "report": state["report"],
            "research": research_context
        })

        update_stage("done")

        return state

    except Exception as e:
        if progress_callback:
            progress_callback("error")
        return str(e)