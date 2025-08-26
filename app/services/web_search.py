# ...existing code...
import logging
from tavily import TavilyClient
from app.config import settings
from typing import List, Dict, Any, Optional
import datetime
import time
import requests

log = logging.getLogger(__name__)

def build_search_query(user_query: str, append_year: bool = False) -> str:
    # ...existing code...
    current_year = str(datetime.datetime.now().year)
    query = user_query.replace("2024", current_year).replace("2023", current_year)
    if append_year and current_year not in query:
        query = f"{query} {current_year}"
    return query

class WebSearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        # optional default location (city/country) from config
        self.default_location = getattr(settings, "DEFAULT_LOCATION", None)
        self._http = requests.Session()
        self._http.headers.update({"User-Agent": "AiWebSearch/1.0 (+https://example.com)"})
    
    def resolve_location_from_ip(self) -> Optional[Dict[str, Any]]:
        """
        Resolve approximate location from the host's public IP using a free IP geolocation service.
        Returns dict with keys: city, region, country, lat, lon
        """
        try:
            resp = self._http.get("http://ip-api.com/json", timeout=4)
            resp.raise_for_status()
            j = resp.json()
            if j.get("status") == "success":
                return {
                    "city": j.get("city"),
                    "region": j.get("regionName"),
                    "country": j.get("country"),
                    "lat": float(j.get("lat")) if j.get("lat") is not None else None,
                    "lon": float(j.get("lon")) if j.get("lon") is not None else None,
                }
        except Exception as e:
            log.debug("IP geolocation failed: %s", e)
        return None

    def geocode_place(self, place: str) -> Optional[Dict[str, Any]]:
        """
        Geocode a place name using Nominatim (OpenStreetMap). No API key required.
        Returns dict with city/display_name, lat, lon.
        """
        if not place:
            return None
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": place, "format": "json", "limit": 1}
            resp = self._http.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            first = data[0]
            return {
                "display_name": first.get("display_name"),
                "lat": float(first.get("lat")) if first.get("lat") else None,
                "lon": float(first.get("lon")) if first.get("lon") else None,
            }
        except Exception as e:
            log.debug("Geocode (nominatim) failed for '%s': %s", place, e)
            return None

    def resolve_location(self, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Accepts:
            - None or "my location" -> resolve from IP
            - "lat,lon" -> parse coordinates
            - place name -> geocode with nominatim
        Returns standardized dict or None.
        """
        if not location:
            # prefer configured default then IP
            if self.default_location:
                loc = self.geocode_place(self.default_location)
                if loc:
                    return loc
            return self.resolve_location_from_ip()

        loc = location.strip().lower()
        if loc in ("my location", "here", "current location"):
            return self.resolve_location_from_ip()

        # parse "lat,lon"
        if "," in loc:
            parts = [p.strip() for p in loc.split(",")]
            if len(parts) >= 2:
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    return {"lat": lat, "lon": lon}
                except ValueError:
                    pass

        # otherwise assume a place name
        return self.geocode_place(location)

    def search_web(self, query: str, max_results: int = 3, freshness_days: Optional[int] = None, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform web search using Tavily API with simple retry/backoff.

        Accepts an optional `location` which can be:
          - a place name string (will be geocoded),
          - "my location"/None (will fallback to IP geolocation or DEFAULT_LOCATION),
          - a dict with lat/lon already resolved.

        If a location is resolved, it will be passed to the Tavily client via extra kwargs
        (best-effort: client may ignore them). Also the query will be annotated with the
        city/display name for better local results.
        """
        # resolve location if provided as string
        resolved_loc = None
        if isinstance(location, dict):
            resolved_loc = location
        else:
            resolved_loc = self.resolve_location(location)

        # if resolved, augment query and client kwargs
        if resolved_loc:
            city = resolved_loc.get("city") or resolved_loc.get("display_name")
            lat = resolved_loc.get("lat")
            lon = resolved_loc.get("lon")
            if city and city.lower() not in query.lower():
                query = f"{query} {city}"
        query = build_search_query(query, append_year=False)

        attempts = 3
        backoff = 1.0
        last_exc = None
        for attempt in range(1, attempts + 1):
            try:
                extra_kwargs = {}
                if freshness_days is not None:
                    extra_kwargs["freshness_days"] = freshness_days
                # pass location hint to the client if available
                if resolved_loc:
                    if lat is not None and lon is not None:
                        extra_kwargs["lat"] = lat
                        extra_kwargs["lon"] = lon
                    elif resolved_loc.get("display_name"):
                        extra_kwargs["location"] = resolved_loc.get("display_name")

                response = self.client.search(
                    query=query,
                    max_results=max_results,
                    include_answer=True,
                    include_raw_content=False,
                    **extra_kwargs
                )

                results: List[Dict[str, Any]] = []
                for result in response.get("results", [])[:max_results]:
                    results.append({
                        "title": result.get("title", "No title"),
                        "url": result.get("url", ""),
                        "content": result.get("content", "No content available")
                    })

                if response.get("answer"):
                    results.insert(0, {
                        "title": "Direct Answer",
                        "url": "",
                        "content": response["answer"]
                    })

                return results

            except Exception as e:
                last_exc = e
                log.warning("Web search attempt %d failed: %s", attempt, e)
                time.sleep(backoff)
                backoff *= 2

        log.exception("Web search error after retries: %s", last_exc)
        return [{
            "title": "Search Error",
            "url": "",
            "content": f"I encountered an error while searching: {str(last_exc)}"
        }]

    def get_latest_news(self, region: Optional[str] = "Odisha", max_results: int = 5, freshness_days: Optional[int] = 7, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Shortcut to fetch latest news for a region or location.
        If `location` is provided it will be used (can be place name, "my location", or lat,lon).
        """
        # If explicit region provided, prefer it as a query; otherwise if location provided resolve
        if region:
            query = f"{region} news"
            return self.search_web(query, max_results=max_results, freshness_days=freshness_days, location=location)
        # if no region, use location to derive local news
        resolved = self.resolve_location(location)
        if resolved:
            place_name = resolved.get("city") or resolved.get("display_name") or self.default_location
            query = f"{place_name} news" if place_name else "local news"
            return self.search_web(query, max_results=max_results, freshness_days=freshness_days, location=resolved)
        # fallback global news
        return self.search_web("latest news", max_results=max_results, freshness_days=freshness_days)

    # ...existing methods (format_search_results, humanize_results, handle_special_queries) ...
    def format_search_results(self, results: List[Dict[str, Any]]) -> str:
        # ...existing code...
        if not results:
            return "No search results found."

        formatted = "Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            if result['url']:
                formatted += f"   URL: {result['url']}\n"
            formatted += f"   {result['content'][:200]}...\n\n"

        return formatted.strip()

    def humanize_results(self, results: List[Dict[str, Any]], max_chars: int = 800) -> str:
        # ...existing code...
        if not results:
            return "Sorry — I couldn't find anything useful on that. Want me to try a different search?"

        parts: List[str] = []
        if results and results[0].get("title") == "Direct Answer":
            answer = results[0]["content"].strip()
            parts.append(f"Here's what I found: {answer}")
        else:
            parts.append("Looks like I found a few things that might help:")
            for idx, r in enumerate(results[:3], 1):
                title = r.get("title", "").strip() or "Untitled result"
                content = r.get("content", "").strip()
                snippet = content.split("\n")[0][:200]
                if r.get("url"):
                    parts.append(f"{idx}. {title} — {snippet} (Read more: {r['url']})")
                else:
                    parts.append(f"{idx}. {title} — {snippet}")

        reply = " ".join(parts)
        if len(reply) > max_chars:
            reply = reply[:max_chars].rsplit('.', 1)[0] + "..."
        return reply

    def handle_special_queries(self, user_query: str) -> str | None:
        # ...existing code...
        normalized = user_query.strip().lower()
        if normalized in ["what is today", "what's today", "today's date", "date today"]:
            now = datetime.datetime.now()
            formatted = now.strftime("%A, %B %d, %Y, %I:%M %p")
            return f"Today is {formatted}."
        if "time" in normalized and "now" in normalized:
            now = datetime.datetime.now()
            formatted = now.strftime("%I:%M %p, %A, %B %d, %Y")
            return f"The current time is {formatted}."

        # News request examples: allow phrasing with location/place or use IP/default
        if "news" in normalized:
            # try to extract a place name after "news of" / "news in"
            import re
            m = re.search(r"(?:news of|news in|news from|latest news of|latest news in)\s+(.+)$", normalized)
            if m:
                place = m.group(1).strip()
                results = self.get_latest_news(region=place, max_results=5, freshness_days=7, location=place)
                return self.humanize_results(results)
            # otherwise use default or IP location for local news
            results = self.get_latest_news(region=None, max_results=5, freshness_days=7, location=None)
            return self.humanize_results(results)

        # Crypto price example: "price of eth" or "eth price"
        if ("price" in normalized and "eth" in normalized) or normalized.strip() in ["eth price", "price eth", "price of eth"]:
            price_text = self.get_crypto_price("ETH") if hasattr(self, "get_crypto_price") else None
            if price_text:
                return price_text
            results = self.search_web("ETH price USD", max_results=2, freshness_days=1)
            if results and results[0].get("title") == "Direct Answer":
                return results[0]["content"]
            return self.humanize_results(results)

        # Domain-specific examples that prefer fresh results
        if "ipl" in normalized and "2025" in normalized and "winner" in normalized:
            results = self.search_web("IPL 2025 winner", max_results=3, freshness_days=60)
            if results and "winner" in (results[0].get("content") or "").lower():
                return f"The winner of IPL 2025 is: {results[0]['content']}"
            return "The IPL 2025 winner information is not conclusive or not available online yet."

        if "ipl" in normalized and "2025" in normalized and ("owner" in normalized or "ownership" in normalized or "own" in normalized):
            results = self.search_web("IPL 2025 owner", max_results=3, freshness_days=60)
            if results and ("owner" in (results[0].get("content") or "").lower() or "ownership" in (results[0].get("content") or "").lower()):
                return f"The owner information I found: {results[0]['content']}"
            return "The IPL 2025 ownership information is not available or clear online."

        return None
# ...existing code...
    def get_latest_news(self, region: Optional[str] = "Odisha", max_results: int = 5, freshness_days: Optional[int] = 7, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # ...existing code...
        if region:
            query = f"{region} news"
            return self.search_web(query, max_results=max_results, freshness_days=freshness_days, location=location)
        # if no region, use location to derive local news
        resolved = self.resolve_location(location)
        if resolved:
            place_name = resolved.get("city") or resolved.get("display_name") or self.default_location
            query = f"{place_name} news" if place_name else "local news"
            return self.search_web(query, max_results=max_results, freshness_days=freshness_days, location=resolved)
        # fallback global news
        return self.search_web("latest news", max_results=max_results, freshness_days=freshness_days)

    # --- NEW: targeted fallbacks used only when LLM returns no Direct Answer ---
    def get_crypto_price(self, symbol: str = "ETH") -> Optional[str]:
        mapping = {"ETH": "ethereum", "BTC": "bitcoin", "USDT": "tether"}
        coin_id = mapping.get(symbol.upper())
        if not coin_id:
            return None
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"}
        try:
            resp = self._http.get(url, params=params, timeout=6)
            resp.raise_for_status()
            data = resp.json()
            price = data.get(coin_id, {}).get("usd")
            change = data.get(coin_id, {}).get("usd_24h_change")
            if price is None:
                return None
            if change is not None:
                return f"{symbol.upper()} price: ${price:,.2f} (24h change: {change:+.2f}%)"
            return f"{symbol.upper()} price: ${price:,.2f}"
        except Exception as e:
            log.debug("CoinGecko fallback failed: %s", e)
            return None

    def get_news_fallback(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        newsapi_key = getattr(settings, "NEWSAPI_KEY", None)
        if newsapi_key:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {"q": query, "pageSize": max_results, "sortBy": "publishedAt", "apiKey": newsapi_key}
                resp = self._http.get(url, params=params, timeout=6)
                resp.raise_for_status()
                j = resp.json()
                for a in j.get("articles", [])[:max_results]:
                    results.append({
                        "title": a.get("title") or "No title",
                        "url": a.get("url") or "",
                        "content": (a.get("description") or a.get("content") or "").strip()
                    })
                if results:
                    return results
            except Exception as e:
                log.debug("NewsAPI fallback failed: %s", e)
        # Google News RSS fallback
        try:
            rss_url = "https://news.google.com/rss/search"
            params = {"q": query}
            resp = self._http.get(rss_url, params=params, timeout=6)
            resp.raise_for_status()
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")[:max_results]
            for it in items:
                title = it.findtext("title") or "No title"
                link = it.findtext("link") or ""
                desc = it.findtext("description") or ""
                results.append({"title": title, "url": link, "content": desc})
            return results
        except Exception as e:
            log.debug("Google News RSS fallback failed: %s", e)
            return results

    def search_with_fallback(self, query: str, max_results: int = 3, freshness_days: Optional[int] = None, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Try Tavily first (search_web). Only if Tavily returns no Direct Answer do targeted fallbacks:
         - crypto -> CoinGecko
         - news -> NewsAPI / Google News RSS
        """
        results = self.search_web(query, max_results=max_results, freshness_days=freshness_days, location=location)
        if results and results[0].get("title") == "Direct Answer":
            return results  # LLM provided direct answer — do not run fallbacks

        # LLM had no direct answer: choose domain fallback heuristics
        q = query.lower()
        if any(tok in q for tok in ["price", "btc", "eth", "ethereum", "bitcoin"]):
            symbol = "ETH" if "eth" in q or "ethereum" in q else "BTC"
            price = self.get_crypto_price(symbol)
            if price:
                return [{"title": "Direct Answer", "url": "", "content": price}]
        if "news" in q or "latest" in q:
            news = self.get_news_fallback(query, max_results=max_results)
            if news:
                return news
        # No fallback available or fallback failed — return original LLM results (possibly empty/error)
        return results
    # --- end NEW methods ---
# ...existing code...
    def handle_special_queries(self, user_query: str) -> str | None:
        # ...existing code...
        normalized = user_query.strip().lower()
        if normalized in ["what is today", "what's today", "today's date", "date today"]:
            now = datetime.datetime.now()
            formatted = now.strftime("%A, %B %d, %Y, %I:%M %p")
            return f"Today is {formatted}."
        if "time" in normalized and "now" in normalized:
            now = datetime.datetime.now()
            formatted = now.strftime("%I:%M %p, %A, %B %d, %Y")
            return f"The current time is {formatted}."
        # News request examples: allow phrasing with location/place or use IP/default
        if "news" in normalized:
            import re
            m = re.search(r"(?:news of|news in|news from|latest news of|latest news in)\s+(.+)$", normalized)
            if m:
                place = m.group(1).strip()
                query = f"{place} news"
                results = self.search_with_fallback(query, max_results=5, freshness_days=7, location=place)
                return self.humanize_results(results)
            # otherwise use default or IP location for local news
            # prefer LLM first, fall back only if no Direct Answer
            results = self.search_with_fallback("local news", max_results=5, freshness_days=7, location=None)
            return self.humanize_results(results)
        # Crypto price example: "price of eth" or "eth price"
        if ("price" in normalized and "eth" in normalized) or normalized.strip() in ["eth price", "price eth", "price of eth"]:
            # try LLM first, then CoinGecko only if LLM had no direct answer
            results = self.search_with_fallback("ETH price USD", max_results=2, freshness_days=1)
            if results and results[0].get("title") == "Direct Answer":
                return results[0]["content"]
            return
        
# Global instance
web_search = WebSearchService()

def handle_special_queries(user_query: str) -> str | None:
    """
    Module-level wrapper that delegates to the global service instance.
    """
    return web_search.handle_special_queries(user_query)