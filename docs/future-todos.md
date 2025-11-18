# arc42-template-build – Future TODOs and Roadmap

**Version:** 0.2.0
**Last Updated:** 2025-11-18
**Status:** Living Document

This document tracks planned improvements, open issues, and future work for arc42-template-build.

---

## Table of Contents

1. [Critical Path (Must-Have for 1.0)](#1-critical-path-must-have-for-10)
2. [High Priority (Should-Have)](#2-high-priority-should-have)
3. [Medium Priority (Nice-to-Have)](#3-medium-priority-nice-to-have)
4. [Low Priority (Future Exploration)](#4-low-priority-future-exploration)
5. [Technical Debt](#5-technical-debt)
6. [Known Issues](#6-known-issues)
7. [Ideas and Proposals](#7-ideas-and-proposals)

---

## 1. Critical Path (Must-Have for 1.0)

### 1.1 Testing Infrastructure

**Status:** ❌ Not started
**Priority:** Critical
**Effort:** Medium (1-2 weeks)

**Tasks:**
- [ ] Add pytest framework to dependencies
- [ ] Create test fixtures for Docker-based tests
- [ ] Add unit tests for converters (mock subprocess calls)
- [ ] Add integration tests (actual builds in Docker)
- [ ] Test all 11 languages × 2 flavors × key formats
- [ ] Add test coverage reporting
- [ ] Document testing approach in `docs/testing.md`

**Blockers:** None

**Acceptance Criteria:**
- [ ] >80% code coverage
- [ ] All converters have unit tests
- [ ] At least one integration test per format
- [ ] Tests run in CI/CD

---

### 1.2 CI/CD Pipeline

**Status:** ❌ Not started
**Priority:** Critical
**Effort:** Low (2-3 days)

**Tasks:**
- [ ] Create `.github/workflows/build.yml`
- [ ] Run tests on every PR
- [ ] Build artifacts on main branch
- [ ] Upload artifacts to GitHub Releases
- [ ] Add status badges to README
- [ ] Test in matrix: multiple Docker versions
- [ ] Cache Docker layers for faster builds

**Blockers:** Testing infrastructure (1.1)

**Acceptance Criteria:**
- [ ] CI runs on every push
- [ ] Releases automated for tags
- [ ] Build status visible in README

---

### 1.3 Multi-Page HTML Support

**Status:** ❌ Not started
**Priority:** High
**Effort:** Medium (3-5 days)

**Tasks:**
- [ ] Create `HtmlMpConverter` (multi-page HTML)
- [ ] Split by `<h2>` sections (chapters)
- [ ] Generate navigation menu
- [ ] Create index.html with TOC
- [ ] Handle cross-references between pages
- [ ] Style with CSS (optional: use arc42 website theme)
- [ ] Test with all languages

**Blockers:** None

**Acceptance Criteria:**
- [ ] One HTML file per chapter
- [ ] Working navigation between pages
- [ ] All internal links work

---

## 2. High Priority (Should-Have)

### 2.1 LaTeX Output Format

**Status:** ❌ Not started
**Priority:** Medium-High
**Effort:** Medium (1 week)

**Tasks:**
- [ ] Add `texlive-full` to Dockerfile (large package)
- [ ] Create `LatexConverter`
- [ ] Test Pandoc AsciiDoc → LaTeX conversion
- [ ] OR: Use asciidoctor-latex gem
- [ ] Handle diagrams (convert to EPS/PDF)
- [ ] Test Unicode support (especially CJK)
- [ ] Add configuration for document class, packages

**Blockers:** None

**Challenges:**
- Large Docker image size increase (~1 GB)
- Complex LaTeX errors hard to debug
- Font configuration tricky for non-Latin

**Acceptance Criteria:**
- [ ] LaTeX files compile with `pdflatex`
- [ ] All languages render correctly

---

### 2.2 Enhanced Validation

**Status:** ⚠️ Partial implementation
**Priority:** Medium-High
**Effort:** Medium (3-5 days)

**Current State:**
- ✅ Asciidoctor reference checking
- ✅ Missing images detection
- ✅ Markdown syntax validation
- ❌ No AsciiDoc linting
- ❌ No translation completeness check

**Tasks:**
- [ ] Add asciidoctor-lint or custom linting
- [ ] Validate AsciiDoc style consistency
- [ ] Check for common errors (wrong section levels, etc.)
- [ ] Optional: Translation sync checker
  - Compare EN section count vs. other languages
  - Warn if sections missing or out of order
- [ ] Validate plain vs. withHelp markers
- [ ] Check version.properties format

**Acceptance Criteria:**
- [ ] Catch 90% of common AsciiDoc errors
- [ ] Clear, actionable error messages
- [ ] Optional translation checks don't block builds

---

### 2.3 Diagram Localization Support

**Status:** ❌ Not started
**Priority:** Medium
**Effort:** Medium (1 week)

**Background:**
Currently, all diagrams are in `arc42-template/images/` (shared).
Future plan: move to `arc42-template/{LANG}/images/` for localized diagrams.

**Tasks:**
- [ ] Support both layouts:
  - Shared: `arc42-template/images/`
  - Localized: `arc42-template/{LANG}/images/`
- [ ] Validate that language-specific diagrams exist
- [ ] Warn if EN has diagram but DE doesn't
- [ ] Handle fallback (use EN diagram if localized missing)
- [ ] Update documentation with best practices

**Acceptance Criteria:**
- [ ] Builds work with both layouts
- [ ] Warnings for missing localized diagrams
- [ ] Clear documentation for translators

---

### 2.4 Performance Optimization

**Status:** ⚠️ Partially optimized
**Priority:** Medium
**Effort:** Low-Medium (2-4 days)

**Current State:**
- ✅ Parallel builds (4 workers)
- ⚠️ No caching of intermediate files
- ⚠️ Redundant Asciidoctor calls per format

**Tasks:**
- [ ] Cache intermediate HTML files
  - Generate once per language/flavor
  - Reuse for Markdown, DOCX, RST, Textile
- [ ] Benchmark current performance
- [ ] Profile slow converters
- [ ] Optimize Docker image size (multi-stage builds)
- [ ] Parallelize per-language builds (not just formats)
- [ ] Add progress indicators

**Acceptance Criteria:**
- [ ] Full build (EN+DE, all formats) <5 minutes
- [ ] Docker image <2 GB
- [ ] Real-time progress feedback

---

## 3. Medium Priority (Nice-to-Have)

### 3.1 req42 Template Support

**Status:** ❌ Not started
**Priority:** Medium
**Effort:** Medium (1 week)

**Description:**
req42 is a requirements documentation template (similar to arc42 for requirements).
The build system should support multiple templates.

**Tasks:**
- [ ] Add req42-template as second submodule
- [ ] Extend configuration to support multiple templates
  ```yaml
  templates:
    - name: arc42
      path: ./arc42-template
    - name: req42
      path: ./req42-template
  ```
- [ ] CLI option: `--template arc42` or `--template req42`
- [ ] Adapt converters to handle template-specific structure
- [ ] Test with req42 structure

**Acceptance Criteria:**
- [ ] Both templates build successfully
- [ ] Clear separation in outputs
- [ ] Easy to add third template

---

### 3.2 Custom PDF Themes

**Status:** ⚠️ Infrastructure present, no themes
**Priority:** Medium
**Effort:** Medium (3-5 days)

**Current State:**
- Dockerfile has `COPY docker/pdf-themes/` directory
- No custom themes defined yet
- Using Asciidoctor-PDF defaults

**Tasks:**
- [ ] Create `arc42-theme.yml` for Asciidoctor-PDF
- [ ] Design consistent branding (colors, fonts, layout)
- [ ] Create language-specific themes (font selection)
- [ ] Add option in config to select theme per language
- [ ] Document theme customization
- [ ] Test with all languages

**Resources Needed:**
- Design input from arc42 team
- PDF theme YAML documentation

**Acceptance Criteria:**
- [ ] Professional-looking PDFs
- [ ] Consistent branding across outputs
- [ ] Easy to customize per deployment

---

### 3.3 Confluence Integration

**Status:** ⚠️ Format exists, no automation
**Priority:** Medium
**Effort:** Medium (1 week)

**Current State:**
- ✅ Confluence XHTML output format implemented
- ❌ No automated upload to Confluence

**Tasks:**
- [ ] Research Confluence REST API
- [ ] Add CLI command: `confluence-publish`
- [ ] Configuration:
  ```yaml
  confluence:
    url: https://company.atlassian.net
    space_key: ARC42
    parent_page_id: 123456
    credentials: env:CONFLUENCE_TOKEN
  ```
- [ ] Authenticate with API token
- [ ] Create/update pages programmatically
- [ ] Handle attachments (diagrams)
- [ ] Support dry-run mode

**Challenges:**
- Authentication complexity
- Confluence API rate limits
- Version conflict handling

**Acceptance Criteria:**
- [ ] One-command publish to Confluence
- [ ] Updates existing pages without duplicates
- [ ] Preserves page hierarchy

---

### 3.4 Web Preview Server

**Status:** ❌ Not started
**Priority:** Low-Medium
**Effort:** Low (2-3 days)

**Description:**
Local web server to preview generated HTML outputs.

**Tasks:**
- [ ] Add CLI command: `serve`
- [ ] Simple HTTP server (Python http.server)
- [ ] Serve `workspace/build/` directory
- [ ] Live reload on file changes (optional)
- [ ] Dockerfile EXPOSE port 8080
- [ ] Update docker-compose.yaml with port mapping

**Usage:**
```bash
make serve
# Opens browser to http://localhost:8080/EN/withHelp/html/
```

**Acceptance Criteria:**
- [ ] Preview HTML outputs in browser
- [ ] Easy to test changes locally

---

## 4. Low Priority (Future Exploration)

### 4.1 Draw.io Diagram Regeneration

**Status:** ❌ Not started
**Priority:** Low
**Effort:** High (2-3 weeks)

**Description:**
Automatically regenerate PNG/JPG diagrams from `.drawio` source files.

**Tasks:**
- [ ] Add draw.io CLI to Docker image
- [ ] Detect `.drawio` files in templates
- [ ] Export to PNG/JPG during build
- [ ] Support multi-page diagrams
- [ ] Validate exported images
- [ ] Handle localized diagram sources

**Challenges:**
- draw.io CLI is Node.js-based (adds complexity)
- Large diagrams may have rendering issues
- Versioning: when to regenerate?

**Decision:** Defer until community requests

---

### 4.2 Interactive Documentation Site

**Status:** ❌ Not started
**Priority:** Low
**Effort:** High (1+ months)

**Vision:**
A searchable, interactive website for browsing arc42 template in all languages and formats.

**Features:**
- [ ] Search across all languages
- [ ] Format switcher (view as HTML/PDF/Markdown)
- [ ] Translation comparison (side-by-side EN/DE)
- [ ] Downloadable artifacts
- [ ] Generated from build artifacts

**Technologies:**
- Static site generator (VuePress, Docusaurus, etc.)
- Algolia search
- GitHub Pages deployment

**Decision:** Separate project, not part of build system core

---

### 4.3 Metrics and Analytics

**Status:** ❌ Not started
**Priority:** Low
**Effort:** Medium (1 week)

**Ideas:**
- Track download counts per format
- Most popular languages
- Build time metrics over releases
- Output file sizes over time

**Implementation:**
- GitHub Releases API for download counts
- Prometheus metrics during builds
- Grafana dashboards (optional)

---

## 5. Technical Debt

### 5.1 Type Hints and Type Checking

**Status:** ⚠️ Partial
**Current:** Some type hints, no checking
**Target:** Full type coverage with mypy

**Tasks:**
- [ ] Add type hints to all functions
- [ ] Add mypy to dependencies
- [ ] Configure mypy.ini
- [ ] Run mypy in CI/CD
- [ ] Fix all type errors

**Benefit:** Catch bugs at development time, better IDE support

---

### 5.2 Error Handling Consistency

**Status:** ⚠️ Inconsistent
**Current:** Mix of exceptions, subprocess errors
**Target:** Unified error handling strategy

**Tasks:**
- [ ] Define custom exception hierarchy
  ```python
  class BuildError(Exception): ...
  class ValidationError(BuildError): ...
  class ConverterError(BuildError): ...
  ```
- [ ] Standardize error messages
- [ ] Add error codes for documentation
- [ ] Improve subprocess error capture

---

### 5.3 Configuration Schema Validation

**Status:** ⚠️ Basic validation only
**Current:** YAML loaded, minimal checks
**Target:** JSON Schema validation

**Tasks:**
- [ ] Create `config/schema.json`
- [ ] Validate YAML against schema on load
- [ ] Add schema to documentation
- [ ] Generate TypeScript types from schema (for tooling)

---

### 5.4 Logging Improvement

**Status:** ⚠️ Functional but basic
**Current:** Python logging with console output
**Target:** Structured logging with file output

**Tasks:**
- [ ] Add JSON log format option
- [ ] Write logs to `workspace/logs/build.log`
- [ ] Separate logs per converter
- [ ] Add log rotation
- [ ] Improve log levels (less noise in INFO)

---

## 6. Known Issues

### 6.1 PDF Metadata Timestamps

**Issue:** PDFs have timestamps, breaking deterministic builds
**Impact:** Low (content is deterministic)
**Workaround:** Compare PDF content, not bytes
**Fix:** Configure Asciidoctor-PDF to use SOURCE_DATE_EPOCH
**Priority:** Low

---

### 6.2 Confluence Converter Requires Manual Gem Install

**Issue:** `asciidoctor-confluence` not in Dockerfile by default
**Impact:** Confluence format fails without manual installation
**Fix:** Already in Dockerfile line 64
**Status:** ✅ Resolved

---

### 6.3 Large Docker Image Size

**Issue:** Image is ~2 GB (fonts + tools)
**Impact:** Slow first build, large downloads
**Mitigation:** Multi-stage builds
**Status:** Acceptable for now
**Priority:** Medium (optimize in 0.3.0)

---

### 6.4 No Windows Native Support

**Issue:** Requires Docker Desktop or WSL2 on Windows
**Impact:** Windows users need extra setup
**Mitigation:** Well-documented in README
**Fix:** Not planned (Docker-only by design)
**Status:** Won't fix

---

## 7. Ideas and Proposals

### 7.1 Plugin System for External Converters

**Idea:** Allow users to add custom converters without modifying core code.

**Approach:**
- Converters in `~/.arc42-builder/plugins/`
- Loaded dynamically at runtime
- Configuration:
  ```yaml
  plugins:
    - custom_format
  ```

**Benefit:** Community can create formatters without PRs
**Risk:** Security (arbitrary code execution)
**Status:** Under consideration

---

### 7.2 Build Caching Service

**Idea:** Cache build artifacts in cloud for faster rebuilds.

**Use Case:** CI/CD builds same commit multiple times
**Approach:** S3-compatible storage, hash-based cache keys
**Benefit:** 10x faster CI builds
**Complexity:** High
**Status:** Nice-to-have for large-scale deployments

---

### 7.3 Translation Management Integration

**Idea:** Integration with Crowdin, Lokalise, or POEditor for managing translations.

**Benefit:** Easier community contributions
**Challenge:** AsciiDoc not well-supported by TMS
**Status:** Research phase

---

### 7.4 Automated Accessibility Checks

**Idea:** Validate HTML/PDF for accessibility (WCAG compliance).

**Tools:**
- axe-core for HTML
- PDF/UA validation for PDFs

**Benefit:** Inclusive documentation
**Status:** Future exploration

---

## Prioritization Matrix

```
              │ Low Effort  │ Medium Effort  │ High Effort
──────────────┼─────────────┼────────────────┼──────────────
High Impact   │ CI/CD (1.2) │ Testing (1.1)  │ LaTeX (2.1)
              │             │ HTML MP (1.3)  │
──────────────┼─────────────┼────────────────┼──────────────
Medium Impact │ Web Server  │ PDF Themes     │ Draw.io (4.1)
              │ (3.4)       │ (3.2)          │ req42 (3.1)
              │             │ Validation     │
              │             │ (2.2)          │
──────────────┼─────────────┼────────────────┼──────────────
Low Impact    │ Type Hints  │ Confluence     │ Site (4.2)
              │ (5.1)       │ Publish (3.3)  │
              │ Logging     │                │
              │ (5.4)       │                │
```

---

## Roadmap

### Version 0.2.1 (Next Patch) - Target: December 2025
- [ ] Testing infrastructure (1.1)
- [ ] CI/CD pipeline (1.2)
- [ ] Fix known issues (6.2, 6.3)

### Version 0.3.0 (Next Minor) - Target: Q1 2026
- [ ] Multi-page HTML (1.3)
- [ ] LaTeX support (2.1)
- [ ] Enhanced validation (2.2)
- [ ] Performance optimization (2.4)

### Version 1.0.0 (Stable) - Target: Q2 2026
- [ ] All critical path items complete
- [ ] Comprehensive test coverage
- [ ] Production CI/CD
- [ ] Stable API and configuration format

### Version 1.x (Future)
- [ ] req42 support (3.1)
- [ ] Custom PDF themes (3.2)
- [ ] Confluence automation (3.3)
- [ ] Diagram localization (2.3)

---

## Contributing

To propose a new TODO or update status:

1. Edit this file
2. Update relevant section
3. Update roadmap if priority changes
4. Commit with message: `docs: Update future-todos - <brief description>`

For major features, create an issue first for discussion.

---

**Document Maintainers:** arc42 core team
**Last Review:** 2025-11-18
**Next Review:** After 0.2.1 release
