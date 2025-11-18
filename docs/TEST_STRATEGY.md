# arc42 Build System Test Strategy

**Version:** 1.0
**Date:** 2025-11-18
**Status:** Draft

## Executive Summary

This document defines a comprehensive testing strategy for the arc42-template-build system. The strategy addresses three critical concerns:

1. **Configuration validation** - Ensuring build configurations are syntactically correct
2. **Output format integrity** - Verifying that generated artifacts are valid in their respective formats
3. **Content fidelity** - Confirming that content is correctly transformed without data loss

## Current State Analysis

### Issue Encountered

The test run failed with:
```
Configuration validation error at formats: Additional properties are not allowed
('github_markdown_mp', 'markdown_mp' were unexpected)
```

**Root Cause:** JSON schema (`config/schema.json`) was out of sync with:
- The actual converters implemented in `src/arc42_builder/converters/`
- The configuration file `config/build.yaml`

**Resolution:** Added `markdown_mp` and `github_markdown_mp` to the schema's allowed formats.

### Current Testing Gaps

1. **No automated tests** - Only one simple `test_config.py` script exists
2. **No format validation** - No checks that output formats are syntactically valid
3. **No content validation** - No verification of images, includes, or links
4. **No regression tests** - No baseline comparisons for output quality
5. **No integration tests** - No end-to-end build testing

## Test Strategy Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Pyramid                              │
│                                                              │
│                     ╱╲  E2E Tests                           │
│                    ╱  ╲  (Full builds, integration)        │
│                   ╱────╲                                    │
│                  ╱      ╲  Format Validation               │
│                 ╱        ╲  (Syntax, structure)            │
│                ╱──────────╲                                 │
│               ╱            ╲  Unit Tests                    │
│              ╱              ╲  (Converters, config)         │
│             ╱────────────────╲                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Testing Layers

### Layer 1: Configuration & Schema Validation

**Purpose:** Ensure all configurations are valid and complete before any build starts.

#### 1.1 Schema Validation Tests

**Location:** `tests/unit/test_config_schema.py`

**Tests:**
- Schema file is valid JSON
- All converter formats are listed in schema
- Schema version matches config version
- All required properties are present
- Data types are correctly specified

**Implementation:**
```python
def test_schema_includes_all_converters():
    """Verify schema allows all implemented converter formats"""
    converter_formats = discover_converter_formats()
    schema_formats = load_schema()['properties']['formats']['properties'].keys()
    assert set(converter_formats) == set(schema_formats)
```

#### 1.2 Configuration Loading Tests

**Location:** `tests/unit/test_config_loader.py`

**Tests:**
- Valid configurations load successfully
- Invalid configurations raise appropriate errors
- Environment variable overrides work correctly
- Default values are applied correctly
- Missing required fields are detected

#### 1.3 Configuration Integrity Tests

**Location:** `tests/unit/test_config_integrity.py`

**Tests:**
- Languages specified exist in template repository
- Output directories are writable
- Enabled formats have corresponding converters
- Log levels are valid
- Worker counts are within reasonable limits

### Layer 2: Converter Unit Tests

**Purpose:** Test individual converters in isolation without full builds.

#### 2.1 Converter Registration Tests

**Location:** `tests/unit/test_converter_registry.py`

**Tests:**
- All converters are discoverable
- Converter priorities are unique and valid
- Converter dependencies are checkable
- Converter output extensions are correct

#### 2.2 Converter Logic Tests

**Location:** `tests/unit/converters/test_<format>_converter.py`

**Per-converter tests:**

##### HTML Converter
- Generates valid HTML5
- Includes proper DOCTYPE
- CSS is correctly embedded/linked
- Images paths are correct
- Sections are properly structured

##### PDF Converter
- Generates valid PDF structure
- Fonts are embedded
- Images are included
- Table of contents is generated
- Page breaks are appropriate

##### DOCX Converter
- Generates valid Office Open XML
- Styles are applied correctly
- Images are embedded
- Heading levels are correct
- Can be opened in MS Word/LibreOffice

##### Markdown Converter (Single-page)
- Generates valid Markdown
- Minimal HTML tags (only when necessary)
- Headers use ATX style (# ## ###)
- Links are functional
- Code blocks have language hints
- Lists are properly formatted

##### Markdown Multi-page Converter
- Splits by chapters correctly
- Generates index/navigation
- Cross-references work
- Each file is valid Markdown
- Directory structure is logical

##### GitHub Markdown Converter
- GitHub-flavored syntax is used
- Anchors match GitHub auto-generation
- Alerts use GitHub syntax (> [!NOTE])
- Tables use GFM format
- Task lists work correctly

##### GitHub Markdown Multi-page Converter
- Same as GitHub Markdown + multi-page features
- GitHub wiki-style navigation
- Relative links work on GitHub

##### AsciiDoc Converter
- Generates valid AsciiDoc
- Includes are properly bundled/referenced
- Images paths are correct
- Attributes are preserved
- Can be re-processed by Asciidoctor

##### Confluence Converter
- Generates valid Confluence Storage Format (XHTML)
- Macros are correctly formatted
- Code blocks use proper macro syntax
- Tables are compatible

##### reStructuredText Converter
- Generates valid reST
- Directives are correctly formatted
- Cross-references work
- Sphinx-compatible

##### Textile Converter
- Generates valid Textile markup
- Formatting is preserved
- Links work correctly

### Layer 3: Format Validation Tests

**Purpose:** Verify that generated outputs are syntactically valid and structurally sound.

#### 3.1 Syntax Validation Tests

**Location:** `tests/validation/test_format_syntax.py`

**Tools & Methods:**

| Format | Validation Tool | Method |
|--------|----------------|---------|
| HTML | `html5lib` or `BeautifulSoup` | Parse and check for errors |
| PDF | `pypdf` or `pdfinfo` | Verify PDF structure, page count |
| DOCX | `python-docx` | Open and validate document structure |
| Markdown | `markdown-it-py` with strict mode | Parse and check for malformed syntax |
| AsciiDoc | `asciidoctor --safe --failure-level WARN` | Check for warnings/errors |
| Confluence | XML schema validation | Validate against Confluence XSD |
| reStructuredText | `rst2html.py` with warnings | Check for syntax errors |
| Textile | `textile` library | Parse and check for errors |

**Example Test:**
```python
def test_html_output_is_valid_html5(build_artifact):
    """Verify HTML output is valid HTML5"""
    from html5lib import parse

    html_file = build_artifact.get_output('html')
    with open(html_file, 'rb') as f:
        document = parse(f, treebuilder='lxml')

    # Check for parse errors
    assert document is not None

    # Check for required elements
    assert document.find('.//head') is not None
    assert document.find('.//body') is not None
    assert document.find('.//title') is not None
```

#### 3.2 Structural Validation Tests

**Location:** `tests/validation/test_format_structure.py`

**Tests for each format:**

##### General Structure
- Document has title
- All expected sections are present (1-12 for arc42)
- Sections are in correct order
- Headings have proper hierarchy (no skipped levels)

##### Content Completeness
- Introduction text is present
- Quality goals section exists
- Architecture diagrams are referenced
- All standard arc42 chapters are included

##### Navigation
- Table of contents is present (where applicable)
- Internal links work
- Section numbering is correct

#### 3.3 Content Fidelity Tests

**Location:** `tests/validation/test_content_fidelity.py`

**Purpose:** Ensure content is not lost or corrupted during conversion.

**Tests:**
- Section count matches source
- Images are all present (no broken references)
- Tables maintain correct dimensions
- Code blocks preserve content
- Special characters are correctly encoded
- Footnotes/references are preserved
- Glossary terms are included

**Approach:**
1. Parse source AsciiDoc to extract content inventory
2. Parse output format to extract content
3. Compare for missing elements

### Layer 4: Image & Resource Validation

**Purpose:** Ensure all images and resources are correctly handled.

#### 4.1 Image Reference Tests

**Location:** `tests/validation/test_images.py`

**Tests:**
- All image references in source exist as files
- All images referenced are used in output
- Image paths are correct in output
- Images are embedded/linked as appropriate
- Image formats are supported
- Image dimensions are reasonable

#### 4.2 Image Quality Tests

**Tests:**
- Embedded images are not corrupted
- Image resolution is sufficient
- PDF images are not overly compressed
- Image file sizes are reasonable

#### 4.3 Missing Image Detection

**Tests:**
- Missing images are detected during validation
- Broken image references produce warnings
- Default/placeholder images are handled

### Layer 5: Multi-Format Consistency Tests

**Purpose:** Ensure consistency across different output formats.

#### 5.1 Cross-Format Comparison

**Location:** `tests/integration/test_cross_format.py`

**Tests:**
- Same sections in all formats
- Same images in all formats
- Heading levels consistent
- Content order identical
- Links/references equivalent

#### 5.2 Flavor Consistency Tests

**Tests:**
- `plain` flavor has no help text
- `withHelp` flavor includes guidance
- Structure is identical between flavors
- Only help text differs

### Layer 6: Integration & End-to-End Tests

**Purpose:** Test complete build workflows.

#### 6.1 Full Build Tests

**Location:** `tests/integration/test_full_build.py`

**Tests:**
- Full build completes successfully
- All configured formats are generated
- All configured languages are built
- Both flavors are created
- Output structure matches expectations
- Log files are created
- No temporary files left behind

#### 6.2 Parallel Build Tests

**Tests:**
- Parallel builds complete successfully
- No race conditions or conflicts
- Output is identical to sequential builds
- Proper error handling in parallel mode

#### 6.3 Error Recovery Tests

**Tests:**
- Single format failure doesn't stop other formats
- Missing dependencies detected gracefully
- Invalid source files produce clear errors
- Partial builds can be resumed

### Layer 7: Performance Tests

**Purpose:** Ensure builds complete in reasonable time.

#### 7.1 Build Time Tests

**Location:** `tests/performance/test_build_time.py`

**Tests:**
- Single format build completes within threshold
- Full build completes within threshold
- Parallel builds are faster than sequential
- Memory usage is acceptable

**Benchmarks (targets for EN language, withHelp flavor):**
- HTML: < 5 seconds
- PDF: < 10 seconds
- DOCX: < 8 seconds
- Markdown: < 6 seconds
- Full build (all formats): < 30 seconds (parallel)

### Layer 8: Regression Tests

**Purpose:** Detect unintended changes to output.

#### 8.1 Golden File Tests

**Location:** `tests/regression/`

**Approach:**
1. Maintain "golden" reference outputs for each format
2. Compare new builds to golden files
3. Report differences
4. Update golden files when changes are intentional

**Tests:**
- HTML structure unchanged
- PDF layout consistent
- Markdown formatting stable
- Content completeness maintained

#### 8.2 Visual Regression Tests

**For HTML/PDF only:**
- Screenshot comparison
- Layout verification
- Font rendering checks

## Test Infrastructure

### Test Organization

```
tests/
├── unit/                          # Fast, isolated tests
│   ├── test_config_schema.py
│   ├── test_config_loader.py
│   ├── test_config_integrity.py
│   ├── test_converter_registry.py
│   └── converters/
│       ├── test_html_converter.py
│       ├── test_pdf_converter.py
│       ├── test_markdown_converter.py
│       ├── test_markdown_mp_converter.py
│       ├── test_github_markdown_converter.py
│       ├── test_github_markdown_mp_converter.py
│       ├── test_docx_converter.py
│       ├── test_asciidoc_converter.py
│       ├── test_confluence_converter.py
│       ├── test_rst_converter.py
│       └── test_textile_converter.py
│
├── validation/                    # Format-specific validation
│   ├── test_format_syntax.py
│   ├── test_format_structure.py
│   ├── test_content_fidelity.py
│   └── test_images.py
│
├── integration/                   # Multi-component tests
│   ├── test_full_build.py
│   ├── test_cross_format.py
│   ├── test_parallel_build.py
│   └── test_error_recovery.py
│
├── performance/                   # Performance benchmarks
│   └── test_build_time.py
│
├── regression/                    # Regression testing
│   ├── golden/                   # Reference outputs
│   │   ├── EN-withHelp.html
│   │   ├── EN-withHelp.pdf
│   │   └── ...
│   └── test_golden_files.py
│
├── fixtures/                      # Test data
│   ├── sample_configs/           # Various config files
│   ├── minimal_template/         # Minimal arc42 template
│   └── test_images/              # Test image files
│
└── conftest.py                   # Pytest configuration
```

### Test Fixtures

#### Configuration Fixtures

```python
@pytest.fixture
def valid_config():
    """Minimal valid configuration"""
    return {
        "version": "1.0",
        "template": {
            "repository": "https://github.com/arc42/arc42-template.git",
            "ref": "main",
            "path": "./arc42-template"
        },
        "languages": ["EN"],
        "formats": {
            "html": {"enabled": True, "priority": 1, "options": {}}
        },
        "flavors": ["withHelp"]
    }

@pytest.fixture
def build_context(tmp_path):
    """BuildContext for converter tests"""
    return BuildContext(
        language="EN",
        flavor="withHelp",
        format="html",
        source_dir=tmp_path / "source",
        output_dir=tmp_path / "output",
        config={}
    )
```

#### Build Artifact Fixtures

```python
@pytest.fixture(scope="session")
def built_artifacts(tmp_path_factory):
    """
    Run a full build once per test session.
    All tests can use the same build artifacts.
    """
    workspace = tmp_path_factory.mktemp("build")
    # Run full build
    # Return paths to all artifacts
    return BuildArtifacts(workspace)
```

### Test Utilities

#### Format Validators

```python
# tests/utils/validators.py

class FormatValidator:
    """Base class for format validators"""
    def validate(self, file_path: Path) -> ValidationResult:
        raise NotImplementedError

class HTMLValidator(FormatValidator):
    def validate(self, file_path: Path) -> ValidationResult:
        """Validate HTML5 syntax and structure"""
        # Implementation using html5lib

class MarkdownValidator(FormatValidator):
    def validate(self, file_path: Path) -> ValidationResult:
        """Validate Markdown syntax"""
        # Implementation using markdown-it-py
        # Check for:
        # - Excessive HTML tags
        # - Malformed links
        # - Invalid code blocks
        # - Broken lists

class PDFValidator(FormatValidator):
    def validate(self, file_path: Path) -> ValidationResult:
        """Validate PDF structure"""
        # Implementation using pypdf

class AsciiDocValidator(FormatValidator):
    def validate(self, file_path: Path) -> ValidationResult:
        """Validate AsciiDoc syntax"""
        # Use asciidoctor --safe --dry-run
```

#### Content Extractors

```python
# tests/utils/extractors.py

class ContentExtractor:
    """Extract content elements from various formats for comparison"""

    def extract_headings(self, file_path: Path) -> List[Heading]:
        """Extract all headings with levels"""

    def extract_images(self, file_path: Path) -> List[ImageRef]:
        """Extract all image references"""

    def extract_sections(self, file_path: Path) -> List[Section]:
        """Extract section structure"""
```

#### Markdown Quality Checker

```python
# tests/utils/markdown_quality.py

class MarkdownQualityChecker:
    """Check Markdown output quality"""

    def check_html_contamination(self, md_file: Path) -> Report:
        """
        Check for excessive HTML tags in Markdown.

        Acceptable HTML in Markdown:
        - <br> for explicit line breaks
        - <img> when advanced image control needed
        - <details>/<summary> for collapsible sections

        Unacceptable (should use Markdown):
        - <h1>, <h2>, etc. (use # ## ###)
        - <strong>, <em> (use ** or *)
        - <ul>, <ol>, <li> (use - or 1.)
        - <a> (use [text](url))
        - <code> (use `code`)
        """
        content = md_file.read_text()

        issues = []

        # Check for heading tags
        if re.search(r'<h[1-6]>', content):
            issues.append("Uses HTML heading tags instead of Markdown")

        # Check for emphasis tags
        if re.search(r'<(strong|em|b|i)>', content):
            issues.append("Uses HTML emphasis tags instead of Markdown")

        # Calculate HTML ratio
        html_tags = len(re.findall(r'<[^>]+>', content))
        lines = len(content.splitlines())
        html_ratio = html_tags / lines if lines > 0 else 0

        if html_ratio > 0.1:  # More than 10% HTML
            issues.append(f"High HTML contamination: {html_ratio:.1%}")

        return Report(issues)

    def check_pure_markdown(self, md_file: Path) -> bool:
        """Verify file uses pure Markdown syntax"""
        return len(self.check_html_contamination(md_file).issues) == 0
```

## Test Execution Strategy

### Test Stages

#### Stage 1: Pre-Commit (Fast)
**Duration:** < 30 seconds
**Tests:**
- Configuration schema tests
- Configuration loading tests
- Converter registration tests
- Linting and formatting

```bash
pytest tests/unit/test_config*.py -v
pytest tests/unit/test_converter_registry.py -v
```

#### Stage 2: Pull Request (Moderate)
**Duration:** < 5 minutes
**Tests:**
- All unit tests
- Format syntax validation
- Single language build test

```bash
pytest tests/unit/ -v
pytest tests/validation/test_format_syntax.py -v
pytest tests/integration/test_full_build.py -k "EN" -v
```

#### Stage 3: Main Branch (Comprehensive)
**Duration:** < 30 minutes
**Tests:**
- All unit tests
- All validation tests
- Full integration tests (all languages)
- Performance tests
- Regression tests

```bash
pytest tests/ -v --cov=src/arc42_builder --cov-report=html
```

#### Stage 4: Release (Exhaustive)
**Duration:** < 1 hour
**Tests:**
- All tests from Stage 3
- Extended performance tests
- Cross-platform tests (if applicable)
- Documentation tests
- Manual QA spot checks

### Continuous Integration

**GitHub Actions Workflow:**

```yaml
name: Tests

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint
        run: make lint

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive
      - name: Run unit tests
        run: make test-unit

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive
      - name: Run integration tests
        run: make test-integration

  validation-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive
      - name: Run validation tests
        run: make test-validation
```

## Implementation Priority

### Phase 1: Foundation (Week 1-2)
**Priority:** CRITICAL

1. ✅ Fix configuration schema sync issue
2. Create test directory structure
3. Setup pytest infrastructure
4. Implement basic format validators (HTML, Markdown, PDF)
5. Write configuration unit tests
6. Write converter registration tests

**Deliverable:** Basic test framework operational

### Phase 2: Core Validation (Week 3-4)
**Priority:** HIGH

1. Implement all format syntax validators
2. Write structural validation tests
3. Create content fidelity tests
4. Implement image validation
5. Write integration tests for single builds

**Deliverable:** Can validate all output formats

### Phase 3: Advanced Testing (Week 5-6)
**Priority: MEDIUM**

1. Implement cross-format consistency tests
2. Create parallel build tests
3. Write error recovery tests
4. Implement performance benchmarks
5. Setup golden file infrastructure

**Deliverable:** Comprehensive test coverage

### Phase 4: CI/CD Integration (Week 7-8)
**Priority:** MEDIUM

1. Setup GitHub Actions workflows
2. Configure test stages
3. Setup coverage reporting
4. Implement regression tracking
5. Document test procedures

**Deliverable:** Automated testing pipeline

## Markdown-Specific Testing

### Markdown Purity Tests

**Purpose:** Ensure Markdown outputs use pure Markdown syntax, not HTML.

**Rationale:** The goal of Markdown output is portability and readability. Excessive HTML defeats this purpose.

#### Test Cases

```python
def test_markdown_uses_atx_headers(markdown_file):
    """Verify headers use # syntax, not <h1> tags"""
    content = markdown_file.read_text()
    assert not re.search(r'<h[1-6]>', content)
    assert re.search(r'^#{1,6} ', content, re.MULTILINE)

def test_markdown_uses_emphasis_syntax(markdown_file):
    """Verify emphasis uses ** and *, not <strong>/<em>"""
    content = markdown_file.read_text()
    assert '<strong>' not in content
    assert '<em>' not in content
    assert '**' in content or '*' in content

def test_markdown_minimal_html(markdown_file):
    """Verify HTML usage is minimal and justified"""
    checker = MarkdownQualityChecker()
    report = checker.check_html_contamination(markdown_file)
    assert len(report.issues) == 0, f"Found HTML issues: {report.issues}"

def test_markdown_github_compatibility(github_markdown_file):
    """Verify GitHub-specific features are used"""
    content = github_markdown_file.read_text()

    # Check for GitHub alerts
    assert re.search(r'> \[!NOTE\]', content)

    # Check for GFM tables (if tables exist)
    if '|' in content:
        # Verify table formatting
        assert re.search(r'\|[^|]+\|', content)  # Table row
        assert re.search(r'\|[-: ]+\|', content)  # Separator row
```

### Multi-Page Markdown Tests

```python
def test_multipage_markdown_structure(output_dir):
    """Verify multi-page Markdown has correct structure"""

    # Check index file exists
    index_file = output_dir / "index.md"
    assert index_file.exists()

    # Check chapter files exist
    expected_chapters = [
        "01_introduction.md",
        "02_architecture_constraints.md",
        "03_context_and_scope.md",
        # ... all 12 chapters
    ]

    for chapter in expected_chapters:
        assert (output_dir / chapter).exists()

def test_multipage_markdown_navigation(output_dir):
    """Verify navigation links work in multi-page Markdown"""
    index = (output_dir / "index.md").read_text()

    # Check links to chapters
    assert "[Introduction](01_introduction.md)" in index

    # Check each chapter has next/prev links
    chapter_01 = (output_dir / "01_introduction.md").read_text()
    assert "[Next: Architecture Constraints](02_architecture_constraints.md)" in chapter_01

def test_multipage_markdown_images(output_dir):
    """Verify image paths are correct in multi-page setup"""
    # Images should use relative paths or be copied to each chapter dir
```

## AsciiDoc-Specific Testing

### AsciiDoc Purity Tests

```python
def test_asciidoc_bundled_includes(asciidoc_file):
    """Verify includes are bundled, not referenced"""
    content = asciidoc_file.read_text()

    # Should NOT have include directives if bundle_includes=true
    assert 'include::' not in content

def test_asciidoc_can_be_reprocessed(asciidoc_file, tmp_path):
    """Verify output AsciiDoc can be processed by Asciidoctor"""
    output_html = tmp_path / "test.html"

    result = subprocess.run(
        ["asciidoctor", str(asciidoc_file), "-o", str(output_html)],
        capture_output=True
    )

    assert result.returncode == 0, f"Asciidoctor failed: {result.stderr}"
    assert output_html.exists()
```

## Success Criteria

### Definition of "Done" for Testing

A format implementation is considered **fully tested** when:

1. ✅ Unit tests pass for converter
2. ✅ Syntax validation passes
3. ✅ Structural validation passes
4. ✅ Content fidelity test passes
5. ✅ Image validation passes
6. ✅ Format-specific quality tests pass
7. ✅ Integration test includes this format
8. ✅ Golden file exists for regression testing
9. ✅ Performance benchmark is within threshold
10. ✅ Documentation exists for format-specific features

### Quality Metrics

**Target Metrics:**
- Test coverage: > 80% for converter code
- Test coverage: > 95% for configuration code
- All formats pass syntax validation: 100%
- All formats pass structure validation: 100%
- Content fidelity: > 99% (allow minor formatting differences)
- Build success rate: > 99.5%
- Performance: All builds within thresholds

## Maintenance

### Keeping Tests Current

1. **When adding a new format:**
   - Add to schema.json
   - Create converter tests
   - Add format validator
   - Create golden file
   - Update integration tests

2. **When changing a converter:**
   - Update unit tests
   - Regenerate golden files
   - Update performance benchmarks

3. **When changing arc42 template:**
   - Update golden files
   - Verify all tests still pass
   - Update structural expectations if needed

### Review Cadence

- **Weekly:** Review failing tests, update as needed
- **Monthly:** Review performance benchmarks
- **Quarterly:** Review and update golden files
- **Yearly:** Comprehensive test strategy review

## Tools & Dependencies

### Testing Dependencies

Add to `requirements-dev.txt`:
```
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-xdist>=3.3.1          # Parallel test execution
pytest-timeout>=2.1.0         # Test timeouts
pytest-mock>=3.11.1           # Mocking

# Format validation
html5lib>=1.1
pypdf>=3.15.0
python-docx>=0.8.11
markdown-it-py>=3.0.0
beautifulsoup4>=4.12.0
lxml>=4.9.3

# Content analysis
pillow>=10.0.0                # Image validation
jsonschema>=4.19.0            # Schema validation

# Performance
pytest-benchmark>=4.0.0       # Performance testing

# Reporting
pytest-html>=3.2.0            # HTML reports
coverage[toml]>=7.3.0         # Coverage reporting
```

### Validation Tools

- **HTML:** html5lib, BeautifulSoup, W3C Validator (optional)
- **PDF:** pypdf, pdfinfo
- **DOCX:** python-docx
- **Markdown:** markdown-it-py, markdownlint (optional)
- **AsciiDoc:** asciidoctor (already required)
- **XML (Confluence):** lxml with XSD validation

## Appendix

### A. Test Case Templates

#### Unit Test Template

```python
"""Test module for [ComponentName]"""
import pytest
from arc42_builder.[module] import [Class]

class Test[ComponentName]:
    """Tests for [ComponentName]"""

    def test_[specific_behavior](self, fixture):
        """Test that [specific behavior] works correctly"""
        # Arrange
        component = [Class](params)

        # Act
        result = component.method()

        # Assert
        assert result == expected
```

#### Integration Test Template

```python
"""Integration test for [Feature]"""
import pytest
from pathlib import Path

class TestIntegration[Feature]:
    """Integration tests for [Feature]"""

    @pytest.mark.slow
    def test_[workflow](self, build_config, tmp_path):
        """Test complete [workflow] workflow"""
        # Arrange - setup configuration
        # Act - run build
        # Assert - verify outputs
```

### B. Validation Checklist

**Per-Format Validation Checklist:**

- [ ] Syntax is valid
- [ ] File can be opened/parsed
- [ ] Document has title
- [ ] All 12 arc42 sections present
- [ ] Section order is correct
- [ ] Headings have correct levels
- [ ] Images are present/referenced correctly
- [ ] Tables are formatted correctly
- [ ] Code blocks are preserved
- [ ] Links are functional
- [ ] Special characters correct
- [ ] File size is reasonable
- [ ] Format-specific features work

### C. Common Issues & Solutions

| Issue | Cause | Solution | Test |
|-------|-------|----------|------|
| HTML with excessive divs | Asciidoctor default styling | Use cleaner theme | test_html_structure |
| Markdown with HTML tags | Pandoc fallback behavior | Configure Pandoc for pure MD | test_markdown_purity |
| Missing images | Incorrect imagesdir path | Use absolute paths | test_image_references |
| Broken PDF fonts | Missing font files | Install required fonts | test_pdf_fonts |
| Invalid XML in Confluence | Special characters | Proper XML escaping | test_confluence_xml |
| Large file sizes | Uncompressed images | Optimize images | test_file_sizes |

### D. Glossary

- **Golden File:** Reference output file used for regression testing
- **Content Fidelity:** Measure of how well content is preserved during conversion
- **Format Purity:** Degree to which output uses native format syntax vs. fallbacks
- **Syntax Validation:** Checking that output conforms to format specification
- **Structural Validation:** Checking that document structure is correct
- **Regression Test:** Test that verifies behavior hasn't changed unintentionally

---

**Document Status:** ✅ Fixed configuration schema issue, comprehensive strategy defined

**Next Steps:**
1. Implement Phase 1 tests (Foundation)
2. Setup CI/CD pipeline
3. Begin format validators development

**References:**
- [Pytest Documentation](https://docs.pytest.org/)
- [AsciiDoc Specification](https://asciidoc.org/)
- [CommonMark Spec](https://commonmark.org/)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [Office Open XML Standard](http://officeopenxml.com/)
