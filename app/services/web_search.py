import logging
from tavily import TavilyClient
from app.config import settings
from typing import List, Dict, Any, Optional
import datetime
import time
import requests
import xml.etree.ElementTree as ET
import re

log = logging.getLogger(__name__)

def build_search_query(user_query: str, append_year: bool = False) -> str:
    current_year = str(datetime.datetime.now().year)
    query = user_query.replace("2024", current_year).replace("2023", current_year)
    if append_year and current_year not in query:
        query = f"{query} {current_year}"
    return query

class WebSearchService:
    def __init__(self):
        self.client = TavilyClient(api_key=getattr(settings, "TAVILY_API_KEY", None))
        self.default_location = getattr(settings, "DEFAULT_LOCATION", None)
        self._http = requests.Session()
        self._http.headers.update({"User-Agent": "AiWebSearch/1.0 (+https://example.com)"})

    def update_api_key(self, new_key):
        """Update the Tavily API key and re-initialize the client."""
        self.client = TavilyClient(api_key=new_key)

    def resolve_location_from_ip(self) -> Optional[Dict[str, Any]]:
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
                "city": first.get("display_name").split(",")[0] if first.get("display_name") else None,
                "lat": float(first.get("lat")) if first.get("lat") else None,
                "lon": float(first.get("lon")) if first.get("lon") else None,
            }
        except Exception as e:
            log.debug("Geocode (nominatim) failed for '%s': %s", place, e)
            return None

    def resolve_location(self, location: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not location:
            if self.default_location:
                loc = self.geocode_place(self.default_location)
                if loc:
                    return loc
            return self.resolve_location_from_ip()

        loc = location.strip().lower()
        if loc in ("my location", "here", "current location"):
            return self.resolve_location_from_ip()

        if "," in loc:
            parts = [p.strip() for p in loc.split(",")]
            if len(parts) >= 2:
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])
                    return {"lat": lat, "lon": lon}
                except ValueError:
                    pass

        return self.geocode_place(location)

    # ---------------- Core Tavily search ----------------
    def search_web(self, query: str, max_results: int = 3, freshness_days: Optional[int] = None, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        resolved_loc = location if isinstance(location, dict) else self.resolve_location(location)

        if resolved_loc:
            city = resolved_loc.get("city") or resolved_loc.get("display_name")
            if city and city.lower() not in query.lower():
                query = f"{query} {city}"
        query = build_search_query(query, append_year=False)

        attempts = 3
        backoff = 1.0
        last_exc = None
        for attempt in range(1, attempts + 1):
            try:
                extra_kwargs: Dict[str, Any] = {}
                if freshness_days is not None:
                    extra_kwargs["freshness_days"] = freshness_days
                if resolved_loc:
                    lat = resolved_loc.get("lat")
                    lon = resolved_loc.get("lon")
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

    # ---------------- News fallbacks (API -> RSS) ----------------
    def get_news_fallback(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        newsapi_key = getattr(settings, "NEWS_API_KEY", None) or getattr(settings, "NEWSAPI_KEY", None)
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
                    log.debug("NewsAPI returned %d articles for query=%s", len(results), query)
                    return results
            except Exception as e:
                log.debug("NewsAPI fallback failed: %s", e)

        # Google News RSS fallback
        try:
            rss_url = "https://news.google.com/rss/search"
            params = {"q": query}
            resp = self._http.get(rss_url, params=params, timeout=6)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")[:max_results]
            for it in items:
                title = it.findtext("title") or "No title"
                link = it.findtext("link") or ""
                desc = it.findtext("description") or ""
                results.append({"title": title, "url": link, "content": desc})
            log.debug("Google News RSS returned %d items for query=%s", len(results), query)
            return results
        except Exception as e:
            log.debug("Google News RSS fallback failed: %s", e)
            return results

    # ---------------- Combined fallback pipeline ----------------
    def search_with_fallback(self, query: str, max_results: int = 3, freshness_days: Optional[int] = None, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = self.search_web(query, max_results=max_results, freshness_days=freshness_days, location=location)
        if results and results[0].get("title") == "Direct Answer":
            return results

        q = query.lower()
        if "news" in q or "latest" in q:
            news = self.get_news_fallback(query, max_results=max_results)
            if news:
                return news
        return results

    # ---------------- High-level news entry ----------------
    def get_latest_news(self, region: Optional[str] = None, max_results: int = 5, freshness_days: Optional[int] = 7, location: Optional[str | Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        query = ""
        if region:
            query = f"{region} news" if not region.lower().strip().endswith("news") else region
        else:
            if isinstance(location, dict):
                place = location.get("city") or location.get("display_name")
            else:
                place = None
            query = f"{place} news" if place else "latest news"

        normalized = query.lower()
        time_tokens = ["latest", "today", "breaking", "now", "just now", "recent", "updates", "update", "headline", "headlines"]
        prefer_api = any(tok in normalized for tok in time_tokens)

        if prefer_api:
            news = self.get_news_fallback(query, max_results=max_results)
            if news:
                return news
            return self.search_with_fallback(query, max_results=max_results, freshness_days=freshness_days, location=location)

        return self.search_with_fallback(query, max_results=max_results, freshness_days=freshness_days, location=location)

    # ---------------- Formatting / helpers ----------------
    def humanize_results(self, results: List[Dict[str, Any]], max_chars: int = 800) -> str:
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

    # ---------------- Intent handler ----------------
    def handle_special_queries(self, user_query: str) -> Optional[str]:
        normalized = (user_query or "").strip().lower()
        if not normalized:
            return None

        # News intent
        if "news" in normalized:
            m = re.search(r"(?:news of|news in|news from|latest news of|latest news in)\s+(.+)$", normalized)
            if m:
                place = m.group(1).strip()
                results = self.get_latest_news(region=place, max_results=5, freshness_days=7, location=place)
                return self.humanize_results(results)
            results = self.get_latest_news(region=None, max_results=5, freshness_days=7, location=None)
            return self.humanize_results(results)

        # Location intent
        if normalized in ["where am i", "where am i?", "what is my location", "my location"]:
            loc = self.resolve_location_from_ip()
            if not loc:
                return "Sorry — I couldn't determine your location."
            parts = []
            if loc.get("city"):
                parts.append(loc["city"])
            if loc.get("region"):
                parts.append(loc["region"])
            if loc.get("country"):
                parts.append(loc["country"])
            coords = ""
            if loc.get("lat") is not None and loc.get("lon") is not None:
                coords = f" (lat: {loc['lat']:.4f}, lon: {loc['lon']:.4f})"
            return f"You appear to be in {', '.join(parts)}{coords}."

        # Domain-specific examples
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


# Global instance and module wrapper
web_search = WebSearchService()

def handle_special_queries(user_query: str) -> Optional[str]:
    return web_search.handle_special_queries(user_query)
