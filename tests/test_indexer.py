"""Tests for documentation indexer"""

import tempfile
from pathlib import Path


from rust_doc_mcp.indexer import DocIndexer, TextExtractor


def test_text_extractor():
    """Test HTML text extraction"""
    html = """
    <html>
        <title>Test Page</title>
        <body>
            <h1>Header</h1>
            <p>Some content</p>
            <script>console.log('hidden')</script>
        </body>
    </html>
    """
    extractor = TextExtractor()
    extractor.feed(html)
    text = extractor.get_text()

    assert "Header" in text
    assert "Some content" in text
    assert "console.log" not in text


def test_indexer_empty_directory():
    """Test indexer with empty directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = Path(tmpdir)
        indexer = DocIndexer(doc_path)

        assert len(indexer.index) == 0
        assert indexer.search("test") == []


def test_indexer_with_html_files():
    """Test indexer with HTML files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = Path(tmpdir)

        # Create test HTML files
        (doc_path / "index.html").write_text(
            "<html><title>Main Index</title><body>Welcome to docs</body></html>"
        )
        (doc_path / "struct.html").write_text(
            "<html><title>Struct Documentation</title><body>This is a struct</body></html>"
        )

        # Index the directory
        indexer = DocIndexer(doc_path)

        # Should have indexed files
        assert len(indexer.index) == 2

        # Search should find results
        results = indexer.search("struct")
        assert len(results) > 0
        assert any("Struct" in r["title"] for r in results)


def test_indexer_search_ranking():
    """Test that search results are ranked by relevance"""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = Path(tmpdir)

        # Create files with varying relevance
        (doc_path / "1.html").write_text(
            "<html><title>DataFrame</title><body>General content</body></html>"
        )
        (doc_path / "2.html").write_text(
            "<html><title>General</title><body>DataFrame content DataFrame content</body></html>"
        )

        indexer = DocIndexer(doc_path)
        results = indexer.search("DataFrame")

        # The first result should be the one with DataFrame in title
        assert results[0]["title"] == "DataFrame"


def test_indexer_get_doc():
    """Test retrieving a specific document"""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = Path(tmpdir)
        html_content = "<html><title>Test</title><body>Test content</body></html>"
        (doc_path / "test.html").write_text(html_content)

        indexer = DocIndexer(doc_path)
        doc = indexer.get_doc("test.html")

        assert doc is not None
        assert doc["title"] == "Test"
        assert doc["html"] == html_content

        # Non-existent document
        assert indexer.get_doc("nonexistent.html") is None


def test_indexer_list_all():
    """Test listing all documents"""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_path = Path(tmpdir)

        for i in range(5):
            (doc_path / f"doc{i}.html").write_text(
                f"<html><title>Doc {i}</title><body>Content {i}</body></html>"
            )

        indexer = DocIndexer(doc_path)
        docs = indexer.list_all(limit=3)

        assert len(docs) == 3
        assert all("key" in doc and "title" in doc for doc in docs)
