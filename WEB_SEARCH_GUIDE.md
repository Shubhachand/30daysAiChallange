# Web Search Skill Integration Guide

## Overview
Your AI agent now has web search capabilities powered by Tavily API. When users ask questions that require current information, the agent will automatically search the web and incorporate the latest information into its responses.

## How It Works

### Automatic Search Trigger
The agent automatically detects when a user's query requires web search based on keywords:
- `search`, `find`, `look up`
- `latest`, `recent`, `news`, `current`, `update`
- `information about`, `tell me about`

### Search Process
1. User asks a question that triggers web search
2. System extracts search query from the prompt
3. Tavily API performs the web search
4. Search results are formatted and added to the LLM prompt
5. LLM generates a response incorporating the search results

## Setup Requirements

### Environment Variables
Add the following to your `.env` file:
```bash
TAVILY_API_KEY=your_tavily_api_key_here
```

### Dependencies
The following packages are required:
- `tavily-python` - Web search API client
- `python-dateutil` - Date parsing utilities

## API Usage Examples

The agent will automatically use web search for queries like:
- "What are the latest developments in AI research?"
- "Find me recent news about space exploration"
- "Search for information about climate change solutions"
- "Tell me about the current stock market trends"

## Customization

### Modifying Search Keywords
Edit the `search_keywords` list in `app/services/llm_gemini.py` to add or remove trigger words.

### Adjusting Search Results
Modify the `max_results` parameter in the web search calls to control how many results are returned.

### Response Formatting
Update the `format_search_results` method in `app/services/web_search.py` to change how search results are presented to the LLM.

## Testing

Run the test scripts to verify functionality:
```bash
python test_web_search.py          # Tests web search API directly
python test_function_calling.py    # Tests integration with Gemini LLM
```

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure `TAVILY_API_KEY` is set in your `.env` file
2. **Network Issues**: Check internet connectivity if searches fail
3. **Rate Limits**: Tavily has usage limits - check their documentation

### Error Handling
The system includes robust error handling:
- Graceful fallback to regular LLM responses if search fails
- Error messages are logged for debugging
- Users receive appropriate fallback responses

## Next Steps
Consider adding additional skills:
- Weather information
- News aggregation
- Stock market data
- Sports scores
- Calculator functions
