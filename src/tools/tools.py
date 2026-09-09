from langchain.tools import tool
import requests
import os
from tavily import TavilyClient
from dotenv import load_dotenv
from rich import print
load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query:str)->str:
    '''
    This function takes a query string as input and returns the search results from Tavily API. Usually, used for recent and reliaable information.
    It returns Titles,Links and snippets of the search results.
    '''
    try:
        search_results = tavily.search(query=query, max_results=5) #maximum 5 results

        results = [] #empty list to store the search results
        for result in search_results.get("results", []): #.get() as tavily.search() returns a dictionary with key "results" which is a list of dictionaries containing the search results
            title = result.get("title", "N/A")
            link = result.get("url", "N/A")
            content = result.get("content", "")
            results.append(
                f"Title: {title}, Link: {link}, Snippet: {content[:300]}\n" #limit snippet to 300 characters
            )

        if not results:
            return "No search results found."

        return "\n---\n".join(results)
    except Exception as e: #Rather than crashing the prgm we catch the exception and return the error message
        return str(e)
            
    


