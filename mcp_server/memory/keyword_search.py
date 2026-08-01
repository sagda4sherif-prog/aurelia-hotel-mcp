from typing import Dict, List, Any

class KeywordStore:
    def __init__(self):
        self.store: List[Dict[str, Any]] = []

    def upsert(self, payload: Dict[str, Any], metadata: Dict[str, Any]):
        record = {"payload": payload, "metadata": metadata}
        self.store.append(record)

    def query(self, query_text: str, top_k: int = 3, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        query_words = set(query_text.lower().split())
        scored_results = []

        for item in self.store:
            # Filter by metadata (e.g., guest_id)
            if filter:
                match = all(item["metadata"].get(k) == v for k, v in filter.items())
                if not match:
                    continue

            # Simple BM25-style keyword overlap score
            text_blob = " ".join(str(v) for v in item["payload"].values()).lower()
            doc_words = set(text_blob.split())
            overlap = len(query_words.intersection(doc_words))

            if overlap > 0:
                scored_results.append((overlap, item))

        # Sort by overlap score descending
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [res[1] for res in scored_results[:top_k]]