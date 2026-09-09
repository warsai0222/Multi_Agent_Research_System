import requests
import os
from tavily import TavilyClient
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re
from langchain.tools import tool

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}
@tool
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

@tool
def scrape_url(url:str)->str:
    '''
    This function takes a URL as input and returns the text content of the webpage. It uses BeautifulSoup to parse the HTML and extract the text.
    '''
    try:
        response = requests.get(
            url,
            headers=DEFAULT_HEADERS,
            timeout=10  # Set a timeout for the request)
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        html = response.text #store the html content of the webpage

        extracted_text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
        )

        if extracted_text and len(extracted_text.strip()) > 200: #check if the extracted text is not empty and has more than 200 characters
            cleaned_text = re.sub(r'\s+', ' ', extracted_text) #clean the text by removing extra whitespace
            return cleaned_text[:5000] # Limit to 5000 characters


        doc = Document(html) #used only if trafilatura fails to extract the text. Document() is a class from readability library which takes html as input and returns a readable version of the html
        readable_html = doc.summary()
        soup = BeautifulSoup(readable_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "header",
            "footer",
            "nav",
            "aside",
        ]):
            tag.decompose()  # Remove unwanted tags
    
        text = soup.get_text(separator=" ", strip=True) #get the text content of the webpage and remove extra whitespace

        if text and len(text.strip()) > 200: #check if the text is not empty and has more than 200 characters
            cleaned_text = re.sub(r'\s+', ' ', text) #clean the text by removing extra whitespace
            return cleaned_text[:5000] # Limit to 5000 characters

        soup = BeautifulSoup(html, "html.parser") # if readability fails as well, we use Beautiful soup to fall back on the original html and extract the text from it. BeautifulSoup is a library that parses HTML and XML documents and creates a parse tree for easy navigation and extraction of data.
        #less clean because it might inlcude cookie banners, ads button labels, random UI text and etc
        for tag in soup([
            "script",
            "style",
            "header",
            "footer",
            "nav",
            "aside",
        ]):
            tag.decompose()  # Remove unwanted tags

        text = soup.get_text(separator=" ", strip=True) #get the text content of the webpage and remove extra whitespace

        cleaned_text = re.sub(r'\s+', ' ', text) #clean the text by removing extra whitespace

        if cleaned_text and len(cleaned_text.strip()) > 200: #check if the cleaned text is not empty and has more than 200 characters
            return cleaned_text[:5000] # Limit to 5000 characters

        return "The webpage does not contain enough readable text."

    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later."

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"

    except Exception as e: #Rather than crashing the prgm we catch the exception and return the error message
        return str(e)
    
        

        

