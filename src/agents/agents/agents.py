#create agents

import os
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser #it is used to parse the output of the agent into a string format, it's required because the agent's output is in a structured format and we need to convert it into a string format for further processing.
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv() #load environment variables from .env file

#model initialization
model = ChatGroq(
    model="groq-llm-chat",
    temperature=0
)

#search agent creation
def build_search_agent():
    return create_agent(
        model=model,
        tools= [web_search],
        system_prompt = ChatPromptTemplate.from_template("""
            You are a web research retrieval agent.

            Your job is to find the most relevant, recent, and reliable webpages for the user's query.

            You have access to a web_search tool.

            Instructions:
            1. Search the web for information relevant to the user's query.
            2. Prefer authoritative, trustworthy, and recent sources.
            3. Select only sources that are likely to contain useful information for answering the query.
            4. Return the URLs of the best sources you find.
            5. Do not write the final answer to the user's question.
            6. Do not summarize the webpages in detail. Another agent will scrape and analyze the content.
            7. Avoid duplicate, low-quality, or irrelevant sources.
            8. If no useful sources are found, return "No relevant sources found."

            User query:
            {input}
            """),

    )

#scrape agent creation
def build_scrape_agent():
    return create_agent(
        model=model,
        tools= [scrape_url],
        system_prompt = ChatPromptTemplate.from_template("""
            You are a web scraping agent.

            Your job is to extract the text content from a given webpage URL.

            You have access to a scrape_url tool.

            Instructions:
            1. Use the scrape_url tool to retrieve the webpage content.
            2. Return the extracted text content from the tool.
            3. Do not answer the original research question.
            4. Do not summarize, analyze, or rewrite the content.
            5. Do not invent or add information that was not returned by the scrape_url tool.
            6. Avoid unnecessary duplicate or irrelevant webpage content.
            7. If the webpage cannot be scraped or contains no useful content, return:
            "No useful content found."
            """)
    )

#writer agent creation
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert research writer.

        Your job is to write clear, structured, factual, and insightful reports
        using only the research provided to you.

        Do not invent facts, claims, statistics, or sources.
        If the provided research is insufficient to support a claim, do not include it.
        """
    ),
    (
        "human",
        """
        Write a detailed research report on the topic below.

        Topic:
        {topic}

        Research Gathered:
        {research}

        Structure the report as:

        - Introduction
        - Key Findings
          - Include at least 3 well-explained findings when the research supports them
        - Conclusion
        - Sources
          - List only the URLs present in the provided research

        Be detailed, factual, clear, and professional.
        """
    )
])

write_chain = writer_prompt | model | StrOutputParser()

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are a research report critic.

        Your job is to evaluate the report for:
        - factual accuracy
        - faithfulness to the provided research
        - clarity
        - structure
        - completeness
        - relevance to the original topic

        Do not assume that a claim is correct just because it sounds plausible.
        Flag any claim that is unsupported by the provided research.
        """
    ),
    (
        "human",
        """
        Evaluate the following research report.

        Original Topic:
        {topic}

        Research Provided:
        {research}

        Report:
        {report}

        Respond in this exact format:

        1. Score: <score from 1-10>/10
        2. Strengths:
           - <strength>
           - <strength>
        3. Weaknesses:
           - <weakness>
           - <weakness>
        4. Unsupported or Questionable Claims:
           - <claim and why it is unsupported>
        5. Suggestions:
           - <specific improvement>
           - <specific improvement>
        6. Overall Assessment:
           <brief overall assessment>
        """
    )
])

critic_chain =critic_prompt | model | StrOutputParser()