import subprocess
from pathlib import Path
import logging
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class ConfluenceConverter(ConverterPlugin):
    """Confluence XHTML converter using Asciidoctor-Confluence"""

    def __init__(self):
        super().__init__("confluence", priority=2)

    def check_dependencies(self) -> bool:
        try:
            # Check for asciidoctor-confluence gem
            result = subprocess.run(
                ["gem", "list", "asciidoctor-confluence"],
                capture_output=True,
                check=True,
                text=True
            )
            if "asciidoctor-confluence" not in result.stdout:
                logger.error("asciidoctor-confluence gem not found. Install with: gem install asciidoctor-confluence")
                return False

            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("Confluence conversion requires Asciidoctor and asciidoctor-confluence gem.")
            return False

    def convert(self, context: BuildContext) -> Path:
        """Convert to Confluence XHTML format"""
        output_file = (context.output_dir / f"arc42-template-{context.language}-{context.flavor}.xhtml").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"

        # Set absolute path to images directory
        images_dir = context.source_dir / "images"

        # Build asciidoctor command with Confluence backend
        cmd = [
            "asciidoctor",
            "-r", "asciidoctor-confluence",
            "-b", "confluence",
            "-a", f"revnumber={context.version_props.get('revnumber', '')}",
            "-a", f"revdate={context.version_props.get('revdate', '')}",
            "-a", f"flavor={context.flavor}",
            "-a", f"imagesdir={images_dir.absolute()}",
            "-o", str(output_file),
            str(main_adoc_file)
        ]

        if context.flavor == "withHelp":
            cmd.append("-a show-help")

        logger.debug(f"Executing command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        logger.info(f"Successfully created Confluence XHTML file: {output_file}")
        return output_file

    def get_output_extension(self) -> str:
        return ".xhtml"
