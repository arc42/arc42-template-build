"""Pytest configuration and shared fixtures"""

import pytest
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def project_root():
    """Return path to project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def config_dir(project_root):
    """Return path to config directory"""
    return project_root / "config"


@pytest.fixture
def schema_file(config_dir):
    """Return path to schema.json file"""
    return config_dir / "schema.json"


@pytest.fixture
def build_config_file(config_dir):
    """Return path to build.yaml file"""
    return config_dir / "build.yaml"


@pytest.fixture
def src_dir(project_root):
    """Return path to src directory"""
    return project_root / "src"


@pytest.fixture
def converters_dir(src_dir):
    """Return path to converters directory"""
    return src_dir / "arc42_builder" / "converters"


@pytest.fixture
def valid_minimal_config():
    """Return a minimal valid configuration dictionary"""
    return {
        "version": "1.0",
        "template": {
            "repository": "https://github.com/arc42/arc42-template.git",
            "ref": "main",
            "path": "./arc42-template"
        },
        "languages": ["EN"],
        "formats": {
            "html": {
                "enabled": True,
                "priority": 1,
                "options": {}
            }
        },
        "flavors": ["withHelp"]
    }


@pytest.fixture
def all_format_names():
    """Return list of all supported format names"""
    return [
        "html",
        "pdf",
        "docx",
        "markdown",
        "markdown_mp",
        "asciidoc",
        "github_markdown",
        "github_markdown_mp",
        "confluence",
        "latex",
        "rst",
        "textile"
    ]
