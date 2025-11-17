"""Configuration module for arc42 build system."""

from .loader import load_config, ConfigLoader, ConfigError
from .models import (
    BuildConfig,
    TemplateConfig,
    FormatConfig,
    FormatOptions,
    BuildSettings,
    BuildConfigOptions,  # Compatibility alias
    LoggingConfig,
    AdvancedSettings,
    BuildContext,
)

__all__ = [
    "load_config",
    "ConfigLoader",
    "ConfigError",
    "BuildConfig",
    "TemplateConfig",
    "FormatConfig",
    "FormatOptions",
    "BuildSettings",
    "BuildConfigOptions",  # Compatibility alias
    "LoggingConfig",
    "AdvancedSettings",
    "BuildContext",
]
