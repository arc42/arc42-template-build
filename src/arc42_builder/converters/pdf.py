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
        output_file = context.output_dir / f"arc42-template-{context.language}-{context.flavor}.pdf"

        # Determine the images directory path
        # Images are in the template root, not in the language-specific directory
        images_dir = context.source_dir.parent.parent / "images"

        cmd = [
            "asciidoctor-pdf",
            "-b", "pdf",
            "-D", str(context.output_dir),
            "-o", str(output_file)
        ]

        attributes = {
            'revnumber': context.version_props.get('revnumber', ''),
            'revdate': context.version_props.get('revdate', ''),
            'revremark': context.version_props.get('revremark', ''),
            'flavor': context.flavor,
            # Fix image paths - override imagesdir to point to actual images location
            'imagesdir': str(images_dir)
        }
        
        if context.flavor == "withHelp":
            attributes['show-help'] = ''

        # Logic for theme detection from the proposal
        theme_yml_path = context.source_dir.parent / "pdf-theme" / f"{context.language.lower()}-theme.yml"
        fonts_dir = context.source_dir.parent / "pdf-theme" / "fonts"
        
        if theme_yml_path.exists():
            logger.info(f"Loading PDF theme from {theme_yml_path}")
            attributes['pdf-theme'] = str(theme_yml_path.absolute())
            if fonts_dir.exists():
                attributes['pdf-fontsdir'] = str(fonts_dir.absolute())
        else:
            logger.warning(f"No language-specific PDF theme found at {theme_yml_path}. Using default.")

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
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"PDF generation failed: {result.stderr}")
        
        logger.info(f"Successfully created PDF file: {output_file}")
        return output_file
