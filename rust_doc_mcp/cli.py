"""CLI utilities for configuration and management"""

from pathlib import Path
from typing import Optional

from rust_doc_mcp.config import ServerConfig, get_config_path, load_config, save_config


def init_config(
    crate_name: Optional[str] = None, crate_path: Optional[str] = None
) -> None:
    """Initialize or update configuration"""
    config_path = get_config_path()
    config = load_config(config_path)

    if crate_name and crate_path:
        # Add a single crate
        config.add_crate(crate_name, crate_path)
        save_config(config, config_path)
        print(f"✓ Added crate '{crate_name}' at {crate_path}")
        print(f"✓ Config saved to {config_path}")
    else:
        # Interactive setup
        print("Rust Documentation MCP Server - Configuration Setup")
        print("=" * 50)

        config = ServerConfig(crates={})

        while True:
            crate = input("\nEnter crate name (or 'done' to finish): ").strip()
            if crate.lower() == "done":
                break

            path = input(f"Enter path to {crate} documentation: ").strip()
            if not path:
                print("Path cannot be empty")
                continue

            path_obj = Path(path).expanduser()
            if not path_obj.exists():
                print(f"Warning: Path does not exist: {path}")
                confirm = input("Continue anyway? (y/n): ").strip().lower()
                if confirm != "y":
                    continue

            config.add_crate(crate, path)
            print(f"✓ Added {crate}")

        if config.crates:
            save_config(config, config_path)
            print(f"\n✓ Configuration saved to {config_path}")
        else:
            print("\nNo crates configured.")


def show_config() -> None:
    """Display current configuration"""
    config_path = get_config_path()
    config = load_config(config_path)

    print(f"Configuration file: {config_path}")
    print("=" * 50)

    if not config.crates:
        print("No crates configured.")
        return

    print(f"\nConfigured crates ({len(config.crates)}):\n")
    for name, crate_config in config.crates.items():
        path_obj = Path(crate_config.path).expanduser()
        exists = "✓" if path_obj.exists() else "✗"
        print(f"{exists} {name}")
        print(f"   Path: {crate_config.path}")
        if crate_config.description:
            print(f"   Description: {crate_config.description}")
        print()


def verify_setup() -> None:
    """Verify that the server is properly set up"""
    config_path = get_config_path()
    config = load_config(config_path)

    print("Rust Doc MCP Server - Setup Verification")
    print("=" * 50)

    # Check config file
    if not config_path.exists():
        print(f"✗ Configuration file not found: {config_path}")
        print("  Run: poetry run rust-doc-mcp-init")
        return

    print(f"✓ Configuration file: {config_path}")

    # Check crates
    if not config.crates:
        print("✗ No crates configured")
        return

    print(f"✓ {len(config.crates)} crate(s) configured\n")

    issues = False
    for name, crate_config in config.crates.items():
        path_obj = Path(crate_config.path).expanduser()

        if not path_obj.exists():
            print(f"✗ {name}: Path does not exist")
            print(f"  {path_obj}")
            issues = True
        elif not (path_obj / "index.html").exists():
            print(f"⚠ {name}: Documentation root not found (missing index.html)")
            print(f"  {path_obj}")
            issues = True
        else:
            html_count = sum(1 for _ in path_obj.rglob("*.html"))
            print(f"✓ {name}: {html_count} HTML files found")

    if not issues:
        print("\n✓ Setup looks good!")
    else:
        print("\n✗ Some issues found. Check paths in configuration.")
