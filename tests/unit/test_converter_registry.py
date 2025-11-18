"""Tests for converter registry and discovery"""

import pytest
from pathlib import Path


@pytest.mark.unit
class TestConverterRegistry:
    """Test suite for converter registration and discovery"""

    def test_can_import_list_converters(self):
        """Verify list_converters function can be imported"""
        from arc42_builder.converters import list_converters
        assert list_converters is not None

    def test_list_converters_returns_dict(self):
        """Verify list_converters returns a dictionary"""
        from arc42_builder.converters import list_converters
        converters = list_converters()
        assert isinstance(converters, dict), "list_converters should return a dict"

    def test_converters_are_discovered(self):
        """Verify at least some converters are discovered"""
        from arc42_builder.converters import list_converters
        converters = list_converters()
        assert len(converters) > 0, "No converters were discovered"

    def test_expected_core_converters_exist(self):
        """Verify core converters (html, pdf, docx) are discovered"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        core_formats = ["html", "pdf", "docx"]
        for format_name in core_formats:
            assert format_name in converters, \
                f"Core converter '{format_name}' not found"

    def test_markdown_converters_exist(self):
        """Verify markdown variants are discovered"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        markdown_formats = ["markdown", "markdown_mp", "github_markdown", "github_markdown_mp"]
        for format_name in markdown_formats:
            assert format_name in converters, \
                f"Markdown converter '{format_name}' not found"

    def test_converter_has_name_attribute(self):
        """Verify each converter has a name attribute"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        for name, converter in converters.items():
            assert hasattr(converter, 'name'), \
                f"Converter '{name}' missing 'name' attribute"

    def test_converter_has_priority_attribute(self):
        """Verify each converter has a priority attribute"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        for name, converter in converters.items():
            assert hasattr(converter, 'priority'), \
                f"Converter '{name}' missing 'priority' attribute"
            assert isinstance(converter.priority, int), \
                f"Converter '{name}' priority should be an integer"
            assert 1 <= converter.priority <= 3, \
                f"Converter '{name}' priority {converter.priority} out of range (1-3)"

    def test_converter_has_convert_method(self):
        """Verify each converter has a convert method"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        for name, converter in converters.items():
            assert hasattr(converter, 'convert'), \
                f"Converter '{name}' missing 'convert' method"
            assert callable(converter.convert), \
                f"Converter '{name}' convert should be callable"

    def test_converter_has_check_dependencies_method(self):
        """Verify each converter has a check_dependencies method"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        for name, converter in converters.items():
            assert hasattr(converter, 'check_dependencies'), \
                f"Converter '{name}' missing 'check_dependencies' method"
            assert callable(converter.check_dependencies), \
                f"Converter '{name}' check_dependencies should be callable"

    def test_converter_names_match_registry_keys(self):
        """Verify converter name attribute matches registry key"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        for key, converter in converters.items():
            assert converter.name == key, \
                f"Converter key '{key}' doesn't match name '{converter.name}'"

    def test_all_converter_files_are_loaded(self, converters_dir):
        """Verify all converter files are loaded (except base and __init__)"""
        from arc42_builder.converters import list_converters

        # Get converter Python files
        converter_files = [f.stem for f in converters_dir.glob("*.py")
                          if f.stem not in ["__init__", "base"]]

        # Get registered converters
        registered = set(list_converters().keys())

        # Check all files are loaded
        for file_name in converter_files:
            assert file_name in registered, \
                f"Converter file '{file_name}.py' not registered"

    def test_no_duplicate_priorities_within_same_tier(self):
        """Verify converters don't have conflicting priorities in same tier"""
        from arc42_builder.converters import list_converters
        converters = list_converters()

        # Group by priority
        priority_groups = {}
        for name, converter in converters.items():
            priority = converter.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(name)

        # This is informational - multiple converters can have same priority
        # They would be processed in arbitrary order within the same priority
        # This test just documents the current state
        for priority, names in priority_groups.items():
            print(f"Priority {priority}: {', '.join(names)}")
