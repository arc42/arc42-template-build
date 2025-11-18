"""Tests for configuration loader"""

import pytest
import yaml
from pathlib import Path


@pytest.mark.unit
class TestConfigLoader:
    """Test suite for ConfigLoader"""

    def test_can_import_config_loader(self):
        """Verify ConfigLoader can be imported"""
        from arc42_builder.config.loader import ConfigLoader
        assert ConfigLoader is not None

    def test_default_config_file_exists(self, build_config_file):
        """Verify default build.yaml exists"""
        assert build_config_file.exists(), f"Config file not found: {build_config_file}"

    def test_default_config_is_valid_yaml(self, build_config_file):
        """Verify build.yaml is valid YAML"""
        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)
        assert isinstance(config, dict), "Config should be a YAML object"

    def test_default_config_has_required_fields(self, build_config_file):
        """Verify build.yaml has all required fields"""
        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)

        required_fields = ["version", "template", "languages", "formats", "flavors"]
        for field in required_fields:
            assert field in config, f"Config missing required field: {field}"

    def test_default_config_languages_not_empty(self, build_config_file):
        """Verify at least one language is configured"""
        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)

        assert "languages" in config, "Config missing 'languages'"
        assert isinstance(config["languages"], list), "Languages should be a list"
        assert len(config["languages"]) > 0, "At least one language must be configured"

    def test_default_config_formats_not_empty(self, build_config_file):
        """Verify at least one format is configured"""
        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)

        assert "formats" in config, "Config missing 'formats'"
        assert isinstance(config["formats"], dict), "Formats should be a dictionary"
        assert len(config["formats"]) > 0, "At least one format must be configured"

    def test_default_config_flavors_not_empty(self, build_config_file):
        """Verify at least one flavor is configured"""
        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)

        assert "flavors" in config, "Config missing 'flavors'"
        assert isinstance(config["flavors"], list), "Flavors should be a list"
        assert len(config["flavors"]) > 0, "At least one flavor must be configured"

    def test_format_definitions_are_complete(self, build_config_file):
        """Verify each format has required properties"""
        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)

        for format_name, format_config in config["formats"].items():
            assert "enabled" in format_config, \
                f"Format '{format_name}' missing 'enabled' property"
            assert "priority" in format_config, \
                f"Format '{format_name}' missing 'priority' property"
            assert "options" in format_config, \
                f"Format '{format_name}' missing 'options' property"

            assert isinstance(format_config["enabled"], bool), \
                f"Format '{format_name}' enabled must be boolean"
            assert isinstance(format_config["priority"], int), \
                f"Format '{format_name}' priority must be integer"
            assert isinstance(format_config["options"], dict), \
                f"Format '{format_name}' options must be dictionary"

    def test_schema_and_config_formats_match(self, schema_file, build_config_file):
        """Verify all formats in config are allowed by schema"""
        import json

        with open(schema_file, 'r') as f:
            schema = json.load(f)

        with open(build_config_file, 'r') as f:
            config = yaml.safe_load(f)

        schema_formats = set(schema["properties"]["formats"]["properties"].keys())
        config_formats = set(config["formats"].keys())

        invalid_formats = config_formats - schema_formats
        assert not invalid_formats, \
            f"Config contains formats not allowed by schema: {invalid_formats}"


@pytest.mark.unit
class TestConfigValidation:
    """Test suite for configuration validation logic"""

    def test_minimal_valid_config_structure(self, valid_minimal_config):
        """Verify minimal valid config has correct structure"""
        assert "version" in valid_minimal_config
        assert "template" in valid_minimal_config
        assert "languages" in valid_minimal_config
        assert "formats" in valid_minimal_config
        assert "flavors" in valid_minimal_config

    def test_template_config_structure(self, valid_minimal_config):
        """Verify template config has required fields"""
        template = valid_minimal_config["template"]
        assert "repository" in template
        assert "ref" in template
        assert "path" in template
