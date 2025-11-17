from typing import Dict, Type
from .base import ConverterPlugin
from .html import HtmlConverter
from .pdf import PdfConverter
from .asciidoc import AsciidocConverter
from .docx import DocxConverter
from .markdown import MarkdownConverter
from .markdown_mp import MarkdownMpConverter
from .github_markdown import GithubMarkdownConverter
from .github_markdown_mp import GithubMarkdownMpConverter
from .rst import RstConverter
from .textile import TextileConverter
from .confluence import ConfluenceConverter

# A registry of all available converter plugins
# The key is the format name (e.g., 'html')
CONVERTERS: Dict[str, ConverterPlugin] = {
    "html": HtmlConverter(),
    "pdf": PdfConverter(),
    "asciidoc": AsciidocConverter(),
    "docx": DocxConverter(),
    "markdown": MarkdownConverter(),
    "markdown_mp": MarkdownMpConverter(),
    "github_markdown": GithubMarkdownConverter(),
    "github_markdown_mp": GithubMarkdownMpConverter(),
    "rst": RstConverter(),
    "textile": TextileConverter(),
    "confluence": ConfluenceConverter(),
}

def get_converter(format_name: str) -> ConverterPlugin:
    """
    Factory function to get a converter instance by its format name.
    """
    converter = CONVERTERS.get(format_name)
    if not converter:
        raise ValueError(f"No converter found for format: {format_name}")
    return converter

def list_converters() -> Dict[str, ConverterPlugin]:
    """
    Returns the dictionary of all registered converters.
    """
    return CONVERTERS
