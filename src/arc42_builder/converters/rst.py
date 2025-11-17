import subprocess
from pathlib import Path
import logging
from .base import ConverterPlugin, BuildContext

logger = logging.getLogger(__name__)

class RstConverter(ConverterPlugin):
    """reStructuredText (RST) converter for Sphinx and Python documentation"""

    def __init__(self):
        super().__init__("rst", priority=3)

    def check_dependencies(self) -> bool:
        try:
            subprocess.run(["asciidoctor", "--version"], capture_output=True, check=True)
            subprocess.run(["pandoc", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("RST conversion requires both Asciidoctor and Pandoc.")
            return False

    def convert(self, context: BuildContext) -> Path:
        """Convert to reStructuredText format"""
        output_file = (context.output_dir / f"arc42-template-{context.language}-{context.flavor}.rst").absolute()
        main_adoc_file = context.source_dir / "arc42-template.adoc"

        # Create a temporary HTML file via Asciidoctor
        temp_html_file = (context.output_dir / f"temp-{context.language}-{context.flavor}.html").absolute()

        # Set absolute path to images directory
        images_dir = context.source_dir / "images"

        asciidoctor_cmd = [
            "asciidoctor",
            "-b", "html5",
            "-a", f"flavor={context.flavor}",
            "-a", f"imagesdir={images_dir.absolute()}",
            str(main_adoc_file),
            "-o", str(temp_html_file)
        ]

        if context.flavor == "withHelp":
            asciidoctor_cmd.append("-a show-help")

        logger.debug(f"Executing Asciidoctor for intermediate HTML: {' '.join(asciidoctor_cmd)}")
        subprocess.run(asciidoctor_cmd, check=True)

        # Convert the intermediate HTML to RST using Pandoc
        pandoc_cmd = [
            "pandoc",
            str(temp_html_file),
            "-f", "html",
            "-t", "rst",
            "--wrap=preserve",  # Preserve line wrapping
            "-o", str(output_file)
        ]

        logger.debug(f"Executing Pandoc for RST conversion: {' '.join(pandoc_cmd)}")
        subprocess.run(pandoc_cmd, check=True)

        # Clean up the temporary HTML file
        temp_html_file.unlink()

        logger.info(f"Successfully created RST file: {output_file}")
        return output_file

    def get_output_extension(self) -> str:
        return ".rst"
