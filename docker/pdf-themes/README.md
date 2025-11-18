# arc42 PDF Themes

This directory contains language-specific PDF themes for arc42 template generation.

## Available Themes

### `en-theme.yml` - Latin Scripts
**Languages:** EN, DE, FR, ES, IT, PT, CZ, NL
**Fonts:** Liberation Sans, DejaVu Sans, Liberation Mono

### `ukr-theme.yml` - Cyrillic Scripts
**Languages:** UKR, RU
**Fonts:** Noto Sans, DejaVu Sans, Noto Mono

### `zh-theme.yml` - CJK Scripts
**Languages:** ZH (Chinese), JA (Japanese), KO (Korean)
**Fonts:** Noto Sans CJK SC, Noto Sans, Noto Mono

### `default-theme.yml` - Universal Fallback
**Languages:** Any (fallback for unlisted languages)
**Fonts:** Noto Sans, DejaVu Sans, Noto Mono

## Theme Selection Logic

The build system uses **script-based fallback**:
- Latin scripts (EN, DE, FR, ES, IT, PT, CZ, NL) → `en-theme.yml`
- Cyrillic scripts (UKR, RU) → `ukr-theme.yml`
- CJK scripts (ZH, JA, KO) → `zh-theme.yml`
- Unknown → `default-theme.yml`
