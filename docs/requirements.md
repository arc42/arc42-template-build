# arc42-template-build – Requirements Specification

**Template:** req42-inspired structure
**Version:** 0.2.0
**Last Updated:** 2025-11-18
**Status:** Active

---

## 1. Business Requirements

### 1.1 Purpose

arc42-template-build provides an automated, reproducible build system for generating the arc42 architecture documentation template in multiple languages and formats.

### 1.2 Business Goals

| ID | Goal | Success Criteria |
|----|------|------------------|
| BG-1 | **Automated Releases** | Full build completes in <10 minutes |
| BG-2 | **Multi-Format Support** | Support 10+ output formats |
| BG-3 | **Multi-Language Support** | Support 11 languages with proper fonts |
| BG-4 | **Zero Installation Friction** | Only Docker required on host |
| BG-5 | **Extensibility** | New format added in <2 hours |

### 1.3 Stakeholder Needs

| Stakeholder | Need | Priority |
|-------------|------|----------|
| **arc42 Core Team** | Reliable, reproducible releases | High |
| **Translators** | Validation of translations, missing images | High |
| **Template Users** | High-quality PDF, Markdown, DOCX outputs | High |
| **Contributors** | Easy-to-understand, maintainable codebase | Medium |
| **CI/CD Systems** | Scriptable, headless execution | Medium |

---

## 2. Functional Requirements

### 2.1 Core Build Capabilities

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1 | Generate HTML (single-page) output | Must | ✅ Implemented |
| FR-2 | Generate PDF with full Unicode font support | Must | ✅ Implemented |
| FR-3 | Generate Microsoft Word (DOCX) output | Must | ✅ Implemented |
| FR-4 | Generate Markdown (GitHub-flavored) output | Must | ✅ Implemented |
| FR-5 | Generate multi-page Markdown output | Must | ✅ Implemented |
| FR-6 | Generate AsciiDoc (bundled, self-contained) | Must | ✅ Implemented |
| FR-7 | Generate GitHub-optimized Markdown | Should | ✅ Implemented |
| FR-8 | Generate Confluence XHTML | Should | ✅ Implemented |
| FR-9 | Generate reStructuredText (RST) | Should | ✅ Implemented |
| FR-10 | Generate Textile markup | Could | ✅ Implemented |
| FR-11 | Generate LaTeX output | Could | ❌ Not implemented |
| FR-12 | Generate multi-page HTML | Could | ❌ Not implemented |

### 2.2 Content Variants

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-20 | Support `plain` flavor (skeleton only) | Must | ✅ Implemented |
| FR-21 | Support `withHelp` flavor (with guidance) | Must | ✅ Implemented |
| FR-22 | Visually distinguish help text in outputs | Should | ⚠️ Partial |

### 2.3 Multi-Language Support

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-30 | Build English (EN) templates | Must | ✅ Implemented |
| FR-31 | Build German (DE) templates | Must | ✅ Implemented |
| FR-32 | Build French, Spanish, Italian, Dutch, Portuguese | Should | ✅ Supported |
| FR-33 | Build Russian, Ukrainian (Cyrillic) | Should | ✅ Supported |
| FR-34 | Build Chinese (CJK fonts) | Should | ✅ Supported |
| FR-35 | Build Czech with proper diacritics | Should | ✅ Supported |

### 2.4 Validation and Quality

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-40 | Validate AsciiDoc include references | Must | ✅ Implemented |
| FR-41 | Detect missing images | Must | ✅ Implemented |
| FR-42 | Validate version.properties exists | Must | ✅ Implemented |
| FR-43 | Validate Markdown syntax post-build | Should | ✅ Implemented |
| FR-44 | Check required fonts installed | Should | ✅ Implemented |
| FR-45 | Lint AsciiDoc source files | Could | ❌ Not implemented |

### 2.5 Distribution and Packaging

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-50 | Create structured build output directory | Must | ✅ Implemented |
| FR-51 | Generate ZIP distributions per format | Must | ✅ Implemented |
| FR-52 | Preserve directory structure in ZIPs | Must | ✅ Implemented |
| FR-53 | Upload to GitHub Releases | Should | ❌ Not implemented |

---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Requirement | Target | Current |
|----|-------------|--------|---------|
| NFR-1 | Full build time (EN+DE, all formats) | <10 minutes | ~5 minutes |
| NFR-2 | Parallel build execution | 4 workers | ✅ 4 workers |
| NFR-3 | Memory usage per worker | <2 GB | ✅ ~500 MB |

### 3.2 Reliability

| ID | Requirement | Measure | Status |
|----|-------------|---------|--------|
| NFR-10 | **Reproducibility** | Identical outputs for same input | ✅ Achieved |
| NFR-11 | **Deterministic builds** | No random ordering/timestamps (except PDFs) | ✅ Achieved |
| NFR-12 | **Error recovery** | Continue on error, report all failures | ✅ Implemented |
| NFR-13 | **Validation before build** | Fail fast on missing dependencies | ✅ Implemented |

### 3.3 Maintainability

| ID | Requirement | Measure | Status |
|----|-------------|---------|--------|
| NFR-20 | **Code modularity** | Plugin architecture for converters | ✅ Implemented |
| NFR-21 | **Clear separation of concerns** | CLI / Core / Converters / Config | ✅ Implemented |
| NFR-22 | **Type hints** | Python type annotations | ⚠️ Partial |
| NFR-23 | **Logging** | Structured logs with levels | ✅ Implemented |
| NFR-24 | **Documentation** | Architecture docs, code comments | ✅ In progress |

### 3.4 Usability

| ID | Requirement | Measure | Status |
|----|-------------|---------|--------|
| NFR-30 | **Single-command build** | `make build` executes full build | ✅ Implemented |
| NFR-31 | **Helpful error messages** | File paths, line numbers in errors | ✅ Implemented |
| NFR-32 | **CLI help text** | `--help` for all commands | ✅ Implemented |
| NFR-33 | **Verbose mode** | `--verbose` flag for debugging | ✅ Implemented |

### 3.5 Portability

| ID | Requirement | Platform | Status |
|----|-------------|----------|--------|
| NFR-40 | Run on Linux | Docker Desktop, native | ✅ Supported |
| NFR-41 | Run on macOS | Docker Desktop | ✅ Supported |
| NFR-42 | Run on Windows | Docker Desktop, WSL2 | ✅ Supported |
| NFR-43 | Run in GitHub Codespaces | Cloud dev environment | ✅ Supported |
| NFR-44 | Run in CI/CD (GitHub Actions) | Automated pipelines | ⚠️ No workflow yet |

---

## 4. System Requirements

### 4.1 Software Dependencies (Inside Container)

| Component | Version | Purpose |
|-----------|---------|---------|
| Ubuntu | 22.04 LTS | Base OS |
| Python | 3.11+ | Orchestration |
| Ruby | Latest (apt) | Asciidoctor runtime |
| Asciidoctor | 2.0.20 | AsciiDoc processing |
| Asciidoctor-PDF | 2.3.10 | PDF generation |
| Asciidoctor-Confluence | 0.0.2 | Confluence output |
| Pandoc | Latest (apt) | Format conversion |
| Fonts (Noto, Liberation, etc.) | Latest (apt) | Unicode rendering |

### 4.2 Host Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Docker | 20.10+ | Latest stable |
| Docker Compose | 2.0+ | Latest stable |
| Disk space | 5 GB | 10 GB |
| RAM | 4 GB | 8 GB |
| CPU | 2 cores | 4+ cores |

---

## 5. Configuration Requirements

### 5.1 Configuration File

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| CR-1 | YAML configuration format | Must | ✅ Implemented |
| CR-2 | Select languages to build | Must | ✅ Implemented |
| CR-3 | Enable/disable formats | Must | ✅ Implemented |
| CR-4 | Select flavors to build | Must | ✅ Implemented |
| CR-5 | Format-specific options (PDF page size, etc.) | Should | ✅ Implemented |
| CR-6 | Parallel build settings (max workers) | Should | ✅ Implemented |
| CR-7 | Logging configuration | Should | ✅ Implemented |
| CR-8 | Validation options | Should | ✅ Implemented |

### 5.2 Command-Line Overrides

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| CR-10 | Override languages via CLI | Should | ✅ Implemented |
| CR-11 | Override formats via CLI | Should | ✅ Implemented |
| CR-12 | Override flavors via CLI | Should | ✅ Implemented |
| CR-13 | Build all vs. selective build | Must | ✅ Implemented |

---

## 6. Interface Requirements

### 6.1 Command-Line Interface

| Command | Purpose | Priority | Status |
|---------|---------|----------|--------|
| `build` | Build templates | Must | ✅ Implemented |
| `validate` | Pre-build validation only | Must | ✅ Implemented |
| `test-artifacts` | Validate build outputs | Should | ✅ Implemented |
| `dist` | Create ZIP distributions | Should | ✅ Implemented |
| `test` | Run test suite | Should | ✅ Implemented |
| `list-formats` | Show available formats | Should | ✅ Implemented |

### 6.2 Makefile Targets

| Target | Purpose | Priority | Status |
|--------|---------|----------|--------|
| `make build` | Full build | Must | ✅ Implemented |
| `make validate` | Validation only | Should | ✅ Implemented |
| `make test-build-artifacts` | Validate outputs | Should | ✅ Implemented |
| `make dist` | Create distributions | Should | ✅ Implemented |
| `make clean` | Remove outputs | Should | ✅ Implemented |
| `make shell` | Debug container | Should | ✅ Implemented |

### 6.3 File System Interface

**Input:**
- `arc42-template/` - Submodule with AsciiDoc sources
- `config/build.yaml` - Configuration file

**Output:**
- `workspace/build/{LANG}/{FLAVOR}/{FORMAT}/` - Generated files
- `workspace/dist/{LANG}/{FLAVOR}/{FORMAT}/*.zip` - ZIP archives
- `workspace/logs/` - Build logs

---

## 7. Data Requirements

### 7.1 Input Data

| Data Type | Source | Format | Required |
|-----------|--------|--------|----------|
| AsciiDoc sources | `arc42-template/{LANG}/` | `.adoc` | Yes |
| Version metadata | `version.properties` | Java properties | Yes |
| Images/diagrams | `arc42-template/images/` | PNG, JPG | No |
| Configuration | `config/build.yaml` | YAML | Yes |

### 7.2 Output Data

| Data Type | Location | Format | Naming Convention |
|-----------|----------|--------|-------------------|
| HTML files | `build/{LANG}/{FLAVOR}/html/` | `.html` | `arc42-template-{LANG}-{FLAVOR}.html` |
| PDF files | `build/{LANG}/{FLAVOR}/pdf/` | `.pdf` | `arc42-template-{LANG}-{FLAVOR}.pdf` |
| Markdown files | `build/{LANG}/{FLAVOR}/markdown/` | `.md` | `arc42-template-{LANG}-{FLAVOR}.md` |
| ZIP archives | `dist/{LANG}/{FLAVOR}/{FORMAT}/` | `.zip` | `arc42-template-{LANG}-{FLAVOR}-{FORMAT}.zip` |

---

## 8. Constraints

### 8.1 Technical Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| TC-1 | Must use Docker for execution | Ensures reproducibility |
| TC-2 | Must use open-source tools only | No licensing costs, community support |
| TC-3 | Must not require network during build | Build isolation, reproducibility |
| TC-4 | Must support offline execution | CI environments may be airgapped |

### 8.2 Organizational Constraints

| ID | Constraint | Impact |
|----|------------|--------|
| OC-1 | Two-repository model (build separate from content) | Submodule management required |
| OC-2 | GitHub as primary platform | CI/CD tied to GitHub Actions |
| OC-3 | Community-maintained translations | Validation critical for quality |

### 8.3 Design Constraints

| ID | Constraint | Rationale |
|----|------------|-----------|
| DC-1 | Plugin architecture for converters | Extensibility requirement |
| DC-2 | Python as orchestration language | Better than shell for complexity |
| DC-3 | YAML for configuration | Human-readable, well-supported |

---

## 9. Acceptance Criteria

### 9.1 Build Completion

- [ ] Build completes without errors for EN and DE
- [ ] All enabled formats are generated
- [ ] Output files exist and are non-empty
- [ ] File naming convention is consistent

### 9.2 Validation

- [ ] Missing includes are detected before build
- [ ] Missing images are reported (warning)
- [ ] Required fonts are verified
- [ ] Markdown syntax is validated post-build

### 9.3 Quality

- [ ] PDF renders all Unicode characters correctly
- [ ] Markdown passes syntax validation
- [ ] HTML has valid structure (no broken links)
- [ ] DOCX opens in Microsoft Word without errors

### 9.4 Usability

- [ ] `make build` executes full build from clean state
- [ ] Error messages include file paths and actionable advice
- [ ] `--help` provides clear usage information
- [ ] Build logs are readable and informative

---

## 10. Open Issues and Decisions

### 10.1 Open Questions

| ID | Question | Status |
|----|----------|--------|
| OQ-1 | Should diagrams be regenerated from draw.io sources? | ❓ Under consideration |
| OQ-2 | Should translation completeness be validated? | ❓ Under consideration |
| OQ-3 | What level of PDF customization is needed? | ❓ Under consideration |

### 10.2 Deferred Requirements

| ID | Requirement | Reason | Target Version |
|----|-------------|--------|----------------|
| DR-1 | LaTeX output format | Low priority | 0.3.0 |
| DR-2 | Multi-page HTML | Requires significant work | 0.3.0 |
| DR-3 | Integration tests | Need Docker test fixtures | 0.2.1 |
| DR-4 | CI/CD pipeline | Blocked on testing | 0.2.1 |
| DR-5 | req42 template support | Separate template | 1.0.0 |

---

## Appendix A: Glossary

See main architecture documentation (`docs/architecture-documentation.md`) for complete glossary.

---

## Appendix B: Traceability Matrix

| Business Goal | Functional Requirements | Non-Functional Requirements |
|---------------|------------------------|----------------------------|
| BG-1 (Automated Releases) | FR-1 to FR-12, FR-50 to FR-53 | NFR-1, NFR-2, NFR-10 |
| BG-2 (Multi-Format) | FR-1 to FR-12 | NFR-20, NFR-21 |
| BG-3 (Multi-Language) | FR-30 to FR-35 | NFR-10, NFR-12 |
| BG-4 (Zero Installation) | - | NFR-40 to NFR-44 |
| BG-5 (Extensibility) | - | NFR-20, NFR-21, NFR-22 |

---

**Document Information:**
- **Based on:** Original requirements in `todo/1-refined-arc42_build_process_requirements.md`
- **Format:** req42-inspired structure
- **Maintained by:** arc42 core team
- **Review Cycle:** Before each release
