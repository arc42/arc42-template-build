from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class TemplateConfig:
    repository: str = ""
    ref: str = "main"
    path: str = "./arc42-template"

@dataclass
class FormatOptions:
    enabled: bool = True
    priority: int = 1
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BuildConfigOptions:
    parallel: bool = True
    max_workers: int = 4
    validate: bool = True
    clean_before: bool = True
    create_zips: bool = True
    verify_fonts: bool = True

@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: bool = True
    console: bool = True

@dataclass
class BuildConfig:
    version: str
    template: TemplateConfig
    languages: List[str]
    formats: Dict[str, FormatOptions]
    flavors: List[str]
    build: BuildConfigOptions
    logging: LoggingConfig
