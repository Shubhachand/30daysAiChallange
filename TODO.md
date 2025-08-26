# Agent Skills Implementation Plan

## Phase 1: Web Search Skill
- [x] Update config.py with TAVILY_API_KEY
- [x] Update requirements.txt with tavily-python
- [x] Create web_search.py service
- [x] Update llm_gemini.py with function calling for web search
- [x] Update agent.py to handle function responses (no changes needed)

## Phase 2: Weather Skill  
- [ ] Update config.py with OPENWEATHER_API_KEY
- [ ] Create weather_service.py
- [ ] Update llm_gemini.py with weather function
- [ ] Test weather functionality

## Phase 3: News Skill
- [ ] Update config.py with NEWS_API_KEY
- [ ] Create news_service.py
- [ ] Update llm_gemini.py with news function
- [ ] Test news functionality

## Phase 4: Testing & Integration
- [x] Test web search functionality
- [x] Test web search integration with Gemini
- [x] Update documentation (WEB_SEARCH_GUIDE.md created)
