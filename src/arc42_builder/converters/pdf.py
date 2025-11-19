import subprocess
from pathlib import Path
import logging
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class PdfConverter(ConverterPlugin):
    def __init__(self):
        super().__init__("pdf", priority=1)

    def check_dependencies(self) -> bool:
        try:
            result = subprocess.run(
                ["asciidoctor-pdf", "--version"],
                capture_output=True,
                check=True,
                text=True
            )
            logger.info(f"Found Asciidoctor PDF: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Asciidoctor PDF not found. Please ensure it is installed.")
            return False

    def convert(self, context: BuildContext) -> Path:
        output_file = (context.output_dir / f"arc42-template-{context.language}-{context.flavor}.pdf").absolute()

        cmd = [
            "asciidoctor-pdf",
            "-b", "pdf",
            "-o", str(output_file)
        ]

        attributes = {
            'revnumber': context.version_props.get('revnumber', ''),
            'revdate': context.version_props.get('revdate', ''),
            'revremark': context.version_props.get('revremark', ''),
            'flavor': context.flavor
        }
        
        if context.flavor == "withHelp":
            attributes['show-help'] = ''

        # Theme detection with smart fallback strategy
        # 1. Check for template-specific theme
        template_theme_path = context.source_dir / "pdf-theme" / f"{context.language.lower()}-theme.yml"
        template_fonts_dir = context.source_dir / "pdf-theme" / "fonts"

        # TEMPORARY: Disable custom themes due to font file naming issues
        # TODO: Fix font file paths in theme files to match actual Ubuntu font locations
        use_custom_themes = False

        if use_custom_themes and template_theme_path.exists():
            # Use template-specific theme (highest priority)
            logger.info(f"Using template-specific PDF theme: {template_theme_path}")
            attributes['pdf-theme'] = str(template_theme_path.absolute())
            if template_fonts_dir.exists():
                attributes['pdf-fontsdir'] = str(template_fonts_dir.absolute())
        else:
            # Use Asciidoctor PDF default theme
            # The built-in theme works with system fonts automatically
            logger.info(f"Using Asciidoctor PDF default theme for language {context.language}")

        # Add language-specific scripts
        if context.language in ['ZH', 'JA', 'KO']:
            attributes['scripts'] = 'cjk'
        elif context.language in ['RU', 'UKR']:
            attributes['scripts'] = 'cyrillic'

        for key, value in attributes.items():
            if value:
                cmd.extend(["-a", f"{key}={value}"])
            else:
                cmd.extend(["-a", key])
        
        cmd.append(str(context.source_dir / "arc42-template.adoc"))
        
        logger.debug(f"Executing command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully created PDF file: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            logger.error(f"PDF conversion failed for {context.language}-{context.flavor}")
            logger.error(f"Command: {' '.join(cmd)}")
            if e.stdout:
                logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logger.error(f"STDERR: {e.stderr}")
            raise

    def _select_theme_for_language(self, language: str, themes_dir: Path) -> Path:
        """
        Select appropriate PDF theme based on language and script type.

        Uses script-based fallback strategy:
        - Latin scripts (EN, DE, FR, ES, IT, PT, CZ, NL) → en-theme.yml
        - Cyrillic scripts (UKR, RU) → ukr-theme.yml
        - CJK scripts (ZH, JA, KO) → zh-theme.yml
        - Unknown → default-theme.yml

        Args:
            language: Language code (e.g., "EN", "UKR", "ZH")
            themes_dir: Directory containing theme files

        Returns:
            Path to the selected theme file
        """
        lang = language.upper()

        # Language to script mapping
        LATIN_SCRIPTS = {'EN', 'DE', 'FR', 'ES', 'IT', 'PT', 'CZ', 'NL'}
        CYRILLIC_SCRIPTS = {'UKR', 'RU'}
        CJK_SCRIPTS = {'ZH', 'JA', 'KO'}

        # Determine theme based on script type
        if lang in LATIN_SCRIPTS:
            theme_name = "en-theme.yml"
        elif lang in CYRILLIC_SCRIPTS:
            theme_name = "ukr-theme.yml"
        elif lang in CJK_SCRIPTS:
            theme_name = "zh-theme.yml"
        else:
            # Fallback for unknown languages
            theme_name = "default-theme.yml"
            logger.info(f"Language '{lang}' not mapped to specific theme, using default")

        theme_path = themes_dir / theme_name

        # If the selected theme doesn't exist, fall back to default
        if not theme_path.exists():
            logger.warning(f"Theme {theme_name} not found, falling back to default")
            theme_path = themes_dir / "default-theme.yml"

        return theme_path
