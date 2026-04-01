"""Documentation indexing and search"""

import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional


class TextExtractor(HTMLParser):
    """Extract text content from HTML"""

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.in_script = False
        self.in_style = False

    def handle_starttag(self, tag: str, attrs):
        if tag in ("script", "style"):
            setattr(self, f"in_{tag}", True)

    def handle_endtag(self, tag: str):
        if tag in ("script", "style"):
            setattr(self, f"in_{tag}", False)

    def handle_data(self, data: str):
        if not self.in_script and not self.in_style:
            text = data.strip()
            if text:
                self.text_parts.append(text)

    def get_text(self) -> str:
        return " ".join(self.text_parts)


class DocIndexer:
    """Index Rust documentation for searching"""

    def __init__(self, doc_path: Path):
        self.doc_path = doc_path
        self.index: Dict[str, Dict] = {}
        self._index_docs()

    def _index_docs(self) -> None:
        """Index all HTML files in the documentation directory"""
        if not self.doc_path.exists():
            return

        for html_file in self.doc_path.rglob("*.html"):
            try:
                self._index_file(html_file)
            except Exception:
                # Skip files that can't be parsed
                pass

    def _index_file(self, file_path: Path) -> None:
        """Index a single HTML file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except (UnicodeDecodeError, IOError):
            return

        # Extract title and text content
        title = self._extract_title(content)
        text = self._extract_text(content)

        # Create a key based on relative path
        relative_path = file_path.relative_to(self.doc_path)
        key = str(relative_path).replace("\\", "/")

        self.index[key] = {
            "title": title or key,
            "text": text[:500],  # Store first 500 chars for indexing
            "path": str(file_path),
            "file_size": len(content),
        }

    def _extract_title(self, html_content: str) -> Optional[str]:
        """Extract title from HTML"""
        match = re.search(r"<title[^>]*>([^<]+)</title>", html_content, re.IGNORECASE)
        if match:
            title = unescape(match.group(1)).strip()
            return title
        return None

    def _extract_text(self, html_content: str) -> str:
        """Extract plain text from HTML"""
        try:
            extractor = TextExtractor()
            extractor.feed(html_content)
            return extractor.get_text()
        except Exception:
            return ""

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search the index for matching documentation"""
        query_lower = query.lower()
        query_words = query_lower.split()

        results = []
        for key, doc in self.index.items():
            title_lower = doc["title"].lower()
            text_lower = doc["text"].lower()

            # Score based on matches in title and text
            title_matches = sum(1 for word in query_words if word in title_lower)
            text_matches = sum(1 for word in query_words if word in text_lower)

            if title_matches > 0 or text_matches > 0:
                score = title_matches * 10 + text_matches
                results.append(
                    {
                        "score": score,
                        "key": key,
                        "title": doc["title"],
                        "preview": doc["text"][:200],
                    }
                )

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_doc(self, key: str) -> Optional[Dict]:
        """Get a specific document by key"""
        if key in self.index:
            with open(self.index[key]["path"], encoding="utf-8") as f:
                content = f.read()
            return {
                "title": self.index[key]["title"],
                "html": content,
                "path": key,
            }
        return None

    def list_all(self, limit: int = 50) -> List[Dict]:
        """List all indexed documents"""
        results = [
            {
                "key": key,
                "title": doc["title"],
                "preview": doc["text"][:100],
            }
            for key, doc in self.index.items()
        ]
        return results[:limit]
