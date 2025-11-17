from typing import Dict, Type
from .base import ConverterPlugin
from .html import HtmlConverter
from .pdf import PdfConverter
from .asciidoc import AsciidocConverter
# Import other converters here as they are created
from .docx import DocxConverter
from .markdown import MarkdownConverter

# A registry of all available converter plugins
# The key is the format name (e.g., 'html')
CONVERTERS: Dict[str, ConverterPlugin] = {
    "html": HtmlConverter(),
    "pdf": PdfConverter(),
    "asciidoc": AsciidocConverter(),
    "docx": DocxConverter(),
    "markdown": MarkdownConverter(),
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
