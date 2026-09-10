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

search_model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=800
)

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=4000
)

#search agent creation
def build_search_agent():
    return create_agent(
        model=search_model,
        tools=[web_search],
        system_prompt="""
        You are a web research retrieval agent.

        Your job is to find a small set of recent, reliable, and sufficiently
        diverse sources that collectively provide strong coverage of the user's
        research question.

        You have access to the web_search tool.

        Follow this process:

        1. Perform an initial web search for the user's research topic.

        2. Examine the titles and snippets returned by the search tool and assess
           whether the results provide sufficient coverage of the main aspects
           of the topic.

        3. Consider coverage sufficient when the sources:
           - directly address the user's question,
           - come from credible or authoritative sources,
           - provide more than one perspective or aspect of the topic where relevant,
           - and contain enough information for another agent to build a useful report.

        4. If the initial search has a clear information gap, perform ONE additional
           targeted search specifically aimed at filling that gap.

        5. Do not perform another search if the initial results already provide
           sufficient coverage.

        6. Prefer primary sources, government or institutional publications,
           academic research, reputable industry reports, and established
           news or analytical organizations.

        7. Avoid duplicate sources, low-quality blogs, SEO content, and sources
           that do not directly contribute useful evidence.

        8. Select at most 5 of the strongest sources from all search results.

        9. Do not answer the user's research question.
           Do not write the research report.
           Do not provide detailed summaries.

        10. Return the selected sources in exactly this format:

            Source 1:
            Title: <title>
            URL: <url>

            Source 2:
            Title: <title>
            URL: <url>

        If no reliable sources can be found, return:
        No relevant sources found.
        """
    )

#We don't need to create a separate scrape agent because we can use the scrape_url tool directly in the pipeline. The scrape_url tool is designed to extract text content from a given URL, which is exactly what we need for the scraping step of our research workflow.

#writer agent creation
writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert research writer.

        Your job is to produce a comprehensive, evidence-based research report
        using only the research provided to you.

        Requirements:
        - Do not invent facts, statistics, dates, claims, or sources.
        - Every important factual claim must be supported by the provided research.
        - Distinguish clearly between findings from different sources.
        - When sources disagree or present different perspectives, explain the difference.
        - Include quantitative evidence whenever it is available.
        - Do not infer conclusions that are not supported by the research.
        - If evidence is limited, explicitly state that limitation.
        - Use clean, simple markdown only.
        - Avoid broken markdown formatting.
        - Do not use unnecessary italics.
        - Avoid large tables unless absolutely necessary.
        - Prefer section headings and bullet points over tables.
        """
    ),
    (
        "human",
        """
        Write a detailed research report on the following topic:

        Topic:
        {topic}

        Research:
        {research}

        Structure the report as follows:

        # Title

        ## Executive Summary
        Provide a concise overview of the most important conclusions.

        ## Introduction
        Explain the topic, why it matters, and the scope of the report.

        ## Key Findings
        Present at least 3 key findings.
        For each finding:
        - explain what the evidence shows
        - identify which source supports it
        - include relevant numbers, dates, or examples when available
        - explain why the finding matters

        ## Trends and Patterns
        Identify broader patterns across the research sources.

        ## Risks and Challenges
        Discuss negative impacts, uncertainties, limitations, or potential risks.

        ## Opportunities and Implications
        Explain what the findings mean for relevant stakeholders.

        ## Areas of Uncertainty
        Identify claims where the available evidence is incomplete, conflicting,
        or insufficient.

        ## Conclusion
        Summarize the strongest conclusions supported by the research.

        ## Sources
        List only URLs that appear in the provided research.

        Important formatting instructions:
        - Use clean markdown.
        - Use bullet points where helpful.
        - Do not use tables.
        - Do not use italic markdown unless necessary.
        - Ensure proper spacing and punctuation.
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
        Flag any claim that is unsupported by the provided research. If no retreived output from srcaper agent, then don't generate a summary and exclusively return "No report was generated, and hence can't be evaluated."
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
            Provide a concise overall assessment of approximately 100-200 words.
            Summarize the report's overall quality, strongest aspects, biggest weaknesses,
            and whether it is sufficiently reliable and complete.
            Do not repeat all previous points in detail.
        7. If applicable:
           - if no report was returned don't generate a summary and exclusively return "No report was generated, and hence can't be evaluated."
        """
    )
])

critic_chain =critic_prompt | model | StrOutputParser()

