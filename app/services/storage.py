from collections import defaultdict
from typing import List, Dict

class InMemorySessionStore:
    def __init__(self, limit: int = 20):
        self.limit = limit
        self._data: Dict[str, List[dict]] = defaultdict(list)

    def append(self, session_id: str, role: str, content: str) -> None:
        hist = self._data[session_id]
        hist.append({"role": role, "content": content})
        if len(hist) > self.limit:
            self._data[session_id] = hist[-self.limit :]

    def history(self, session_id: str) -> List[dict]:
        return self._data.get(session_id, [])

store = InMemorySessionStore(limit=20)
