"""Configuration loader for arc42 build system."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

import yaml
import jsonschema
from jsonschema import ValidationError

from .models import (
    BuildConfig,
    TemplateConfig,
    FormatConfig,
    BuildSettings,
    LoggingConfig,
    AdvancedSettings,
)


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


class ConfigLoader:
    """Loads and validates build configuration."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize config loader.

        Args:
            schema_path: Path to JSON schema file. If None, uses default location.
        """
        if schema_path is None:
            # Default to config/schema.json relative to project root
            schema_path = Path(__file__).parent.parent.parent.parent / "config" / "schema.json"

        self.schema_path = schema_path
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from file."""
        if not self.schema_path.exists():
            raise ConfigError(f"Schema file not found: {self.schema_path}")

        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON schema: {e}")

    def load(self, config_path: Path) -> BuildConfig:
        """
        Load and validate configuration from YAML file.

        Args:
            config_path: Path to build.yaml file

        Returns:
            BuildConfig object

        Raises:
            ConfigError: If configuration is invalid
        """
        # Load YAML
        config_data = self._load_yaml(config_path)

        # Apply environment variable overrides
        config_data = self._apply_env_overrides(config_data)

        # Validate against schema
        self._validate_schema(config_data)

        # Convert to dataclass models
        build_config = self._build_config_from_dict(config_data)

        # Run additional validation
        errors = build_config.validate_basic()
        if errors:
            raise ConfigError("Configuration validation failed:\n  - " + "\n  - ".join(errors))

        return build_config

    def _load_yaml(self, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not config_path.exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConfigError("Configuration must be a YAML object/dictionary")
                return data
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML syntax: {e}")

    def _validate_schema(self, config_data: Dict[str, Any]) -> None:
        """Validate configuration against JSON schema."""
        try:
            jsonschema.validate(instance=config_data, schema=self.schema)
        except ValidationError as e:
            # Provide more user-friendly error message
            path = " -> ".join(str(p) for p in e.path) if e.path else "root"
            raise ConfigError(f"Configuration validation error at {path}: {e.message}")

    def _apply_env_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.

        Environment variables format: ARC42_BUILD_<SECTION>_<KEY>
        Examples:
            ARC42_BUILD_PARALLEL=false
            ARC42_BUILD_MAX_WORKERS=8
            ARC42_BUILD_LOG_LEVEL=DEBUG
        """
        # Build settings
        if os.getenv("ARC42_BUILD_PARALLEL"):
            if "build" not in config_data:
                config_data["build"] = {}
            config_data["build"]["parallel"] = os.getenv("ARC42_BUILD_PARALLEL").lower() == "true"

        if os.getenv("ARC42_BUILD_MAX_WORKERS"):
            if "build" not in config_data:
                config_data["build"] = {}
            config_data["build"]["max_workers"] = int(os.getenv("ARC42_BUILD_MAX_WORKERS"))

        if os.getenv("ARC42_BUILD_VALIDATE"):
            if "build" not in config_data:
                config_data["build"] = {}
            config_data["build"]["validate"] = os.getenv("ARC42_BUILD_VALIDATE").lower() == "true"

        # Logging settings
        if os.getenv("ARC42_LOG_LEVEL"):
            if "logging" not in config_data:
                config_data["logging"] = {}
            config_data["logging"]["level"] = os.getenv("ARC42_LOG_LEVEL")

        # Template path override
        if os.getenv("ARC42_TEMPLATE_PATH"):
            if "template" not in config_data:
                config_data["template"] = {}
            config_data["template"]["path"] = os.getenv("ARC42_TEMPLATE_PATH")

        return config_data

    def _build_config_from_dict(self, data: Dict[str, Any]) -> BuildConfig:
        """Convert dictionary to BuildConfig dataclass."""

        # Parse template config
        template_data = data["template"]
        template = TemplateConfig(
            repository=template_data["repository"],
            ref=template_data["ref"],
            path=template_data["path"]
        )

        # Parse format configs
        formats = {}
        if "formats" in data:
            for format_name, format_data in data["formats"].items():
                formats[format_name] = FormatConfig(
                    enabled=format_data["enabled"],
                    priority=format_data["priority"],
                    options=format_data.get("options", {})
                )

        # Parse build settings
        build_data = data.get("build", {})
        build = BuildSettings(
            parallel=build_data.get("parallel", True),
            max_workers=build_data.get("max_workers", 4),
            validate=build_data.get("validate", True),
            clean_before=build_data.get("clean_before", True),
            create_zips=build_data.get("create_zips", True),
            verify_fonts=build_data.get("verify_fonts", True),
            output_dir=build_data.get("output_dir", "workspace/build"),
            dist_dir=build_data.get("dist_dir", "workspace/dist"),
            log_dir=build_data.get("log_dir", "workspace/logs")
        )

        # Parse logging config
        logging_data = data.get("logging", {})
        logging = LoggingConfig(
            level=logging_data.get("level", "INFO"),
            file=logging_data.get("file", True),
            console=logging_data.get("console", True),
            filename=logging_data.get("filename", "arc42-build.log")
        )

        # Parse advanced settings
        advanced_data = data.get("advanced", {})
        advanced = AdvancedSettings(
            fail_fast=advanced_data.get("fail_fast", False),
            retry_failed=advanced_data.get("retry_failed", False),
            retry_count=advanced_data.get("retry_count", 1),
            continue_on_error=advanced_data.get("continue_on_error", True)
        )

        # Create and return BuildConfig
        return BuildConfig(
            version=data["version"],
            template=template,
            languages=data["languages"],
            formats=formats,
            flavors=data["flavors"],
            build=build,
            logging=logging,
            advanced=advanced
        )


def load_config(config_path: Path = None) -> BuildConfig:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to build.yaml. If None, uses default config/build.yaml

    Returns:
        BuildConfig object

    Raises:
        ConfigError: If configuration is invalid
    """
    if config_path is None:
        # Default to config/build.yaml relative to project root
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "build.yaml"

    loader = ConfigLoader()
    return loader.load(config_path)
