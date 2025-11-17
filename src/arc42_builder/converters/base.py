from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

@dataclass
class BuildContext:
    language: str
    flavor: str
    source_dir: Path
    output_dir: Path
    version_props: Dict[str, str]
    config: Dict[str, Any]

class ConverterPlugin(ABC):
    """Abstract base for all format converters"""
    
    def __init__(self, name: str, priority: int = 1):
        self.name = name
        self.priority = priority
    
    @abstractmethod
    def check_dependencies(self) -> bool:
        """Verify required tools are available"""
        pass
    
    @abstractmethod
    def convert(self, context: BuildContext) -> Path:
        """Execute conversion and return output path"""
        pass
    
    def get_output_extension(self) -> str:
        """Return file extension for this format"""
        # Default implementation, can be overridden
        return f".{self.name}"
