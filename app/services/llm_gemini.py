import logging
import datetime
import re
from typing import Any, Dict, Optional

import requests
import google.generativeai as genai
from app.config import settings
from app.services.web_search import web_search
from app.services.news_service import news_service

log = logging.getLogger(__name__)

# -------------------------------
# Helper functions
# -------------------------------

def words_to_digits(text: str) -> str:
    """Convert simple number words to digits, e.g. 'two zero twenty five' -> '2025'."""
    mapping = {
        "zero": "0", "one": "1", "two": "2", "three": "3",
        "four": "4", "five": "5", "six": "6", "seven": "7",
        "eight": "8", "nine": "9"
    }
    words = text.lower().split()
    converted = "".join([mapping.get(w, w) for w in words])
    return converted

def get_crypto_price(symbol: str = "BTC") -> str:
    """Fetch real-time crypto price from CoinGecko."""
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        resp = requests.get(url, timeout=5).json()
        price = resp[symbol.lower()]["usd"]
        return f"The current price of {symbol.upper()} is ${price:,} USD."
    except Exception as e:
        log.exception("Crypto API error: %s", e)
        return f"Unable to fetch price for {symbol.upper()}."

def handle_special_queries(user_query: str) -> Optional[str]:
    """Handle dynamic special queries like date, time, IPL winner, crypto prices."""
    query = words_to_digits(user_query.lower())

    now = datetime.datetime.now()

    # -------------------- Date/Time --------------------
    if any(word in query for word in ["time", "now"]):
        return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."
    if any(word in query for word in ["date", "today"]):
        return f"Today is {now.strftime('%A, %B %d, %Y')}."

    # -------------------- Sports --------------------
    if "ipl" in query or "fifa" in query or "match" in query or "league" in query:
        results = web_search.search_web(user_query, max_results=3)
        return f"Here are the latest sports updates:\n{web_search.format_search_results(results)}"

    # -------------------- Cryptocurrency --------------------
    if "bitcoin" in query or "btc" in query:
        return get_crypto_price("BTC")
    if "ethereum" in query or "eth" in query:
        return get_crypto_price("ETH")

    # -------------------- Weather --------------------
    if "weather" in query or "temperature" in query or "forecast" in query:
        results = web_search.search_web(user_query, max_results=3)
        return f"Weather update:\n{web_search.format_search_results(results)}"

    # -------------------- General news / updates --------------------
    if any(word in query for word in ["news", "update", "latest", "developments"]):
        # Extract location from query if present
        location = None
        if "in " in user_query.lower() or "of " in user_query.lower():
            # Try to extract location after "in" or "of"
            import re
            location_match = re.search(r"(?:in|of|from)\s+([a-zA-Z\s]+?)(?:\s+(?:news|update|latest|developments)|$)", user_query.lower())
            if location_match:
                location = location_match.group(1).strip()
        
        # Try dedicated news service first
        if location:
            news_results = news_service.get_news_by_location(location, max_results=5)
        else:
            news_results = news_service.get_latest_news(user_query, max_results=5)
            
        if news_results:
            return f"Here's the latest news:\n{web_search.format_search_results(news_results)}"
        # Fallback to web search if news service fails
        results = web_search.search_web(user_query, max_results=3)
        return f"Here's the latest news:\n{web_search.format_search_results(results)}"

    # -------------------- Fallback --------------------
    return None

# -------------------------------
# Gemini LLM Class
# -------------------------------

class GeminiLLM:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=api_key or settings.GEMINI_API_KEY)
        try:
            self.model = genai.GenerativeModel(model_name)
        except Exception:
            self.model = None
            self.model_name = model_name

    def _call_generate(self, prompt: str, **kwargs) -> Any:
        if self.model:
            return self.model.generate_content(prompt, **kwargs)
        return genai.generate_content(model=self.model_name, contents=prompt, **kwargs)

    def generate_persona_prompt(self, persona: str, user_input: str) -> str:
        """Persona prompts designed to sound like a news anchor."""
        persona_prompts = {
            "Teacher": f"I am Echo, an AI teacher and news anchor made by Shubhachand Patel. Deliver facts clearly and concisely: {user_input}",
            "Pirate": f"I am Echo, an AI pirate made by Shubhachand Patel. Arrr! Here's the scoop: {user_input}",
            "Cowboy": f"I am Echo, an AI cowboy made by Shubhachand Patel. Howdy! Listen up: {user_input}",
            "Robot": f"I am Echo, an AI robot made by Shubhachand Patel. Reporting in robotic precision: {user_input}",
        }
        return persona_prompts.get(persona, f"I am Echo, an AI news anchor made by Shubhachand Patel. {user_input}")

    def generate(self, prompt: str, persona: str = "Teacher") -> str:
        """High-level generate method with dynamic query handling and persona."""
        try:
            # 1️⃣ Handle special queries first
            special_response = handle_special_queries(prompt)
            if special_response:
                return special_response

            # 2️⃣ Build persona prompt
            persona_prompt = self.generate_persona_prompt(persona, prompt)

            # 3️⃣ Generate content via Gemini
            response = self._call_generate(persona_prompt)
            text = getattr(response, "text", None) or "".join(
                [p.text for p in response.candidates[0].content.parts if hasattr(p, "text")]
            )
            return text.strip() if text else "Sorry, I couldn't generate a response."
        except Exception as e:
            log.exception("LLM generation error: %s", e)
            return "Sorry, I couldn't generate a response."

# -------------------------------
# Instantiate
# -------------------------------
llm = GeminiLLM(settings.GEMINI_API_KEY)
