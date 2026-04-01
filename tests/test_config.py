"""Tests for configuration module"""

import tempfile
from pathlib import Path


from rust_doc_mcp.config import ServerConfig, CrateConfig, load_config, save_config


def test_crate_config():
    """Test CrateConfig model"""
    config = CrateConfig(
        name="polars", path="/path/to/polars", description="Fast DataFrame library"
    )
    assert config.name == "polars"
    assert config.path == "/path/to/polars"
    assert config.description == "Fast DataFrame library"


def test_server_config_add_crate():
    """Test adding crates to ServerConfig"""
    config = ServerConfig(crates={})
    config.add_crate("polars", "/path/to/polars", "Fast DataFrame library")

    assert "polars" in config.crates
    assert config.crates["polars"].name == "polars"
    assert config.crates["polars"].path == "/path/to/polars"


def test_server_config_list_crates():
    """Test listing crates"""
    config = ServerConfig(crates={})
    config.add_crate("polars", "/path/to/polars", "DataFrame library")
    config.add_crate("serde", "/path/to/serde", "Serialization")

    crates = config.list_crates()
    assert len(crates) == 2
    assert crates["polars"] == "DataFrame library"
    assert crates["serde"] == "Serialization"


def test_save_and_load_config():
    """Test saving and loading configuration"""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.json"

        # Create and save config
        config = ServerConfig(crates={})
        config.add_crate("polars", "/path/to/polars", "DataFrame library")
        save_config(config, config_path)

        # Verify file was created
        assert config_path.exists()

        # Load and verify
        loaded_config = load_config(config_path)
        assert "polars" in loaded_config.crates
        assert loaded_config.crates["polars"].name == "polars"


def test_get_crate_path():
    """Test getting crate path"""
    config = ServerConfig(crates={})
    config.add_crate("polars", "~/polars", "DataFrame library")

    path = config.get_crate_path("polars")
    assert path is not None
    assert "polars" in str(path)

    # Non-existent crate
    assert config.get_crate_path("nonexistent") is None
