# Multi Agent Research System

An LLM-powered research workflow that searches the web, scrapes source pages, drafts a report, and critiques the result in a multi-step pipeline.

The project is intentionally small and easy to extend. You can run the full pipeline from `main.py`, or import the individual tools, agents, and pipeline functions into your own scripts.

## What it does

- Searches the web for recent, relevant sources using Tavily.
- Scrapes and cleans content from selected URLs.
- Generates a structured research report from the collected context.
- Produces a critique of the report to highlight gaps or unsupported claims.

## Project Architecture

The code is organized into a simple layered flow:

- `src/tools/tools.py` contains the low-level web utilities:
	- `web_search(query)` queries Tavily and formats search results.
	- `scrape_url(url)` fetches and extracts readable page content.
- `src/agents/agents/agents.py` builds the agent and chain objects:
	- a search agent for source discovery,
	- a scrape agent for page extraction,
	- a writing chain for report generation,
	- a critic chain for review and feedback.
- `src/pipelines/pipeline.py` orchestrates the multi-step workflow:
	- search,
	- scrape,
	- write,
	- critique.
- `main.py` is the simplest entry point for running the pipeline locally.

## Repository Layout

```text
Multi_Agent_Research_System/
├── main.py
├── app.py
├── requirements.txt
└── src/
    ├── tools/
    │   └── tools.py
    ├── agents/
    │   └── agents/
    │       └── agents.py
    └── pipelines/
        └── pipeline.py
```

## Requirements

- Python 3.12 or newer is recommended.
- A valid Tavily API key.
- A Python environment with the packages listed in `requirements.txt`.

## Environment Variables

Create a `.env` file in the project root and set:

```env
TAVILY_API_KEY=your_tavily_api_key_here
```

## Setup

If you already have a virtual environment named `mlangagent`, activate it first:

```bash
conda activate mlangagent
```

Then install dependencies:

```bash
python -m pip install -r requirements.txt
```

If you are using VS Code, make sure the workspace interpreter is set to the same environment so the editor and terminal agree on imports.

## Running the project

Run the sample entry point:

```bash
python main.py
```

This will execute the full research pipeline for the topic defined in `main.py`.

## How to work with the code

You can use the project at several levels:

### 1. Use the pipeline directly

```python
from src.pipelines.pipeline import research_pipeline

result = research_pipeline("The impact of AI on healthcare in 2026")
print(result)
```

### 2. Reuse individual tools

```python
from src.tools.tools import web_search, scrape_url

results = web_search("recent AI research in healthcare")
page_text = scrape_url("https://example.com")
```

### 3. Build on the agent layer

The agent builders in `src/agents/agents/agents.py` are the best place to customize prompts, swap models, or add new tools.

## Customization ideas

- Change the topic in `main.py` to research a different subject.
- Replace the model in `src/agents/agents/agents.py` with another Groq-supported model.
- Add more tools in `src/tools/tools.py` for PDF extraction, citation formatting, or summarization.
- Expand the pipeline in `src/pipelines/pipeline.py` to loop through multiple source URLs instead of only one.

## Notes

- The current pipeline is optimized for a simple single-run workflow, not a full production research system.
- Search results are formatted as plain text to keep the system easy to inspect and debug.
- The scraping layer uses BeautifulSoup, readability-lxml, and trafilatura to extract readable content from pages.

## Troubleshooting

- If `readability.Document` fails to import, make sure `readability-lxml` is installed and that the unrelated `readability` package is not shadowing it.
- If imports fail in VS Code but work in the terminal, the editor is probably using a different Python interpreter.
- If `TAVILY_API_KEY` is missing, web search calls will fail during runtime.

## Contributing

Contributions are welcome. Good first improvements include:

- improving source selection,
- scraping multiple URLs,
- adding citation formatting,
- adding tests,
- and improving error handling and logging.

Please keep changes focused and maintain the current modular structure.

## License

This project is provided under the terms of the repository license.