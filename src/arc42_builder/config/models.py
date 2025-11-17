"""Configuration data models for arc42 build system."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any


@dataclass
class TemplateConfig:
    """Configuration for the template repository."""
    repository: str
    ref: str
    path: str

    def get_path(self) -> Path:
        """Get template path as Path object."""
        return Path(self.path).expanduser().resolve()


@dataclass
class FormatOptions:
    """Options for a specific output format."""
    options: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get an option value with default."""
        return self.options.get(key, default)


@dataclass
class FormatConfig:
    """Configuration for an output format."""
    enabled: bool
    priority: int
    options: Dict[str, Any] = field(default_factory=dict)

    def is_enabled(self) -> bool:
        """Check if format is enabled."""
        return self.enabled

    def get_option(self, key: str, default: Any = None) -> Any:
        """Get a format-specific option."""
        return self.options.get(key, default)


@dataclass
class BuildSettings:
    """Build execution settings."""
    parallel: bool = True
    max_workers: int = 4
    validate: bool = True
    clean_before: bool = True
    create_zips: bool = True
    verify_fonts: bool = True
    output_dir: str = "workspace/build"
    dist_dir: str = "workspace/dist"
    log_dir: str = "workspace/logs"

    def get_output_path(self) -> Path:
        """Get output directory as Path."""
        return Path(self.output_dir)

    def get_dist_path(self) -> Path:
        """Get distribution directory as Path."""
        return Path(self.dist_dir)

    def get_log_path(self) -> Path:
        """Get log directory as Path."""
        return Path(self.log_dir)


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    file: bool = True
    console: bool = True
    filename: str = "arc42-build.log"

    def get_log_level(self) -> str:
        """Get logging level."""
        return self.level.upper()


@dataclass
class AdvancedSettings:
    """Advanced build options."""
    fail_fast: bool = False
    retry_failed: bool = False
    retry_count: int = 1
    continue_on_error: bool = True


@dataclass
class BuildConfig:
    """Complete build configuration."""
    version: str
    template: TemplateConfig
    languages: List[str]
    formats: Dict[str, FormatConfig]
    flavors: List[str]
    build: BuildSettings = field(default_factory=BuildSettings)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    advanced: AdvancedSettings = field(default_factory=AdvancedSettings)

    def get_enabled_formats(self) -> List[str]:
        """Get list of enabled format names."""
        return [name for name, config in self.formats.items() if config.is_enabled()]

    def get_format_config(self, format_name: str) -> Optional[FormatConfig]:
        """Get configuration for a specific format."""
        return self.formats.get(format_name)

    def is_format_enabled(self, format_name: str) -> bool:
        """Check if a format is enabled."""
        config = self.get_format_config(format_name)
        return config.is_enabled() if config else False

    def has_language(self, language: str) -> bool:
        """Check if a language is configured."""
        return language in self.languages

    def has_flavor(self, flavor: str) -> bool:
        """Check if a flavor is configured."""
        return flavor in self.flavors

    def get_template_path(self) -> Path:
        """Get the template directory path."""
        return self.template.get_path()

    def validate_basic(self) -> List[str]:
        """
        Perform basic validation of configuration values.
        Returns list of error messages (empty if valid).
        """
        errors = []

        # Validate version format
        if not self.version or '.' not in self.version:
            errors.append("Invalid version format. Expected 'X.Y'")

        # Validate languages
        if not self.languages:
            errors.append("At least one language must be specified")

        valid_languages = {"EN", "DE", "FR", "CZ", "ES", "IT", "NL", "PT", "RU", "UKR", "ZH"}
        for lang in self.languages:
            if lang not in valid_languages:
                errors.append(f"Invalid language: {lang}")

        # Validate flavors
        if not self.flavors:
            errors.append("At least one flavor must be specified")

        valid_flavors = {"plain", "withHelp"}
        for flavor in self.flavors:
            if flavor not in valid_flavors:
                errors.append(f"Invalid flavor: {flavor}")

        # Validate at least one format is enabled
        if not self.get_enabled_formats():
            errors.append("At least one output format must be enabled")

        # Validate format priorities
        for name, format_config in self.formats.items():
            if format_config.priority not in [1, 2, 3]:
                errors.append(f"Invalid priority for format {name}: {format_config.priority}")

        # Validate build settings
        if self.build.max_workers < 1:
            errors.append("max_workers must be at least 1")

        # Validate logging level
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if self.logging.level.upper() not in valid_levels:
            errors.append(f"Invalid log level: {self.logging.level}")

        return errors


@dataclass
class BuildContext:
    """
    Context object passed to format converters.
    Contains all information needed to perform a conversion.
    """
    language: str
    flavor: str
    source_dir: Path
    output_dir: Path
    version_props: Dict[str, str]
    config: FormatConfig
    template_path: Path = None

    def get_version_attr(self, key: str, default: str = "") -> str:
        """Get a version property with default."""
        return self.version_props.get(key, default)

    def get_format_option(self, key: str, default: Any = None) -> Any:
        """Get a format-specific option."""
        return self.config.get_option(key, default)


# Compatibility alias for existing code
BuildConfigOptions = BuildSettings
