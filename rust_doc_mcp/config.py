"""Configuration management for Rust documentation paths"""

import json
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel


class CrateConfig(BaseModel):
    """Configuration for a Rust crate's documentation"""

    name: str
    path: str  # Path to the root of the crate documentation
    description: Optional[str] = None


class ServerConfig(BaseModel):
    """Server configuration"""

    crates: Dict[str, CrateConfig]

    def add_crate(
        self, name: str, path: str, description: Optional[str] = None
    ) -> None:
        """Add a crate configuration"""
        self.crates[name] = CrateConfig(name=name, path=path, description=description)

    def get_crate_path(self, crate_name: str) -> Optional[Path]:
        """Get the documentation path for a crate"""
        if crate_name in self.crates:
            return Path(self.crates[crate_name].path).expanduser().resolve()
        return None

    def list_crates(self) -> Dict[str, str]:
        """List all configured crates"""
        return {
            name: config.description or "No description"
            for name, config in self.crates.items()
        }


def load_config(config_path: Path) -> ServerConfig:
    """Load configuration from a JSON file"""
    if not config_path.exists():
        return ServerConfig(crates={})

    with open(config_path) as f:
        data = json.load(f)
    return ServerConfig(**data)


def save_config(config: ServerConfig, config_path: Path) -> None:
    """Save configuration to a JSON file"""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config.model_dump(), f, indent=2)


def get_config_path() -> Path:
    """Get the default configuration file path"""
    config_dir = Path.home() / ".config" / "rust-doc-mcp"
    return config_dir / "config.json"
