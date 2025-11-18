"""Tests for configuration schema validation"""

import json
import pytest
from pathlib import Path


@pytest.mark.unit
class TestConfigSchema:
    """Test suite for configuration schema"""

    def test_schema_file_exists(self, schema_file):
        """Verify schema.json file exists"""
        assert schema_file.exists(), f"Schema file not found: {schema_file}"

    def test_schema_is_valid_json(self, schema_file):
        """Verify schema file is valid JSON"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        assert isinstance(schema, dict), "Schema should be a JSON object"

    def test_schema_has_required_top_level_properties(self, schema_file):
        """Verify schema defines all required top-level properties"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        required_props = ["version", "template", "languages", "formats", "flavors"]
        assert "properties" in schema, "Schema missing 'properties' key"

        for prop in required_props:
            assert prop in schema["properties"], f"Schema missing required property: {prop}"

    def test_schema_includes_all_implemented_formats(self, schema_file, converters_dir, all_format_names):
        """Verify schema includes all formats that have converters implemented"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        # Get format names from schema
        schema_formats = set(schema["properties"]["formats"]["properties"].keys())

        # Get implemented converter names
        converter_files = list(converters_dir.glob("*.py"))
        implemented_formats = set()
        for file in converter_files:
            name = file.stem
            if name not in ["__init__", "base"]:
                implemented_formats.add(name)

        # Check that all implemented formats are in schema
        missing_in_schema = implemented_formats - schema_formats
        assert not missing_in_schema, \
            f"Formats implemented but missing from schema: {missing_in_schema}"

    def test_schema_format_definitions_are_complete(self, schema_file):
        """Verify each format in schema references formatConfig definition"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        format_properties = schema["properties"]["formats"]["properties"]

        for format_name, format_def in format_properties.items():
            assert "$ref" in format_def, \
                f"Format '{format_name}' missing $ref to formatConfig"
            assert format_def["$ref"] == "#/definitions/formatConfig", \
                f"Format '{format_name}' has incorrect $ref"

    def test_schema_has_format_config_definition(self, schema_file):
        """Verify schema has formatConfig definition"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        assert "definitions" in schema, "Schema missing 'definitions'"
        assert "formatConfig" in schema["definitions"], \
            "Schema missing 'formatConfig' definition"

        format_config = schema["definitions"]["formatConfig"]
        assert "type" in format_config, "formatConfig missing 'type'"
        assert format_config["type"] == "object", "formatConfig should be object type"
        assert "properties" in format_config, "formatConfig missing 'properties'"

        # Check required properties
        required = ["enabled", "priority"]
        assert "required" in format_config, "formatConfig missing 'required'"
        for field in required:
            assert field in format_config["required"], \
                f"formatConfig missing required field: {field}"

    def test_schema_allows_all_standard_formats(self, schema_file, all_format_names):
        """Verify schema allows all standard arc42 output formats"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        schema_formats = set(schema["properties"]["formats"]["properties"].keys())

        for format_name in all_format_names:
            assert format_name in schema_formats, \
                f"Standard format '{format_name}' not in schema"

    def test_schema_validates_language_enum(self, schema_file):
        """Verify schema defines valid language codes"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        languages_def = schema["properties"]["languages"]
        assert "items" in languages_def, "languages definition missing 'items'"
        assert "enum" in languages_def["items"], "languages items missing 'enum'"

        valid_languages = languages_def["items"]["enum"]
        expected_languages = ["EN", "DE", "FR", "CZ", "ES", "IT", "NL", "PT", "RU", "UKR", "ZH"]

        for lang in expected_languages:
            assert lang in valid_languages, \
                f"Expected language '{lang}' not in schema enum"

    def test_schema_validates_flavor_enum(self, schema_file):
        """Verify schema defines valid flavor types"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        flavors_def = schema["properties"]["flavors"]
        assert "items" in flavors_def, "flavors definition missing 'items'"
        assert "enum" in flavors_def["items"], "flavors items missing 'enum'"

        valid_flavors = flavors_def["items"]["enum"]
        expected_flavors = ["plain", "withHelp"]

        for flavor in expected_flavors:
            assert flavor in valid_flavors, \
                f"Expected flavor '{flavor}' not in schema enum"

    def test_schema_priority_constraint(self, schema_file):
        """Verify formatConfig defines priority constraints"""
        with open(schema_file, 'r') as f:
            schema = json.load(f)

        format_config = schema["definitions"]["formatConfig"]
        priority_def = format_config["properties"]["priority"]

        assert "type" in priority_def, "priority missing 'type'"
        assert priority_def["type"] == "integer", "priority should be integer"
        assert "minimum" in priority_def, "priority missing 'minimum'"
        assert "maximum" in priority_def, "priority missing 'maximum'"
        assert priority_def["minimum"] == 1, "priority minimum should be 1"
        assert priority_def["maximum"] == 3, "priority maximum should be 3"
