from src.agents.agents.agents import build_search_agent, build_scrape_agent, write_chain, critic_chain  
import time
import re

def research_pipeline(topic:str)->dict:
    '''
    This function takes a research topic as input and returns the research results from Tavily API. It uses the build_search_agent() to create a search agent, which is then used to perform the search. The results are then passed to the write_chain() to generate a summary of the research.
    '''
    try:
        state = {} #state dictionary to store the search results and summary
        #search agent working
        print("Step 1: Searching for research papers on the topic...")
        print("="*50)

        search_agent = build_search_agent()
        search_results = search_agent.invoke({
                            "messages": [
                                (
                                    "user",
                                    f"Find the most relevant, recent, and reliable sources for: {topic}"
                                )
                            ]
                        })
        state["search_results"] = search_results['messages'][-1].content 
        print("\n search results:", state["search_results"])


        # reader agent working
        print("Step 2: Reading the research papers...")
        print("=" * 50)

        reader_agent = build_scrape_agent()

        urls = re.findall(
                    r'https?://[^\s\]\)\>,]+',
                    state["search_results"]
                )

        print("URLs found:", urls)

        reader_results = ""

        for url in urls[:3]:
            print("Scraping:", url)

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
            time.sleep(1)  # Add a short delay between requests to avoid overwhelming the server

        state["scraped_content"] = reader_results

        print("\nScraped Content:", state["scraped_content"])



        
        # writer chain working
        print("Step 3: Generating the research report...")
        print("=" * 50)

        research_context = (
            f"Search Results:\n{state['search_results']}\n\n"
            f"Scraped Content:\n{state['scraped_content']}\n"
        )

        state["report"] = write_chain.invoke({
            "topic": topic,
            "research": research_context
        })

        print("\nResearch Report:", state["report"])

        #critic report working
        print("Step 4: Critiquing the research report...")
        print("=" * 50)

        state["critique"] = critic_chain.invoke({
            "topic": topic,
            "report": state["report"],
            "research": research_context
        })

        print("\nCritique Report:", state["critique"])

        return state

    except Exception as e:
        return str(e)