import subprocess
from pathlib import Path
import logging
import shutil
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

        # Copy images directory to output directory for relative referencing
        source_images_dir = context.source_dir / "images"
        output_images_dir = context.output_dir / "images"

        if source_images_dir.exists():
            if output_images_dir.exists():
                shutil.rmtree(output_images_dir)
            shutil.copytree(source_images_dir, output_images_dir)
            logger.debug(f"Copied images from {source_images_dir} to {output_images_dir}")

        # Build asciidoctor command with Confluence backend
        cmd = [
            "asciidoctor",
            "-r", "asciidoctor-confluence",
            "-b", "confluence",
            "-a", f"revnumber={context.version_props.get('revnumber', '')}",
            "-a", f"revdate={context.version_props.get('revdate', '')}",
            "-a", f"revremark={context.version_props.get('revremark', '')}",
            "-a", f"flavor={context.flavor}",
            # Use relative path to images directory
            "-a", "imagesdir=images",
            "-o", str(output_file),
            str(main_adoc_file)
        ]

        if context.flavor == "withHelp":
            cmd.append("-a show-help")

        logger.debug(f"Executing command: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Successfully created Confluence XHTML file: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            logger.error(f"Confluence conversion failed for {context.language}-{context.flavor}")
            logger.error(f"Command: {' '.join(cmd)}")
            if e.stdout:
                logger.error(f"STDOUT: {e.stdout}")
            if e.stderr:
                logger.error(f"STDERR: {e.stderr}")
            raise

    def get_output_extension(self) -> str:
        return ".xhtml"
